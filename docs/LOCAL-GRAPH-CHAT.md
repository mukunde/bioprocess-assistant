# Run the local graph chat

Install Git, Python 3.13, and Docker Desktop on Windows. Start Docker Desktop,
then run the following commands in PowerShell. The app runs on the host
and Neo4j runs in Docker. The application Dockerfile uses Python 3.11.

## 1. Install the application

```powershell
git clone https://github.com/mukunde/bioprocess-assistant.git
cd bioprocess-assistant
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

## 2. Configure local services and authentication

Edit the ignored `.env`. Its template still contains Aura placeholders: replace the four database settings with the local values below and choose a password **before the first database start**.

```dotenv
NEO4J_URI=bolt://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=replace_with_a_local_password
NEO4J_DATABASE=neo4j
```

For default graph-chat requests, set `ANTHROPIC_API_KEY`. Generate the Chainlit signing secret:

```powershell
.\.venv\Scripts\chainlit.exe create-secret
```

Copy the generated value into `CHAINLIT_AUTH_SECRET` in `.env`, then set `DEMO_USERNAME` and `DEMO_PASSWORD` for the login screen. Replace all placeholders and keep credentials in the ignored `.env`. Offline regressions need no API key or running Neo4j.

## 3. Start Neo4j and load the seed

```powershell
docker compose -f compose.neo4j.yaml up -d --wait
.\.venv\Scripts\python.exe scripts/load_graph.py
```

The loader creates constraints and the English full-text index, waits for indexes and applies seed updates transactionally while preserving unrelated records. To change an existing database password, follow the Neo4j procedure. Persistent Docker storage and connection troubleshooting are covered in the [local Neo4j guide](LOCAL-NEO4J.md).

## 4. Start the interface

```powershell
.\.venv\Scripts\chainlit.exe run app.py -w
```

Open [localhost:8000](http://localhost:8000) and log in with the credentials you configured. Try *“My capture yield has dropped”* or *“La pression de ma colonne est anormalement élevée.”* The settings slider adjusts the lexical threshold. Lower values can admit weak matches.

Stop the database when finished:

```powershell
docker compose -f compose.neo4j.yaml stop
```

For an application container, configure a database address reachable **from that container**: `127.0.0.1` would refer to the application container itself. The host-based setup above avoids that mismatch. See the [Dockerfile](../Dockerfile) for the application image. Configure credentials and network access for your deployment.

## Use Ministral on the host

Start Ollama with the installed `bioprocess-local:latest` model available.
This option uses Ministral 3 3B Instruct 2512 (Q4_K_M). Keep Neo4j on a
direct loopback Bolt connection as configured above. Ollama must listen on
`127.0.0.1:11434`.

```powershell
$env:BIOPROCESS_MODE = "graph"
$env:BIOPROCESS_GRAPH_BACKEND = "ministral"
.\.venv\Scripts\chainlit.exe run app.py --host 127.0.0.1
```

Check for **Mode local · Ministral 3 3B Instruct** in the welcome message.
In the composer settings, choose the language for headings and abstentions.
The technical descriptions and citations come from Neo4j. The model sees
compact result labels when selecting IDs. The renderer validates that
selection and uses the complete graph results for citations.

This mode requires no Anthropic key. If Ollama or Neo4j is unavailable,
Chainlit shows a service error. To return to the default Claude backend,
remove `BIOPROCESS_GRAPH_BACKEND` from the shell and restart Chainlit.

### Local acceptance results

On 16 November 2026, an authenticated Chainlit session ran all four cases
with Ministral and a disposable Neo4j instance loaded from the benchmark
seed. The lexical threshold was 2.5. The session used the explicit
French or English setting and ran without an Anthropic key.

| Case | Result | Citation entries |
| --- | --- | ---: |
| G02 | Valid selection for high column pressure. French headings, bed efficiency, and resin-specific cleaning. | 5 |
| G03 | Abstention on upstream cell viability. No Neo4j lookup. | 0 |
| G04 | Abstention on endotoxins after a lookup below the threshold. | 0 |
| M01 | Valid selection for high column pressure and capture yield drop after two searches. | 10 |

This replay checks selection, citations, and abstention on four known
questions. G02–G04 are defined in the
[graph chat measurement protocol](GRAPH-CHAT-MEASUREMENT.md#question-set).
M01 combines a measured increase in column pressure with declining capture
yield and antibody in the flow-through.

Run the targeted offline regressions from the repo root with the chat and
evaluation test dependencies installed.

```powershell
python -m unittest tests.test_graph_chat_ministral tests.test_reliability tests.test_graph_chat_tracing tests.test_graph_chat_benchmark
```

## Optional local traces

These instructions cover the default Claude backend. Install the optional OpenTelemetry dependencies in the chat environment. Set
the flag in the shell before launching Chainlit. Use the shell, not `.env`, to control tracing.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-observability.txt
$env:BIOPROCESS_GRAPH_CHAT_TRACE = "1"
.\.venv\Scripts\chainlit.exe run app.py
```

After a graph chat request, look in `tmp/graph-chat-traces/` for the process's
JSON Lines file. Group rows by trace ID to see the request, each Anthropic
SDK call, and each Neo4j search. Durations are in milliseconds. A model span
includes any SDK-internal retries in its elapsed time; it does not count or
price those attempts separately.

Traces contain only timing, outcomes, the configured model, provider-reported
token counts, and an estimated USD cost when usage and pricing are known.
The estimate uses the standard [Sonnet 4.6 API rates][sonnet-price] checked
on 6 November 2026. It applies the US-only surcharge when reported, assumes
standard routing when the SDK reports no geography, and omits cost for an
unrecognized geography. If cache writes are reported without the duration
breakdown, the cost is omitted. The estimate is neither a bill nor a spending
cap. Prompts, answers, citations, queries, credentials, and exception text are
excluded. Initialization and export are local and asynchronous. Requests
that start before the exporter is ready proceed without a trace. If the SDK or file is unavailable,
the chat still works; a full export queue can drop spans. Delete the local
files when no longer needed and remove the flag to turn tracing off.

Run the offline checks with `python -m unittest tests.test_graph_chat_tracing -v`.
The integration checks use simulated clients and require the optional SDK.

[sonnet-price]: https://platform.claude.com/docs/en/models/sonnet-4-6/overview

Open the local trace viewer in a separate shell from the repository root.

```powershell
python scripts/view_graph_chat_traces.py
```

Open [the trace viewer](http://127.0.0.1:8765/), select a request, and refresh
after the exporter has written new spans. The viewer shows the timeline,
outcome, token counts, and estimated cost for each span. It reads existing
local traces and listens on loopback.
