# S01-S12 compact reviewed package: proposed versioning scope

Date: 26 October 2026. Prepared locally; no staging, commit or push performed.
Exactly 19 files are proposed. Existing runtime implementation, README, roadmap,
older experiments, historical review notes and original private results are not
included or altered. The 24 saved outputs are retained once in the compact export;
the original run snapshots stay private rather than duplicating tracked support.

## Files

- `docs/experiments/cytiva-structured-control-s-package.md`
- `docs/experiments/cytiva-structured-control-s-results.md`
- `experiments/cytiva/reviewed-structured-control/README.md`
- `experiments/cytiva/reviewed-structured-control/events.json`
- `experiments/cytiva/reviewed-structured-control/manifest.json`
- `experiments/cytiva/reviewed-structured-control/provenance.json`
- `experiments/cytiva/reviewed-structured-control/results.json`
- `experiments/cytiva/reviewed-structured-control/review.json`
- `experiments/cytiva/structured-control-evaluation-v01/PROTOCOL.md`
- `experiments/cytiva/structured-control-evaluation-v01/manifest.json`
- `experiments/cytiva/structured-control-evaluation-v01/method-lock.json`
- `experiments/cytiva/structured-control-evaluation-v01/questions.json`
- `experiments/cytiva/structured-control-evaluation-v01/references.json`
- `experiments/cytiva/structured-control-evaluation-v01/review-template.json`
- `experiments/cytiva/structured-control-evaluation-v01/submissions.json`
- `experiments/cytiva/structured_evaluation.py`
- `experiments/cytiva/verify_structured_reviewed_package.py`
- `tests/test_structured_evaluation.py`
- `tests/test_structured_reviewed_package.py`

## Checks

The frozen method and preparation hashes are unchanged. Actual human review is
complete; all twelve original messages and reservations are retained. The export
preserves original artifact hashes, complete 24-output order, the original
24/24 scores and 12/12 paired outcome, and both source exclusions. Portable
verification re-scores saved evidence without planning or retokenization.

Package regression tests cover a checkout without private files, LF/CRLF
portability and altered source, score, quarantine, review, amendment and budget
data. All 23 targeted tests pass: seven portable-package tests and the original
16 runner/scorer safeguard tests. The stdlib-only verifier and portable tests
also pass without private files. The frozen trial was not repeated.

The complete maintained application suite could not load in the currently
available `.venv-ingestion` environment: `tests/test_app.py` imports Chainlit,
which is not installed there (`ModuleNotFoundError: chainlit`). No complete-suite
pass is claimed for this handoff. The historical 549-test preparation result
remains a separate earlier record, not a new execution result. No dependency
installation or application configuration change is included in this package.

Pending flags inside the original preparation are historical and unchanged;
completed review and run status live in the reviewed export. This validates
structured context/diagnostics on a known corpus, not free-text interpretation,
generated answers, scientific correctness or production readiness.

## Proposed commit

```text
test(cytiva): preserve reviewed S01-S12 structured-control trial

Archive the frozen challenge, twelve human decisions and all 24 saved outputs.
Add portable provenance verification and tamper-regression tests.
Keep E118-I/E121-EQ excluded and document the bounded 24/24 outcome.
```

Suggested branch: `codex/cytiva-structured-control-reviewed`.
Only the listed files belong to this proposal. Other local preparation reports,
individual decision notes and private artifacts remain preserved outside it.
