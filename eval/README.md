# Evaluation suite

Measures the troubleshooting agent's contract - retrieval, refusals, anti-hallucination,
and sourcing - so the "zero hallucination" claim is **measured, not asserted**.

## Two levels

| Level | What it checks | How | Cost |
|---|---|---|---|
| **Tool-level** | `query_graph` returns the expected symptom for in-scope questions, and nothing for refusal cases | direct call, score vs threshold | free, deterministic |
| **Agent-level** | the full agent answer is grounded (no claim outside the tool output), cites sources, and refuses when it should | runs `run_agent`, then an LLM-as-judge (`judge.py`) | API tokens |

## Files

- `cases.yaml` - the dataset: 22 typed cases (`in_scope`, `in_domain_miss`, `out_of_scope`, `off_topic`). In-scope cases carry the exact `expected_symptom`. Several paraphrases per symptom stress the matching.
- `run_eval.py` - the runner (tool-level always; agent-level with `--agent`).
- `judge.py` - the LLM-as-judge: given `(question, tool output, agent answer)`, returns `hallucination_free`, `sources_cited`, `refused`.
- `threshold_sweep.py` - sweeps the match threshold and plots the precision/recall frontier.

## Running

```bash
python eval/run_eval.py                      # tool-level (free, deterministic, CI-friendly)
python eval/run_eval.py --agent              # + agent-level LLM judge (costs API tokens)
python eval/run_eval.py --agent --limit 1    # smoke test: first case of each type
python eval/run_eval.py --min-score 2.0      # try a different decision threshold
python eval/threshold_sweep.py               # regenerate threshold_calibration.png
```

Requires the same `.env` as the app (Neo4j + Anthropic). `run_eval.py` exits non-zero
on any failure, so the tool-level pass can gate CI.

## Metrics

- **Retrieval accuracy** (in-scope): the correct symptom is returned above the threshold.
- **Refusal accuracy**: refusal cases correctly return nothing (tool) / decline (agent).
- **Hallucination-free rate** (agent): no factual claim outside the tool output.
- **Source-citation rate** (agent): every cause/action cites a source from the tool output.

## Latest results

Tool-level: 12/14 in-scope (two paraphrases sit at the recall frontier, just under the
2.5 threshold), 8/8 refusals. Agent-level: 22/22 hallucination-free, 14/14 sourced,
8/8 refusals clean. The threshold sweep shows overall accuracy plateaus across a
wide band; the default 2.5 sits in the precision-optimal region (refusals at 100%).

> Note: Neo4j full-text BM25 scores have minor run-to-run variability near the
> threshold, so counts at the recall frontier can shift by ±1 case.
