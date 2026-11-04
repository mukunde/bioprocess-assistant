# Reusable trace demo: review corrections

Local correction prepared on 4 November 2026 against main `f7ce8066c58a7ba4d17e86c64c8e2728409f16b8`. This addresses both P2 findings in the [review](REGISTRY-TRACE-DEMO-REVIEW.md). The original implementation report, failed probes and previous verification logs remain historical. No commit or push was performed.

## HTTP error traces

The reader now accepts the closed GET/POST × controlled-route vocabulary emitted by the existing exporter: `/`, `/api/reviewed/v1/evaluate`, the templated source route and `unmatched`. It still rejects arbitrary raw paths and reapplies the same metadata/resource allowlists. No exporter, schema or frozen method changed.

Expected registry children are determined by the exact operation, not any POST. A rejected evaluation/source root without a recorded child is labeled **root only / HTTP rejection; registry dispatch not established**. Its coverage value is `null`, distinct from complete `true` and partial/unlinked `false`. This does not claim dispatch, a lost span or complete delivery. A recorded valid child remains visible even for a 400 response; a successful evaluation with a missing child remains partial.

Regression coverage includes real malformed JSON (400, no child), validation inside the registry (400, child present), wrong-method routes, an unmatched POST with a private sentinel path, a source-route POST and a forbidden Host (403). All valid exported roots remain visible; no raw private path/body sentinel appears in the summary.

## Optional SDK metadata

The advisory dependency check now contains unexpected metadata-read exceptions with a fixed diagnostic and continues through the existing safe tracing configuration. `PackageNotFoundError` retains its existing missing-SDK message. No exception detail is printed. Authority validation remains a separate mandatory gate, and missing/invalid authority still refuses startup.

Launcher regressions inject `PermissionError` and `RuntimeError`, verify that configuration and serving are reached, check the absence of injected private detail, and confirm resource cleanup. Existing real failed-sink/summary integration tests continue to cover available guidance with unavailable telemetry.

## Verification

The corrected targeted module passed **18 tests** (18.124 seconds). The final seven-case real HTTP regression was then run separately and passed (0.940 seconds), after adding the explicit inside-registry validation case. These are overlapping checks, not 19 distinct tests.

The final complete suite passed: **991 executed, 990 passed, one optional PDFium skip, zero failures/errors**, in 551.299 seconds. All 18 demo/summary tests, including the three new regression methods, and the existing 28 tracing tests passed. No background Unicode decoding diagnostic appeared in this run.

Runtime and test code remained unchanged after the complete suite started. The short [operator guide](../REGISTRY-TRACE-DEMO.md) explains neutral root-only rejection and non-blocking metadata errors. This correction does not repeat the earlier browser trial, claim a new acceptance score or create a runtime freeze.

Raw logs remain ignored in `.local-tools/otel-ui-walkthrough/`: `reusable-demo-corrections-targeted.log`, `reusable-demo-corrections-http-final.log`, `reusable-demo-corrections-full.log` and its result JSON. The original review probes are retained separately.

## Preservation

The final preservation check passed for private registry bytes/inventory, both freezes (36/52 pins with environment verification), 16 old notes, pilots and previous raw walkthrough evidence. No existing tracked implementation file, source record or human decision is part of these edits; the local demo candidate remains additive to main. The initial implementation/review reports remain unchanged. HEAD and index remain unchanged.
