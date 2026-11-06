# Roadmap for evidence-grounded bioprocess assistance

Help bioprocess engineers inspect source-backed troubleshooting guidance.
Keep source review, documentary previews, and operational decisions separate.

## What works today

| Area | Available now |
| --- | --- |
| Graph chat | Chainlit retrieves curated Neo4j facts, validates the model's selections, and displays citations. [Grounding decision](ADR-001-knowledge-graph-grounding.md) |
| Local demo | Guided and bounded English and French requests use reviewed Cytiva excerpts. The Windows setup has same-PC evidence. [Demo guide](DEMO-FIRST.md) |
| MabSelect | The guided Chainlit mode uses an approved local registry. Citations and withdrawal checks follow the current registry authority. [Operator guide](CHAINLIT-MABSELECT.md) |
| Protein A/G Sepharose | The merged candidate provides a separate Chainlit preview with scoped sources, clarification, and simulated withdrawals. Its status is staged and non-activated. [Candidate guide](CHAINLIT-SEPHAROSE-CANDIDATE.md) · [PR #91](https://github.com/mukunde/bioprocess-assistant/pull/91) |
| Evidence preparation | Local Docling Graph extraction and a separate reviewed model extraction have produced development evidence. [Ingestion guide](INGESTION.md) · [Reviewed extraction](../experiments/cytiva/reviewed-r2/README.md) |
| Observability | The registry UI has optional local metadata tracing and a read-only trace summary. [Tracing guide](REGISTRY-TRACING.md) · [Trace demo](REGISTRY-TRACE-DEMO.md) |

The [project README](../README.md#watch-the-demo) links to the recorded demos.
The [Chainlit Sepharose recording](https://mukunde.github.io/bioprocess-assistant/sepharose/)
plays on GitHub Pages. Browser verification followed the README thumbnail
through to the end of the video. [Publication record](CYTIVA-VIDEO-HOSTING.md#published-chainlit-sepharose-video)
Find dated test results and design decisions in the [documentation index](README.md)
and the [history of this roadmap through 5 November 2026](https://github.com/mukunde/bioprocess-assistant/blob/6be6ce24ce7e0da547a93de9042826dc3cbe818a/docs/ROADMAP.md).

## Next priority

Prepare the local activation review for the staged Protein A/G Sepharose
candidate. The [seven-case replay](validation/SEPHAROSE-CHAINLIT-WINDOWS-PATH-REPLAY.md)
already covers scope, clarification, abstention, citations, and simulated
withdrawals. It also checks provenance delivery on short and long Windows paths.

Tie that evidence to the exact candidate revision. List any remaining gaps,
including the limits of the browser walkthrough, and document the proposed
serving scope, withdrawal rules, and rollback. Recheck only gaps that affect the
decision. Keep the candidate staged pending explicit approval. The public video
shows one preview path. Operational use requires a separate decision.

## Follow-up work

| Work | When it is ready to advance |
| --- | --- |
| Windows portability | Run the pinned protocol on a second physical PC and record the mandatory checks and any retries. [Second-PC protocol](validation/WINDOWS-SECOND-PC.md) |
| Independent acceptance | Define a held-out set for new evidence or behavior. Cover missing context, conflicting sources, negation, and unsupported quantities. Record false acceptances, abstentions, latency, and cost. [Evaluation guide](../eval/README.md) |
| Model observability | Link chat, extraction, and judge calls to their workflows. Record retries, latency, and provider usage. Version prices, label cost estimates, and enforce spending limits. Default to metadata without prompts, documents, or personal data. [Tracing guide](REGISTRY-TRACING.md) |
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
