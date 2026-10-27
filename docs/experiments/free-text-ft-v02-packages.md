# Proposed FT frozen comparison and v02 delivery lots

Prepared on 27 October 2026. The index is empty; this inventory stages nothing.
The two lots must be integrated in order A then B. B imports A's pure scorer and
uses its reviewed FT data as development regression fixtures.

## Lot A: reviewed frozen FT01-FT12 comparison (33 files)

The original lock, preparation cards and twelve individual human decision records
remain unchanged. The new package README explains their historical status labels;
results.json exports every scored language observation, plus native attempt and
completion metadata, without exporting the 48 raw outputs. The package manifest
binds all 32 other files using LF-normalized SHA-256. Neither v02 nor any old local
note belongs to A.

- `docs/experiments/free-text-comparison-v01-preparation.json`
- `docs/experiments/free-text-comparison-v01-preparation.md`
- `docs/experiments/free-text-comparison-v01-results-checks.json`
- `docs/experiments/free-text-comparison-v01-results.md`
- `experiments/cytiva/free-text-comparison-v01/METHOD.md`
- `experiments/cytiva/free-text-comparison-v01/README.md`
- `experiments/cytiva/free-text-comparison-v01/REVIEW-PROGRESS.md`
- `experiments/cytiva/free-text-comparison-v01/REVIEW-SUMMARY.md`
- `experiments/cytiva/free-text-comparison-v01/REVIEW.md`
- `experiments/cytiva/free-text-comparison-v01/manifest.json`
- `experiments/cytiva/free-text-comparison-v01/method-lock.json`
- `experiments/cytiva/free-text-comparison-v01/package-manifest.json`
- `experiments/cytiva/free-text-comparison-v01/questions.json`
- `experiments/cytiva/free-text-comparison-v01/references.json`
- `experiments/cytiva/free-text-comparison-v01/results.json`
- `experiments/cytiva/free-text-comparison-v01/review-completion.json`
- `experiments/cytiva/free-text-comparison-v01/review-decisions/FT01.json`
- `experiments/cytiva/free-text-comparison-v01/review-decisions/FT02.json`
- `experiments/cytiva/free-text-comparison-v01/review-decisions/FT03.json`
- `experiments/cytiva/free-text-comparison-v01/review-decisions/FT04.json`
- `experiments/cytiva/free-text-comparison-v01/review-decisions/FT05.json`
- `experiments/cytiva/free-text-comparison-v01/review-decisions/FT06.json`
- `experiments/cytiva/free-text-comparison-v01/review-decisions/FT07.json`
- `experiments/cytiva/free-text-comparison-v01/review-decisions/FT08.json`
- `experiments/cytiva/free-text-comparison-v01/review-decisions/FT09.json`
- `experiments/cytiva/free-text-comparison-v01/review-decisions/FT10.json`
- `experiments/cytiva/free-text-comparison-v01/review-decisions/FT11.json`
- `experiments/cytiva/free-text-comparison-v01/review-decisions/FT12.json`
- `experiments/cytiva/free-text-comparison-v01/review-template.json`
- `experiments/cytiva/free-text-comparison-v01/review.json`
- `experiments/cytiva/free-text-comparison-v01/submissions.json`
- `experiments/cytiva/free_text_evaluation.py`
- `tests/test_free_text_evaluation.py`

Branch: `codex/cytiva-ft-comparison-reviewed`.

```text
test(cytiva): preserve reviewed frozen EN/FR comparison

Record FT01-FT12 bilingual approvals, provenance and immutable method inputs.
Export all scored observations and document 12/24 free-text passes without rerunning or replacing the frozen trial.
Add static delivery and review-binding checks; retain raw outputs locally.
```

## Lot B: opt-in v02 candidate (6 files)

This lot depends on A. It does not replace the default runtime or change the
frozen method. The retained full-suite checkpoint is 667/667, including 57 v02
checks; the 24 FT language cases are development data after repair, not a second
prospective result. This package adds two further static tests to A; they verify
content bindings and score denominators without interpreting the frozen inputs.

- `docs/experiments/free-text-candidate-v02-checks.json`
- `docs/experiments/free-text-ft-v02-packages.md`
- `docs/technical/FREE-TEXT-CANDIDATE-V02.md`
- `ingestion/free_text_bridge_v02.py`
- `ingestion/free_text_interpreter_v02.py`
- `tests/test_free_text_v02.py`

Branch: `codex/free-text-v02-grammar-routing`.

```text
fix(ingestion): add v02 grammar and pressure routing candidate

Add an opt-in EN/FR candidate with bounded grammar coverage, complete owner tokens and explicit pressure routing.
Preserve v01, quarantine and independent-task handling; add FT development regressions and interface compatibility tests.
Document the 667-test baseline and the need for fresh prospective validation.
```

## Verification and exclusions

The review and score inventories, compact export, hashes, local Markdown links,
source exclusions, explicit file lists and branch dependency are checked during
preparation. No method or reviewed record is rewritten to update its status.

The 16 `docs/experiments/cytiva-structured-control-s-*` older local notes remain
byte-identical, untracked and outside both lists. `.local-tools/`, native raw
outputs under `data/experiments/`, PDFs, credentials and model weights are also
outside both lists. README and roadmap are not part of this delivery.

Run static lot A checks from the repository root:

```powershell
python -m unittest tests.test_free_text_evaluation -q
```

After A and B are both present, run the 57 candidate checks:

```powershell
python -m unittest tests.test_free_text_v02 -q
```

The existing complete-suite evidence and candidate preservation audit are in
[the v02 verification record](free-text-candidate-v02-checks.json); the frozen
comparison has its own [results report](free-text-comparison-v01-results.md).
Git operation rules are centralized in [AGENTS.md](../../AGENTS.md).
