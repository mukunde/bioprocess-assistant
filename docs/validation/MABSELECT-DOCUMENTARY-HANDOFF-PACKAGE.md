# Corrected MabSelect documentary handoff — versioning package

Prepared on 2 November 2026 against `main` at `6c8bfe0`.
Status: local corrected implementation, ready for versioning review; not frozen,
activated or published. No new scientific or operational approval is asserted.

## Included behavior

The new deterministic handoff reuses the existing reviewed MabSelect selector.
It delivers complete product/context-bound documentary support, original
citations, provenance and scoped human reservations. Missing product/context
produces clarification; unsupported numerical pressure/hold-time requests produce
scoped abstention. It preserves separate alternatives, following washes and
warnings without choosing a suitable laboratory treatment.

The three implementation-review findings are corrected: exact task-to-bundle
references (including Q09), contained unexpected errors with independent task
service, and faithful `Wash immediately` machine wording. The
[implementation and review report](MABSELECT-DOCUMENTARY-HANDOFF.md) records the
behavior, tests, historical results and deferred features.

The contract, decision records and schemas are included because they are still
local and required by this implementation. A commit containing only the runtime
or the six correction files would not be self-contained. Original human messages
and accepted proposal hashes are preserved. Pending labels in the old proposals
describe their original preparation state; later bound decision records record
their acceptance without rewriting those historical proposals.

## Verification

- Replayed all **24 documentary-handoff tests** during package preparation:
  passed, no failures/errors/skips. Includes six added regression tests and actual
  loopback HTTP requests.
- The corrected implementation previously passed the combined **48-test**
  selector/UI/freeze verification, as recorded in the implementation report.
- Nine machine schemas, 32 unchanged synthetic structural fixtures and actual
  response shapes were checked locally with no remote schema resolution.
- A disposable copy of tracked `main` plus exactly these 24 files verifies
  authority loading, the accepted examples, cross-product task references,
  clarification, scoped pressure abstention and excerpt resolution. It contains
  no ignored PDF, local pilot, private audit folder, virtual environment or cache.
  This is a clean-materialization smoke test using the prepared host Python,
  not a second-PC Windows installation test or an activated serving release.
- Original scoped decisions, v03 and its 36 pins, the sixteen excluded historical
  notes and the pilots remain unchanged. All files outside this explicit package
  retain their preparation-baseline hashes. No Git index mutation is required.

The full 848-test run in the implementation report predates the corrections; it
is retained as historical evidence, not claimed as a new complete-suite run.
The package changes no legacy selector, frozen engine, dependency lock, root
README, roadmap or deployment workflow.

## Exact inventory — 24 files

```text
demo/documentary.py
demo/documentary_preview.py
demo/static/documentary.html
docs/schemas/reviewed-serving-v1/README.md
docs/schemas/reviewed-serving-v1/authority.schema.json
docs/schemas/reviewed-serving-v1/common.schema.json
docs/schemas/reviewed-serving-v1/mapping.schema.json
docs/schemas/reviewed-serving-v1/release.schema.json
docs/schemas/reviewed-serving-v1/request.schema.json
docs/schemas/reviewed-serving-v1/response.schema.json
docs/schemas/reviewed-serving-v1/shape-fixtures.json
docs/schemas/reviewed-serving-v1/source-index.schema.json
docs/schemas/reviewed-serving-v1/source-view.schema.json
docs/schemas/reviewed-serving-v1/validation-error.schema.json
docs/technical/REVIEWED-DOSSIER-SERVING-CASES-V01.md
docs/technical/REVIEWED-DOSSIER-SERVING-CONTRACT-V01.md
docs/technical/REVIEWED-DOSSIER-SERVING-REVIEW-V01.md
docs/technical/REVIEWED-DOSSIER-SERVING-TECHNICAL-V01.md
docs/technical/reviewed-dossier-serving-decisions-v01.json
docs/technical/reviewed-dossier-serving-interface-examples-v01.json
docs/technical/reviewed-dossier-serving-technical-decisions-v01.json
docs/validation/MABSELECT-DOCUMENTARY-HANDOFF.md
docs/validation/MABSELECT-DOCUMENTARY-HANDOFF-PACKAGE.md
tests/test_documentary_handoff.py
```

## Proposed branch and commit

Branch: `codex/mabselect-documentary-handoff`.

```text
feat: add corrected MabSelect documentary handoff

Add the accepted serving design, machine schemas and a local selector-backed
preview with complete citations, scoped reviews, clarification and abstention.

Bind exact context objects to each task, contain unexpected service failures,
and preserve immediate following-wash wording. Add regression coverage and
record verification without activating a serving release or changing v03.
```

## Boundaries

No source PDF, raw extraction, screenshot, private audit, environment, cache,
dependency tree or pilot asset belongs to this package. The source view serves
only the registered excerpts and their scoped reviews. E118-I and E121-EQ remain
excluded. Production activation/withdrawal authority, unrestricted text handling,
parsed quantities, LLM answering and Neo4j publication remain deferred.
Do not describe this package as a frozen runtime or a production serving release.
