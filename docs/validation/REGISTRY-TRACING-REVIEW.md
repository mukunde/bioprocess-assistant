# Local registry UI tracing review

Review scope: the uncommitted OpenTelemetry candidate for registry UI v02, against main `88a1177a4386c487be9d36da49538d2cd81463c2`. No runtime corrections, registry changes, commits or pushes were performed during this review.

## Decision

The candidate is not ready to freeze. The metadata boundary and response availability are covered by passing tests, but two tracing failure-handling gaps need correction. The complete suite also exposes a pre-existing documentary binding failure.

## Findings

### P1 — Historical delivery manifest prevents a green complete suite

`experiments/cytiva/free-text-v02-comparison-v01/package-manifest.json`, lines 16 and 44, retains old LF-normalized hashes for two documentary manifests:

| Referenced file | Recorded SHA-256 | Current SHA-256 |
| --- | --- | --- |
| `experiments/cytiva/compositional-navigation-v04-results/manifest.json` | `2d2d1266d412a92cca7c0ff994a4af1858810f41d23b71982136b961da404204` | `bf7d85f684c3ad7fc97de4057c3a3505ac77084a4a1f782900f70d5d6fc5e7ee` |
| `experiments/cytiva/reviewed-v05-evaluation/manifest.json` | `81e771f6b9179ebb933b954d74927a8aa7a0469f6c1a8342ecf87f4c54233330` | `976621fc8de7333b25b198011d669a14169c39989d6f6a64d7f3efb4871041b3` |

Both mismatches are already present in HEAD; the tracing changes did not introduce them. The failing regression is `FreeTextV02EvaluationTests.test_delivery_manifest_and_actual_collective_review_bindings`, in `tests/test_free_text_v02_evaluation.py:118`.

Required correction: inspect the previous documentation changes, then refresh only these documentary-envelope hashes. Preserve source, review, result and runtime bindings; retain the existing integrity test.

### P2 — SDK span failures silently disable trace evidence

`demo/registry_tracing.py:109` catches a failed `start_span` without a warning or health counter. Attribute, status and span-end failures are similarly swallowed in `Span`.

A controlled tracer failure returned the business operation normally, but produced no recording span, zero export failures and zero diagnostic warnings. Availability is preserved, but an operator cannot distinguish missing telemetry from successful instrumentation. Existing failure tests establish response preservation without requiring this diagnostic signal.

Required correction: add a safe, bounded diagnostic signal for SDK instrumentation failures, distinct from exporter failures. Use fixed categories without exception messages, stacks or request content, and preserve non-blocking responses. Add diagnostic regression assertions.

### P2 — Partial initialization can retain an export worker and open file

At `demo/registry_tracing.py:323`, a batch processor is constructed before registration with the provider. If registration raises, the exception handler warns but does not own and close the unregistered processor/exporter.

A controlled registration failure using the actual SDK confirmed that tracing became disabled while the worker remained alive and the JSONL stream stayed open. The review probe explicitly cleaned up these resources afterward.

Required correction: retain ownership of partially initialized resources and clean them up on registration failure, with bounded shutdown. Add regression checks for worker termination and stream closure, alongside response availability.

## Checks that passed

- Disabled-by-default, optional SDK integration; no replacement of the global tracer provider.
- Explicit attribute and resource allowlists. Inspected paths do not export request bodies, quotations, headers, raw URLs, user text, exception messages or stacks.
- Incoming trace context and baggage are not adopted. Ambient metrics export is disabled for the dedicated provider and batch processors.
- JSONL and loopback-only OTLP exports are asynchronous and bounded. Export failures preserve HTTP response behavior and produce a generic warning/counter.
- Citation bodies and response payloads remain intact; an enabled trace identifier is added separately in a response header.
- No trace file may be placed inside the protected registry authority directory through the CLI configuration path.

These checks support the tested metadata-only boundary; they do not establish durable audit delivery, production latency percentiles or complete failure observability.

## Test evidence

Command: `python scripts/run_tests.py --temp-root <Windows temporary directory>`, using the prepared Python 3.13.0 verification environment.

- Complete suite: **969 tests; 967 passed, 1 failed, 1 optional PDFium skip**; no unittest errors.
- All **24 OpenTelemetry tests passed** in that complete run.
- The sole test failure is the historical manifest binding above. The failed log was preserved.
- Two background reader-thread Unicode decoding diagnostics occurred during the existing Windows launcher negative-input test. That test was marked passed; this limits confidence in those subprocess diagnostic captures and is separate from the tracing findings.
- Additional controlled probes confirmed both P2 findings; no implementation changes followed those probes.

Local diagnostic evidence is retained outside the versioned package in `.local-tools/backpressure-commit/registry-ui-v02-telemetry/`: `full-suite.log`, `full-suite-result.json`, `review-probes.json` and `review-preservation.json`.

## Preservation checks

Raw-file comparisons confirmed the private registry, all 16 old notes, both pilots, the original acceptance trial and all unrelated pre-existing files unchanged. Both frozen inventories passed environment verification: free-text v03 (36 pinned files) and MabSelect documentary handoff (52 pinned files). HEAD remained unchanged and the Git index remained empty. No commit or push was performed.

## Before freeze

Correct the two failure-handling gaps, add their regressions, repair the separately identified documentary bindings and rerun the appropriate tests and complete suite. Do not alter either frozen method or historical trial results.
