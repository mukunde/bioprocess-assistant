# FT01-FT12: reviewed frozen comparison

Current checkpoint: the twelve bilingual scenarios were reviewed with reservations
and the frozen comparison was completed once. S passes 24/24 language observations;
F0 passes 12/24, including 8/12 EN and 4/12 FR. Four of twelve bilingual pairs pass.
The declared complete-equivalence acceptance criterion is not met.

## Evidence and timeline

1. [Method](METHOD.md) and [lock](method-lock.json) were created before the exact
   questions and paired forms. [Preparation manifest](manifest.json),
   [cards](REVIEW.md), [references](references.json) and [template](review-template.json)
   retain their original pending labels as historical preparation snapshots.
2. The actual [review ledger](review.json), twelve individual decision records,
   [progress](REVIEW-PROGRESS.md), [summary](REVIEW-SUMMARY.md) and
   [completion check](review-completion.json) record all twelve real human approvals
   with exact quotations, reservations and content bindings. That completion check
   describes its pre-execution checkpoint; it is not a current no-run claim.
3. The [compact results](results.json) copy all 24 scored observations, the original
   attempt and completion records, and hashes of the native scores. The
   [results report](../../../docs/experiments/free-text-comparison-v01-results.md)
   explains the failures and the scorer's unassessed `execution_error` placeholder.
   There were zero actual execution exceptions and zero network attempts.

The [package manifest](package-manifest.json) binds this delivery, including the
unaltered original method/data/review files. It does not replace the earlier lock.
All 48 raw outputs remain local and unchanged, outside Git. Their LF hashes are in
the [results audit](../../../docs/experiments/free-text-comparison-v01-results-checks.json).

E118-I and E121-EQ remain excluded. No source approval or scientific validation is
inferred. This code/source-aware set is diagnostic evidence, not a blinded external
benchmark. After being consulted for v02 repairs it is development/regression data
for that candidate; the original 12/24 result remains historical evidence for v01.

## Verification

From the repository root, run pure package/scorer guards without executing arms:

```powershell
python -m unittest tests.test_free_text_evaluation -q
```

The default `python -m experiments.cytiva.free_text_evaluation` checks the frozen
method and preparation files only. Its returned pending review label refers to the
preparation snapshot; actual review completion and execution are separate records
linked above. The completed run is never automatically repeated by these checks.
