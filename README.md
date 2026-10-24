# Bioprocess Troubleshooting Assistant

A demonstrator for **troubleshooting Protein A capture chromatography**. Describe a symptom, retrieve documented possible causes and corrective actions, and inspect their handbook citations.

For example: *“My column pressure is unusually high. What should I check?”* The assistant searches a small curated knowledge graph and displays stored facts selected by the model. Possible causes are documentary hypotheses, not a diagnosis.

The project explores two engineering questions: how to constrain an assistant to traceable knowledge, and how to turn public technical manuals into reviewable, source-linked records. It is a development project, **not a scientifically validated or GxP-qualified system**.

[Architecture](#architecture) · [Run locally](#run-locally) · [Validation](#validation-and-results) · [Documentation](#documentation)

## Current status

Updated 24 October 2026. The merged baseline is `main` at `081a30d`, after
[PR #34](https://github.com/mukunde/bioprocess-assistant/pull/34) (reviewed frozen
v03b) and [PR #35](https://github.com/mukunde/bioprocess-assistant/pull/35) (v04
and the maintained test suite). Reviewed manual knowledge is still separate from
the chat. A new W01-W12 evaluation packet exists only in the local workspace and
is awaiting human review; it is not included in that merged checkpoint.

| Component | Status and scope |
|---|---|
| Troubleshooting chat | Implemented: six curated Protein A symptoms, English full-text retrieval in Neo4j, Anthropic tool use and application-controlled rendering |
| French and English questions | Supported by the agent's English search-phrase selection; headings and refusals are localized, technical graph facts remain in English |
| Local PDF ingestion | Experimental: Docling Graph with Ollama, structural chunking, source localization and a local review UI; optional publication creates a separate graph |
| Reviewed manual extraction | Completed development example: 33 statements reviewed against pages 100–102, with 14 retaining reservations; not served by the chatbot |
| Conversion and structural chunking | Targeted human reviews completed on pages 77, 88, 104 and 152–153, including deterministic table repairs, note scope and figure limitations; three ambiguous rows remain quarantined on 152–153 |
| Local passage retrieval | Merged experimental BM25 and bounded context assembly: frozen v03b fails its acceptance gate; opt-in v04 recovers the required sources on known V/H/C development cases. Neither is the chat default |
| Prospective v04 challenge | Local only: v04 is frozen for W01-W12, twelve new bilingual question/reference pairs awaiting human review; no search or trial has been run |
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
They need neither paid APIs nor an external service. **433/433 tests passed on the
merged `main` checkpoint `081a30d`.** With the uncommitted W preparation and its
13 integrity/synthetic harness checks, the local suite passes **446/446**. Those
13 checks do not search, plan or score the real W questions. Both counts are dated
24 October 2026 and use existing application/ingestion environments; they do not
certify a fresh installation or the quality of generated answers. Earlier test
counts remain in their historical reports.

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
| [Evaluation contract](eval/README.md) | 33 development cases covering scope, refusals and grounding | Existing cases and historical results are not independent validation |

The question series have distinct histories: Q/N/C contain 28 reviewed development
intents; H01-H10 and V01-V12 add reviewed same-corpus challenges whose failures
subsequently informed tuning. EN/FR formulations are paired observations, and
source facts overlap. The earlier section-only preference was a historical
ablation choice; the current local prospective candidate is frozen v04.

**Local only, pending review:** `experiments/cytiva/v04-evaluation-v01/` contains
W01-W12, twelve new EN/FR question pairs with exact excerpts, required/acceptable
sources, expected answers and reservations. Its protocol fixes the six-seed and
2,048-token policy before measurement. It covers negations, combined requests,
unavailable parameters and a synthetic contradictory request. All twelve
references await human review; there are no W retrieval results. This packet,
`experiments/cytiva/v04_evaluation.py` and `tests/test_v04_evaluation.py` are not
part of the merged checkpoint or a fresh clone of it. Review and authorize the
single frozen run before searching any W question.

The W gate requires complete evidence in both languages for all twelve intents,
zero explicitly unrequested sources, zero failed reference diagnostic criteria
and no hard invariant violation. A pass only permits considering a limited
end-to-end pilot. Outside-acceptable context remains a separate noise proxy;
no answer quality, refusal quality, diagnosis or measured precision is established.
All W sources remain the known pages 118-121; the questions were prepared with
knowledge of the implementation and prior failures. E118-I and E121-EQ remain
excluded, even if W10/W11 are validated. The context cap excludes future prompt
and generated output tokens.

The three-arm graph/passages/LightRAG comparison remains unexecuted. Current BM25
trials are a lexical baseline, not the multilingual vector arm specified in that
protocol. OpenTelemetry, Ragas and Promptfoo are not integrated yet.

With Neo4j running, `python eval/run_eval.py` evaluates the eligible English lexical subset without model calls. `--agent` additionally calls Anthropic for the assistant and judge and incurs API costs; it is a separate, deliberate evaluation step.

The [conversion/chunking launcher](experiments/cytiva/README.md#local-table-conversion-and-chunking-no-llm) runs without extraction LLMs or paid APIs, using the selected manual and cached weights. General local extraction and manual review have separate [installation and workflow instructions](docs/INGESTION.md).

Manuals and raw experiment outputs stay local and ignored. A fresh clone includes code, curated reports and the selected review package, but not PDFs, model weights or full local journals. Requirements are not a complete dependency lock.

## Next steps

1. Review local W01-W12, including source scope and diagnostic criteria, then authorize the one frozen v04 run. Preserve all results and apply the declared gate without post-result tuning. Any subsequent fix is a separate development variant requiring another prospective set.
2. Build the missing reviewed-records-to-chatbot slice with the v0.2 adapter and validated renderer: retain source snapshots, conditions, reservations and quarantine; exercise clarification, activation, correction, revocation and rollback. A retrieval experiment does not complete this serving adapter.
3. Instrument that integration with minimal OpenTelemetry spans and portable usage/budget accounting; then evaluate actual answers, citations and abstentions with deterministic checks, calibrated local Ragas and Promptfoo plus benign controls.
4. Compare graph/passages/LightRAG on a common corpus and budget once adapters and evaluation inputs exist. Benchmark lightweight local serving; keep KAG and fine-tuning conditional on measured unmet needs.

W is the next retrieval decision point, not approval to repeat tuning indefinitely.
No additional whole-manual page review is a prerequisite unless a measured failure
or a newly required format exposes a concrete conversion/chunking gap.

The [active roadmap](docs/ROADMAP.md) defines acceptance criteria. The earlier vector experiment is recorded in [ADR-002](docs/ADR-002-multilingual-retrieval.md); it does not settle the planned comparison on a larger reviewed corpus.

## Documentation

Use the [documentation index](docs/README.md) for the ontology, claim contract, experiment protocols, operational guides and delivery history. The implementation separates [agent/tool use](agent.py), [validated rendering](grounding.py), [graph retrieval](tools.py), [ingestion](ingestion/) and [evaluation](eval/).

Reference hosted demo: [bioprocess-assistant.onrender.com](https://bioprocess-assistant.onrender.com). Its authenticated end-to-end behaviour has not been verified; local setup is the documented development path. For a walkthrough, contact [Gaël Mukunde](mailto:gaelmukunde@gmail.com) or connect on [LinkedIn](https://www.linkedin.com/in/gaelmukunde/).

## License

Project code: [MIT](LICENSE). Source manuals and technology logos retain their respective rights; the manuals are not redistributed in this repository.
