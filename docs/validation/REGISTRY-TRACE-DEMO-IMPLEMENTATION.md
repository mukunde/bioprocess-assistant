# Reusable local trace demo: implementation verification

Local candidate prepared on 4 November 2026 against main `f7ce8066c58a7ba4d17e86c64c8e2728409f16b8`. No commit or push was performed. This separate entry does not replace registry UI v02, expand a frozen closure or activate authority.

## Delivered behavior

- `demo.registry_demo` reuses the existing UI/service and adds a link to a local, read-only metadata summary. The default port is 8786, separate from 8784/8785. Authority is an explicit argument and passes the existing registry snapshot validator before startup; no preparation, approval or repair is performed.
- Each run chooses a new JSONL session filename outside authority. There is no automatic package/cache installation or browser opening. Tracing failure leaves guidance available; binding/authority failure returns a controlled diagnostic.
- `/demo/traces` reads only the server-configured session file. It accepts no client-selected filename, does not flush the exporter or trace its own refreshes, and retains loopback Host checks, no-store and the existing response security headers. Summary failure returns a generic 503 while later guidance remains available.
- `demo.trace_summary` is also a standard-library-only terminal reader. It validates the closed local trace schema, resource constants, identities, timestamps and attribute vocabulary, rejects duplicate keys/spans, skips malformed/oversized lines and leaves incomplete final lines pending. Reads are bounded to 8 MiB, 4096 spans and 16 KiB per line. Missing roots/children are shown as partial/unlinked; separate citation requests are not made children of a preceding evaluation.
- Request and source-response content are unchanged by instrumentation. Only the root page of the separate demo receives the summary panel; the original UI modules/static pages remain unchanged.

See the [short operator guide](../REGISTRY-TRACE-DEMO.md) for setup and the request → source → trace path. New-clone installation and private activation are separate prerequisites, not newly validated capabilities of this candidate.

## Targeted tests

The 15 tests in `tests/test_trace_demo.py` pass with the project test runner and an explicit Windows temporary root (31.044 seconds). They cover actual request/source/summary integration and equality with the baseline, read-only file bytes, partial lines, malformed/oversized/duplicate/untrusted data, cross-trace missing parents, standard-library operation, explicit authority and new session filenames, failed summary/sink behavior, controlled bind errors, protected trace paths and lifecycle cleanup.

The initial targeted run had one subprocess capture error because Windows child output encoding differed from the test's UTF-8 decoder. The test now sets its child `PYTHONIOENCODING` explicitly. That failed run is retained locally; it is not counted as successful verification.

## Focused browser smoke

Started the new launch function on synthetic authority inside `TemporaryDirectory`, using existing fixture helpers marked SYNTHETIC TEST ONLY. No approvals were created for project/private data. A test-only wrapper retained the created server solely for graceful shutdown; guidance, source and summary handlers were the actual new implementation.

The browser displayed the new summary link, submitted one known MabSelect cleaning request, opened E167-P, returned to guidance and opened the summary. The summary showed **5 HTTP requests / 7 spans**, including the request and source child spans with distinct trace IDs. Refresh left that count unchanged. No warning/error entry was returned by the consulted browser log. The existing favicon request remained an unrelated 404.

The launcher returned zero, the server stopped and the temporary authority was removed. This checks only the new navigation/summary behavior, not a repeat of the four-case instrumented trial, independent acceptance, scientific validation or a fresh-install/second-PC gate. Raw smoke traces and the test-only harness remain local and ignored.

## Complete suite and preservation

The complete maintained suite passed: **988 executed, 987 passed, one optional PDFium skip, zero failures/errors**, in 837.503 seconds. All 15 new demo/summary tests and all 28 existing tracing tests passed. No background Unicode decoding diagnostic appeared in this corrected complete run. Runtime/test code was unchanged after that run started. This is regression evidence, not a new independent answer-quality score.

Local evidence stays ignored under `.local-tools/otel-ui-walkthrough/`: `reusable-demo-targeted.log` (initial failed capture), `reusable-demo-targeted-corrected.log`, `reusable-demo-full-suite.log`, `reusable-demo-full-suite-result.json`, `reusable-demo-checks.json` and the disposable smoke folder. No raw session traces or private authority files are included in this report.

Preservation checks pass for the private registry inventory/bytes, 16 old notes, both pilots and prior raw walkthrough evidence. Both original freezes pass environment verification: v03 (36 pins) and MabSelect documentary handoff (52 pins). No pre-existing tracked file is modified; all candidate files are additive. HEAD and index remain unchanged.

## Limits

The summary is a local diagnostic projection, not a durable audit, causal workflow reconstruction, model-cost monitor or production latency benchmark. Export batching means a refresh can initially be incomplete. A large/unreadable trace file is refused rather than scanned without a bound. Arbitrary stalled third-party exporter shutdown cannot be forcibly stopped; existing bounded cleanup applies. The observation environment is separate from the frozen demo environment, and optional OTel dependencies are not a full transitive wheel-hash lock.

No application defect was observed in the focused smoke. This implementation still needs the normal code review before any new freeze or serving-default change; neither is part of this delivery.
