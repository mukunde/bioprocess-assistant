# Architecture illustration

The English diagram shows the logical flow verified against `agent.py`, `tools.py`,
`grounding.py`, `ingestion/publish.py`, the reviewed r2 package and the active roadmap.
The SVG is the editable, self-contained source; its embedded logos require no
external requests. The README displays the matching PNG export for consistent
rendering. Keep the SVG and PNG in sync when editing the illustration.

The spatial layout is inspired by the user's [agentic RAG reference illustration](https://github.com/jamwithai/production-agentic-rag-course/blob/main/static/week7_telegram_and_agentic_ai.png):
sources and ingestion at the top, storage on the right, then the client, agent,
retrieval loop and cross-cutting future capabilities below. The content describes
this repository: the reference's Redis, Telegram, FastAPI, Jina embeddings and hybrid
search are not depicted as implemented project components.

The retained detailed illustration covers document conversion, local extraction
and review, optional reviewed-record publication, the subscription experiment,
tool calls and planned adapters. The earlier overview is not included in this package.

## Flow and status

1. The question goes from Chainlit to the agent.
2. The agent invokes `query_graph`; the tool uses Neo4j English full-text search
   and parameterized Cypher. It does not generate arbitrary Cypher.
3. Retrieved results return to the agent.
4. The agent selects result IDs; the renderer receives that selection and the
   retrieved facts for ID/source checks and deterministic rendering.
5. The response returns to the client. Invalid output, missing knowledge and
   operational errors have separate handling; out-of-scope questions may bypass retrieval.

The two extraction routes branch from document conversion:

- **Local pipeline:** Docling converts the PDF; Docling Graph uses its native
  HybridChunker and a local Ollama model for schema-based extraction, followed by
  source checks and append-only manual decisions in SQLite. Optional Neo4j
  publication produces a separate snapshot.
- **Reviewed manual test, pages 100–102:** Docling converts the excerpt; the full
  three-page input (59 source elements) is manually submitted to GPT‑6.1 Sol
  through a subscription, followed by validation and human review. This test
  does not use Docling Graph extraction or automatic chunking. The final package
  contains 33 reviewed statements: 19 validated and 14 validated with reservations.

Neither route automatically enriches the current chatbot. The legacy local
snapshot and the reviewed v0.2 package need separate reviewed adapters before
contributing to chatbot knowledge; publication of the reviewed package is disabled.
Dashed coral arrows represent those planned integrations, not working pipelines.

Ragas, Promptfoo, OpenTelemetry and the LightRAG comparison remain roadmap items.
The detailed diagram distinguishes OpenTelemetry runtime traces and usage metadata,
Ragas retrieval/answer quality evaluation, and Promptfoo adversarial tests and
regression checks. A shared instrumentation/test interface groups the planned
connections into three parallel lanes: runtime metadata, evaluation inputs, and
adversarial cases with returned checks/failures. It is a logical grouping, not an
additional implemented service; none of these arrows denotes an installed integration.
Ollama is used for the local extraction route; local chatbot serving is future work.
Human documentary review is not scientific validation or authorization to execute
the laboratory procedures described in a manual.

## Chunking strategy

The local route uses **document-based and hierarchical chunking**: document
structure guides boundaries around sections, paragraphs, lists and table context;
headings and source page references travel with the chunks. The HybridChunker
then splits or merges content to respect a token budget. The local example uses
800 tokens, which is a configuration choice, not a demonstrated optimum.
Large tables can still be split; row/header associations, footnotes and conditions
need checking. The diagram's chunking callout applies only to this local route.
The reviewed three-page test used the full input, not this chunking stage.

## Plain-language labels

- **Reviewed manual test** replaces the internal experiment label **r2** in the
  diagrams. `r2` identifies the second prepared test package with a revised prompt;
  it is not an edition of the Cytiva manual or a model version. Technical paths
  retain that identifier for reproducibility.
- **Source-linked statements / reviewed records** replace **evidence** in the
  diagrams. Here evidence means the source passage, page and location supporting
  a statement, with provenance identifiers. It does not mean independent scientific
  proof. In extraction contracts, a **claim** is an extracted statement to verify.
- **Graph search vs text passages vs LightRAG** names a planned comparison on the
  same corpus and questions: current lexical symptom search plus graph traversal;
  a simple baseline retrieving text passages without a graph; and LightRAG as an
  alternative candidate. These are retrieval approaches, not three language models
  or three already deployed backends.

## Tables and illustrations: capability versus tested configuration

Docling can reconstruct structured tables and export their contents; it can also
extract figure images. Picture classification and descriptions are optional
enrichment steps, including local vision-model options. Extracting an image is
different from interpreting its chart values or diagram relationships. See the
official [table export example](https://github.com/docling-project/docling/blob/main/docs/examples/export_tables.py),
[figure export example](https://docling-project.github.io/docling/_generated/examples/export_figures/)
and [enrichment documentation](https://docling-project.github.io/docling/usage/enrichments/).

Docling Graph builds on [Docling conversion](https://docling-project.github.io/docling-graph/fundamentals/extraction-process/document-conversion/)
to extract schema-constrained entities and relationships. It is not a second
independent table parser. Correct table structure, readable figure content and
preserved context remain prerequisites for reliable extraction. Complex merged
cells, multi-page tables, chart quantities and diagram semantics need dedicated
checks against the rendered PDF.

The frozen pages 100–102 preparation profile disables OCR and table-structure
recognition for this born-digital, non-tabular excerpt. The reviewed result therefore
does not validate table or illustration understanding. Those require a separate
representative test; the historical conversion profile has not been changed.

## Logo sources

Original files and SHA-256 values are recorded in [logos/sources.json](logos/sources.json).
The marks identify technologies, including future candidates; they do not indicate
that all depicted components have been integrated.

| Technology | Asset origin |
|---|---|
| Docling | [Official Docling repository](https://github.com/docling-project/docling/tree/main/docs/assets) |
| Chainlit | `frontend/dist/logo_light.svg` from the installed Chainlit distribution; [upstream project](https://github.com/Chainlit/chainlit) |
| Neo4j, Anthropic, SQLite, Ollama, OpenTelemetry | [Simple Icons](https://github.com/simple-icons/simple-icons), monochrome technology marks |
| OpenAI | [OpenAI brand asset in Promptfoo's repository](https://github.com/promptfoo/promptfoo/blob/main/site/static/img/brands/openai-logo.svg) |
| Ragas | [Official Ragas repository](https://github.com/vibrantlabsai/ragas/blob/main/docs/_static/imgs/logo.png) |
| Promptfoo | [Official Promptfoo repository](https://github.com/promptfoo/promptfoo/blob/main/site/static/img/logo-panda.svg) |
| LightRAG | [Official LightRAG web UI asset](https://github.com/HKUDS/LightRAG/blob/main/lightrag_webui/src/assets/logo.svg) |
