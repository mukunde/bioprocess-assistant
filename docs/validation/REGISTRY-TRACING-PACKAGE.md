# Corrected local OpenTelemetry tracing delivery

Prepared on 2026-11-04 against main `88a1177a4386c487be9d36da49538d2cd81463c2`. This package adds optional metadata-only tracing to registry UI v02 and addresses the three findings recorded in the initial review. It does not introduce a new runtime freeze or activate a registry.

## Explicit delivery inventory

| File | Purpose |
| --- | --- |
| `demo/registry_tracing.py` | Dedicated OTel provider, metadata allowlist, asynchronous local sinks, safe diagnostics and bounded cleanup. |
| `demo/registry_ui_v02.py` | Explicit sink options, HTTP and registry spans, response trace header and lifecycle handling. |
| `requirements-observability.txt` | Three optional OTel packages pinned to 1.45.1, outside frozen environments. |
| `eval/requirements.txt` | Includes optional tracing dependencies for the evaluation/test environment. |
| `tests/test_registry_tracing.py` | 28 tracing regressions using disposable authorities and loopback collectors. |
| `docs/REGISTRY-TRACING.md` | Startup, captured metadata, failure policy, dependency boundaries and limitations. |
| `docs/CYTIVA-REGISTRY-UI-V02.md` | Links UI v02 to the optional tracing path. |
| `experiments/cytiva/free-text-v02-comparison-v01/package-manifest.json` | Refreshes only two stale documentary-envelope digests. |
| `docs/validation/REGISTRY-TRACING-REVIEW.md` | Historical review before corrections, including the original failing-suite evidence. |
| `docs/validation/REGISTRY-TRACING-CORRECTIONS.md` | Corrective changes, regression coverage and successful complete-suite result. |
| `docs/validation/REGISTRY-TRACING-PACKAGE.md` | This inventory and delivery assessment. |
| `docs/validation/REGISTRY-TRACING-PACKAGE.json` | Explicit 12-file list, LF-normalized hashes, compact verification evidence and exclusions. |

The machine inventory hashes the other 11 files and excludes its own digest to avoid self-reference. Existing historical manifests retain their original hash conventions.

## Verification and assessment

- Targeted tracing and historical binding checks: **40 passed**.
- Complete suite: **973 executed, 972 passed, 1 optional PDFium skip, zero failures/errors**, in 1749.526 seconds. All **28 tracing tests** passed, including four new correction regressions.
- Metadata is limited to explicit resource/attribute vocabularies. SDK and export failures remain non-blocking. Partial processor registration failure closes the real worker and stream in the regression fixture.
- Source/response equality, clarification, abstention and withdrawals retain baseline behavior in the disposable integration tests.
- Both existing freezes pass environment verification. The private registry inventory and bytes, 16 old notes, pilots, preserved acceptance trial and unrelated existing local work remain unchanged.
- Diff whitespace checks pass. No runtime or test file was edited after the successful complete-suite run; preparing this inventory does not require repeating that run.

Ready for an explicitly scoped commit of these 12 files. This is a reviewed local observability candidate, not a durable audit journal, a new prospective acceptance score, a dashboard or a model-cost monitor. Queues can drop spans; bounded shutdown does not forcibly terminate arbitrary blocked third-party code. Optional dependencies are pinned at the top level, without a complete wheel-hash lock.

## Exclusions

Do not include the private registry directory, either frozen runtime/inventory, the 16 old notes, either Flowshot pilot, historical raw acceptance-trial files, temporary logs, caches, virtual environments or model/PDF assets. The raw logs remain local; their digests and test summaries are recorded in the compact JSON inventory. README and roadmap are outside this delivery.

## Proposed Git metadata

Branch: `codex/registry-ui-v02-otel`

Commit subject:

```text
feat(observability): add safe local tracing for registry UI v02
```

Suggested body:

```text
Add opt-in metadata-only OpenTelemetry spans with local JSONL and loopback OTLP sinks.
Contain SDK/export failures, report fixed-phase diagnostics, and clean up partial initialization.
Add 28 tracing regressions and refresh two historical documentary bindings.
Record review evidence and the successful 973-test run (one optional skip).
```

Git authorization follows [AGENTS.md](../../AGENTS.md). This preparation does not stage or publish files.
