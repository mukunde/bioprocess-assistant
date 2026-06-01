"""Tool-level evaluation of the troubleshooting agent's retrieval.

Deterministic and free: it calls `query_graph` directly (no LLM) and checks,
for every case in cases.yaml:
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


def load_cases() -> list[dict]:
    data = yaml.safe_load(CASES_FILE.read_text(encoding="utf-8"))
    return data["cases"]


def evaluate(cases: list[dict], min_score: float) -> list[dict]:
    rows = []
    for c in cases:
        result = query_graph(c["question"], min_score=min_score)
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

    return not failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Tool-level eval of query_graph.")
    parser.add_argument("--min-score", type=float, default=DEFAULT_MIN_MATCH_SCORE,
                        help="Minimum Lucene score threshold (default: tool default).")
    args = parser.parse_args()

    cases = load_cases()
    rows = evaluate(cases, args.min_score)
    all_pass = report(rows, args.min_score)
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
