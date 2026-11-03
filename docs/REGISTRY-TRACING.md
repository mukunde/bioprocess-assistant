# Minimal local OpenTelemetry tracing — registry UI v02

This local implementation is not a new runtime freeze. Tracing is disabled by
default. The baseline 8784 UI, both original freezes, source/selector contracts,
private authority and recorded acceptance trial are unchanged. Only explicit v02
startup options enable sinks; no global OTel provider or automatic instrumentation
is installed. The model-free path makes no model/embedding/judge calls.

## Dependencies and startup

Use a separate development environment or the prepared verification environment;
do not install new packages into the frozen `.venv-demo` environment.

```powershell
python -m pip install -r requirements-observability.txt
New-Item -ItemType Directory -Force .local-tools\telemetry | Out-Null
python -m demo.registry_ui_v02 --registry-root .local-tools\mabselect-registry-v02-runtime --port 8785 --trace-file .local-tools\telemetry\registry-v02-run-001.jsonl
```

The three top-level OTel packages are pinned to 1.45.1. This is an optional pin
set, not a wheel-hash lock for the entire dependency closure. The verification
machine already has these versions; this implementation required no installation.
Use an existing approved registry root; startup never creates or activates one.
Choose a new trace filename for each run. Existing files are never overwritten or
appended to. CLI trace files inside the configured authority root are refused.
The parent directory must already exist. If a sink/dependency cannot
be initialized, startup continues with the remaining sinks or tracing disabled,
and emits only a generic diagnostic. Keep trace files in ignored local storage.

Optional standard OTLP/protobuf export to an already running local collector:

```powershell
python -m demo.registry_ui_v02 --registry-root .local-tools\mabselect-registry-v02-runtime --port 8785 --trace-otlp-endpoint http://127.0.0.1:4318/v1/traces
```

Both options can be supplied together, with independent batch queues. Only literal
loopback HTTP endpoints with `/v1/traces` are accepted; no credentials, query,
fragment, hostname resolution, proxy configuration, redirect or retry is used.
Each OTLP transport operation has a one-second socket timeout and a bounded response
body. Standard protobuf encoding comes from the pinned OTel package. Failed or
partially rejected exports are counted as failures without copying response text.
External backends/authentication and collector deployment are outside this slice.

## Data contract

The allowlist uses stable HTTP attribute names plus `bioprocess.*`, versioned by
`bioprocess.trace_schema = registry-ui/v1`. Resource fields are explicit constants:
`service.name = bioprocess-registry-ui-v02` and the schema version. Environment
resource detectors, incoming `traceparent`/baggage and exporter credential variables
are not used. SDK internal metrics use an explicit no-op meter, not an ambient
backend. Each HTTP GET/POST starts a fresh generated trace; `registry.evaluate`
or `registry.source` is its child. A later source-page request has its own trace,
not a fabricated parent relationship to a previous evaluation. Enabled responses
add only `X-Trace-Id`; response bodies, source HTML and citation URLs are unchanged.

Captured span data:

- trace/span/parent IDs, fixed operation name and span kind;
- start/end timestamps, elapsed milliseconds and status;
- method, templated route and HTTP status;
- validated release/source IDs, bounded item/citation counts and outcome enum;
- controlled error categories, without exception messages, stack traces or events.

No payload, quotation, request ID, raw URL/query, user text, request headers, IP,
credentials, private filesystem path, prompt or PDF is captured. Unknown metadata
fields are rejected. Local trace files still reveal usage times and release/source
identities: retain them locally and manage retention deliberately. No token/cost
fields or percentile benchmark are manufactured for this deterministic slice.
These are server-side durations, not browser-rendering or model-inference timings.

Clarification, partial support and scoped abstention are normal outcomes. Registry
unavailability and server errors set error status. Source-operation exceptions
have a fixed category; a 404 does not become a server error. Authority checks and
withdrawal decisions always remain the registry's responsibility.

## Failure and lifecycle policy

Every sink uses the SDK BatchSpanProcessor: 256 queued spans, batches of at most
32, a one-second scheduling interval. Export/file I/O runs outside request threads.
A slow or failed sink cannot select a different answer, activate authority, retry a
business operation or prevent another response. Queues may drop traces under load;
this is best-effort observability, not a durable compliance audit journal. A generic
first-export-failure warning and in-process failure counter aid diagnosis.

SDK start/attribute/status/context/end failures are contained and counted by fixed
phase in `Tracing.sdk_failures`, separately from `export_failures`. Each phase emits
at most one generic warning per tracing instance; no SDK error text is logged.
A broken diagnostic logger cannot interrupt responses. Disabled tracing does not
count missing spans as failures. If sink registration fails, the unregistered
processor (or exporter if processor construction failed) is shut down with a
bounded wait; a permanently stalled third-party shutdown may finish later.
Shutdown waits at most one second
for telemetry cleanup; a stuck exporter may lose pending spans. Explicit diagnostic
flush is available to tests/operators and is never invoked by a response handler.
The existing 15-second UI fetch/body deadline and source-failure boundaries remain.

## Tests and scope

```powershell
python scripts/run_tests.py --temp-root "$env:LOCALAPPDATA\Temp" tests.test_registry_tracing tests.test_registry_ui_v02
```

The tests use the actual OTel SDK, disposable authorities and a loopback collector,
not the private registry. They cover trace parentage/concurrency, payload/resource/
header privacy, exact response/source equality, unknown/missing authority, withdrawals,
SDK/export/logger failures, per-phase diagnostics, partial-initialization resource
cleanup, stalled exporters and saturated queues, new-file-only
JSONL and OTLP wire data/redirect/partial-rejection handling.
No LLM, paid service or external collector is needed. The previous UA01-UA08 result
remains historical; regression reuse is not a new independent acceptance score.
This adds tracing only, not dashboards, model-budget enforcement, Ragas or Promptfoo.

## Primary references

- [OTel Python manual instrumentation](https://opentelemetry.io/docs/languages/python/instrumentation/)
- [SDK trace/export API](https://opentelemetry-python.readthedocs.io/en/latest/sdk/trace.export.html)
- [OTLP protocol](https://opentelemetry.io/docs/specs/otlp/)
