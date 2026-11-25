# Second Windows PC results for the CPU graph chat

Overall status: **NOT_RUN**

Follow the [second-PC protocol](WINDOWS-GRAPH-CHAT-SECOND-PC.md). Fill a copy
after testing. Use `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN` for each row.

## Environment

| Field | Observation |
| --- | --- |
| Date, tester and machine alias | |
| Second physical PC confirmed | |
| Windows edition, build and architecture | |
| CPU and installed RAM | |
| PowerShell, Git and Python versions | |
| Docker Desktop, Engine and Compose versions | |
| Ollama, Chainlit and Neo4j versions | |
| Actual Git revision | |
| Package cache reuse and install duration | |
| GGUF SHA-256, model alias and model ID | |
| Ollama store initially empty | |
| Local ports and disposable Compose project name | |

## Mandatory checks

| ID | Check | Status | Observation or evidence |
| --- | --- | --- | --- |
| CPU01 | Fresh checkout at the pinned revision, isolated Python and consistent dependencies | NOT_RUN | |
| CPU02 | Disposable Neo4j project healthy, bundled seed loaded, verified GGUF imported | NOT_RUN | |
| CPU03 | Check-only passes, allocation 0 bytes, both RAM readings ≥ 1,024 MiB, temporary ports released | NOT_RUN | After model: ___ MiB. Full stack: ___ MiB. |
| CPU04 | Live startup, both RAM checks pass, login and local model label verified, Ollama allocation 0 bytes | NOT_RUN | After model: ___ MiB. Full stack: ___ MiB. |
| CPU05 | Both symptom paths and expected citations displayed | NOT_RUN | Latency: ___ s. Paths and citation labels: |
| CPU06 | Pressure limit withheld and no citations shown | NOT_RUN | Latency: ___ s. Observed abstention: |
| CPU07 | Ctrl+C releases both ports, restart on those ports works, second stop releases both | NOT_RUN | |
| CPU08 | Disposable Neo4j project stopped and Git worktree clean | NOT_RUN | |

## Attempts and follow-up

- First failure or blocker and exact stage:
- Retry, change made and outcome:
- Findings to investigate:
- Redacted evidence paths:
