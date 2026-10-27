# Opt-in v02 freeze and FV01-FV12 paired review preparation

The opt-in candidate merged in PR47 is frozen by the new
[method lock](../../experiments/cytiva/free-text-v02-comparison-v01/method-lock.json),
created on 27 October 2026 at 00:28:51 UTC, before writing the exact new questions,
forms and references. It pins 44 files plus Python/dependency versions and the
offline tokenizer asset. The baseline is main `1696c69`, after PR46 and PR47.

The lock covers `FreeTextControlV02`, its versioned interpreter/bridge, shared
contracts/structured engine, source/catalog/review policy, scorer, runner and
[protocol](../../experiments/cytiva/free-text-v02-comparison-v01/METHOD.md).
Historical documents describing development/not-frozen v02 remain snapshots of
the earlier checkpoint; this new lock is the freeze authority. The older PR45
lock's internal legacy corrected-v02 name is distinct from this opt-in v02.

## New cases, all pending human review

There are **12 semantic scenarios, 24 language observations and 48 planned S/F0
arm executions**. Both EN/FR texts and structured forms need actual approval.
The complete [review cards](../../experiments/cytiva/free-text-v02-comparison-v01/REVIEW.md)
contain the proposed answers, required source bundles, exact original manual
quotations, Unicode input origins, reservations and points to validate.

| Case | New combination to review |
|---|---|
| FV01 | Three preparations: P washing, Q loading and independent R HIC principle, with reverse request/declaration order |
| FV02 | Q declared before P; P natural washing question precedes Q loading and washing requests |
| FV03 | P elution-buffer alternatives plus Q operating-elution flow, with operating elution excluded only for P |
| FV04 | Binding and elution buffer formulations as distinct items of P, plus a positive washing request and an inactive negated exclusion |
| FV05 | General maximum pressure before P loading flow, with independent Q washing endpoints |
| FV06 | Explicitly washing-specific P pressure versus general Q pressure and Q loading; distinguish unsupported selector from missing evidence |
| FV07 | Unknown column blocks P loading flow but allows P qualitative washing endpoints and independent Q HIC principle |
| FV08 | Conflicting 5 mL label and separate 1 mL column for P: hold both P procedural units under current policy, keep Q loading independent |
| FV09 | Observed zero, 2.5 mL available sample and unknown loaded volume, with separate loading/elution flow requests |
| FV10 | Separately supplied 5 mL column, washing CV and flow, plus an independent IEX principle with supplied conditional false |
| FV11 | Quarantined P equilibration, supported P elution and independent Q loading |
| FV12 | Quarantined equilibration and bounded missing general pressure together, with washing and independent SEC still supported |

These are new combinations over the same known eligible corpus, written by the
same code/source-aware author. They are prospective diagnostic material, not a
blinded external validation set. No candidate run was used to select wording.
Natural constructions that the bounded grammar may reject remain in the dataset.
FT01-FT12 and prior IF checks are development evidence, outside this denominator.

## Boundaries to preserve during review

- Validate both actual language texts against the proposed structured meaning;
  source support alone does not establish text/form equivalence.
- Preserve task/item order, separate preparation ownership, explicit versus
  qualified-label column assertions, exact numeric roles and complete negation.
- Keep binding/elution alternatives separate without pairing or nomenclature
  correction. No duration, CV-to-mL conversion or universal drops/min conversion.
- FV07 is missing context; FV08 is contradictory context. The reviewed conservative
  policy may block an entire product-specific scope for the latter. This is not a
  scientific necessity assertion and must not silently change the frozen method.
- FV06 distinguishes explicit phase-qualified unsupported representation from
  general pressure absence. Pressure absence is bounded to the exact 25 eligible
  excerpts, never the entire manual.
- E118-I and E121-EQ remain excluded. No new source approval, scientific suitability
  conclusion, diagnostic certainty or recipe choice follows from these questions.
- Keep all units counted when some need clarification, are unsupported, missing
  or quarantined; independently supported siblings remain required.

## Static verification and future execution

The default command verifies hashes, schemas, source provenance, dependencies,
origin geometry and reference inventory only:

```powershell
python -m experiments.cytiva.free_text_v02_evaluation
```

Ten [guard/scorer tests](../../tests/test_free_text_v02_evaluation.py) pass without
initializing a real runtime or evaluating a new input. They also verify that the
actual pending template is rejected before initialization/output creation and
that a mocked future factory selects v02 rather than the default v01.

The [preparation checks](free-text-v02-comparison-v01-preparation.json) retain the
lock/data fingerprints and preservation checks. The prior 669-test merged-main
result remains historical integration evidence. The full runtime suite is not
rerun as preparation for this new set.

There is no comparison output directory. A future run needs all twelve actual
human pair approvals and a separate execution instruction. It will use a new
exclusive directory, alternate first arm by case parity, save all 48 outputs before
scoring and retain errors without retry or overwrite. Run with `PYTHONHASHSEED=0`
in the pinned Python environment. Any later repair needs a new named checkpoint.

The former frozen trial/results, all previously tracked files and the 16 older
local notes remain unchanged. No LLM or paid API is used in preparation.
