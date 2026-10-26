# Corrected EN/FR runtime: proposed delivery package

Date: 26 October 2026. Local preparation on main at `e82de807532b0a51fad5efe7ba84560aaf40e6c8` (PR #44).
The GR01-GR04 reviewed design is already merged. This package contains the new
implementation and its corrected review; it does not freeze the candidate or
activate a chat path. Git-operation rules are in [AGENTS.md](../../AGENTS.md).

## Exact proposed files (12)

- `ingestion/free_text_contract.py`
- `ingestion/free_text_interpreter.py`
- `ingestion/free_text_bridge.py`
- `tests/test_free_text_interface.py`
- `tests/test_free_text_review_regressions.py`
- `docs/technical/free-text-runtime-policy-v01.json`
- `docs/technical/FREE-TEXT-RUNTIME-V01.md`
- `docs/technical/FREE-TEXT-RUNTIME-REVIEW-V02.md`
- `docs/technical/free-text-runtime-v01-checks.json`
- `docs/technical/free-text-runtime-v02-checks.json`
- `docs/technical/free-text-runtime-package-v01.md`
- `docs/technical/free-text-runtime-package-v01.json`

## Scope and evidence

- Three runtime modules implement the bounded EN/FR grammar, offline schema and
  cross-record validation, exact UTF-8/code-point provenance and bridge accounting.
  The unchanged structured engine is called zero or one time per request.
- The five reviewed corrections preserve positive requests in mixed clauses,
  typed restriction selectors and owner boundaries, ledger/projection value
  consistency, explicitly unknown columns, and individual request ownership.
- The original 33-test module is unchanged from the initial implementation;
  14 additional regression methods cover R01-R05. The complete maintained suite
  passed **603/603 tests**, including all **47 targeted tests**, with no errors,
  failures, skipped tests or external connection attempts. Existing loopback
  tests account for 33 local operations. No historical S trial was repeated.
- Current component bytes match the v02 verification report. No code changed
  since that complete run. Packaging checks validate hashes, test inventories,
  local Markdown links and unchanged baselines; they do not rerun the suite.
- The v01 report is retained as historical evidence for the earlier source
  snapshot, not as a claim that its old component hashes match corrected code.
  Its recorded results are superseded for current status by the v02 report.
  Schema titles mentioning a proposed/unimplemented interface also remain
  historical preparation metadata; schemas and reviewed fixtures are unchanged.

The [manifest](free-text-runtime-package-v01.json) lists the exact delivery scope
and binds the other eleven files by SHA256 with CRLF normalized to LF. It excludes
its own hash to avoid a cycle. The [corrected review](FREE-TEXT-RUNTIME-REVIEW-V02.md)
and [runtime guide](FREE-TEXT-RUNTIME-V01.md) retain the operating limits and
distinguish caller input, preclassified-ledger tests and injected failures.

## Exclusions and remaining work

All 16 older local S preparation/review notes remain byte-identical, untracked and
outside the list. Private verification launchers/logs in `.local-tools`, PDFs,
credentials, model assets and raw extraction artifacts are excluded. No deletion,
archiving or staging is performed. No existing tracked file changes: the common
core/catalog/schema/source adapter, GR decisions/examples, prior experiments,
README and roadmap remain unchanged. E118-I/E121-EQ remain excluded.

The review found no remaining blocker within the five tested boundaries. This
bounded grammar is not universal language understanding or scientific validation.
A separately requested freeze, P/G equivalence review, a new human-reviewed
prospective paired evaluation and a separately reviewed serving integration remain
planned. The tests are development evidence, not held-out accuracy certification.

## Proposed commit

Branch: `codex/free-text-runtime`.

```text
feat(cytiva): add deterministic EN/FR interpreter and structured bridge

Preserve literal provenance, scoped exclusions and whole-request accounting.
Validate ledger/projection consistency before a single unchanged core invocation.
Add IF01-IF14 coverage, review regressions and the corrected implementation report.
```
