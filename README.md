# Bioprocess Troubleshooting Assistant

A demonstrator for **troubleshooting Protein A capture chromatography**. Describe a symptom, retrieve documented possible causes and corrective actions, and inspect their handbook citations.

For example: *“My column pressure is unusually high. What should I check?”* The assistant searches a small curated knowledge graph and displays stored facts selected by the model. Possible causes are documentary hypotheses, not a diagnosis.

The project explores two engineering questions: how to constrain an assistant to traceable knowledge, and how to turn public technical manuals into reviewable, source-linked records. It is a development project, **not a scientifically validated or GxP-qualified system**.

[Architecture](#architecture) · [Run locally](#run-locally) · [Validation](#validation-and-results) · [Documentation](#documentation)

## Current status

Updated 24 October 2026. The application and documentary experiments are separate:
reviewed manual knowledge is not yet available in the chat.

| Component | Status and scope |
|---|---|
| Troubleshooting chat | Implemented: six curated Protein A symptoms, English full-text retrieval in Neo4j, Anthropic tool use and application-controlled rendering |
| French and English questions | Supported by the agent's English search-phrase selection; headings and refusals are localized, technical graph facts remain in English |
| Local PDF ingestion | Experimental: Docling Graph with Ollama, structural chunking, source localization and a local review UI; optional publication creates a separate graph |
| Reviewed manual extraction | Completed development example: 33 statements reviewed against pages 100–102, with 14 retaining reservations; not served by the chatbot |
| Conversion and structural chunking | Targeted human reviews completed on pages 77, 88, 104 and 152–153, including deterministic table repairs, note scope and figure limitations; three ambiguous rows remain quarantined on 152–153 |
| Local passage retrieval | Experimental BM25 and bounded context assembly evaluated on 28 reviewed bilingual intents; six-hit and section-context candidates remain separate from chat |
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

These tests mock external model/database calls; some start loopback HTTP servers. They need neither paid APIs nor an external service. **351 main-suite tests and 13 supplementary Cytiva checks passed on integrated `main` on 24 October 2026.** This dated result used the existing application and ingestion environments; it does not certify a fresh dependency installation. This is regression coverage, not a quality score for live answers.

| Development evidence | What it establishes | Limits |
|---|---|---|
| [Reviewed extraction, pages 100–102](experiments/cytiva/reviewed-r2/README.md) | 33 corrected statements: 19 validated and 14 validated with reservations; decisions and hashes preserved | Documentary review only; no exhaustive recall, scientific approval or publication |
| [Page 77 review](experiments/cytiva/reviewed-page-077/README.md) and [page 88 review](experiments/cytiva/reviewed-page-088/README.md) | Species/header scope, pH, remarks, reconstructed product cells and five notes reviewed with reservations | Original conversion defects remain documented; targeted repairs do not fix Docling generally; table-only retrieval may omit adjacent context |
| [Figure 104 review](experiments/cytiva/reviewed-page-104/README.md) | Image/caption, five paths, alternative role, applicability and K0/K800 text conservation reviewed | Human interpretation is not native extracted graph edges; automatic text-only diagram semantics remain quarantined |
| [Pages 152–153 annotated review](experiments/cytiva/reviewed-pages-152-153-v2/README.md) | Continued table, repaired HiTrap/HiScreen row and reviewed note annotations retained in new chunks | Three ambiguous rows remain physically separated in quarantine; no complete property-cell or production retrieval validation |
| [Cleaning retrieval](docs/experiments/cytiva-retrieval-depth-results.md) | Six-hit candidate supplies all required sources for Q01–Q10 and N01–N08 in both languages, under a 2,048-token context cap | Known development questions; additional context is not proven more precise; no generated answers evaluated |
| [Contaminant context ablation](docs/experiments/cytiva-contaminants-context-results.md) | On C01–C10, section context raises complete evidence from 6/10 to 10/10 in both languages; combined vocabulary/context also reaches 10/10 | Tuned after inspecting failures; no independent generalization or answer-quality result; E118-I and E121-EQ remain pending and excluded |
| [Evaluation contract](eval/README.md) | 33 development cases covering scope, refusals and grounding | Existing cases and historical results are not independent validation |

The 28 bilingual intents are three reviewed development series (Q: 10, N: 8,
C: 10), not one locked test set. Retrieval scores measure presence of indispensable
source passages after assembly, not correctness of a generated answer, diagnosis
or measured retrieval precision. The C-series section-only and combined variants
reach at most 2,027 serialized context tokens; the 2,048-token cap excludes any
future answer prompt and output. Section-only is the simpler candidate to test
next; neither variant changes the application default.

The three-arm graph/passages/LightRAG comparison remains unexecuted. Current BM25
trials are a lexical baseline, not the multilingual vector arm specified in that
protocol. OpenTelemetry, Ragas and Promptfoo are not integrated yet.

With Neo4j running, `python eval/run_eval.py` evaluates the eligible English lexical subset without model calls. `--agent` additionally calls Anthropic for the assistant and judge and incurs API costs; it is a separate, deliberate evaluation step.

The [conversion/chunking launcher](experiments/cytiva/README.md#local-table-conversion-and-chunking-no-llm) runs without extraction LLMs or paid APIs, using the selected manual and cached weights. General local extraction and manual review have separate [installation and workflow instructions](docs/INGESTION.md).

Manuals and raw experiment outputs stay local and ignored. A fresh clone includes code, curated reports and the selected review package, but not PDFs, model weights or full local journals. Requirements are not a complete dependency lock.

## Next steps

1. Freeze a simple retrieval/context candidate and evaluate separately prepared questions before further tuning. Measure missing and unnecessary sources, conditions, exclusions and resource use; keep earlier trials unchanged.
2. Connect a small reviewed corpus to the assistant through the v0.2-to-serving adapter and common validated renderer. Preserve reservations, quarantine, source snapshots and missing-context behaviour; test activation, correction and revocation.
3. Add OpenTelemetry instrumentation during that integration, then evaluate actual answers and abstentions using deterministic checks, calibrated local Ragas and Promptfoo adversarial cases.
4. Complete the common-corpus graph/passages/LightRAG comparison once adapters and a frozen evaluation set exist. Assess lightweight local serving within the PC and budget constraints; consider KAG or fine-tuning only if measured failures justify them.

The [active roadmap](docs/ROADMAP.md) defines acceptance criteria. The earlier vector experiment is recorded in [ADR-002](docs/ADR-002-multilingual-retrieval.md); it does not settle the planned comparison on a larger reviewed corpus.

## Documentation

Use the [documentation index](docs/README.md) for the ontology, claim contract, experiment protocols, operational guides and delivery history. The implementation separates [agent/tool use](agent.py), [validated rendering](grounding.py), [graph retrieval](tools.py), [ingestion](ingestion/) and [evaluation](eval/).

Reference hosted demo: [bioprocess-assistant.onrender.com](https://bioprocess-assistant.onrender.com). Its authenticated end-to-end behaviour has not been verified; local setup is the documented development path. For a walkthrough, contact [Gaël Mukunde](mailto:gaelmukunde@gmail.com) or connect on [LinkedIn](https://www.linkedin.com/in/gaelmukunde/).

## License

Project code: [MIT](LICENSE). Source manuals and technology logos retain their respective rights; the manuals are not redistributed in this repository.
