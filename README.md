# Bioprocess Troubleshooting Assistant

A demonstrator for **troubleshooting Protein A capture chromatography**. Describe a symptom, retrieve documented possible causes and corrective actions, and inspect their handbook citations.

For example: *“My column pressure is unusually high. What should I check?”* The assistant searches a small curated knowledge graph and displays stored facts selected by the model. Possible causes are documentary hypotheses, not a diagnosis.

The project explores two engineering questions: how to constrain an assistant to traceable knowledge, and how to turn public technical manuals into reviewable, source-linked records. It is a development project, **not a scientifically validated or GxP-qualified system**.

[Architecture](#architecture) · [Run locally](#run-locally) · [Validation](#validation-and-results) · [Documentation](#documentation)

## Current status

Updated 26 October 2026. The merged code/evidence checkpoint is `main` at
`1b852f4`, after [PR #39](https://github.com/mukunde/bioprocess-assistant/pull/39)
(reviewed v05 X trial), [PR #40](https://github.com/mukunde/bioprocess-assistant/pull/40)
(request contract/specification), [PR #41](https://github.com/mukunde/bioprocess-assistant/pull/41)
(corrected structured control) and [PR #42](https://github.com/mukunde/bioprocess-assistant/pull/42)
(reviewed S01-S12 trial). The complete maintained suite passed **556/556 tests**
on that checkpoint, with no skipped tests or external connection attempts.

The free-text comparison protocol, interface and machine-schema choices are
human-approved **local design artifacts, not yet merged or implemented**. Refined
examples still await grouped review. Reviewed manual knowledge remains separate
from the chat, and no experimental retriever is activated by these results.

| Component | Status and scope |
|---|---|
| Troubleshooting chat | Implemented: six curated Protein A symptoms, English full-text Neo4j retrieval, Anthropic tool use and application-controlled rendering |
| French and English questions | Agent selects English search phrases; headings/refusals are localized and technical graph facts remain in English |
| Local PDF ingestion | Experimental Docling Graph/Ollama route with structural chunking, localization and review UI; separate optional evidence publication |
| Reviewed manual extraction | Merged development example: 33 statements reviewed on pages 100–102, with 14 reservations; not served by the chatbot |
| Conversion and chunking | Selected page 77/88/104/152–153 reviews and repairs are merged; three ambiguous rows remain quarantined on 152–153 |
| Passage retrieval | Merged BM25/atomic assembly experiments; frozen v03b, v04 and v05 gates remain blocked and none is the chat default |
| Structured request control | Merged offline control. S01-S12: all 24 EN/FR submissions and all 12 paired scenarios pass reviewed context/diagnostic criteria; known-corpus diagnostic evidence only |
| Free-text interface | Local approved CP/FI/MC design and three machine schemas; 16 refined examples plus three invalid inputs await GR01–GR04 review. No interpreter/bridge implementation or S/F trial |
| Reviewed records → chatbot | Adapter pending; ingestion does not automatically enrich the serving graph |
| Observability and evaluation extensions | OpenTelemetry, Ragas and Promptfoo remain pending; LightRAG is a comparison candidate and KAG remains conditional |

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
.\.venv\Scripts\python.exe -m pip install -r eval/requirements.txt -r requirements-structured.txt
.\.venv\Scripts\python.exe -m unittest tests -v
```

The [current suite notes](tests/README.md) explain the maintained entry point and preservation of frozen historical fixtures.

These tests mock external model/database calls; some use loopback HTTP servers
and Windows asynchronous sockets. They need no paid API or external service.
The **556/556** result above is from the existing local verification environment,
not a fresh-install certification or an answer-quality measurement. Structured
runtime dependencies are listed separately in `requirements-structured.txt`;
private tokenizer assets may also be required by optional runtime workflows.

The merged structured export can be verified with only the standard library,
without PDFs, tokenizer assets, credentials, models or private run files:

```powershell
python -S -m experiments.cytiva.verify_structured_reviewed_package
python -S -m unittest tests.test_structured_reviewed_package -v
```

These commands inspect saved evidence; they never rerun S01-S12. The new
free-text schemas/examples have static shape, origin geometry, reference,
accounting and corruption checks only. Those checks are not executed IF
implementation tests and do not establish language understanding.

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
| [Frozen v05 / X01-X12](experiments/cytiva/reviewed-v05-evaluation/README.md) | Merged compact export: 12 reviewed intents and 24 contexts; EN 8/12, FR 7/12 complete; only X02/X05/X09 satisfy all scope/diagnostic criteria in both languages | Gate blocked: 9/24 explicit scope failures and 6/24 diagnostic failures; task ownership, nested negation and routing/lexical disagreement remain unresolved |
| [Structured S01-S12 trial](experiments/cytiva/reviewed-structured-control/README.md) | Merged: 12 human-reviewed scenarios, all 24 saved submissions pass context/diagnostics; no EN/FR semantic divergence; 348–1,504 context tokens | Structured intent control on known sources/code, not free-text or generated-answer validation; E118-I/E121-EQ remain excluded |
| [Free-text design and grouped examples](docs/technical/FREE-TEXT-MACHINE-DESIGN-V01.md) | Local CP01–CP06, FI01–FI06/IF01–IF14 and MC01–MC06 decisions recorded; exact refined fixtures remain pending | Declarative design only; no parser, bridge, S/F experiment, performance result or new source approval |
| [Evaluation contract](eval/README.md) | 33 development cases covering scope, refusals and grounding | Existing cases and historical results are not independent validation |

The question series have distinct histories: Q/N/C contain 28 reviewed development
intents; H, V, W and X add reviewed same-corpus challenges. Inspected failures
subsequently become development/regression inputs. EN/FR formulations are paired,
source facts overlap, and the author knows the implementation: these are not
independently authored or new-manual evaluations. Do not compare v04's W score
with v05's X score as though they were the same questions.

The [X review and blocked outcome](docs/experiments/cytiva-v05-prospective-results.md)
are merged historical evidence. Their failures motivated the now-implemented
structured request contract/control. The separate S trial passes its own
reviewed structured references; it does not retroactively repair X or prove that
free text is understood. S and X are different diagnostic experiments, not a
controlled before/after answer-quality comparison.

E118-I and E121-EQ remain excluded. Pressure absence is bounded to 25 eligible
excerpts, not the full manual. S's 2,048-token budget counts serialized context
including bindings, not a future answer prompt or output. The source-reviewed
claims have not been connected to the chatbot's serving path.

**Next priority:** complete [GR01–GR04 fixture review](docs/experiments/free-text-interface-group-review-v01.md),
then implement the bounded deterministic free-text interpreter/bridge under the
approved design. Use known P/G cases for development, freeze that candidate,
then author and review the new 12-intent bilingual prospective set before one
preserved S/F run. Do not tune after its results or treat schema validation as
proof of faithful interpretation. The local [design delivery scope](docs/experiments/free-text-design-package-v01.md)
separates approved choices from pending exact example/origin decisions.

The three-arm graph/passages/LightRAG comparison remains unexecuted. Current BM25
trials are a lexical baseline, not the multilingual vector arm specified in that
protocol. OpenTelemetry, Ragas and Promptfoo are not integrated yet.

With Neo4j running, `python eval/run_eval.py` evaluates the eligible English lexical subset without model calls. `--agent` additionally calls Anthropic for the assistant and judge and incurs API costs; it is a separate, deliberate evaluation step.

The [conversion/chunking launcher](experiments/cytiva/README.md#local-table-conversion-and-chunking-no-llm) runs without extraction LLMs or paid APIs, using the selected manual and cached weights. General local extraction and manual review have separate [installation and workflow instructions](docs/INGESTION.md).

Manuals and raw experiment outputs stay local and ignored. A fresh clone includes code, curated reports and the selected review package, but not PDFs, model weights or full local journals. Requirements are not a complete dependency lock.

## Next steps

1. Review the four refined fixture groups, including exact origins, task ownership, preblocking and external test conditions. The protocol/interface/schema choices are approved; the examples are still pending.
2. Implement the smallest deterministic EN/FR interpreter and bridge without changing the structured core. Pass IF01–IF14, freeze the candidate, then prepare/review the new prospective S/F set. No additional design cycle is needed unless a concrete unresolved interface gap appears.
3. Build the reviewed-records-to-chatbot slice with the v0.2 adapter and validated renderer, retaining conditions, reservations and quarantine. This does not activate a blocked retriever.
4. Instrument that path with OpenTelemetry and portable accounting; evaluate actual answers/citations/abstentions with deterministic checks, calibrated local Ragas and Promptfoo plus benign controls.
5. Compare graph/passages/LightRAG on a common corpus and budget after adapters and references exist. Keep KAG and fine-tuning conditional on measured needs.

No free-text candidate or architecture comparison has executed. No additional
whole-manual page review is required unless a measured failure or newly required
format exposes a concrete conversion/chunking gap.

The [active roadmap](docs/ROADMAP.md) defines acceptance criteria. The earlier vector experiment is recorded in [ADR-002](docs/ADR-002-multilingual-retrieval.md); it does not settle the planned comparison on a larger reviewed corpus.

## Documentation

Use the [documentation index](docs/README.md) for the ontology, claim contract, experiment protocols, operational guides and delivery history. The implementation separates [agent/tool use](agent.py), [validated rendering](grounding.py), [graph retrieval](tools.py), [ingestion](ingestion/) and [evaluation](eval/).

Reference hosted demo: [bioprocess-assistant.onrender.com](https://bioprocess-assistant.onrender.com). Its authenticated end-to-end behaviour has not been verified; local setup is the documented development path. For a walkthrough, contact [Gaël Mukunde](mailto:gaelmukunde@gmail.com) or connect on [LinkedIn](https://www.linkedin.com/in/gaelmukunde/).

## License

Project code: [MIT](LICENSE). Source manuals and technology logos retain their respective rights; the manuals are not redistributed in this repository.
