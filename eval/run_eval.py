"""Tool-level evaluation of the troubleshooting agent's retrieval.

Deterministic and free: it calls `query_graph` directly (no LLM) and checks
eligible English/explicit-query cases (excluding agent_only cases):
  - in_scope        -> the expected symptom is returned (found == True, right name)
  - in_domain_miss  -> nothing is returned (found == False, score under threshold)
  - out_of_scope    -> nothing is returned (the agent also refuses semantically, Rule 4)
  - off_topic       -> nothing is returned

This measures retrieval accuracy and refusal correctness, and validates the
score threshold calibration. The agent-level eval (hallucination, sourcing) is
a separate concern handled by the LLM-as-judge runner.

Usage:
    python eval/run_eval.py [--min-score 2.5]
Exit code is non-zero if any case fails (CI-friendly).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

# Make the project root importable so `tools` resolves when run as `python eval/run_eval.py`.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools import DEFAULT_MIN_MATCH_SCORE, query_graph  # noqa: E402

CASES_FILE = Path(__file__).resolve().parent / "cases.yaml"
REFUSAL_TYPES = {"in_domain_miss", "out_of_scope", "off_topic"}


def retrieval_cases(cases: list[dict]) -> list[dict]:
    """BM25 receives English phrases, not raw French or semantic scope decisions."""
    return [c for c in cases if not c.get("agent_only")
            and (c.get("lang") == "en" or c.get("retrieval_query"))]


def load_cases() -> list[dict]:
    data = yaml.safe_load(CASES_FILE.read_text(encoding="utf-8"))
    return data["cases"]


def evaluate(cases: list[dict], min_score: float) -> list[dict]:
    rows = []
    for c in cases:
        result = query_graph(c.get("retrieval_query", c["question"]), min_score=min_score)
        found = result["found"]
        score = result["match_score"]
        matched = result["symptom"]["name"] if found else None

        if c["type"] == "in_scope":
            ok = found and matched == c["expected_symptom"]
        else:  # any refusal type: the tool must NOT return a match
            ok = not found

        rows.append({
            "id": c["id"],
            "type": c["type"],
            "ok": ok,
            "score": score,
            "matched": matched,
            "expected": c.get("expected_symptom"),
        })
    return rows


def fmt_score(s) -> str:
    return f"{s:.2f}" if isinstance(s, (int, float)) else " -- "


def report(rows: list[dict], min_score: float) -> bool:
    by_type: dict[str, list[dict]] = {}
    for r in rows:
        by_type.setdefault(r["type"], []).append(r)

    print(f"\n=== Tool-level evaluation (min_score = {min_score:.2f}) ===\n")

    order = ["in_scope", "in_domain_miss", "out_of_scope", "off_topic"]
    labels = {
        "in_scope": "Retrieval accuracy (in-scope)",
        "in_domain_miss": "Refusal rate (in-domain miss)",
        "out_of_scope": "Refusal rate (out of scope)",
        "off_topic": "Refusal rate (off topic)",
    }
    for t in order:
        group = by_type.get(t, [])
        if not group:
            continue
        passed = sum(1 for r in group if r["ok"])
        print(f"  {labels[t]:<34} {passed}/{len(group)}")

    total = len(rows)
    total_ok = sum(1 for r in rows if r["ok"])
    print(f"\n  {'OVERALL':<34} {total_ok}/{total}\n")

    failures = [r for r in rows if not r["ok"]]
    if failures:
        print("  Failures:")
        for r in failures:
            if r["type"] == "in_scope":
                got = r["matched"] or "<no match>"
                print(f"    [{r['id']}] expected '{r['expected']}' "
                      f"but got '{got}' (score {fmt_score(r['score'])})")
            else:
                print(f"    [{r['id']}] should have refused but matched "
                      f"'{r['matched']}' (score {fmt_score(r['score'])})")
        print()
    else:
        print("  All cases pass.\n")

    return bool(rows) and not failures


def select_cases(cases: list[dict], limit: int) -> list[dict]:
    """First `limit` cases of each type for balanced coverage; 0 = all."""
    if not limit:
        return cases
    seen: dict[str, int] = {}
    out = []
    for c in cases:
        n = seen.get(c["type"], 0)
        if n < limit:
            out.append(c)
            seen[c["type"]] = n + 1
    return out


def run_agent_level(cases: list[dict], min_score: float) -> list[dict]:
    """Run the full agent on each case and have the LLM judge the answer.
    Costs API tokens (one agent run + one judge call per case)."""
    from agent import run_agent          # lazy import: pulls the Anthropic SDK
    from eval.judge import judge_response

    rows = []
    for i, c in enumerate(cases, 1):
        print(f"  [{i}/{len(cases)}] {c['id']} ...", flush=True)
        tool_outputs: list = []
        metadata: dict = {}
        text, _, _ = run_agent(c["question"], min_score=min_score,
                              tool_outputs=tool_outputs, answer_metadata=metadata)
        verdict = judge_response(c["question"], tool_outputs, text)
        contract_ok = (
            metadata.get("status") == "answer"
            and metadata.get("symptoms") == [c["expected_symptom"]]
        ) if c["type"] == "in_scope" else metadata.get("status") == "refuse"
        rows.append({**verdict, "id": c["id"], "type": c["type"],
                     "contract_ok": contract_ok})
    return rows


def report_agent(rows: list[dict]) -> bool:
    in_scope = [r for r in rows if r["type"] == "in_scope"]
    refusals = [r for r in rows if r["type"] != "in_scope"]

    print("\n=== Agent-level evaluation (LLM judge) ===\n")
    if in_scope:
        hf = sum(1 for r in in_scope if r["hallucination_free"])
        sc = sum(1 for r in in_scope if r["sources_cited"])
        ans = sum(1 for r in in_scope if r["refused"] is False)
        print(f"  In-scope ({len(in_scope)}):")
        print(f"    {'hallucination-free':<24} {hf}/{len(in_scope)}")
        print(f"    {'sources cited':<24} {sc}/{len(in_scope)}")
        print(f"    {'answered (not refused)':<24} {ans}/{len(in_scope)}")
    if refusals:
        rf = sum(1 for r in refusals if r["refused"])
        hf = sum(1 for r in refusals if r["hallucination_free"])
        print(f"\n  Refusals ({len(refusals)}):")
        print(f"    {'correctly refused':<24} {rf}/{len(refusals)}")
        print(f"    {'hallucination-free':<24} {hf}/{len(refusals)}")

    total_hf = sum(1 for r in rows if r["hallucination_free"])
    print(f"\n  {'OVERALL hallucination-free':<26} {total_hf}/{len(rows)}\n")

    problems = [
        r for r in rows
        if r.get("hallucination_free") is not True
        or r.get("sources_cited") is not True
        or r.get("contract_ok") is not True
        or (r["type"] == "in_scope" and (r.get("refused") is not False
                                             or r.get("answers_question") is not True))
        or (r["type"] != "in_scope" and r.get("refused") is not True)
    ]
    if problems:
        print("  Issues:")
        for r in problems:
            print(f"    [{r['id']}] contract_ok={r.get('contract_ok')}: {r.get('rationale', 'Missing verdict')}")
        print()
    else:
        print("  No hallucination, sourcing, or refusal issues.\n")
    return bool(rows) and not problems


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate the troubleshooting agent.")
    parser.add_argument("--min-score", type=float, default=DEFAULT_MIN_MATCH_SCORE,
                        help="Minimum Lucene score threshold (default: tool default).")
    parser.add_argument("--agent", action="store_true",
                        help="Also run the agent-level eval (LLM judge; costs API tokens).")
    parser.add_argument("--limit", type=int, default=0,
                        help="Limit to the first N cases per type (0 = all).")
    args = parser.parse_args()
    if args.limit < 0:
        parser.error("--limit must be non-negative")

    all_cases = load_cases()
    cases = select_cases(all_cases, args.limit)
    lexical_cases = select_cases(retrieval_cases(all_cases), args.limit)
    print(f"Lexical retrieval: {len(lexical_cases)} English/explicit-query cases; "
          f"bilingual and agent-only cases are evaluated with --agent.")
    rows = evaluate(lexical_cases, args.min_score)
    tool_ok = report(rows, args.min_score)

    agent_ok = True
    if args.agent:
        agent_ok = report_agent(run_agent_level(cases, args.min_score))

    return 0 if (tool_ok and agent_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
