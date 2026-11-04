# Local demo: request → source → trace

This separate entry point reuses registry UI v02 and adds a read-only trace page.
It does not change the baseline UI, either frozen runtime, source routes or
authority rules. No model, database, paid API or collector is needed.

## Prerequisites

Use an existing **approved active registry** and the verified offline demo runtime
and tokenizer cache. A fresh clone has no approved private authority; this command
neither prepares nor activates one. Follow the existing
[installation guide](DEMO-FIRST.md#install-from-a-fresh-windows-clone) and
[registry guide](CYTIVA-REGISTRY-UI.md) first if those prerequisites are absent.
Do not turn synthetic test-fixture approvals into normal serving approvals.

Use a separate development environment with `requirements-observability.txt`, not
the frozen `.venv-demo`. The prepared verification environment is suitable.
If an observation environment is needed on Windows, after preparing the existing
runtime/cache, explicitly create one from the repository root:

```powershell
py -3.13 -m venv .venv-observe
.\.venv-observe\Scripts\python.exe -m pip install --only-binary=:all: --require-hashes -r demo\requirements-windows.lock
.\.venv-observe\Scripts\python.exe -m pip install -r requirements-observability.txt
```

The wheel lock targets CPython **3.13.0 Windows x64**. These setup commands may
download packages; they are not run by the demo. The OTel pins are not a complete
transitive wheel-hash lock. Existing frozen environments/cache stay unchanged.

## Start with one command

Replace the path with your own approved authority directory:

```powershell
.\.venv-observe\Scripts\python.exe -m demo.registry_demo --registry-root "C:\path\to\approved-registry"
```

Or use the prepared verification Python instead of `.venv-observe` if available.
Open **http://127.0.0.1:8786/**. The server is loopback-only. It checks authority
without repairing or activating it, and creates a new session filename under
ignored `.local-tools/telemetry/`. Optional flags: `--port 8786` and
`--trace-dir .local-tools/telemetry`. The trace directory must be outside authority.
An existing trace file is never overwritten. Ctrl+C stops the foreground server.

## Five-minute operator path

1. Choose the exact MabSelect product, precipitated/denatured context and cleaning
   options. Submit and read the separate alternatives, conditions and reservations.
2. Open E167-P, inspect the complete source quotation and page/provenance, then use
   **Return to MabSelect registry**. No PDF or trace data is sent to a backend.
3. Click **view the local trace summary**. If necessary, wait a moment and click
   **Refresh summary**: the exporter normally batches once per second. Inspect the
   POST root and `registry.evaluate` child, then the separate citation GET and
   `registry.source` child. The summary prints trace IDs, outcome, duration, HTTP
   status and validated release/source metadata. It does not infer a relationship
   between separate requests merely because they happened close together.
4. Optionally return to guidance and try variant/context unknown, or ask only for
   numerical maximum pressure: clarification and scoped abstention are normal
   outcomes, not telemetry errors. Retain any observations separately from earlier
   acceptance results.

Do not withdraw anything from the approved private registry for a demonstration.
The existing [instrumented walkthrough](validation/REGISTRY-TRACING-UI-WALKTHROUGH.md)
records the withdrawal case using disposable authority. Repeat it only for a
changed behavior or failure, with another explicitly disposable fixture.

## Terminal alternative and failure behavior

Use the session path printed at startup. This reader needs only the standard
library and does not open a server or access authority:

```powershell
python -m demo.trace_summary ".local-tools\telemetry\registry-demo-SESSION.jsonl"
```

There is no file-path selector or export/activation action on the summary page.
It reads only the configured session file, never displays a malformed raw line or
exception message, and applies the metadata allowlist again. Responses are
`no-store`. Reads are bounded to 8 MiB, 4096 spans and 16 KiB per line; a final
unfinished line is pending until the next refresh. Invalid/duplicate records are
counted as ignored. Missing parents/children are marked partial or unlinked.
Controlled GET/POST error-route spans are retained, including rejected methods
and unmatched routes. A rejected evaluation/source request with no recorded
registry child is labeled **root only / HTTP rejection**: dispatch is not
established. It is not presented as proof of a missing span or a completed
registry call. If the child is recorded and correctly linked, it remains visible.

A missing/oversized/unreadable file makes the summary unavailable without
interrupting guidance. Missing SDK or a failed trace sink similarly leaves the
answer path available, with generic diagnostics. An unexpected optional
SDK-metadata read error is contained and startup continues through the existing
safe tracing configuration. Authority validation remains mandatory: missing or
invalid authority refuses startup or later requests; no preview fallback, activation or repair is
performed. The trace viewer does not record traces of its own refreshes.

This is best-effort local diagnostics, not a durable audit, production benchmark,
cost monitor or new runtime freeze. Keep session files local: even metadata reveals
usage times and release/source identities. See the [tracing contract](REGISTRY-TRACING.md).
