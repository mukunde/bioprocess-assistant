# Instrumented UI walkthrough delivery

Prepared on 4 November 2026 against main `875d3aec860cca320ce5cca3e412b8dfee4edac9`. This is a documentary delivery of the already executed registry UI v02 walkthrough; no new browser trial, runtime change or source approval is implied.

## Explicit five-file inventory

| File | Purpose |
| --- | --- |
| `docs/validation/REGISTRY-TRACING-UI-WALKTHROUGH.md` | Original walkthrough report: four browser scenarios, citation/trace checks, anomalies and limits. |
| `docs/validation/REGISTRY-TRACING-UI-WALKTHROUGH.json` | Original compact outcomes, preservation results and raw local-evidence digests. |
| `docs/validation/REGISTRY-TRACING-UI-PROVENANCE.json` | Compact provenance linking source identities, reviewed code, retained local evidence and offline checks. No quotations or raw traces. |
| `docs/validation/REGISTRY-TRACING-UI-PACKAGE.md` | This inventory, delivery assessment and proposed commit. |
| `docs/validation/REGISTRY-TRACING-UI-PACKAGE.json` | Explicit file list and LF-normalized delivery hashes; excludes its own hash to avoid self-reference. |

See the [walkthrough report](REGISTRY-TRACING-UI-WALKTHROUGH.md),
[results](REGISTRY-TRACING-UI-WALKTHROUGH.json) and
[provenance](REGISTRY-TRACING-UI-PROVENANCE.json).

## Retained results and verification

- Four known browser scenarios observed once each: sourced support, clarification, pressure abstention and withdrawal. The four response bodies matched the untraced comparison at the appropriate authority state.
- Supplemental deterministic HTTP checks verified nine unique source pages, complete quotations, page labels and quotation hashes. Only E167-P was opened as a full source page in the browser; the nine-source sweep is not nine manual inspections.
- Thirty-seven JSONL spans: 20 HTTP roots and 17 registry children, with response trace-header correlation, correct parent links, separate citation traces and allowlisted metadata. The one favicon request returned 404; scenario/source requests returned 200.
- Twenty deliberately failed OTLP batch exports did not block responses or local JSONL delivery; no SDK failures were observed. This count is not a count of failed user requests or lost JSONL spans.
- The withdrawn old/current source quotations were refused. A supplemental combined request kept an independent hydrophobic-cleaning task supported.
- Packaging checks reread retained evidence and verify its original raw digests, source/response bindings, trace structure/privacy, code identity and cleanup. They do not rerun or rescore the browser trial.
- Exact untraced-response/HTML equality remains the recorded assertion from the original live comparison. The untraced baseline bodies were not separately archived; this packaging pass does not independently recompute that comparison.
- Both frozen closures still verify (36 and 52 pins). Private registry bytes/inventory, 16 old notes, pilots, earlier trial artifacts and tracked files remain unchanged. The Git index is empty.

The previous complete-suite evidence remains 972 passed / one optional skip on `a8272e9`; the 20 documentary tests passed on `875d3ae`. Neither is represented as a new complete-suite run for this report-only package.

## Limits and exclusions

This is known-corpus diagnostic evidence with synthetic authorizations in a disposable `TemporaryDirectory`, not independent prospective acceptance, scientific validation, a new freeze, second-PC validation or a production latency benchmark. The original records retain the favicon 404 and an automation selector wait that expired before the correct held state was observed, without a repeated submission.

Exclude the test-only runner, raw HTTP response recordings, raw JSONL spans, temporary controls, private authority, both frozen closures, 16 old notes, both pilots, earlier raw trials, dependencies, caches and PDFs. Those excluded local files are not needed to read the compact report, but independently replaying all original checks requires the retained local evidence. Hashes alone do not prove browser interaction or independently reproduce the original observations.

No application code, README or roadmap is included. No new consent or manual approval is manufactured by the synthetic fixture authorizations. The servers stopped and the temporary authority was removed at the end of the recorded run.

## Proposed Git metadata

Branch: `codex/registry-otel-ui-walkthrough`

Commit subject:

```text
test(observability): record instrumented registry UI walkthrough
```

Suggested body:

```text
Record four known UI scenarios with exact baseline-response checks.
Preserve citation provenance, scoped withdrawal and metadata-only trace evidence.
Document unavailable-collector behavior, limitations and protected-file checks.
Keep raw recordings, the disposable harness and private data outside the delivery.
```

Git authorization follows [AGENTS.md](../../AGENTS.md). This preparation does not stage or publish files.
