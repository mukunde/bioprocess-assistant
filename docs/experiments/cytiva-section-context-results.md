# Cytiva cleaning: opt-in section-context experiment

Executed on 23 October 2026. **Historical development comparison; no production integration.**

Current status: the [N01–N08 documentary reference review](cytiva-section-questions-human-review.md)
is complete with reservations. The original run C predates that review and retains
its original candidate/pending metadata and 7/8 coverage result. Those historical
artifacts, their hashes and their code snapshots have not been rewritten.

New executions verify both reviewed reference packages before tokenizer loading
or measurement, record each review/manifest hash, and snapshot both decision
journals and reviews. `new_references_human_reviewed` is derived from the verified
review states; it does not grant benchmark, scientific or publication approval.
The dataset key `new_candidate` remains a stable historical identifier, not its
current approval status. Each new result separates `reference_status_at_preparation`
from `reference_review_decision`.

Summaries now reject missing/duplicate intent-language-variant rows and invalid
completeness flags against an explicit expected inventory. Prior valid scores
remain reproducible from the unchanged original result files.

## Change and frozen method

The v03 policy adds source-section overviews to the existing v02 lexical/procedural retrieval. BM25 documents, aliases, k1/b and top five hits are identical in the paired comparison. Only assembly changes. The query text, never question IDs or expected evidence, controls the policy:

- A positive retrieval hit and a pressure/backpressure, flow or threshold term trigger a section overview. The existing local FR/EN lexical normalization is reused; English pressure also activates the backpressure trigger.
- Explicit Protein A/G Sepharose mentions select that family overview; MabSelect mentions select its overview. An unspecified/unrecognized product keeps both families labelled unresolved; this does not authorize either recipe. Whole-phrase matching tolerates punctuation and avoids product-name prefix matches.
- Product/deposit headings and the general cleaning indication are preserved as available source records. Both families remain separate; no invented causal link or rewritten protocol is introduced.
- Reserve the entire selected overview before fitting ranked procedural bundles into the same 2048-token serialized-context budget. If the complete overview cannot fit or touches quarantine, report it unavailable. Never truncate it silently or treat budget completeness as answerability.

The source policy and eight new bilingual reference intents were frozen before any measurement. A pre-measurement unit test exposed missing handling of the English word pressure; this was fixed before the first run. No change was made after seeing the measured answers/evidence. At measurement time, the additional annotations were assistant-prepared candidates pending human review; that documentary review has since completed with reservations. The source manual and the ten earlier intents are already known; this is not a blind or held-out study.

Implementation: [section policy](../../ingestion/section_context.py), [paired evaluator](../../experiments/cytiva/section_retrieval.py), [v03 configuration](../../experiments/cytiva/cleaning_source_context_v03.json), [new candidate questions](../../experiments/cytiva/cleaning_section_questions_v01.json), [tests](../../tests/test_section_context.py). The earlier modules/configurations/reports, original runs A/B and all reviewed inputs remain byte-identical; 25 existing file fingerprints were checked.

## Paired results

| Reference set | v02 complete in both languages | v03 complete in both languages | v03 max context |
|---|---:|---:|---:|
| Ten human-reviewed intents | 8/10 | 10/10 | 1618 tokens |
| Eight new candidate intents | 7/8 | 7/8 | 1604 tokens |

**Q08:** both languages now include E166-T, the general cleaning indication, in addition to the scoped warning; each expanded context contains 1347 tokens. No numerical flow/pressure answer is generated or evaluated.

**Q09:** EN restores E166-PH and E166-T; FR restores E166-PH, E167-PH and E167-SH. The product remains unresolved. Context sizes are 1618 tokens EN and 1449 FR. This is complete reference context for a clarification, not an executed clarification response.

There are no observed budget exclusions. The fully serialized 17-atom corpus would require 2215 tokens, exceeding 2048; v03 is not simply dumping every source record into the prompt. It nevertheless adds more background and can carry both products at once. More complete evidence does not establish a more precise or safer final answer.

## Additional questions (candidates at measurement time)

All are bilingual in the JSON file; this table gives the English wording and the indispensable source references. These expected statuses have since received documentary human approval with reservations; they remain reference response policies, not measured assistant behaviour.

| ID | English question | Required references | Expected status |
|---|---|---|---|
| N01 | With Protein G Sepharose, pressure is rising and the foulant is unknown. What does the cleaning section distinguish before a recipe can be selected? | E166-H, E166-T, E166-PH, E166-LH | clarify |
| N02 | What reduced flow rate in mL/min does the MabSelect section specify for cleaning with 30% 2-propanol? | E167-H, E167-E, E167-W | refuse |
| N03 | Compare the nonionic-detergent route on Protein A Sepharose with the one on MabSelect, including wash conditions. | E166-H, E166-LH, E166-D, E167-H, E167-LH, E167-D | answer |
| N04 | On Protein A Sepharose, give both the ethanol hold time and the volume of ethanol required for the hydrophobic-deposit alternative. | E166-H, E166-LH, E166-E, E166-W | refuse |
| N05 | Can the 100–500 mM sodium hydroxide sequence for MabSelect SuRe LX be treated as the Protein G Sepharose cleaning procedure? | E167-H, E167-PH, E167-SH, E167-S, E166-H, E166-PH, E166-P | answer |
| N06 | Is pH 7.0–8.0 stated for the binding-buffer wash after the MabSelect detergent route, and what other wash conditions accompany it? | E167-H, E167-LH, E167-D | answer |
| N07 | Why does the MabSelect solvent paragraph mention increasing gradients and lower flow, and does it specify a pressure limit in bar? | E167-H, E167-LH, E167-E, E167-W | refuse |
| N08 | For Protein A Sepharose, does the 6 M guanidine hydrochloride cleaning block specify a contact time? | E166-H, E166-PH, E166-P | refuse |

**Remaining failure: N05, in both languages and both variants.** The comparison between the SuRe LX stronger-alkali sequence and Protein G Sepharose misses E166-PH and E166-P (the other family’s precipitated/denatured-protein block). This request has no pressure/flow/threshold trigger, so v03 intentionally leaves assembly unchanged. Its coverage is 5/7 required source atoms. Do not add a question-ID exception or relabel this as complete. Reference relevance and the intended comparison have since been confirmed in the documentary review, without changing this measured failure.

On the new set, mean indispensable-evidence coverage remains 96.4% in each language; both variants are complete for N01–N04 and N06–N08. This gives no measured improvement on the added questions, despite fixing Q08/Q09 in the development set.

## Operations and verification

Same-process paired timings, without allocation tracing: reviewed-set median assembly 4.94 ms v02 versus 5.88 ms v03; new-set medians 6.44 versus 8.15 ms. Three repetitions, variant order alternated by intent. This tiny sample is not a production-latency benchmark; it excludes startup/tokenizer initialization and is not directly comparable to runs A/B under tracemalloc. RAM was not measured in this run.

Verified 72 variant/formulation contexts: identical paired rankings, full exact quotations and source scopes, accepted dependency closure, unique source IDs, complete requested overviews and <=2048 tokens. Code/input snapshots, source policy/question freeze and artifact hashes pass. Python networking was guarded and recorded zero attempts. No LLM/VLM, embeddings, paid API, model download, database mutation, scientific validation or graph publication.

Thirteen section-policy regressions cover product routing, bilingual triggers, punctuation/prefix handling, whole-overview budget rejection, quarantine, dependency/quote preservation, no-hit behaviour and refusal to overwrite existing runs. The earlier 16 retrieval tests also pass.

## Post-fix verification (separate run D)

A new local run `section-context-reviewed-20261023-d` exercises the corrected
launcher without overwriting run C. Both review packages pass before tokenizer
loading. Its manifest records eight reviewed additional references, hashes both
reviews/package manifests and snapshots both original decision journals. New
result rows retain historical preparation status separately from the verified
current decision; documentary approval does not authorize publication or approve
benchmark results.

Run D reproduces the same evidence coverage: 8/10 for v02 and 10/10 for v03 on
Q01–Q10; 7/8 for both on N01–N08. N05 still lacks E166-PH and E166-P. No historical
score or failure was replaced. Timings in the earlier table/paragraphs still
belong to run C. The two previously malformed range strings in the question table
were corrected as UTF-8 display text; frozen questions/source quotations are unchanged.

## Reproduction and preserved artifacts

```powershell
.\.venv-ingestion\Scripts\python.exe -m unittest tests.test_section_context tests.test_local_passage_retrieval -v
.\.venv-ingestion\Scripts\python.exe -m experiments.cytiva.section_retrieval --output data/experiments/cytiva/retrieval-pilot-v01/runs/section-context-new
```

The original run is local and ignored: `data/experiments/cytiva/retrieval-pilot-v01/runs/section-context-20261023-c/`. It contains the frozen corpus, code/policy/input snapshots, pre-run manifest, exact ordered contexts/scores, timings, metrics, artifact hashes and post-run checks. The launcher refuses an existing output directory. The separate reference-freeze/preservation audits retain the hashes recorded before execution.

## Decision and next step

Retain v03 as an experimental option for pressure/flow/threshold requests; do not replace the general default or claim generalization from 10/10 on known questions. Human documentary review of N01–N08 is now complete. The next retrieval experiment can separately compare evidence retrieval across explicitly named product families for requests like N05, while preserving this 7/8 result and all reservations. A runtime completeness decision must come from independent query/coverage signals, never the gold reference lists.

The [earlier report](cytiva-cleaning-retrieval-results.md) retains the historical A/B observations. Its current runtime-status note and this report’s review-status/encoding corrections do not change source inputs, human decisions, measured outputs or reservations. The new questions may recombine known facts; they are additional development probes, not independent unseen evidence. Complete source presence does not score refusal/clarification correctness, scientific applicability or production safety.
