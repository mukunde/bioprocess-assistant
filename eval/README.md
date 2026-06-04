# Evaluation suite

Measures the troubleshooting agent's contract - retrieval, refusals, anti-hallucination,
and sourcing - so the "zero hallucination" claim is **measured, not asserted**.

## Two levels

| Level | What it checks | How | Cost |
|---|---|---|---|
| **Tool-level** | `query_graph` returns the expected symptom for in-scope questions, and nothing for refusal cases | direct call, score vs threshold | free, deterministic |
| **Agent-level** | the full agent answer is grounded (no claim outside the tool output), cites sources, and refuses when it should | runs `run_agent`, then an LLM-as-judge (`judge.py`) | API tokens |

## Files

- `cases.yaml` - the dataset: 28 typed, **bilingual** cases (`in_scope`, `in_domain_miss`, `out_of_scope`, `off_topic`; each tagged `lang: fr|en`). In-scope cases carry the exact (English) `expected_symptom`. French and English paraphrases per symptom stress both the matching and the agent's cross-lingual bridge.
- `run_eval.py` - the runner (tool-level always; agent-level with `--agent`).
- `judge.py` - the LLM-as-judge: given `(question, tool output, agent answer)`, returns `hallucination_free`, `sources_cited`, `refused`.
- `threshold_sweep.py` - sweeps the match threshold and plots the precision/recall frontier of the BM25 retrieval component (calibrated on English, the input the agent feeds `query_graph`).

## Running

The eval needs a few extra packages (kept out of the app's `requirements.txt`):

```bash
pip install -r eval/requirements.txt   # pyyaml + matplotlib (app deps assumed installed)
```

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

Agent-level (the bilingual system): **19/19 in-scope answered with sources** (French and
English), refusals clean, **~27-28/28 hallucination-free**. The threshold sweep - run on
the BM25 component's actual input (English; the agent bridges French) - shows **100%
recall and 100% refusal across a wide plateau**, with the default 2.5 inside it.

> Notes: the tool-level pass scores `query_graph` on the *raw* question, so raw French
> in-scope cases intentionally fall through (no cross-lingual lexical match) - they are
> the agent's job, covered at the agent level. LLM judging has minor run-to-run
> variance (±1 case).
