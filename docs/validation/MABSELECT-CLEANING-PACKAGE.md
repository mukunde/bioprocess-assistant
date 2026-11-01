# Corrected MabSelect journey — combined versioning package

Prepared on 1 November 2026 against merged `main` at `d8c8e84`. Status: local implementation and suite repairs, ready for repository review; not committed, merged or frozen. The published Flowshot tour contains recorded screenshots of this local work, not the executable Python extension.

## Result and scope

The separate MabSelect entry supports exact plain MabSelect, SuRe and SuRe LX identities from already reviewed cleaning excerpts. It retains four general formulations and their shared conditions, the separate SuRe/SuRe LX restricted block, detergent/solvent alternatives, the original backpressure warning and complete citations. Unknown, mixed, other or conflicting inputs lead to scoped clarification. The page-166 Protein A/G cleaning trigger is not transferred to MabSelect.

MR01 is resolved through a portable approved contract and an independently anchored verifier for that contract, the source dossier and the twelve original design decisions. The runtime checks approval integrity before using source reviews. Approval messages, exact quotations and scientific/operational reservations remain unchanged.

MR02 is resolved by executing the shipped HTML/JavaScript against the real loopback API with jsdom. A positive control must pass; five in-memory mutations must fail at their intended assertions. This is DOM behavior testing, not browser layout certification. Node/jsdom is test-only, with its own npm lock; neither the end-user launcher nor the frozen Python dependency set acquires Node dependencies.

## Suite repairs included

The [repair report](MABSELECT-SUITE-REPAIR.md) documents the separate integration fixes:

- Three historical manifests refresh only support-document hashes for the root README, test guide and updated enclosing manifests. No source, method, human-decision or result field changes.
- A maintained test runner creates a unique temporary workspace under an explicit short root, rejects overly long Windows roots and restores the previous Python temporary setting on success or failure. It cleans only its own child and preserves existing root contents.
- DOM polling yields for 10 ms; page/API fetches have 8-second abort deadlines. Request progress and partial subprocess diagnostics are retained. The existing 40-second process ceiling is unchanged, and timeouts remain failures without automatic retries.

The original timeout's negative remaining duration is consistent with a substantial scheduling interruption; the retained evidence does not establish a unique cause. The same mutant passes after repair, including in the full suite. No timing-only scientific or UI-correctness claim is inferred.

## Verification and historical evidence

**Latest complete suite: 830 executed, 829 passed, one optional PDFium preview skip, zero failures and zero errors.** Unittest execution: 118.291 seconds; total invocation including loading: 447.824 seconds. This run includes MC01–MC12, original route regressions, approval tamper checks, DOM/mutation tests, timeout diagnostics, temporary-workspace tests and historical package verification.

The first combined preparation run is retained separately: 826 executed, three failures, eleven errors and one optional skip in 417.641 seconds. Its five README-binding failure/error entries, eight Windows temporary-path error entries (including subtests), and one DOM timeout are explained in the repair report. The subsequent 40/40 targeted rerun, 74-case repair run with one remaining nested-manifest failure, and isolated corrected binding check remain distinct. The latest green run supersedes the integration blocker without erasing those records.

The original [implementation review](../technical/MABSELECT-CLEANING-IMPLEMENTATION-REVIEW-V01.md), [corrected re-review](../technical/MABSELECT-CLEANING-IMPLEMENTATION-REVIEW-V02.md) and [implementation verification](MABSELECT-CLEANING-DEMO.md) retain their historical test counts and browser observations. No new browser or independent retrieval/answer evaluation is claimed in this packaging step. The portable verifier confirms twelve decisions using three immutable artifacts.

From the repository root, using the prepared Python environment and test dependencies:

```powershell
npm ci --prefix tests/ui --ignore-scripts --no-audit --no-fund
python -S -m experiments.cytiva.verify_mabselect_design
python scripts/run_tests.py --temp-root "$env:LOCALAPPDATA\Temp"
```

Choose a writable short root on other systems. See the [test guide](../../tests/README.md) and [DOM test setup](../../tests/ui/README.md). Packaging checks cover local links, documentation-only manifest deltas, exact inventory, exclusions and frozen-v03 preservation. The green run is local regression evidence, not clean-machine or scientific certification.

## Preservation and limits

Frozen v03 and its 36 pins, the sixteen excluded notes, both Flowshot pilots, earlier videos, source/review events, source quarantines and historical trial outputs remain unchanged. This is bounded documentary support, not diagnosis, treatment selection, operational authorization or scientific validation. The new runtime remains unfrozen. No model, paid API, database, deployment or new source publication is part of this package.

Exclude `node_modules`, environments, source PDFs, private logs/previews and raw experiment artifacts. Only the npm lock and test sources are included. No root README or roadmap refresh is included in this lot.

## Exact inventory — 27 files

```text
demo/cytiva.py
demo/mabselect.py
demo/static/cytiva.html
docs/technical/MABSELECT-CLEANING-IMPLEMENTATION-REVIEW-V01.md
docs/technical/MABSELECT-CLEANING-IMPLEMENTATION-REVIEW-V02.md
docs/technical/MABSELECT-CLEANING-JOURNEY-V01.md
docs/technical/mabselect-cleaning-approved-contract-v01.md
docs/technical/mabselect-cleaning-review-v01.json
docs/technical/mabselect-cleaning-sources-v01.json
docs/validation/MABSELECT-CLEANING-DEMO.md
docs/validation/MABSELECT-CLEANING-PACKAGE.md
docs/validation/MABSELECT-SUITE-REPAIR.md
experiments/cytiva/compositional-navigation-v04-results/manifest.json
experiments/cytiva/free-text-v02-comparison-v01/package-manifest.json
experiments/cytiva/reviewed-v05-evaluation/manifest.json
experiments/cytiva/verify_mabselect_design.py
scripts/run_tests.py
tests/README.md
tests/test_mabselect_design_integrity.py
tests/test_mabselect_journey.py
tests/test_mabselect_ui.py
tests/test_test_workspace.py
tests/ui/.gitignore
tests/ui/README.md
tests/ui/mabselect.cjs
tests/ui/package-lock.json
tests/ui/package.json
```

## Proposed branch and commit

Branch: `codex/cytiva-mabselect-corrected`

```text
feat(demo): add reviewed MabSelect journey and regression safeguards
```
