# FV01-FV12: reviewed frozen opt-in v02 comparison

Prepared locally for versioning on 27 October 2026; this delivery is not yet
merged. The v02 runtime itself is already merged in PR47. This new method was
locked before exact FV wording and then evaluated once after actual human review.

| Official frozen result | Passed / total |
|---|---:|
| Structured S observations | 22/24 |
| F0 intent observations | 19/24 |
| Complete free-text observations | 17/24 |
| Complete EN / FR observations | 10/12 / 7/12 |
| Complete bilingual pairs | 7/12 |

Acceptance is not met. FV04 collapses separate binding/elution formulation items;
FV07/FV11/FV12 expose French phase-association failures. FV06 EN/FR fails both
arms only on a shared aggregate/reference mismatch: all individual expected
states match, but the core intentionally sets coverage false for an unsupported
selector. No adjusted score, reference amendment or method repair is included.

## Evidence timeline

1. [Method](METHOD.md), [lock](method-lock.json) and [preparation manifest](manifest.json)
   bind 44 files, environment and the dataset authored afterwards. The
   [cards](REVIEW.md), [references](references.json) and [template](review-template.json)
   retain their original pending labels as preparation snapshots.
2. [Actual review](review.json), twelve immutable per-case records,
   [progress](REVIEW-PROGRESS.md), [summary](REVIEW-SUMMARY.md) and
   [review completion](review-completion.json) preserve four individual approvals
   and one collective FV05-FV12 approval, exact original quotations, reservations,
   origins and content bindings. The completion record describes its pre-run
   checkpoint, not a current assertion that the trial is unexecuted.
3. [Compact results](results.json) copy all 24 original scored observations and
   native attempt/completion metadata. All 48 raw outcomes were saved before
   scoring and remain local, unchanged, outside Git. See the
   [results report](../../../docs/experiments/free-text-v02-comparison-v01-results.md)
   and [integrity audit](../../../docs/experiments/free-text-v02-comparison-v01-results-checks.json).
4. [Delivery manifest](package-manifest.json) binds this package and the current
   documentation/support-digest updates without replacing the earlier lock.
   The [delivery inventory](../../../docs/experiments/free-text-v02-reviewed-package.md)
   gives the exact proposed scope and commit message.

The two handled projection failures are retained; zero exceptions escaped arm
calls. The scorer's default context `execution_error` after failed intent must
not be mistaken for a thrown runtime error. Native outputs provide that distinction.
Source provenance and serialized token counts verify in all 44 emitted contexts;
maximum usage was 1,674 tokens and three roots. E118-I/E121-EQ remain excluded.

## Static checks, not trial execution

```powershell
python -m unittest tests.test_free_text_v02_evaluation -q
```

The 12 guards inspect saved evidence and mock construction boundaries. They do not
execute the new inputs. No private PDF, native run directory or raw arm outputs
are needed for these static delivery checks, but the schema-validation dependency
is required. If native results are present, checks preserve them byte-for-byte
under the LF hash convention; historical template labels are not live approvals.

`python -m experiments.cytiva.free_text_v02_evaluation` verifies the original
freeze/preparation, not current delivery status. Its pending label describes the
initial snapshot. A historical completed run must not be overwritten or retried.

FT and FV are different same-corpus, same-author diagnostic sets, not a controlled
gain measurement or blinded independent validation. No generated-answer quality,
scientific suitability or default-chat activation is established. Any repair
turns FV into development evidence and needs a new candidate/freeze and fresh
reviewed questions. The 16 older local notes remain outside this delivery.
