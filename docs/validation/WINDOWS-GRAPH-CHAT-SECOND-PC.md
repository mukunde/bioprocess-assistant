# Validate the CPU graph chat on a second Windows PC

Status: **prepared, not run on a second PC**. Use the
[results sheet](windows-graph-chat-second-pc-results.md) on a different physical
Windows x64 PC. The [reference machine results](../LOCAL-GRAPH-CHAT.md#windows-launcher-verification)
cover the launcher on the first PC. This protocol tests portability of the
graph chat with local Ministral. It does not run LX01–LX12.
Keep both protocol files available separately from the pinned checkout.

## Prepare a clean checkout

Install Git, CPython 3.13 x64, Docker Desktop with Linux containers, and Ollama
for Windows. Start Docker Desktop and the regular Ollama service for the model
import. Record tool versions, Windows build, CPU and installed RAM in the sheet.
Use a PowerShell session without inherited Neo4j, Chainlit, Anthropic or Ollama
overrides. Check ports 7474, 7687, 8000 and 11435 before starting. Keep existing
services running and record any conflict. The launcher can use alternative
Chainlit and Ollama ports, but this protocol tests the defaults.

Run these commands from a directory where `bioprocess-graph-chat-second-pc` does
not exist. Check each external command's exit code before moving on.

```powershell
git --version
py -3.13 -c "import platform, sys; print(sys.version); print(platform.machine())"
docker version
docker compose version
ollama --version
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, BuildNumber, OSArchitecture
Get-CimInstance Win32_Processor | Select-Object Name
Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory
Get-NetTCPConnection -State Listen -LocalPort 7474,7687,8000,11435 -ErrorAction SilentlyContinue

git clone --branch main --single-branch https://github.com/mukunde/bioprocess-assistant.git bioprocess-graph-chat-second-pc
if ($LASTEXITCODE -ne 0) { throw 'Clone failed.' }
Set-Location -LiteralPath .\bioprocess-graph-chat-second-pc
git switch --detach a39d27f1cb48956f409b50e2a2ad01a823e5974e
if ($LASTEXITCODE -ne 0) { throw 'Pinned revision unavailable.' }
git rev-parse HEAD
git status --short
New-Item -ItemType Directory -Force .local-tools\graph-chat-second-pc | Out-Null
py -3.13 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
.\.venv\Scripts\python.exe -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dependency check failed.' }
.\.venv\Scripts\python.exe -m pip show chainlit neo4j
git check-ignore .env .local-tools/graph-chat-second-pc/results.md
.\.venv\Scripts\chainlit.exe create-secret
```

Expect empty initial Git status and `No broken requirements found`. Dependencies
are installed from the pinned checkout's requirements. Record resolved versions
and any reused cache. Source, package, image and weight downloads are required
for a clean setup. No Anthropic key or account is required for inference.

## Configure the disposable stack

Create a new ignored `.env` at the clone root. Fill in the placeholders with a
new local database password, the generated Chainlit secret, and local test
credentials. Keep credentials out of the results sheet and use the bundled seed
as the only graph data.

```dotenv
NEO4J_URI=bolt://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=replace_with_local_password
NEO4J_DATABASE=neo4j
CHAINLIT_AUTH_SECRET=replace_with_generated_secret
DEMO_USERNAME=replace_with_local_test_username
DEMO_PASSWORD=replace_with_local_test_password
```

Use a fresh Compose project name so Neo4j uses a new volume. Keep the generated
name for shutdown. Start Neo4j and load the bundled seed.

```powershell
$graphChatProject = 'bioprocess-second-pc-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
docker compose -p $graphChatProject -f compose.neo4j.yaml up -d --wait
if ($LASTEXITCODE -ne 0) { throw 'Neo4j startup failed.' }
.\.venv\Scripts\python.exe scripts/load_graph.py
if ($LASTEXITCODE -ne 0) { throw 'Neo4j seed load failed.' }
```

Follow the [verified GGUF import instructions](../LOCAL-GRAPH-CHAT.md#use-ministral-on-the-host)
from a directory outside the checkout. Check the SHA-256 before importing
Ministral 3 3B Instruct 2512 Q4_K_M under `bioprocess-local:latest`. Use a model
store where this alias is absent so the import does not replace an existing
model. Return to the checkout and run `ollama list` to confirm the alias and
record its ID. Record whether the store was empty.

## Verify CPU startup and the browser

In the same PowerShell session, run:

```powershell
.\Start-LocalGraphChat.ps1 -Profile CPU -CheckOnly
```

Require exit code 0, GPU allocation **0 bytes**, and at least **1,024 MiB**
of available RAM both after model load and when the full stack is ready.
A memory failure is `BLOCKED`. Record both readings and retain the first result
if you retry after freeing memory. Keep the threshold unchanged.

After check-only exits, confirm the temporary ports have no listeners:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 8000,11435 -ErrorAction SilentlyContinue
```

Start a live session:

```powershell
.\Start-LocalGraphChat.ps1 -Profile CPU
```

Confirm the same CPU and RAM checks. Open [Chainlit on loopback](http://127.0.0.1:8000/)
on the second PC, sign in, and verify **Mode local · Ministral 3 3B Instruct**.
Use English output, lexical threshold 2.5, and a fresh chat for each probe.
While the live session runs, a second PowerShell window can check the dedicated
Ollama server directly:

```powershell
(Invoke-RestMethod http://127.0.0.1:11435/api/ps).models |
    Select-Object name, size_vram
```

Expect `bioprocess-local:latest` with `size_vram` equal to 0. Record the time
from submitting each question until the full reply is visible. Use these
portability probes based on the earlier M01 and ML06 scenarios.

| ID | Enter in Chainlit | Expected |
| --- | --- | --- |
| CPU05 | My column pressure is higher than usual, my capture yield has dropped, and I find antibody in the flow-through. What should I check? | Both symptom paths appear, high column pressure and capture yield drop. Expect ten citation entries on the bundled seed. Record the actual labels and open one reference from each path if presented as links. The response treats causes as possibilities. |
| CPU06 | What is the numerical maximum pressure for my column? | The chat abstains from supplying a numerical pressure limit and cites no passages for this unsupported request. |

Browser results test the rendered outputs. Timing is descriptive because speed
depends on the machine. This run does not establish a cold/warm benchmark.

## Stop, restart and finish

Press Ctrl+C in the launcher terminal. Check that ports 8000 and 11435 are
free. Repeat the live start on those ports, confirm readiness and reload
Chainlit. Press Ctrl+C again and verify both listeners are gone. Then stop only
the disposable Compose project and confirm a clean checkout.

```powershell
Get-NetTCPConnection -State Listen -LocalPort 8000,11435 -ErrorAction SilentlyContinue
docker compose -p $graphChatProject -f compose.neo4j.yaml stop
if ($LASTEXITCODE -ne 0) { throw 'Stopping the second-PC Neo4j project failed.' }
git diff --exit-code HEAD
if ($LASTEXITCODE -ne 0) { throw 'Tracked files changed.' }
git status --short
```

Copy the blank sheet to the ignored `.local-tools/graph-chat-second-pc/`
directory and update that copy. Keep any logs there and redact credentials and
personal paths before sharing. Record each attempt. A portability pass requires
every mandatory row to pass on the second physical PC. Report a failure or
blocker as observed and keep the original record when retrying.
