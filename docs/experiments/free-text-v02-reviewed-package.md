# FV01-FV12: proposed compact reviewed delivery

Prepared on 27 October 2026. This 38-file package is local and not merged. The
merged baseline remains main `1696c69` after PR46/PR47; its last full maintained
suite passed 669 tests. No files are staged by preparing this inventory.

## Scope and exact proposed files

The original freeze, dataset, twelve review records and native run remain
unchanged. The new README explains historical pending/pre-run labels separately
from actual completed review/execution. results.json contains all 24 native scored
observations and original attempt/completion metadata; the 48 raw outcomes remain
local with their existing audit hashes. The package manifest binds the 37 other
files after LF normalization and excludes itself to avoid a self-reference.

- `README.md`
- `docs/ROADMAP.md`
- `docs/experiments/free-text-v02-comparison-v01-preparation.json`
- `docs/experiments/free-text-v02-comparison-v01-preparation.md`
- `docs/experiments/free-text-v02-comparison-v01-results-checks.json`
- `docs/experiments/free-text-v02-comparison-v01-results.md`
- `docs/experiments/free-text-v02-reviewed-package.md`
- `experiments/cytiva/compositional-navigation-v04-results/manifest.json`
- `experiments/cytiva/free-text-v02-comparison-v01/METHOD.md`
- `experiments/cytiva/free-text-v02-comparison-v01/README.md`
- `experiments/cytiva/free-text-v02-comparison-v01/REVIEW-PROGRESS.md`
- `experiments/cytiva/free-text-v02-comparison-v01/REVIEW-SUMMARY.md`
- `experiments/cytiva/free-text-v02-comparison-v01/REVIEW.md`
- `experiments/cytiva/free-text-v02-comparison-v01/manifest.json`
- `experiments/cytiva/free-text-v02-comparison-v01/method-lock.json`
- `experiments/cytiva/free-text-v02-comparison-v01/package-manifest.json`
- `experiments/cytiva/free-text-v02-comparison-v01/questions.json`
- `experiments/cytiva/free-text-v02-comparison-v01/references.json`
- `experiments/cytiva/free-text-v02-comparison-v01/results.json`
- `experiments/cytiva/free-text-v02-comparison-v01/review-completion.json`
- `experiments/cytiva/free-text-v02-comparison-v01/review-decisions/FV01.json`
- `experiments/cytiva/free-text-v02-comparison-v01/review-decisions/FV02.json`
- `experiments/cytiva/free-text-v02-comparison-v01/review-decisions/FV03.json`
- `experiments/cytiva/free-text-v02-comparison-v01/review-decisions/FV04.json`
- `experiments/cytiva/free-text-v02-comparison-v01/review-decisions/FV05.json`
- `experiments/cytiva/free-text-v02-comparison-v01/review-decisions/FV06.json`
- `experiments/cytiva/free-text-v02-comparison-v01/review-decisions/FV07.json`
- `experiments/cytiva/free-text-v02-comparison-v01/review-decisions/FV08.json`
- `experiments/cytiva/free-text-v02-comparison-v01/review-decisions/FV09.json`
- `experiments/cytiva/free-text-v02-comparison-v01/review-decisions/FV10.json`
- `experiments/cytiva/free-text-v02-comparison-v01/review-decisions/FV11.json`
- `experiments/cytiva/free-text-v02-comparison-v01/review-decisions/FV12.json`
- `experiments/cytiva/free-text-v02-comparison-v01/review-template.json`
- `experiments/cytiva/free-text-v02-comparison-v01/review.json`
- `experiments/cytiva/free-text-v02-comparison-v01/submissions.json`
- `experiments/cytiva/free_text_v02_evaluation.py`
- `experiments/cytiva/reviewed-v05-evaluation/manifest.json`
- `tests/test_free_text_v02_evaluation.py`

## Preserved results and methodological limits

- Official S 22/24, F0 intent 19/24, complete F0 17/24 (EN 10/12, FR 7/12),
  complete bilingual pairs 7/12. Acceptance is not met; no replacement score.
- FV04: two handled projection failures after distinct buffer-use items collapse.
  FV07/FV11/FV12: FR phase-association defects; FV06: shared aggregate semantics
  differ from the reviewed reference while individual states/bindings match.
- Four individual human messages and one collective FV05-FV12 message are retained
  verbatim and bound per case. Reservations and pending historical snapshots stay
  intact; no source approval or scientific suitability is inferred.
- E118-I/E121-EQ stay excluded; 44 contexts have original source/token integrity,
  maximum 1,674 tokens and three roots. FT/FV use different questions and are not
  a controlled improvement estimate. No generated answers are evaluated.

## Documentation and test maintenance

README and roadmap now distinguish merged design/GR/runtime/FT/v02 from this
local completed FV package, and prioritize the coverage-contract decision, bounded
parser repair and a small confirmed/structured serving slice. The detailed diagram
and startup commands remain unchanged.

Only supporting documentation digests change in the v04 and reviewed-v05 manifests:
README for both and roadmap for reviewed-v05. Their native files/results/provenance,
source hashes and human decisions remain unchanged. Neither manifest is pinned by
this FV method lock.

Two static preparation guards previously assumed the run directory was absent.
They now snapshot before/after so they preserve a completed run and also work in
fresh clones without native data. Two delivery tests verify exact manifest/review
bindings and the full scored denominators, retaining the FV06 aggregate failures.
The 12 static guards never evaluate an FV input.

## Excluded material and next checkpoint

Current local delivery verification passes **681/681 maintained tests** with no
failures, errors, skips or external connection attempts (33 loopback operations).
The 12 static delivery/scorer guards also pass separately. The 669-test result
in README/roadmap is explicitly the earlier merged-main checkpoint; 681 is the
current local package result. No frozen comparison is repeated by packaging.

Original manual quotations in the frozen REVIEW.md retain their source trailing
spaces and line breaks. Do not reformat that evidence to satisfy cosmetic Git
whitespace warnings; delivery hashes bind its unchanged content.

All 16 older `docs/experiments/cytiva-structured-control-s-*` local notes remain
byte-identical and outside this inventory. Native raw outputs, PDFs, credentials,
weights and `.local-tools/` remain local/ignored. Runtime implementation, scorer,
source policy, historical lock/data/decisions and default chat routing are unchanged.

The next contract decision should distinguish coverage of eligible ready units
from complete request service; it is not silently resolved here. Any new parser
candidate needs FV regressions and fresh prospective references after its own freeze.
Git operation rules are centralized in [AGENTS.md](../../AGENTS.md).

## Proposed commit

Branch: `codex/cytiva-v02-fv-reviewed`.

```text
test(cytiva): preserve reviewed v02 comparison and update roadmap

Record FV01-FV12 approvals, immutable freeze inputs and all original comparison scores.
Retain the 22/24 structured and 17/24 free-text outcomes, including the shared FV06 aggregate mismatch, without rescoring.
Update README and roadmap, refresh documentation-only support hashes, and make static guards preserve existing runs.
```
