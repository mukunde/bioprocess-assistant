# Bioprocess Troubleshooting Assistant

A demonstrator for **troubleshooting Protein A capture chromatography**. Describe a symptom, retrieve documented possible causes and corrective actions, and inspect their handbook citations.

For example: *“My column pressure is unusually high. What should I check?”* The assistant searches a small curated knowledge graph and displays stored facts selected by the model. Possible causes are documentary hypotheses, not a diagnosis.

The project explores two engineering questions: how to constrain an assistant to traceable knowledge, and how to turn public technical manuals into reviewable, source-linked records. It is a development project, **not a scientifically validated or GxP-qualified system**.

[Architecture](#architecture) · [Run locally](#run-locally) · [Validation](#validation-and-results) · [Documentation](#documentation)

## Current status

Updated 25 October 2026. The merged checkpoint before this update is `main`
at `a6026ca`, after [PR #37](https://github.com/mukunde/bioprocess-assistant/pull/37)
(reviewed frozen v04) and [PR #38](https://github.com/mukunde/bioprocess-assistant/pull/38)
(v05 development). This workspace additionally contains the completed, reviewed
X01-X12 frozen v05 trial and its compact export, prepared for versioning but not
yet merged. Its gate is blocked. Reviewed manual knowledge remains separate from
the chat; no experimental retrieval candidate is activated by these results.

| Component | Status and scope |
|---|---|
| Troubleshooting chat | Implemented: six curated Protein A symptoms, English full-text retrieval in Neo4j, Anthropic tool use and application-controlled rendering |
| French and English questions | Supported by the agent's English search-phrase selection; headings and refusals are localized, technical graph facts remain in English |
| Local PDF ingestion | Experimental: Docling Graph with Ollama, structural chunking, source localization and a local review UI; optional publication creates a separate graph |
| Reviewed manual extraction | Completed development example: 33 statements reviewed against pages 100–102, with 14 retaining reservations; not served by the chatbot |
| Conversion and structural chunking | Targeted human reviews completed on pages 77, 88, 104 and 152–153, including deterministic table repairs, note scope and figure limitations; three ambiguous rows remain quarantined on 152–153 |
| Local passage retrieval | Merged experimental BM25 and atomic context assembly, with opt-in v04/v05 development variants; known-case coverage is not generalization. The frozen v03b and v04 gates are blocked; none is the chat default |
| Frozen v05 challenge | Completed local X01-X12 review and single run, prepared for versioning: 7/12 intents have complete evidence in both languages, but only X02/X05/X09 also satisfy explicit scope and diagnostic criteria |
| Reviewed records → chatbot | Adapter pending; ingestion does not automatically expand the serving graph |
| Observability and evaluation extensions | OpenTelemetry, Ragas and Promptfoo are planned; LightRAG is a comparison candidate, KAG remains conditional |

The current chat model is configured as `claude-sonnet-4-6` in [agent.py](agent.py). The separate reviewed extraction used GPT-6.1 Sol through a subscription interface; that subscription does not fund the chatbot's API calls.

## Architecture

![Detailed architecture: separate local Docling Graph and reviewed GPT extraction routes above the Chainlit, agent and Neo4j serving loop. Structural chunking is shown for the local route. Planned OpenTelemetry tracing, Ragas evaluation and Promptfoo adversarial testing have distinct roles.](docs/architecture/architecture-detailed.png)

**Solid arrows** show implemented paths. **Dashed coral arrows** show planned connections. Read ingestion and storage at the top, then the serving loop below:

1. Chainlit sends the question to the agent.
2. The agent calls `query_graph` with an English symptom phrase. Neo4j searches the English symptom index and traverses `Symptom → INDICATES → Cause → RESOLVED_BY → Action` using parameterized Cypher.
3. The model selects retrieved result IDs. Application code validates the selection and renders stored facts and citations. Unsupported selections, missing knowledge and operational errors have separate handling.

Free-form model advice is not displayed. This constrains generation, but does not guarantee relevant retrieval or scientifically correct source material. A Lucene score measures lexical relevance, not diagnostic confidence.

Ingestion has two separate routes: **Docling → Docling Graph + local Ollama → review**, and the completed **Docling → GPT-6.1 Sol → checks and human review** experiment. Local chunking follows document structure and hierarchy, then token budgets; the reviewed three-page experiment used its full input without automatic chunking. Neither route currently feeds the chatbot.

[Full-size SVG](docs/architecture/architecture-detailed.svg) · [Diagram notes and logo sources](docs/architecture/README.md) · [Grounding decision](docs/ADR-001-knowledge-graph-grounding.md)

## Run locally

The reference workstation uses **Windows, Python 3.13 and Docker Desktop**. The application Dockerfile targets Python 3.11. These are documented configurations, not a cross-platform certification. PDF ingestion uses a separate optional environment.

The commands below use PowerShell and run the application on the host, with Neo4j in Docker. Install Git, Python 3.13 and Docker Desktop first; start Docker Desktop before starting the database.

### 1. Install the application

```powershell
git clone https://github.com/mukunde/bioprocess-assistant.git
cd bioprocess-assistant
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

### 2. Configure local services and authentication

Edit the ignored `.env`. Its template still contains Aura placeholders: replace the four database settings with the local values below and choose a password **before the first database start**.

```dotenv
NEO4J_URI=bolt://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=replace_with_a_local_password
NEO4J_DATABASE=neo4j
```

For real chat requests, set `ANTHROPIC_API_KEY`. Generate the Chainlit signing secret:

```powershell
.\.venv\Scripts\chainlit.exe create-secret
```

Copy the generated value into `CHAINLIT_AUTH_SECRET` in `.env`, then set `DEMO_USERNAME` and `DEMO_PASSWORD` for the login screen. Replace all placeholders; keep credentials in the ignored `.env`. Offline regressions need no API key or running Neo4j.

### 3. Start Neo4j and load the seed

```powershell
docker compose -f compose.neo4j.yaml up -d --wait
.\.venv\Scripts\python.exe scripts/load_graph.py
```

The loader creates constraints and the English full-text index, waits for indexes and applies seed updates transactionally while preserving unrelated records. Changing `.env` later does not change an existing database password. Persistent Docker storage and connection troubleshooting are covered in the [local Neo4j guide](docs/LOCAL-NEO4J.md).

### 4. Start the interface

```powershell
.\.venv\Scripts\chainlit.exe run app.py -w
```

Open [localhost:8000](http://localhost:8000) and log in with the credentials you configured. Try *“My capture yield has dropped”* or *“La pression de ma colonne est anormalement élevée.”* The settings slider adjusts the lexical threshold; lowering it can admit weak matches.

Stop the database when finished:

```powershell
docker compose -f compose.neo4j.yaml stop
```

For an application container, configure a database address reachable **from that container**: `127.0.0.1` would refer to the application container itself. The host-based setup above avoids that mismatch. The [Dockerfile](Dockerfile) is available; hosted infrastructure and credentials require their own configuration.

## Validation and results

Install the additional test dependencies into the application environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -r eval/requirements.txt
.\.venv\Scripts\python.exe -m unittest tests -v
```

The [current suite notes](tests/README.md) explain the maintained entry point and preservation of frozen historical fixtures.

These tests mock external model/database calls; some start loopback HTTP servers.
They need neither paid APIs nor an external service. **463/463 tests passed on
the merged `main` checkpoint `a6026ca`.** The local X preparation adds 15 integrity
and synthetic-harness checks, and its compact export adds five portable checks.
The complete current local suite passed **483/483 tests** on 25 October 2026,
including this prepared, uncommitted packet.
The X harness tests do not search, plan or score the actual X questions; the
single real X trial is a separate, preserved result. Counts use existing local
application/ingestion environments, not a fresh-install certification or an
answer-quality evaluation. Earlier counts remain in historical reports.

| Development evidence | What it establishes | Limits |
|---|---|---|
| [Reviewed extraction, pages 100–102](experiments/cytiva/reviewed-r2/README.md) | 33 corrected statements: 19 validated and 14 validated with reservations; decisions and hashes preserved | Documentary review only; no exhaustive recall, scientific approval or publication |
| [Page 77 review](experiments/cytiva/reviewed-page-077/README.md) and [page 88 review](experiments/cytiva/reviewed-page-088/README.md) | Species/header scope, pH, remarks, reconstructed product cells and five notes reviewed with reservations | Original conversion defects remain documented; targeted repairs do not fix Docling generally; table-only retrieval may omit adjacent context |
| [Figure 104 review](experiments/cytiva/reviewed-page-104/README.md) | Image/caption, five paths, alternative role, applicability and K0/K800 text conservation reviewed | Human interpretation is not native extracted graph edges; automatic text-only diagram semantics remain quarantined |
| [Pages 152–153 annotated review](experiments/cytiva/reviewed-pages-152-153-v2/README.md) | Continued table, repaired HiTrap/HiScreen row and reviewed note annotations retained in new chunks | Three ambiguous rows remain physically separated in quarantine; no complete property-cell or production retrieval validation |
| [Cleaning retrieval](docs/experiments/cytiva-retrieval-depth-results.md) | Six-hit candidate supplies all required sources for Q01–Q10 and N01–N08 in both languages, under a 2,048-token context cap | Known development questions; additional context is not proven more precise; no generated answers evaluated |
| [Contaminant context ablation](docs/experiments/cytiva-contaminants-context-results.md) | On C01–C10, section context raises complete evidence from 6/10 to 10/10 in both languages; combined vocabulary/context also reaches 10/10 | Tuned after inspecting failures; no independent generalization or answer-quality result; E118-I and E121-EQ remain pending and excluded |
| [Frozen v03b / V01-V12](experiments/cytiva/reviewed-v03b-evaluation/README.md) | Twelve reviewed references; 24 saved contexts; 6/12 intents have complete evidence in both languages, but only V02/V05/V09 also respect explicit scope | Merged; acceptance gate blocked. Source omissions and unrequested phases remain visible; no generated answers evaluated |
| [v04 development A-D](experiments/cytiva/compositional-navigation-v04-results/README.md) | Composes requests and handles bounded negations; final known-case coverage V12/12, H10/10, C10/10 in both languages; no unrequested or outside-acceptable V context | Merged development result after inspecting failures; no independent validation or default activation. One optional V03 seed still exceeds the six-seed cap |
| [Frozen v04 / W01-W12](experiments/cytiva/reviewed-v04-evaluation/README.md) | Merged review and 24 saved contexts: 8/12 intents evidence-complete in both languages, but only W10/W11 satisfy completeness, explicit scope and diagnostics | Gate blocked: 13/24 explicit scope failures and 2/24 diagnostic failures; no generated answers evaluated |
| [v05 development A-B](experiments/cytiva/polarity-navigation-v05-results/README.md) | Merged known-case coverage W12/12, V12/12, H10/10, C10/10; both attempts retained, including intermediate C02 failure | Tuned after inspecting W failures; not prospective validation or default activation; absent H/C scope annotations remain unavailable |
| [Frozen v05 / X01-X12](experiments/cytiva/reviewed-v05-evaluation/README.md) | Local compact export: 12 reviewed intents and 24 contexts; EN 8/12, FR 7/12 complete; only X02/X05/X09 satisfy all scope/diagnostic criteria in both languages | Gate blocked: 9/24 explicit scope failures and 6/24 diagnostic failures; task ownership, nested negation and routing/lexical disagreement remain unresolved |
| [Evaluation contract](eval/README.md) | 33 development cases covering scope, refusals and grounding | Existing cases and historical results are not independent validation |

The question series have distinct histories: Q/N/C contain 28 reviewed development
intents; H, V, W and X add reviewed same-corpus challenges. Inspected failures
subsequently become development/regression inputs. EN/FR formulations are paired,
source facts overlap, and the author knows the implementation: these are not
independently authored or new-manual evaluations. Do not compare v04's W score
with v05's X score as though they were the same questions.

The [completed X review and frozen outcome](docs/experiments/cytiva-v05-prospective-results.md)
are local additions in this update. All twelve references are validated with
reservations; X03-X12 were approved collectively in one actual message. The
original preparation's pending flags remain historical, not a current review
queue. All contexts, diagnostics, timings and original hashes are retained.

The frozen gate requires complete evidence in both languages for all twelve
intents, no explicitly unrequested source, no failed required diagnostic and no
hard invariant violation. v05 does not pass. Outside-acceptable context is a noise
proxy, not measured precision; answer quality, refusal quality and scientific
suitability have not been established. E118-I and E121-EQ remain excluded. Missing
pressure is bounded to 25 eligible excerpts, not the full manual. The 2,048-token
context cap excludes future prompts and generated output.

**Next priority:** design task-scoped requests with explicit products, column sizes,
phases, parameters and exclusions; compare a structured-input control with free
text mapped to that same contract. Avoid another isolated synonym expansion.
This redesign is proposed, not implemented. Then reserve a new reviewed challenge
before evaluating a new variant. The reviewed-record serving adapter is still
missing; adding it does not promote a blocked retriever.

The three-arm graph/passages/LightRAG comparison remains unexecuted. Current BM25
trials are a lexical baseline, not the multilingual vector arm specified in that
protocol. OpenTelemetry, Ragas and Promptfoo are not integrated yet.

With Neo4j running, `python eval/run_eval.py` evaluates the eligible English lexical subset without model calls. `--agent` additionally calls Anthropic for the assistant and judge and incurs API costs; it is a separate, deliberate evaluation step.

The [conversion/chunking launcher](experiments/cytiva/README.md#local-table-conversion-and-chunking-no-llm) runs without extraction LLMs or paid APIs, using the selected manual and cached weights. General local extraction and manual review have separate [installation and workflow instructions](docs/INGESTION.md).

Manuals and raw experiment outputs stay local and ignored. A fresh clone includes code, curated reports and the selected review package, but not PDFs, model weights or full local journals. Requirements are not a complete dependency lock.

## Next steps

1. Preserve the completed X review/results and design an explicit task-scoped request contract before coding another variant: product, column size, phase, requested parameters, exclusions and uncertainty.
2. Compare deterministic structured input with free text mapped to that same contract, separating retrieval quality from language interpretation. Neither path is implemented. Use X as regression evidence, then freeze a new version before preparing another reviewed challenge.
3. Build the missing reviewed-records-to-chatbot slice with the v0.2 adapter and validated renderer: retain source snapshots, conditions, reservations and quarantine; exercise clarification, correction, revocation and rollback. This does not activate a blocked retriever.
4. Instrument that integration with minimal OpenTelemetry spans and portable accounting; then evaluate actual answers, citations and abstentions with deterministic checks, calibrated local Ragas and Promptfoo plus benign controls.
5. Compare graph/passages/LightRAG on a common corpus and budget once adapters and evaluation inputs exist. Keep KAG and fine-tuning conditional on measured unmet needs.

The X result is a reason to revisit request representation, not to expand synonyms
indefinitely. No new variant or architecture comparison has been executed here.
No additional whole-manual page review is a prerequisite unless a measured failure
or a newly required format exposes a concrete conversion/chunking gap.

The [active roadmap](docs/ROADMAP.md) defines acceptance criteria. The earlier vector experiment is recorded in [ADR-002](docs/ADR-002-multilingual-retrieval.md); it does not settle the planned comparison on a larger reviewed corpus.

## Documentation

Use the [documentation index](docs/README.md) for the ontology, claim contract, experiment protocols, operational guides and delivery history. The implementation separates [agent/tool use](agent.py), [validated rendering](grounding.py), [graph retrieval](tools.py), [ingestion](ingestion/) and [evaluation](eval/).

Reference hosted demo: [bioprocess-assistant.onrender.com](https://bioprocess-assistant.onrender.com). Its authenticated end-to-end behaviour has not been verified; local setup is the documented development path. For a walkthrough, contact [Gaël Mukunde](mailto:gaelmukunde@gmail.com) or connect on [LinkedIn](https://www.linkedin.com/in/gaelmukunde/).

## License

Project code: [MIT](LICENSE). Source manuals and technology logos retain their respective rights; the manuals are not redistributed in this repository.
