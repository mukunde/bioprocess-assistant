# Corrected EN/FR freeze and paired question preparation

Current checkpoint: the corrected runtime merged in PR #45 is frozen by the
[method lock](../../experiments/cytiva/free-text-comparison-v01/method-lock.json).
The user requested this freeze and new questions explicitly. The lock was created
on 26 October 2026 at 19:53:09 UTC, before authoring the new exact questions/forms/
references. It binds 40 files, the shared six-root/2,048-token budgets, source
policy, comparator, Python/dependency versions and offline tokenizer asset.

This is a method freeze, not a completed evaluation or approval of the new gold.
Older documents/policy labels describing a not-yet-frozen candidate remain their
historical snapshot; this lock is the new freeze record. No pinned byte is edited
just to change a status label. Candidate repair requires another named freeze.

## New draft paired set

There are **12 bilingual scenarios**, **24 language observations** and **48 planned
S/F0 arm executions**. All twelve actual human pair reviews are pending.

| Case | Family | Main review point |
|---|---|---|
| FT01 | Multi-task ownership | E washing flow versus D endpoints; preserve declaration order despite reverse request order |
| FT02 | Multi-task ownership | E loading flow versus D washing flow; keep formats and stages separate |
| FT03 | Stage/formulation | D loading flow versus washing column volumes; no duration or CV conversion |
| FT04 | Stage/formulation | Elution-buffer preparation remains requested despite excluding operating elution |
| FT05 | Negation/restrictions | Positive D flow survives a same-sentence endpoint ban; independent E SEC principle |
| FT06 | Negation/restrictions | Negated loading-flow ban remains inactive; operating-elution ban stays active |
| FT07 | Facts/uncertainty | Unknown column with 7.5 mL available sample and unknown loaded volume; E SEC stays independent |
| FT08 | Facts/uncertainty | Qualified 1 mL label conflicts with explicit 5 mL column; E remains independently answerable |
| FT09 | Numeric roles | Observed zero is not missing or prescribed flow; E conditional false scenario and HIC principle |
| FT10 | Numeric roles | Available sample volume, unknown loaded volume and qualified column size remain distinct |
| FT11 | Partial support/policy | Washing flow and IEX principle supported; maximum pressure absent only from the 25 eligible excerpts |
| FT12 | Partial support/policy | Equilibration remains quarantined; loading and independent binding formulation remain eligible |

FT07/FT08 supply two real context ambiguities representable by the existing form.
FT11/FT12 are two explicit mixed-support cases. No unresolved-owner scenario is
forced into an invented valid structured form. The new texts are post-freeze
wording/recombinations over the same known corpus, authored by the same code-aware
assistant: they are prospective diagnostic material, not blinded independent
validation. Natural wording outside the bounded grammar is retained and may fail;
the candidate is not tuned or the case discarded in response.

Start the [human review cards FT01-FT12](../../experiments/cytiva/free-text-comparison-v01/REVIEW.md).
They contain both language texts, proposed critical structured meaning, expected
answers, exact Unicode input spans, complete support bundles, reservations and
verbatim original manual quotations. The full [forms](../../experiments/cytiva/free-text-comparison-v01/submissions.json)
and [references/provenance](../../experiments/cytiva/free-text-comparison-v01/references.json)
are separate from runtime input. Source eligibility derives from the pinned human
review/policy, not newly rewritten historical registry status fields.

## Guarded execution, not started

The default command is static verification only, from the frozen Python environment:

```powershell
python -m experiments.cytiva.free_text_evaluation
```

No runtime is constructed by verification. The pending review template is rejected
before initialization or output creation. All twelve actual human approvals must
bind the frozen lock and exact EN/FR question, form, origin/reference records and
retained reservations. A separately authorized run then alternates S/F0-first by
scenario parity, EN before FR, with independent arm instances and no query cache.
All 48 raw outcomes, including failures, are saved before scoring. Existing output
is never overwritten or retried. Case IDs, answers and source gold never reach the
interpreter or the structured engine. No F1 interaction is silently simulated.

The prior P/G equivalence reviews remain pending and are excluded from this new
denominator. No earlier approval is extended to new text/form pairs. Human review
may amend draft references before dataset freeze, preserving prior drafts and
updating content bindings; it must not rewrite the frozen candidate to fit them.

## Verification performed

See [static preparation checks](free-text-comparison-v01-preparation.json). Current
method/data hashes, original source quotes, dependencies, schemas, origins, forms,
pair inventories and review gates verify. Seven pure scorer/gate tests pass. The
prospective set has not been interpreted, planned, scored or used to tune code.
The runtime's 603-test merged-main result remains prior integration evidence;
the full suite is not rerun as a prospective exercise during preparation.

E118-I/E121-EQ stay excluded. All previously tracked files, old frozen trials,
GR01-GR04 decisions and the 16 older local notes remain unchanged. There is no
trial output directory. No LLM, paid API, commit or push is performed.
