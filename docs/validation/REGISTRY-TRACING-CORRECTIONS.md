# Local tracing correction and verification

This follow-up addresses the three findings in [the initial review](REGISTRY-TRACING-REVIEW.md). That report and its failed-suite evidence remain historical; this document records the corrected local candidate. No commit or push is authorized or performed.

## Changes

1. **SDK failure visibility:** `Tracing.sdk_failures` counts failures using the closed vocabulary `start`, `attributes`, `status`, `context`, `end`. The first failure of each phase emits one generic warning per tracing instance. No exception text, stack, request content or private path is included. A disabled span is not treated as an SDK failure. Export failures retain their separate counter. Diagnostic logging failures remain contained.
2. **Partial initialization cleanup:** sink setup retains explicit references to the exporter and batch processor. A registration failure shuts down the unregistered processor; a processor construction failure shuts down the exporter. Cleanup waits at most one second on a daemon thread, so a permanently stalled third-party shutdown cannot block startup indefinitely. This is bounded waiting, not forced termination of arbitrary blocked code.
3. **Historical documentary bindings:** only the two stale documentary-envelope hashes in `free-text-v02-comparison-v01/package-manifest.json` were refreshed. Referenced artifacts, reviews, results, source bindings and frozen runtime inventories were not rewritten. The existing manifest integrity regression is unchanged and passes.

## Regression coverage

Four new tests extend the existing 24 tracing tests:

- phase counters, one warning per phase, no private error details, normal response delivery even when the logger fails;
- actual SDK processor registration failure: worker stopped, JSONL stream closed, HTTP still available;
- processor construction failure: exporter stream closed;
- bounded return when partial-resource shutdown stalls.

The targeted tracing and historical-manifest modules passed **40 tests** in 198.013 seconds using the prepared verification environment and `scripts/run_tests.py` with an explicit Windows temporary root. An earlier direct unittest invocation failed because the restricted process selected an inaccessible Sandbox temporary directory; it is not counted as successful verification. The project launcher run used disposable fixtures and loopback servers, never the private registry.

## Complete suite and preservation

The complete suite passed: **973 tests executed, 972 passed, 1 optional PDFium test skipped, zero failures and errors**, in 1749.526 seconds. All **28 tracing tests** passed in that run. No background `UnicodeDecodeError` diagnostic was observed in this execution. Expected fault-injection warnings (queue saturation, unavailable sinks and generic SDK/export failures) do not indicate failed tests. The initial review logs and acceptance-trial artifacts remain separate from this corrected run.

The post-suite preservation check passed: private registry bytes and inventory unchanged; both freezes valid with environment verification (36 and 52 pinned files); 16 old notes, pilots, original trial and unrelated pre-existing files unchanged; HEAD unchanged and index empty. `git diff --check` passed. No commit or push was performed.

The three initial findings are addressed for this local candidate. This correction does not activate a new serving version, change either freeze or establish independent prospective acceptance results.

Local diagnostic evidence: `.local-tools/backpressure-commit/registry-ui-v02-telemetry/corrected-targeted.log`, `corrected-full-suite.log`, `corrected-full-suite-result.json` and `corrected-preservation.json`. These temporary verification files are not a new runtime freeze or an independent UI acceptance trial.
