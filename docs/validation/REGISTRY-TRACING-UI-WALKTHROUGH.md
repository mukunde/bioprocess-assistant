# Instrumented registry UI v02 walkthrough

Executed on 4 November 2026 against merged main `875d3aec860cca320ce5cca3e412b8dfee4edac9` (tracing implementation from PR83, status documentation from PR84). This is a known-case browser rehearsal with supplemental deterministic HTTP checks, not a blinded evaluation, new source approval or prospective acceptance score.

## Isolation and method

- Used the actual `demo.registry_ui_v02` server and OTel SDK, with no implementation changes, model calls or paid APIs.
- Created an authority inside a Python `TemporaryDirectory`. Existing test helpers issued explicitly marked **SYNTHETIC TEST ONLY** fixture authorizations; these are not human approvals and never applied to project/private data.
- Served the instrumented UI and an untraced comparison server over loopback, sharing only that disposable authority. A test-only response recorder captured outgoing responses after the normal handler completed.
- Enabled a new local JSONL trace file and a loopback OTLP endpoint deliberately bound without a listener. The unavailable collector tested sink failure while JSONL remained usable.
- Submitted each of the four browser scenarios once in the in-app browser. Inspected the rendered states, the source page, provenance disclosure and clarification focus action. Supplemental HTTP requests separately compared exact response/source content and withdrawal scope.

## Browser observations

| Scenario | Controls | Observed outcome and checks |
| --- | --- | --- |
| Sourced response | Exact unsuffixed MabSelect; precipitated/denatured substances; cleaning options only | Documented support, Q05. Four formulations remain alternatives, with conditions and reservations. Opened E167-P: complete quotation, PDF page 167, offsets, quote/PDF hashes and reviewed source provenance available. |
| Clarification | MabSelect family, variant unknown; context unknown; cleaning options only | One clarification action asks for exact product and context, without requiring a confirmed diagnosis or selecting a recipe. Its button focuses the product control. Expanded Q09 citations and review limits. |
| Abstention | MabSelect SuRe; hydrophobic context; numerical maximum pressure only | No numerical pressure or substitute supplied. Absence explicitly limited to selected reviewed excerpts, not the whole manual. No unsupported citation is fabricated. |
| Withdrawal | Repeat the first controls after withdrawing E167-P in both disposable releases | UI displays Evidence held; the item is quarantined, aggregate status is abstained, and no incomplete procedure/passages/citations are supplied. The previously opened release-v01 source URL now displays Source held without a quotation. |

The withdrawal introduced release-v02 with two explicitly scoped synthetic withdrawal events: one for release-v01/E167-P, one for release-v02/E167-P. It did not globally withdraw every product or source. Supplemental checks confirmed the current-release URL also refuses the quotation, while an independent hydrophobic-cleaning task remains supported alongside the held task.

## Citations and traces

- All four UI response bodies exactly matched the untraced server at the corresponding authority state.
- Supplemental checks covered **nine unique cited sources** across the first two cases. All nine source pages matched untraced HTML exactly, retained the complete original quotation and correct page, and passed the stored quotation SHA-256 check. Only E167-P was opened as a full browser source page; the nine-source sweep is HTTP evidence, not nine manual browser inspections.
- **37 JSONL spans**: 20 HTTP root spans and 17 registry child spans, including browser and supplemental requests. Each of the 20 captured HTTP responses has a matching `X-Trace-Id` and status attribute. Registry evaluation/source children have the correct parent and trace IDs. Source requests are separate traces from evaluation requests.
- Resource constants and attribute allowlists pass. No source quotation, request body, request identifier, private path, credential/header field or exception detail was found in the inspected traces. Counts and identifiers are metadata only; the local raw response recorder is separate from telemetry and remains ignored.
- **20 expected failed OTLP batch exports**, zero SDK failures. JSONL export and the observed responses continued normally; this tests one unavailable-collector condition, not every transport failure.
- All scenario and source-check requests returned HTTP 200. One unrelated browser request for `/favicon.ico` returned 404, recorded with an unmatched templated route. No browser warning/error entry was returned by the final console-log check; this is not a continuous console recording across every navigation.

## Anomalies and limits

- Cosmetic: the demo has no favicon at the requested path. It does not affect guidance, citation safety or trace delivery to JSONL.
- One automation wait for the held-state text expired before the next accessibility observation showed the completed correct result. No second submission or method change was made; no application timeout/failure was displayed. This is retained as a harness observation rather than counted as an application defect.
- The actual browser viewport was narrow and used the existing stacked layout. This walkthrough does not establish desktop-wide layout quality, second-PC portability, production performance, scientific suitability or whole-manual coverage.
- Queues remain best effort; the trace set is a diagnostic artifact, not a durable compliance audit. No model token/cost values are inferred.

No blocking application anomaly was observed in these four known scenarios. No code correction or new freeze was needed.

## Cleanup and evidence

Both test servers stopped and the temporary authority was automatically removed. The approved private registry, both frozen closures, 16 old notes, both pilots, prior trials and tracked implementation files remain unchanged. No commit or push was performed.

The compact [machine-readable result](REGISTRY-TRACING-UI-WALKTHROUGH.json) records checks and preservation. Raw responses, JSONL traces, test-only harness and control files remain ignored under `.local-tools/otel-ui-walkthrough/`; they are excluded from this documentary report. The former full-suite result remains 972 passed / one optional skip on the merged tracing checkpoint; this walkthrough does not claim a new complete-suite run.

For the startup options and privacy boundaries, see the [tracing guide](../REGISTRY-TRACING.md). A polished one-command walkthrough and integration of this local report into the README/roadmap remain separate follow-up work.
