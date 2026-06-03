"""Threshold calibration sweep for the retrieval match score.

For every case we fetch the *raw* top BM25 score once (querying with min_score=0),
then sweep the decision threshold in Python and recompute, at each threshold:

  - in-scope recall      : in-scope cases that still return the correct symptom
  - refusal accuracy      : refusal cases (miss / out-of-scope / off-topic) that
                            correctly return nothing
  - overall accuracy      : both combined

Low threshold  -> high recall, but refusals leak false positives.
High threshold -> clean refusals, but in-scope recall drops.
The plot makes this precision/recall frontier explicit and justifies (or
recalibrates) the default threshold.

Usage:
    python eval/threshold_sweep.py
Writes eval/threshold_calibration.png and prints a summary table.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import yaml  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools import DEFAULT_MIN_MATCH_SCORE, query_graph  # noqa: E402

CASES_FILE = Path(__file__).resolve().parent / "cases.yaml"
PLOT_FILE = Path(__file__).resolve().parent / "threshold_calibration.png"
THRESHOLDS = [round(i * 0.25, 2) for i in range(0, 25)]  # 0.00 .. 6.00


def load_cases() -> list[dict]:
    return yaml.safe_load(CASES_FILE.read_text(encoding="utf-8"))["cases"]


def raw_scores(cases: list[dict]) -> list[dict]:
    """One query per case at threshold 0 -> top score + best-matched symptom,
    independent of any decision threshold."""
    out = []
    for c in cases:
        r = query_graph(c["question"], min_score=0.0)
        out.append({
            "type": c["type"],
            "expected": c.get("expected_symptom"),
            "score": r["match_score"],          # None if no candidate at all
            "matched": r["symptom"]["name"] if r["found"] else None,
        })
    return out


def metrics_at(rows: list[dict], t: float) -> dict:
    in_scope = [r for r in rows if r["type"] == "in_scope"]
    refusals = [r for r in rows if r["type"] != "in_scope"]

    def fires(r):
        return r["score"] is not None and r["score"] >= t

    in_ok = sum(1 for r in in_scope if fires(r) and r["matched"] == r["expected"])
    ref_ok = sum(1 for r in refusals if not fires(r))
    return {
        "recall": in_ok / len(in_scope),
        "refusal": ref_ok / len(refusals),
        "overall": (in_ok + ref_ok) / len(rows),
    }


def main() -> int:
    cases = load_cases()
    rows = raw_scores(cases)

    recall, refusal, overall = [], [], []
    for t in THRESHOLDS:
        m = metrics_at(rows, t)
        recall.append(m["recall"])
        refusal.append(m["refusal"])
        overall.append(m["overall"])

    # Overall accuracy is flat over a wide range, so a plain argmax is misleading.
    # On that plateau we pick the *precision-optimal* point: the threshold with the
    # highest refusal accuracy (an anti-hallucination system prefers a clean refusal
    # over a confident wrong answer), tie-broken toward the lower threshold to keep
    # recall. On this data that lands on the empirically chosen default.
    max_overall = max(overall)
    plateau = [i for i, o in enumerate(overall) if abs(o - max_overall) < 1e-9]
    best_i = max(plateau, key=lambda i: (refusal[i], -THRESHOLDS[i]))
    best_t = THRESHOLDS[best_i]
    plateau_lo, plateau_hi = THRESHOLDS[plateau[0]], THRESHOLDS[plateau[-1]]

    print(f"\n=== Threshold sweep ({len(cases)} cases) ===\n")
    print(f"  {'thresh':>7} {'recall':>8} {'refusal':>8} {'overall':>8}")
    for i, t in enumerate(THRESHOLDS):
        mark = "  <- default" if t == DEFAULT_MIN_MATCH_SCORE else ""
        mark += "  *opt*" if i == best_i and t != DEFAULT_MIN_MATCH_SCORE else ""
        if t % 0.5 == 0 or t == DEFAULT_MIN_MATCH_SCORE or i == best_i:
            print(f"  {t:>7.2f} {recall[i]:>8.0%} {refusal[i]:>8.0%} {overall[i]:>8.0%}{mark}")
    print(f"\n  Overall accuracy peaks at {max_overall:.0%} on a plateau "
          f"[{plateau_lo:.2f} .. {plateau_hi:.2f}].")
    print(f"  Precision-optimal point (max refusal accuracy on the plateau): {best_t:.2f} "
          f"(recall {recall[best_i]:.0%}, refusal {refusal[best_i]:.0%}).")
    print(f"  Current default: {DEFAULT_MIN_MATCH_SCORE:.2f}\n")

    plt.figure(figsize=(8, 5))
    plt.plot(THRESHOLDS, recall, label="In-scope recall", color="#0E7C7B", marker="o", ms=3)
    plt.plot(THRESHOLDS, refusal, label="Refusal accuracy", color="#C2185B", marker="s", ms=3)
    plt.plot(THRESHOLDS, overall, label="Overall accuracy", color="#1F4E79", lw=2.5)
    plt.axvline(DEFAULT_MIN_MATCH_SCORE, color="gray", ls="--", lw=1,
                label=f"Default ({DEFAULT_MIN_MATCH_SCORE})")
    plt.axvline(best_t, color="#17A8A0", ls=":", lw=1.5, label=f"Precision-optimal ({best_t})")
    plt.xlabel("Match score threshold (min_score)")
    plt.ylabel("Rate")
    plt.title("Retrieval threshold calibration")
    plt.ylim(-0.03, 1.03)
    plt.grid(alpha=0.3)
    plt.legend(loc="lower center")
    plt.tight_layout()
    plt.savefig(PLOT_FILE, dpi=130)
    print(f"  Wrote {PLOT_FILE.name}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
