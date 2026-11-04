# Reusable local trace demo review

Reviewed on 4 November 2026 against main `f7ce8066c58a7ba4d17e86c64c8e2728409f16b8`, with the additive local demo candidate unchanged. Scope: metadata-only rendering, read-only summary behavior, non-blocking optional telemetry and regression coverage. No implementation correction, commit or push was performed.

## Assessment

Two P2 gaps need correction before validating or freezing this candidate. The normal request → source → trace path works, metadata filtering and read-only behavior are covered, and the existing tests pass. Those tests do not cover the confirmed error-path gaps below.

## P2 — Valid HTTP error traces are discarded or misclassified

Locations: `demo/trace_summary.py:19` (accepted operation names) and `demo/trace_summary.py:113` (unconditional expectation of a registry child for an evaluation POST).

The existing exporter names root spans from the actual GET/POST method and controlled route template, including rejected requests. The reader accepts only part of that vocabulary. Real HTTP probes using disposable authority produced:

| Request | Actual HTTP result | Exporter result | Reader result |
| --- | --- | --- | --- |
| Malformed JSON POST to `/api/reviewed/v1/evaluate` | 400; rejected before registry dispatch | One valid HTTP root, no registry child | Retained but marked partial/unlinked because a child is always expected |
| POST to `/` | 404 | One valid `POST /` root | Discarded as an ignored record |
| GET to `/api/reviewed/v1/evaluate` | 404 | One valid `GET /api/reviewed/v1/evaluate` root | Discarded as an ignored record |
| POST to an unregistered route | 404 | One valid `POST unmatched` root | Discarded as an ignored record |

These are not malformed telemetry lines: the unchanged server/exporter produced them while correctly rejecting HTTP requests. Losing or mislabeling them makes the diagnostic view misleading precisely when inspecting failures. Guidance and authority enforcement still behave correctly.

Correction: align accepted names with the closed method/template combinations the exporter actually emits, without admitting arbitrary raw paths. Account for pre-dispatch rejection when describing child coverage. Do not infer dispatch or guaranteed span delivery merely from a status code; explicit bounded dispatch metadata or a neutral root-only/rejected label would avoid inventing a missing child. Add real HTTP regressions for these rejected requests and retain malformed-input/privacy tests.

## P2 — Optional dependency metadata failure aborts startup

Location: `demo/registry_demo.py:74–75`.

The advisory `importlib.metadata.version('opentelemetry-sdk')` probe catches only `PackageNotFoundError`. A controlled `PermissionError` during that optional metadata read escaped `main`, before `create_server` was called. The authority was valid and separately verified; this was not an authority refusal.

This bypasses the existing failure-tolerant tracing configuration: an optional diagnostic check can prevent guidance from starting even though it could run without telemetry. The exception also escapes the controlled startup diagnostic boundary. The current failed-sink test exercises `configure` and `create_server` directly; it does not test this launch-stage failure.

Correction: remove the redundant advisory probe or contain unexpected optional-metadata errors with a generic diagnostic and continue through the existing fail-open tracing configuration. Add a launcher regression for an unexpected metadata read failure, asserting that guidance still starts, no exception detail is emitted, and cleanup remains correct. Keep authority validation failures blocking.

## Confirmed boundaries and test evidence

- Metadata: the summary reapplies the attribute/resource allowlists and rejects unexpected keys/values, invalid identities/timestamps and duplicate records. HTML is escaped; arbitrary raw lines, file paths and exception details are not rendered by the HTTP summary path. No content leakage was observed in the tested paths.
- Read-only: a configured file is read with `rb`; the endpoint accepts no browser-selected path and offers no activation/export mutation. Summary refreshes do not emit spans or flush queues. No-store, loopback Host checks and existing security headers are retained. The new entry leaves baseline JSON responses and source HTML unchanged.
- Failure isolation: malformed/large/missing trace files and summary rendering errors are contained on the summary route; a failed trace sink preserves later guidance in the existing integration tests. This does not eliminate the launch-stage gap above.
- The 15 targeted candidate tests passed again in **16.806 seconds** during review. No full suite was rerun: the previously completed **988 executed / 987 passed / one optional PDFium skip** remains valid regression evidence for the identical runtime/test files, but does not cover these new probes.
- Four additional real HTTP probes plus one optional-metadata fault injection confirmed the findings. Probes awaited handler completion before flushing so root-span closure was not confused with missing telemetry. All probe authorities were synthetic `TemporaryDirectory` fixtures; they and their servers/exporters were cleaned up.

## Preservation and limits

Runtime/test/guide/implementation-report digests still match the prior verification record. The approved private registry, both freezes (36/52 pins), 16 old notes, pilots and earlier walkthrough evidence remain unchanged. HEAD is unchanged and the Git index is empty. Review output is additive only.

Local evidence remains ignored under `.local-tools/otel-ui-walkthrough/`: `reusable-demo-review-tests.log`, `reusable-demo-review-probes.json` and `reusable-demo-review-preservation.json`. These probes are diagnostic tests, not a new browser acceptance trial, source approval or production security/performance certification.
