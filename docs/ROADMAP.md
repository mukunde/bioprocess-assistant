# Roadmap for evidence-grounded bioprocess assistance

Help bioprocess engineers inspect source-backed troubleshooting guidance.
Keep source review, documentary previews, and operational decisions separate.

## What works today

| Area | Available now |
| --- | --- |
| Graph chat | Anthropic selects curated Neo4j results. The app validates the model's structured JSON selection and renders graph facts with citations. [Grounding decision](ADR-001-knowledge-graph-grounding.md) |
| Local demo | Guided and bounded English and French requests use reviewed Cytiva excerpts. The Windows setup has same-PC evidence. [Demo guide](DEMO-FIRST.md) |
| MabSelect | The guided Chainlit mode uses an approved local registry. Citations and withdrawal checks follow the current registry authority. [Operator guide](CHAINLIT-MABSELECT.md) |
| Protein A/G Sepharose | The merged candidate provides a separate Chainlit preview with scoped sources, clarification, and simulated withdrawals. Release v03 was verified in one approved local installation. The public recording shows the preview; it does not provide access to that installation. [Candidate guide](CHAINLIT-SEPHAROSE-CANDIDATE.md) · [PR #91](https://github.com/mukunde/bioprocess-assistant/pull/91) |
| Evidence preparation | Local Docling Graph extraction and a separate reviewed model extraction have produced development evidence. [Ingestion guide](INGESTION.md) · [Reviewed extraction](../experiments/cytiva/reviewed-r2/README.md) |
| Observability | The local OpenTelemetry viewer shows request, Anthropic, and Neo4j timing, token counts, and estimated model cost. The benchmark links each result to its trace and enforces a spending reserve. The registry UI has its own local metadata traces and read-only summary. [Graph chat traces](LOCAL-GRAPH-CHAT.md#optional-local-traces) · [Benchmark protocol](GRAPH-CHAT-MEASUREMENT.md) · [Registry trace demo](REGISTRY-TRACE-DEMO.md) |

The [README thumbnail](../README.md#watch-the-demo) opens the
[1080p graph chat demo](https://mukunde.github.io/bioprocess-assistant/graph-chat/).
Browser verification confirmed that the 27-second video plays inline at
1920 × 1080 without signing in or downloading the file.
[Pages deployment](https://github.com/mukunde/bioprocess-assistant/actions/runs/42224594186)

The [Chainlit Sepharose recording](https://mukunde.github.io/bioprocess-assistant/sepharose/)
remains available separately.

Find dated test results and design decisions in the [documentation index](README.md)
and the [history of this roadmap through 5 November 2026](https://github.com/mukunde/bioprocess-assistant/blob/6be6ce24ce7e0da547a93de9042826dc3cbe818a/docs/ROADMAP.md).

## Latest graph chat result

On 6 November 2026, one structured-output run of G01 returned both expected
paths with five citations that matched the Neo4j seed. It took 9.01 s and used
3,515 input and 124 output tokens, at an estimated USD 0.012405.
[Result and limits](GRAPH-CHAT-MEASUREMENT.md#g01-with-structured-output)

## Next priority

Complete the structured-output baseline. Verify the simulated retrieval
failure offline first. Then propose a separate budget for a repeatable run
of G01–G04. Check citation fidelity, abstention, and consistency between
passes. Report trace coverage, request and stage latency, token use, and
estimated cost.

The first successful G01 run does not establish repeatability or coverage of
the other questions. The prior runs reserved USD 0.984984 of the USD 1.00
ceiling. Get approval for a new ceiling before making live calls.

## Follow-up work

| Work | When it is ready to advance |
| --- | --- |
| Windows portability | Run the pinned protocol on a second physical PC and record the mandatory checks and any retries. [Second-PC protocol](validation/WINDOWS-SECOND-PC.md) |
| Independent acceptance | Define a held-out set for new evidence or behavior. Cover missing context, conflicting sources, negation, and unsupported quantities. Record false acceptances, abstentions, latency, and cost. [Evaluation guide](../eval/README.md) |
| Wider model observability | After the chat baseline, apply the same metadata and budget rules to extraction and judge calls. [Tracing guide](REGISTRY-TRACING.md) |
| Generated-answer evaluation | Calibrate Ragas judges and run Promptfoo attacks with benign controls once the corresponding answering path is in scope. |
| Evidence publication | Measure extraction precision and recall on annotated claims. Check source identity, quotations, quantities, and applicability. Exercise review, idempotent import, and rollback before publishing claims to Neo4j. [Claim contract](CLAIM-CONTRACT-V02.md) · [Ingestion guide](INGESTION.md) |
| Retrieval comparison | Compare graph retrieval, passage retrieval, and LightRAG on the same reviewed corpus, inputs, and budget. Measure evidence quality and resource use before choosing a serving approach. [Three-arm protocol](experiments/retrieval-comparison-protocol.md) |

Consider OpenSPG KAG only if measured reasoning failures justify a separate
comparison. Consider fine-tuning only after an evaluation identifies a gap it
could address. Reopen document conversion when a new format, a required source,
or a measured failure calls for it.

## Scope of validation

The current evidence supports bounded documentary and software checks.
Operational use requires separate scientific validation and approval.
