# Evaluation suite

## Offline regressions

Install the app dependencies plus `eval/requirements.txt`, then run:

```bash
python -m unittest discover -s tests -v
```

These tests mock API/Neo4j boundaries. They check grounded rendering, required
sources, invalid model output, truncation, unexpected refusals, wrong symptoms,
invalid judge verdicts, threshold zero and managed seed transactions. They do not
establish scientific correctness, live retrieval quality or real database rollback.

The lot 1 checks can also be run separately:

```bash
python -m unittest discover -s tests -p test_reliability.py -v
python -m unittest discover -s tests -p test_app.py -v
```

The Chainlit regressions cover model connection/rate-limit failures and Neo4j
connection/authentication failures, a safe user-facing fallback, cancellation,
and the successful zero-threshold path. Operational failures are logged server-side
and are not presented as knowledge refusals or sourced answers.

## Live retrieval and agent evaluation

```bash
python eval/run_eval.py
python eval/run_eval.py --agent
python eval/run_eval.py --agent --limit 1
python eval/threshold_sweep.py
```

Requires a configured Neo4j database. `--agent` also requires Anthropic credentials
and consumes tokens for both the agent and judge. No live evaluation was run as
part of the reliability patch. Exit status is non-zero on a failed contract.

The lexical pass and threshold sweep use the same subset: English cases or cases
with an explicit English `retrieval_query`, excluding `agent_only` cases. Raw
French questions and semantic scope decisions belong to the end-to-end agent
pass. The current dataset has 33 cases: 21 in scope and 12 expected refusals;
9 cases belong to the lexical subset. `--limit` is applied separately to each
pass after choosing its eligible cases.

The agent pass checks deterministic metadata from the response renderer:
- in-scope: an actual answer selecting exactly the expected symptom;
- refusal: an intentional refusal, not a protocol failure or exhausted loop.

The LLM judge additionally checks grounding, citations, refusal and whether the
answer addresses the actual question (`answers_question`). Every verdict field
must have the expected type. Missing/invalid judgments fail closed; unexpected
refusals, irrelevant answers and missing citations fail the report. Empty suites
are not successful evaluations. A judge is still fallible and should be calibrated
against expert annotations.

## Interpretation

The original 19/19 and approximately 27-28/28 results describe an older prompt and
free-form response pipeline. They are not validation of this version. The existing
`threshold_calibration.png` is historical and must be regenerated using the new
English-only subset before reporting current calibration results.

The case set is a development/regression set. Threshold tuning on these cases is
not independent validation. Reserve a separate held-out set for deployment, repeat
stochastic agent runs, and review recommendations and evidence with a domain
expert. Graph fidelity does not establish source accuracy or GxP suitability.
