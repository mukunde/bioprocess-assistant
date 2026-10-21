# CLAUDE.md - Bioprocess Troubleshooting Assistant

Persistent context for Claude Code. Read each session. Repository collaboration rules are in [AGENTS.md](AGENTS.md); the [README](README.md) and [roadmap](docs/ROADMAP.md) describe current status.

## Project objective

An AI troubleshooting demonstrator for **Protein A capture chromatography**, a downstream bioprocess operation. Given a symptom in natural language, it returns documented possible causes and corrective actions with citations. This is an interview/portfolio project for bioprocess equipment use cases. Prioritize a small working end-to-end system over exhaustive coverage.

## Architecture

The current assistant retrieves from a **Neo4j knowledge graph**, without vector retrieval in its serving path. The graph stores documentary knowledge; the agent selects retrieved results rather than supplying technical advice from parametric knowledge. This supports traceability but does not guarantee scientific accuracy or absence of errors. See [ADR-001](docs/ADR-001-knowledge-graph-grounding.md).

## Stack

- Python; the reference workstation uses 3.13, while the application Dockerfile targets 3.11.
- Neo4j Community in local Docker for development; Aura is an optional separately configured alternative. Python driver: `neo4j`.
- Chainlit conversational UI with password authentication.
- Anthropic SDK (`anthropic`) with tool use; the configured model is defined in `agent.py`.
- Ignored `.env` configuration: `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`, `ANTHROPIC_API_KEY` and Chainlit authentication settings.

## Serving graph

Three node types and two relationships:

- `(:Symptom {name, description, source})`
- `(:Cause {name, description, source})`
- `(:Action {name, description, source})`
- `(:Symptom)-[:INDICATES]->(:Cause)`
- `(:Cause)-[:RESOLVED_BY]->(:Action)`

Source fields must accompany displayed facts. The small seed covers six symptoms; historical expansion targets were approximately 12 causes and 15 actions. Public sources only. This is not a GxP-qualified system.

## Agent contract

The single tool, `query_graph(symptom: str)`, performs parameterized Cypher retrieval and returns structured results. It does not ask an LLM to generate Cypher.

The contract amended on 17 October 2026 requires:

- Model output is JSON containing only `status`, `language` and `result_ids`.
- `grounding.py` validates IDs/sources and renders stored graph facts; free-form model advice is not displayed.
- Headings/refusals are bilingual; descriptions remain English until translations are reviewed.
- Protocol failure is an evaluation error, not a successful refusal.
- Fidelity to the graph does not establish scientific correctness or relevance.
- Seed loading is additive and transactional. Do not reintroduce global deletion. Index changes require explicit migrations.
- PDF ingestion, monitoring and conditional KAG work are described in the active roadmap.

## Historical build sequence

The original walking-skeleton plan was: minimal sourced seed/schema; Chainlit-to-graph end-to-end question; graph expansion; demonstration polish and a backup recording. These are delivery history, not instructions to rebuild completed features. The earlier exclusions of authentication and cloud deployment were superseded by the current password-protected reference deployment.

## Conventions and scope

Use explicit names and concise code comments. Keep documentation in English, with original source and human decision quotations preserved. Maintain ADR-001 in `docs/`. Keep the agent/graph-query boundary small and reusable. Do not use real internal data. Vector retrieval, extended automation and CI/CD are separate decisions, not implicit dependencies of the current POC.
