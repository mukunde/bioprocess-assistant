# PR74 corrections — local registry v02 before activation

Prepared on 2 November 2026. The original v01 implementation/replay remains
historical evidence. Corrected candidate: `mabselect-local-v02`, staged only.
No real activation decision, active pointer or authority journal is created.

## Three review findings resolved

### Restored old pointers cannot revive withdrawn content

The current pointer must match the newest record of a distinct durable activation
journal, `authority-log/<generation>.json`. Generation numbers are contiguous,
withdrawal versions increase and each record binds its predecessor by hash.
Records are created exclusively and flushed before pointer replacement. All
active response/source operations validate the journal, including after restart.

A restored v01 pointer after a v02 withdrawal now yields `invalid_authority` and
no source quotation. Missing, corrupted or incomplete history is rejected; it is
not recreated from the old pointer. An interrupted pointer replacement keeps the
newer durable head and fails closed instead of serving the old version. No
automatic recovery/rollback is introduced; an interrupted store requires explicit
operator review. Tests cover restart, pointer restoration, journal corruption,
missing history, generation gaps and interrupted replacement.

This guards pointer-only rollback. The trust boundary remains the configured
user-controlled directory: restoring/replacing the entire directory and its
journal needs an external anchor to detect and is outside this candidate's
single-process cooperative-writer model. No signatures or extra service are
implied.

### History validation is deduplicated per operation

Complete version validation is memoized by release identity, staged/active mode
and manifest digest during a single operation. Historical review references and
source targets share that operation's cache. Cycle checks remain in force.
Every new operation and final authority check starts with a fresh cache.

The regression witness uses five versions with preserved withdrawal/reinstatement
history. It requires exactly five full validations, replacing the previous
1/2/4/8/16 growth; a second operation performs five fresh validations. No persistent
cache, mtime shortcut or stale cross-request authority is admitted.

### Backend failure is distinct from authority drift

Unexpected backend errors trigger a fresh authority check. If authority actually
changed, the response remains empty `unavailable: authority_changed`. If it is
unchanged, requested items become `unavailable: required_dependency_unavailable`,
with task identity, exclusions and coverage retained. The envelope uses the
existing `item_outcomes` reason, preserving both frozen schemas. Only the boundary
and exception class are logged privately; raw exception contents are not returned
or logged. Regressions cover an unchanged authority and a simultaneous backend/
authority failure.

## Corrected candidate and replay

The CLI now defaults to `mabselect-local-v02`. The new directory preserves the
original five bundle purposes, thirteen source objects and five scoped reviews,
but binds the corrected registry code. Its empty withdrawal inventory remains
**proposed**, with no human approval message. Source/review facts and the old
v01 artifacts/results are unchanged. Current commands:

```powershell
python -S -m experiments.cytiva.mabselect_registry_candidate
python -S -m experiments.cytiva.mabselect_registry_candidate --replay
```

SX01–SX06 passed with complete requests, responses and citation checks retained
in [the v02 replay](../../experiments/cytiva/mabselect-registry-candidate-v02/replay-results.json).
No socket attempts, LLM calls or paid API calls were recorded. This is known-case
conformance, not an independent answer/scientific quality result.

## Verification status

The registry suite passed **32 tests**, including eight new regressions for the
three review findings and crash/restart behavior (147.222 seconds). The subsequent
complete suite passed **896 tests executed: 895 passed and one optional PDFium
preview skip**, in 259.538 seconds. No previous test result is overwritten.

The four v02 candidate artifacts passed the existing registry schemas; all six
saved responses and the new service-failure outcome passed the unchanged response
schemas. An inventory-only copy of 62 files, run with `python -S`, reproduced
the full v02 output identically without site packages, PDF, cache or private
files. It created neither an active pointer nor an authority journal.

The original v01 mapping/source objects remain identical in v02 except for the
release identity; no quotation, condition or human reservation is rewritten.
Both original freeze verifiers passed with their existing lock digests. The
sixteen notes, pilots and every existing file outside the explicit correction
scope were checked by raw SHA-256 and preserved. No activation follows from a
passing result.

Review conclusion: the three reproduced findings are resolved, with no remaining
blocking discrepancy found for this local single-writer candidate. The operational
recovery/whole-store rollback limits above remain explicit and are not claimed as
an external tamper-proof authority service.

## Review boundary

The two original freezes, source/review decisions, sixteen old notes and pilots
are unchanged. The corrected registry is an outer adapter, not an alteration of
the frozen handoff or v03. Candidate checks are explicit developer preview mode;
production/default evaluation remains unavailable without reviewed activation.
No UI/chat connection or deployment is added. Any later behavior change requires
a new version and review; no old digest is refreshed to bless changed frozen
inputs.

## Correction delivery

This correction changes/adds only these 13 files on PR74's existing branch:

```text
docs/validation/MABSELECT-LOCAL-REGISTRY-CANDIDATE.md
docs/validation/MABSELECT-LOCAL-REGISTRY-REVIEW-FIXES.md
experiments/cytiva/mabselect_registry_candidate.py
experiments/cytiva/mabselect-registry-candidate-v02/replay-results.json
serving-data/releases/mabselect-local-v02/catalog.json
serving-data/releases/mabselect-local-v02/mapping.json
serving-data/releases/mabselect-local-v02/release.json
serving-data/releases/mabselect-local-v02/source-index.json
serving-data/releases/mabselect-local-v02/withdrawal-decision.json
serving-data/releases/mabselect-local-v02/withdrawals.json
serving/README.md
serving/local_registry.py
tests/test_local_registry.py
```

The full PR contains 21 files, including the retained original v01 evidence. No
activation, authority journal, pilot, frozen input, PDF, environment, cache or
private log belongs to this correction delivery.
