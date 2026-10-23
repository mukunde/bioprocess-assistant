# Cytiva cleaning: local lexical retrieval and context assembly

Executed on 23 October 2026. **Historical development pilot, not production validation.**

Current runtime review: summaries now require one unique EN/FR result for every
expected question. Missing intents/languages, duplicates and non-boolean
completeness flags fail explicitly; complete-intent counts are no longer tied to
a hardcoded Q01–Q10 range. Expected IDs come from the frozen reference inventory.
This guard was added after the recorded runs; original A/B outputs, scores,
configurations and code snapshots remain unchanged.

## Scope and implementation

The 10 human-reviewed question intents (20 FR/EN formulations) were evaluated against 17 curated source excerpts from pages 166–167. The index contains only whitelisted source quotes and page/product provenance. Questions, expected answers, human messages, decision labels and review reports are never indexed. The evaluator reads references only after the corpus/index and run configuration are frozen. Package verification does read the reference files beforehand to check integrity; no reference text enters scoring or expansion.

Implementation: [BM25 and assembler](../../ingestion/local_passage_retrieval.py), [isolated runner](../../experiments/cytiva/cleaning_retrieval.py), [initial source topology](../../experiments/cytiva/cleaning_source_context.json), [procedural variant](../../experiments/cytiva/cleaning_source_context_v02.json), and [regression tests](../../tests/test_local_passage_retrieval.py). Neither production retrieval nor Chainlit/Neo4j defaults change.

- BM25: k1=1.2, b=0.75, top 5 positive-score hits; stable ID tie-break.
- A small explicit accent-insensitive FR/EN vocabulary bridge runs on queries and source text; it is not a multilingual embedding or a general translation system.
- Dependency assembly is source-based and independent of question IDs or gold evidence lists. It restores product/deposit headings and the separate warning for each ethanol/solvent recipe; SuRe/SuRe LX recipes retain their restricted scope. This topology is manually authored for these two pages, not automatic structure understanding.
- Full exact quotes are serialized with source IDs, page indices, product scope, quote hashes and offsets. All metadata/wrappers count against an experimental 2048-token cap, using locally cached cl100k_base. This is not a final answering prompt or a budget validated for another model.
- A seed and its transitive dependencies form an atomic bundle: deduplicate by canonical source ID, reject cycles/missing references, propagate quarantine, skip an entire over-budget bundle rather than cut a warning or number. Budget completeness is not proof of complete evidence or answerability.

## Two preserved development runs

**Run A** searches all 17 source atoms independently; its assembler adds their dependencies. After seeing headings outrank recipes, **Run B** searches 10 procedural/indication/warning roots enriched with their source dependencies; context-only headings are no longer independent candidates. The same top-k and token budget remain. Both candidate selection and indexed text change, so improvement is attributed to the complete profile, not isolated causal proof of one change. No question-specific expansion or higher top-k was added.

| Measure | Run A EN | Run A FR | Run B EN | Run B FR |
|---|---:|---:|---:|---:|
| Complete indispensable evidence after assembly | 4 | 4 | 8 | 8 |
| Mean required source-atom coverage after assembly | 78.3% | 77.1% | 94.2% | 92.9% |
| Maximum serialized-context tokens | 918 | 918 | 1381 | 1514 |
| Excluded bundles | 0 | 0 | 0 | 0 |

Run B has **8/10 complete intents in both languages**: Q01–Q07 and Q10. That is 16/20 formulations, not 20 independent observations. Within B, raw unexpanded seeds cover 35.8% of required atoms on average and no question has all required headers; assembly raises this to 94.2% EN and 92.9% FR. Raw seeds alone deliberately lack context-only headers. This does not make B raw-only a fair alternative architecture. Run A raw coverage is 70.8% EN / 72.1% FR with 4/10 complete; assembly raises coverage to 78.3% / 77.1% but remains 4/10 complete.

Ranking Precision@5/MRR/NDCG@5 are retained in local metrics against canonical reference atoms. Across A and B they are not directly comparable: B removes context-only atoms as search roots and retrieves their text through bundles. Complete canonical evidence after assembly is the primary comparison; surplus, possibly irrelevant context remains visible.

## Results per intent (Run B)

| Intent | EN complete | FR complete | Missing EN | Missing FR |
|---|---|---|---|---|
| Q01 | yes | yes | — | — |
| Q02 | yes | yes | — | — |
| Q03 | yes | yes | — | — |
| Q04 | yes | yes | — | — |
| Q05 | yes | yes | — | — |
| Q06 | yes | yes | — | — |
| Q07 | yes | yes | — | — |
| Q08 | no | no | E166-T | E166-T |
| Q09 | no | no | E166-PH, E166-T | E166-PH, E167-PH, E167-SH |
| Q10 | yes | yes | — | — |

**Q08:** both languages miss E166-T, the general cleaning indication. The top five emphasize flow/ethanol warnings and recipes; no numerical threshold is invented by this retrieval-only output, but the expected refusal behaviour itself is not executed or scored.

**Q09:** EN misses E166-PH and E166-T; FR misses E166-PH, E167-PH and E167-SH. The generic pressure query does not retrieve all product/deposit distinctions needed by the reviewed clarification reference. This requires better section/context selection, not silently pretending a recipe is an appropriate answer.

## Integrity, budget and operations

All returned quotes retain their exact source strings, units, conjunctions and original hashes. Every accepted expanded seed includes its source dependencies; no primary context contains a quarantined unit. The real pilot has no quarantined source units, so zero observed leakage is not an adversarial quarantine benchmark; synthetic regressions exercise child/parent quarantine and atomic budget rejection. Cross-product passages can be present together: explicit scopes are preserved, but no answering model was tested for respecting them.

Run-B median retrieval latency under Python allocation tracing: 0.97 ms EN / 1.25 ms FR. Median expanded assembly: 9.27 / 10.29 ms. Three fixed-order repetitions per formulation, no best-run selection. These are in-process prototype timings over a tiny corpus, excluding interpreter startup, package verification and tokenizer initialization; no production or p95/p99 claim.

Run-B Python traced peak allocations: 462705 bytes; this is not process/system peak RAM. All contexts fit (maximum 1514 tokens); no budget rejection explains Q08/Q09. Extra index, model, electricity or human costs are not inferred from zero API spend.

Measured runs used the local tokenizer cache, with Python networking guarded and zero network attempts recorded. No LLM/VLM, embedding inference, external API, paid service, model download or database write was executed by the runner. An initial unguarded tokenizer-cache probe before implementation attempted a public tokenizer fetch and failed DNS; the runner subsequently checks the local asset hash and refuses any download.

## Reproduction and artifacts

Use the existing ingestion environment with its cached tokenizer. Always choose a fresh output directory; the launcher refuses overwrite.

```powershell
.\.venv-ingestion\Scripts\python.exe -m unittest tests.test_local_passage_retrieval -v
.\.venv-ingestion\Scripts\python.exe -m experiments.cytiva.cleaning_retrieval --output data/experiments/cytiva/retrieval-pilot-v01/runs/lexical-context-new-a
.\.venv-ingestion\Scripts\python.exe -m experiments.cytiva.cleaning_retrieval --spec experiments/cytiva/cleaning_source_context_v02.json --output data/experiments/cytiva/retrieval-pilot-v01/runs/lexical-context-new-b
```

Original local runs (ignored): `data/experiments/cytiva/retrieval-pilot-v01/runs/lexical-context-20261023-a/` and `lexical-context-20261023-b/`. Each retains corpus JSON, configuration/input/code hashes, ordered scores, raw/expanded exact contexts, missing evidence, exclusions, three timing samples, CSV and metrics. Separate `audit-run-a-code/` and `audit-run-b-code/` directories retain the measured code/config snapshots; later runs are new experiments, never replacements.

## Limits and historical next priority

The curated corpus, question family, bilingual vocabulary and hand-authored source topology are known development inputs. No whole-manual omission rate, independent test score, general multilingual retrieval capability or automatic layout extraction is demonstrated. Full reference coverage only means required source atoms were present; it is not semantic answer correctness. The expected 7 answer / 1 clarify / 2 refuse labels remain untested without a response layer. Ragas, LightRAG and production integration remain separate work.

At the end of these A/B runs, the next proposed step was a separately versioned section-level context fallback. That later experiment and its additional reference review are summarized in the [completed N01–N08 review](cytiva-section-questions-human-review.md); the optional section runtime is a separate lot. This historical recommendation is not a current pending-review status. Keep Q08/Q09 as visible development regressions. Do not infer run-time incompleteness using gold evidence lists; a deployable policy needs an independently defined signal. Do not increase top-k after inspecting these questions and present the resulting score as independent validation.

The [completed human reference review](cytiva-cleaning-retrieval-human-review.md) and its frozen questions, evidence, messages and reservations remain unchanged. No scientific, operational or publication approval follows from this experiment.
