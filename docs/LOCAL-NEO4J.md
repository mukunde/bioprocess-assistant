# Local Neo4j in Docker

The working database replaces the unavailable Aura connection. It rebuilds the graph from `graph/schema.cypher` and `graph/seed.cypher`; it does not recover additions that may have existed in the old instance.

## Configuration

The ignored `.env` contains the four local settings:

```dotenv
NEO4J_URI=bolt://127.0.0.1:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<local-password>
NEO4J_DATABASE=neo4j
```

The initial password was generated locally. For a new installation, choose a password before the first start. Editing `.env` after the volume is created does not change the password stored in Neo4j.

The database is accessible only from this PC. The named Docker volume `bioprocess-assistant-local_neo4j_data` preserves data when the container stops or is recreated. This volume belongs to Docker Desktop/WSL storage, not the project's OneDrive folder; back it up separately.

## Commands from the repository root

```powershell
docker compose -f compose.neo4j.yaml up -d --wait
.\.local-tools\integration-venv\Scripts\python.exe scripts/load_graph.py
.\.local-tools\integration-venv\Scripts\python.exe eval/run_eval.py
docker compose -f compose.neo4j.yaml stop
```

The `integration-venv` environment is local and unversioned. On another machine, install `requirements.txt` and `eval/requirements.txt` into a Python environment and use its interpreter.

Neo4j Browser: <http://127.0.0.1:7474>. Connect with `bolt://127.0.0.1:7687`, user `neo4j` and the password from the local `.env`. Driver connection checks and lexical evaluation do not call a model. Do not use `--agent` for an evaluation without API charges.

The local Neo4j `.env` does not configure the model or Chainlit demo credentials. Integration testing uses a simulated model; normal chat retains its Anthropic configuration and can incur charges when an API key is supplied.

The container memory limit is 1.5 GiB, including up to 512 MiB Java heap and 256 MiB page cache. Docker Desktop/WSL and the application need additional memory. Stopping the database releases the container's resources.

## Lot 1 validation

A temporary database, separate from the working database, validated loading, the English index, constraints, source presence, idempotence, preservation of an independent node, real rollback after an invalid statement, the nine lexical cases and a Chainlit round trip with real Neo4j and a simulated model. It was then removed.

These checks do not validate the seed's scientific fidelity to the manual or a real model's semantic choices on French questions.
