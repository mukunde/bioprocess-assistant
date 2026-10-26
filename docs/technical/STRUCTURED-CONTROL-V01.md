# Offline structured control v0.1

Status: local implementation of the approved T01-T08/TC01-TC04 design, not a
frozen prospective method or a deployed answering service. See the
[26 October review corrections and exclusion-scope clarification](STRUCTURED-CONTROL-REVIEW-FIXES-V01.md).

The [technical specification](TASK-REQUEST-TECHNICAL-SPEC-V01.md) and its
[approval record](../decisions/2026-10-25-task-request-technical-review.json)
remain unchanged historical design artifacts. Their statements about code not
existing describe the point of approval. This document records the subsequent
implementation; the identifiers containing `tech-proposed` are deliberately
retained so the approved format remains verifiable.

## Components

- [structured_request.py](../../ingestion/structured_request.py): strict public
  input validation, canonical provenance, scoped semantic checks, candidate
  scheduling and complete context-plan/audit output.
- [structured_sources.py](../../ingestion/structured_sources.py): exact catalog
  resolution, approval and source hash verification, atomic dependency/guard
  bundles, metadata-first ranking with BM25 tie-breaking, and local token counting.
- [test_structured_request.py](../../tests/test_structured_request.py): CF01-CF12
  conformance cases using typed development fixtures, not prospective questions.

The runtime reads the approved schema, catalog and adapter in this directory.
It verifies their LF-normalized hashes against the technical decision, then
verifies the corpus, review manifest, inherited policy and lexical primitive.
Corrupt or unavailable inputs raise an operational `IntegrityError`; they are
never converted into a missing-documentary-source answer. The 25 eligible
excerpts and the exclusions E118-I/E121-EQ retain their existing identities.

## Run locally

Use Python 3.10 or later and the optional
[requirements-structured.txt](../../requirements-structured.txt). The existing
project ingestion environment already contains these dependencies. Package
installation is separate from executing the offline control.

The verified local `cl100k_base` asset must already exist in
`.local-tools/tiktoken-cache/`. The runtime constructs the encoding from that
local file with pinned tiktoken 0.12.0, pattern and special-token IDs; it does not
call `get_encoding()` or fall back to downloading a missing asset.

From the repository root in PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path .local-tools/structured-control | Out-Null
.venv-ingestion\Scripts\python.exe -m ingestion.structured_request examples/structured-control/washing-partial.json --output .local-tools/structured-control/washing-partial-01.json
```

Choose a new output filename on every run. Existing output files are refused,
including at exclusive file creation, and parent directories are not implicitly
created. Duplicate keys in a submitted JSON object are rejected rather than
silently overwritten.

The [example](../../examples/structured-control/washing-partial.json) copies the
specification's washing request: column size is unknown, so flow needs
clarification while stopping criteria retain documentary support. It is a
development/conformance example, not an independent evaluation question.

Output contains:

1. `canonical_request`: unchanged input snapshot, reproducible input digest,
   field origins, catalog resolutions, scoped issues and version hashes.
2. `plan`: independent interpretation/support diagnostics per information unit,
   exact source passages, permitted task/item bindings and global resource counts.
3. `audit`: considered/ranked candidates, score components, rejected bundles,
   marginal token costs, selection order and context digest. Audit-only fields
   are not silently appended to the model-facing context envelope.

Bindings associate the full admitted dependency/guard bundle with each supported
unit, so mandatory warnings remain attached. Unit-level `source_ids` identify
direct documentary support. Adjacent values in the same exact quote do not
authorize their use for a different column, stage, buffer use or task.

## Conformance checks

```powershell
.venv-ingestion\Scripts\python.exe -m unittest discover -s tests -p test_structured_request.py -v
python -m unittest tests
```

If the execution sandbox cannot write its default temporary directory, select a
writable project-local temporary directory for that test process:

```powershell
New-Item -ItemType Directory -Force -Path .local-tools/test-temp | Out-Null
$env:TEMP = (Resolve-Path .local-tools/test-temp).Path
$env:TMP = $env:TEMP
```

The targeted tests block socket connections. Exact 2,048/2,049-token and
six-root scheduling branches use an explicitly synthetic internal counter;
separate integration tests use the real pinned tokenizer and verify the full
context cost including additional bindings. Synthetic boundary counts are not
reported as measured real-text token counts.

Use the maintained full-suite entry point `python -m unittest tests` with both
application and ingestion dependencies installed (see [tests/README.md](../../tests/README.md)).
Direct discovery under `-s tests` bypasses the existing historical-fixture
override and is not the maintained full-suite command. Some existing review-UI
tests require local loopback sockets; an execution sandbox must allow them.

| Requirement | Implemented test coverage |
|---|---|
| CF01 | Strict public boundary, four states, false/zero, input digests, field origins, duplicate JSON keys |
| CF02 | Unit/domain checks, no sample-volume-to-column inference, no automatic conversion |
| CF03 | Exact labels/aliases, French spellings, ambiguity, out-of-scope identities, label/column conflicts |
| CF04 | Semantic restriction validation, task/item/information exclusions, product-size qualifiers, preparation versus operation, invalid owners and duplicate identifiers |
| CF05 | Preserved conflicting assertions and origins, explicitly separate scenarios |
| CF06 | Partial washing support and mode-dependent versus mode-independent elution items |
| CF07 | Concurrent unknown-context and quarantine diagnostics without blocked-unit bindings |
| CF08 | Bounded absence, unresolved/unmapped roles and coverage aggregates, cation-exchange principle versus excluded pH/pI condition |
| CF09 | Separate buffer-use items sharing exact source content, no inferred comparison or pairing |
| CF10 | Mandatory warnings, joint roots, exact syringe-reference lookup, corruption and missing-tokenizer errors |
| CF11 | Lexicographic ranking, admissible zero lexical scores, deterministic serialization, ineligible-bundle rejection |
| CF12 | Global roots/tokens, admissible-item interleaving, partial items, whole-bundle admission, continued scheduling, deduplication and binding costs |

The initial 25 October check recorded **35 targeted tests and 518 maintained-suite
tests passing**, with zero external connection attempts. The subsequent review
identified gaps in that coverage; those original counts describe the historical
[v01 check record](structured-control-v01-checks.json), not proof of the corrected
behavior. Its file hashes and the original CLI example (five source passages,
816 context tokens) are preserved. Revised checks are recorded separately after
the corrections, without overwriting that record or claiming a prospective result.

The 26 October correction check passed **50 targeted tests and 533 maintained-suite
tests**, with no failures, errors, skips or external connection attempts in the
guarded full-suite run. See the [revision-2 check record](structured-control-v02-checks.json)
and [correction review](STRUCTURED-CONTROL-REVIEW-FIXES-V01.md) for current hashes,
qualifier semantics and the remaining freeze boundary. The revision number applies
to the check record; it does not name a new retrieval experiment or frozen method.

## Limits and next gate

This is an offline structured control. It does not interpret free-text questions,
generate answers, invoke models, query Neo4j, run RAGAS, or establish suitability
for a real sample. The source-role catalog intentionally covers the approved
small perimeter; missing role mappings remain explicit adapter gaps.

Conformance success is not a whole-manual retrieval result or scientific
validation. Historical trials, reviews, source hashes and method locks remain
unchanged. The implementation has not been frozen as v06. Review this code and
its checks before freezing a method or preparing an independently reviewed
prospective comparison.
