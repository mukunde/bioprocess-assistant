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

Complete steps 1–3 above, including the local Neo4j seed and Chainlit login
settings. Install Ollama for Windows and put `ollama` on PATH. The launcher
expects the text model `bioprocess-local:latest` (Ministral 3 3B Instruct 2512,
Q4_K_M) in Ollama's local model store. Check with `ollama list`. To install
the model, download the [official Q4_K_M GGUF][ministral-gguf]. Open PowerShell
in its folder outside the repository. Verify the hash, then import it while
your regular Ollama service is running.

```powershell
$expected = '9ed150d4367e68df0ac8e1540f6ddc65b42d0ee26378329d1ecbca60f93fc5f8'
$weights = '.\Ministral-3-3B-Instruct-2512-Q4_K_M.gguf'
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $weights).Hash -ne $expected) {
    throw 'Ministral GGUF checksum mismatch.'
}
@(
    'FROM ./Ministral-3-3B-Instruct-2512-Q4_K_M.gguf'
    'PARAMETER num_ctx 8192'
    'PARAMETER temperature 0'
) | Set-Content -Encoding ascii Modelfile.ministral
ollama create bioprocess-local -f Modelfile.ministral
```

[ministral-gguf]: https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512-GGUF/blob/main/Ministral-3-3B-Instruct-2512-Q4_K_M.gguf

Keep weights and the generated Modelfile outside version control. The launcher
uses the installed alias and keeps model calls local. It does not fetch weights.

Run the launcher from the repo root in PowerShell:

```powershell
.\Start-LocalGraphChat.ps1
.\Start-LocalGraphChat.ps1 -Profile Hybrid
.\Start-LocalGraphChat.ps1 -Profile IrisXe
```

| Profile | Behavior |
| --- | --- |
| CPU (default) | Starts Ollama with GPU acceleration disabled and confirms CPU-only model residency. |
| Hybrid | Verifies 13 layers on Intel Iris Xe via Vulkan and runs the rest on CPU. Uses a 4,096-token context. Use CPU if the device or RAM check fails. |
| IrisXe | Enables Vulkan and verifies full offload to an Intel Iris Xe device. Use CPU if the device or RAM check fails. |

Each command starts one temporary Ollama server on `127.0.0.1:11435` and
Chainlit on `127.0.0.1:8000`. The regular Ollama service can stay on port
11434. Use `-OllamaPort` or `-Port` to resolve a port conflict. The launcher
verifies access to the seeded local graph, preloads Ministral, and requires
1,024 MiB available physical RAM after the model loads and again once Chainlit
is ready. It prints both readings. Add `-CheckOnly` to any profile command to check
startup and exit. For a live session, press Ctrl+C to stop Chainlit and its
temporary Ollama process. The database remains running for reuse.

Open the printed address and sign in. Look for
**Mode local · Ministral 3 3B Instruct**. Choose the language for headings
and abstentions in the composer settings. Ministral selects IDs from compact
search results. The renderer validates the selection and displays the
complete graph facts and citations. The local launcher needs no Anthropic key.

For an existing Ollama server on port 11434, the manual launch remains available:

```powershell
$env:BIOPROCESS_MODE = "graph"
$env:BIOPROCESS_GRAPH_BACKEND = "ministral"
.\.venv\Scripts\chainlit.exe run app.py --host 127.0.0.1
```

### Windows launcher verification

On 24 November 2026, a fresh checkout of GitHub main at `1d01d53` with
the launcher changes used a new Python 3.13 virtual environment, Chainlit
2.12.0, and a newly seeded Neo4j database. The reference PC used its existing
Ollama installation and Ministral weights.

| Startup check | Result |
| --- | --- |
| Default CPU | Chainlit answered on loopback. Available RAM was 1,572 MiB with all three services ready. |
| Iris Xe | Ollama confirmed full GPU offload. The launcher stopped before opening Chainlit because only 50 MiB of RAM remained. It directed the operator to the CPU profile. |

Both checks stopped their temporary listeners on exit. The regular Ollama
process remained available.

A follow-up imported the verified GGUF into an empty Ollama store and checked
the resulting weights, template, and parameters against the reference model.
With that store and the PowerShell launcher, an authenticated CPU session
returned both M01 symptom paths with ten exact citation entries in 21.58 s.
ML06 abstained with no citations in 9.83 s. Both requests used the dedicated
Ollama process. A Windows Ctrl+C event stopped the launcher and released ports
8000 and 11435. The launcher restarted on the same ports, and a second Ctrl+C
released them again. The regular Ollama process remained available throughout.

### Hybrid profile measurements

On 26 November 2026, one Windows PC ran the same Ministral Q4_K_M weights
with Ollama 0.40.17 through Chainlit and disposable Neo4j. M01 combines a
measured pressure increase and a capture yield drop. Across three warm
passes per profile at 4,096 tokens, median response time was 15.80 s on CPU
and 12.31 s in hybrid mode. Minimum available RAM during responses was
2,831 MiB on CPU and 1,289 MiB in hybrid mode. All six selections passed
JSON validation and displayed the same ten citations.

A separate hybrid check ran M01 and a longer combined question once at
each context size. Both sizes returned the same validated selections and
citations for each question. The largest input was 933 tokens, and Ollama
reported no truncation.

| Hybrid context | KV cache | Minimum available RAM during requests | M01 | Longer question |
| --- | ---: | ---: | ---: | ---: |
| 2,048 tokens | 208 MiB | 1,965 MiB | 21.60 s | 25.00 s |
| 4,096 tokens | 416 MiB | 1,822 MiB | 19.40 s | 23.40 s |

The hybrid profile uses 4,096 tokens to retain context headroom. The
two-question check provides one timing per setting and question. A live
M01 check through the PowerShell launcher confirmed 13 of 27 layers on
Iris Xe, 1,835 MiB available when ready, and ten exact citations in 19.74 s.
The default check confirmed CPU-only residency.

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
