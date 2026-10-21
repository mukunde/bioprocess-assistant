# Protocol: current retrieval, simple passages and LightRAG

Date: 2026-10-19. Status: prepared, not executed. LightRAG is a candidate, not an agreed migration. This document initiates no installation, indexing, generation, API expenditure, database changes or publication.

## 1. Research question and possible decisions

On a small verified Cytiva corpus, which approach retrieves the evidence needed for troubleshooting with the fewest errors, lowest latency and least complexity? Compare solutions usable on the reference PC (i5-1135G7, 16 GB RAM, Iris Xe), without assuming a graph outperforms passages.

Possible decisions are to retain current retrieval, add passage retrieval, use LightRAG as a retrieval component, or conclude that the data is insufficient. Any adoption retains the v0.2 contract, provenance and human review. Storage or generation migration is outside this first trial.

## 2. Prerequisites and genuinely comparable scope

- Generation and human review of `pages-100-102-v02-r2` completed on 20 October 2026: 33 corrected claims, 19 approved and 14 approved with reservations. The [selected package](../../experiments/cytiva/reviewed-r2/README.md) preserves decisions and hashes; publication remains unauthorized. These pages are development data, without an exhaustive omission reference. This r2 review does not approve pages 97–99 or the older cards.
- Assemble approved claims and located evidence, including actual symptoms/causes/actions. Mainly procedural pages 100–102 cannot establish causal coverage; add relevant troubleshooting pages if needed before freezing questions.
- Successful lexical checks are not scientific approval. The user verifies documentary fidelity; industrial operational suitability is outside scope.
- Freeze PDF/edition, conversion, pages, ambiguous sources, claims, human decisions and claim-evidence links with SHA-256. No reference answer or test verdict enters an index.
- Adapters from v0.2 to retrieval and the common renderer still need implementation and verification. Record missing prerequisites as not ready, rather than producing artificial scores.

### Existing control and common-corpus comparison

`tools.query_graph` uses an English symptom index, a Lucene threshold of 2.5 and the best symptom, then `INDICATES` / `RESOLVED_BY` paths. It is not LLM-generated Text2Cypher.

**A0, unchanged control:** retain current code, seed and threshold; replay existing cases separately. The development suite is already known, so its scores are not new independent results. Without a precise source retrievable in the common corpus, a seed fact is not comparable evidence. A0 results do not enter the equal-coverage ranking.

**A, current retrieval family on a common corpus:** create an evaluation copy using the same lexical symptom logic and parameterized traversals, with an explicit adapter from v0.2 claims. Keep procedures without causal paths in the coverage inventory; never invent a cause to make them accessible. A is an experimental adaptation, not the unchanged current application. The serving graph is untouched.

Report two preassigned strata: questions compatible with causal traversal and broader procedural/synthesis questions. For each, distinguish representable coverage from retrieval quality. Structural inability counts against overall coverage but does not prove poor lexical ranking.

## 3. Three main approaches

| Arm | Index and retrieval | Shared controls |
|---|---|---|
| A — current family | English lexical symptom search, traversal of approved claims, links to source passages; initial threshold 2.5, any tuning on development only | Approved corpus, evidence, question normalization, canonical output |
| B — simple passages | One local multilingual embedding per canonical passage; cosine ranking, without entity extraction, graph, reranker or LLM expansion | Same embeddings and passages as C; same context budget |
| C — LightRAG | Import the same passages and an approved-claim projection through `insert_custom_kg`, use `mix` retrieval, retrieve context without a final answer | Same documentary graph as A, same embeddings as B, same canonical output |

B is deliberately simple vector retrieval rather than another full framework. A passage BM25 control may be added as the B-lexical ablation, with separate results and declared cost; do not replace B after seeing test results.

For C, pin a commit/release and dependency lock before the trial. Test that version's APIs: documentation consulted describes `insert_custom_kg`, `only_need_context` and `aquery_data`, but documented availability is not an integration test. Return usable objects and evidence rather than relying on fragile parsing of formatted context.

Context-only mode removes final generation but does not guarantee zero LLM calls: keyword extraction, merging or summarization may still use them. Account for and log every role. No reconstruction call may reintroduce rejected or quarantined claims.

If C wins, run `naive` / `mix` ablations with identical passages, embeddings and budgets, followed by frozen keywords. Without these controls, conclusions concern the tested LightRAG system, not the causal effect of the graph alone. Native automatic extraction and LightRAG's own chunking are separate later experiments.

## 4. Corpus, chunking and preservation of conditions

Use our document-structure and hierarchy strategy. All three arms share exactly the same passage manifest:

- Group paragraphs/lists by section and subsection; target 150–350 tokens, cap at 512, without separating an instruction from its condition, negation or unit. Longer instructions are declared exceptions, never silently truncated.
- Preserve document/version, title and hierarchy path, PDF/printed pages, item_refs, offsets and text hashes. Tables retain headers and row associations; captions remain distinct from protocol instructions.
- Preserve child-parent links to restore context. The same assembler applies parent expansion to all arms under the same budget; C must not receive extra passages alone.
- Assign stable canonical passage and evidence IDs. The LightRAG projection must preserve claim IDs, force, product/phase scope, AND/OR conditions, quantities and evidence links. If an edge cannot hold information, retain a separate Claim representation and versioned external registry rather than flattening it into an authoritative summary.
- Check round-trip export on negation, alternatives, adjacent products and numbers. Evidence or condition loss blocks C before measurement.

A passage may contain ambiguous text useful for explaining abstention; its flag remains and it never becomes an authorized recommendation. The common publication/review filter applies to all arms. Where a source unit mixes clear and ambiguous content, apply the existing conservative block or create a newly reviewed segmentation shared by all arms.

## 5. Questions and human reference

Prepare 24 intents, each in French and English: 48 formulations total. Confirm this planned distribution against real sources before freezing:

| Family | Intents | Expected behaviour |
|---|---:|---|
| Direct causal troubleshooting | 6 | Symptom, possible causes and documented actions |
| Conditions, necessity and negation | 4 | Conditional applicability or context request, without invented permission |
| Quantities and product/phase boundaries | 4 | Exact values/units, no transfer to an adjacent product |
| Evidence dispersed across passages | 4 | All indispensable evidence, without newly inferred relations |
| Outside coverage, missing context or ambiguous source | 4 | Refusal, clarification or ambiguity notice as appropriate |
| Direct injection or injection in a test document | 2 | Hostile instruction treated as data, with no evidence-policy override |

An injected document variant is a distinct, labelled synthetic fixture, never attributed to the original PDF or published in the graph. Every arm sees the same variant and review status.

Reserve eight intents (16 formulations) for development and 16 intents (32 formulations) for locked evaluation. Choose a seed, distribute families and keep both languages and every variant of an intent in the same group. Avoid near-duplicates between groups. Test questions remain hidden during tuning; the corpus is indexed for everyone. Since pages have already been inspected, this is neither an unseen manual nor a fully blind evaluation.

Before execution, the user validates for each question: relevant and indispensable passage IDs, acceptable evidence alternatives, authorized claims, product/phase, essential parameters, missing context, expected status (`answer`, `clarify`, `refuse`, `source_ambiguity`) and rationale. A passage without an explicit causal link cannot justify an invented cause.

Both formulations must have the same meaning. Report language metrics separately, then aggregate by intent; these are not 48 independent observations. Retain the current 33 cases as a separate development control, not a fresh test set.

## 6. Configuration and execution

### Stage 0 — Feasibility before scoring

Create isolated evaluation spaces, save configurations and verify the serving graph is unchanged. Do not use global deletion procedures. Verify import, round-trip provenance, context-only mode and absence of unconfigured cloud providers.

Select and freeze one local multilingual embedding compatible with the PC: name, revision, dimension, tokenizer, quantization and prefixes. Measure memory on two development questions. Do not select the model after reading the test. If it does not fit memory, stop and declare the candidate infeasible on this hardware.

Use an available local model for LightRAG keywords; record name/revision/quantization and parameters. An open-source library cannot use a ChatGPT subscription through its API calls: no API key or extra expenditure is authorized here. Subscription-based extraction remains a separate documentary stage shared by all arms.

### Stage 1 — Retrieval only, the main comparison

- Supply the same original question to each arm. For A's English index, use a frozen English reformulation prepared without answers, also supplied to B/C in the controlled track. Keep English originals unchanged. Archive both versions and the reformulation rule.
- A secondary native FR/EN track may let B/C handle French directly and use A's actual model bridge: account for that bridge and report these scores separately. Never mix tracks.
- A retains the best symptom; project its paths to cited passages. B and C rank passages; convert each result into canonical evidence units. Deduplicate before metrics. Fix tie-breaking by ID and the evidence order within a path.
- Export at most five canonical passages, then impose a common 2,048-token context cap including headings, using one measurement tokenizer. Remove whole over-budget passages without truncating conditions or quantities; record exclusions. Measure ranking before assembly and effective coverage after the cap. LightRAG top-k entities are not top-k passages.
- Tune thresholds on development only; Lucene, cosine and LightRAG scores are not directly comparable. If a score cannot be calibrated, fix and disclose the selection rule on development.
- Disable reranking in the main comparison. Any later activation is a dedicated variant with its own cost.
- Freeze all settings before testing: one main pass, then three timed retrieval repetitions per question, alternating A/B/C order. Never select the best repetition.
- Separate cold start, warm operation with answer/query caches disabled, and any cache-enabled profile. Index caches remain frozen artifacts; disclose caches that cannot be disabled and distinguish them from fresh computation.

### Stage 2 — Complete answers, only after adapters exist

Reuse contexts recorded in stage 1. Use the same local answering model, revision, parameters, prompt, output cap and refusal policy for all arms; one generation per question/arm, without choosing among multiple attempts. Errors and truncated outputs remain in denominators. An identical seed does not make execution perfectly deterministic.

The current renderer rejects free technical prose; the main answer comparison must retain this constraint. A common adapter maps retrieved evidence to eligible approved claims with conditions and scope; the model selects IDs, and the same validator/renderer produces output. Retrieved evidence alone does not confer approval. This adapter remains to be built: until then, limit conclusions to retrieval, without claiming comparable generation scores.

A conventional free-generation experiment may follow with an identical prompt and explicit checks, but its scores remain separate from constrained rendering. Ragas with explicitly configured local judges/embeddings supplements deterministic verification; its verdicts do not become human decisions. If the local judge has not been calibrated on reviewed cases, label scores exploratory and prioritize manual review with arm identities concealed.

## 7. Measures and denominators

| Level | Measures | Interpretation |
|---|---|---|
| Retrieval | Precision@5, Recall@5, MRR, NDCG@5 | Questions with relevant reference evidence; frozen 0/1/2 graded relevance. Missing evidence scores zero, rather than removing the question |
| Complete evidence | Fraction of questions containing all indispensable evidence or an accepted alternative set | Before and after the context cap; an approved evidence alternative is not an omission |
| Coverage | Questions representable by A, mappable evidence, failures by family | Separate structural limits, adapter losses and ranking failures |
| Answer | Supported claims; relation/force/condition/quantity/product errors; citation accuracy | Deterministic checks followed by human comparison of outputs and evidence |
| Abstention | Correct refusals/clarifications, false acceptances, excessive refusals | Matrix of the four expected statuses; questions without evidence do not receive an artificial zero Recall@5 |
| Operations | Indexing/review time, median/p95 latency, system/process peak RAM, index size | Small sample: exploratory p95, no p99 or production promise |
| Calls/cost | Calls by role, reported/estimated tokens, failures/retries, cache, estimated cost | Unknown prices stay unknown; subscriptions/electricity/human time are not demonstrated zero costs |

For top-5 results, divide Precision@5 by 5, counting unreturned positions as irrelevant. Recall@5 uses canonical reference evidence; separately report coverage of minimal alternative sets. MRR measures the first relevant evidence and is insufficient for procedures needing multiple sources. NDCG uses identical graded annotations across arms.

Report raw counts and paired results by intent, family and language. Any bootstrap resamples intents with their languages, not timing repetitions. This small documentary set cannot support generalization to the whole manual or regulated sector. Failures/OOM/timeouts remain visible; establish an identical per-query time budget on development and freeze it.

## 8. Traceability, resources and budget

Keep a run manifest: project and LightRAG commits, locked environment, corpus/claim/passage/question SHA-256 hashes, hardware, models/weights, parameters, thresholds, context budgets, caches and execution order. Set exact time/RAM limits after feasibility but before locked questions. On the 16 GB PC, reserve headroom for Windows/WSL; stop runs causing sustained memory pressure or compromising the PC, without hiding failures.

Each result contains `run_id`, arm/track, `question_id`, `intent_id`, language, ordered passages/claims, native scores, filtering reasons, exact context and hash, result/error, latency, RAM, calls and tokens by role. The benchmark log is local and controlled; operational traces default to metadata, without secrets or full text exported to third parties.

Additional API budget for this protocol: **EUR 0**. All runtime models are local; no remote fallback provider. The project ceiling below EUR 10/month remains a constraint, not spending authorization. Stop rather than silently switching provider. Separately account for index/embedding construction, queries, generation, judges and human time. No API invoice does not establish zero total cost.

Store runs in new Git-ignored `data/experiments/retrieval/<run_id>/` directories. Separate manifests, results, metrics and review notes from frozen inputs. Do not index expected answers or another arm's outputs.

## 9. Decision rule to freeze before testing

Minimum requirements: no published output with an incorrect product, dangerously altered quantity, omitted condition, invented evidence or bypassed quarantine in the checked set; verifiable provenance and compliance with hardware limits. Retrieval errors remain measured even when filters block them. Absence of errors on this small set is not certification.

A proposed working threshold for a LightRAG pilot, to freeze after annotation but before execution: at least two additional evaluation intents with complete evidence out of 16 versus the best simpler arm, no regression in false acceptances, median latency at most twice that competitor's and no resource-limit breach. Two intents is a practical pilot threshold, not statistical significance. Report losing variants and sensitivity to individual cases too; this trial alone does not justify general adoption.

If B suffices, prefer B. If A suffices, retain A. If C only improves broader questions, consider a bounded documentary supplement instead of replacing troubleshooting retrieval. Do not continue if C loses conditions or requires disproportionate manual repair, despite a good mean score. Corrections after unlocking define a new experiment, never a retroactive score improvement.

## 10. Deliverables and work order

1. Human review of sources/claims, coverage inventory and common passage manifest.
2. Annotated questions, development/evaluation groups and frozen measurement plan.
3. A/C adapters and local feasibility pilot; complete unselected configuration fields before locked measurement.
4. A/B/C retrieval results, A0 controls and necessary ablations; resource/error log.
5. Comparable answers only once the common renderer exists; concealed-arm review and exploratory Ragas.
6. Decision report with raw counts, limitations, maintenance cost and reasoned recommendation.

This document prepares the method. It does not claim that validated questions, adapters or an executable benchmark already exist.

## Technical sources consulted on 2026-10-19

- [LightRAG README](https://github.com/HKUDS/LightRAG/blob/main/README.md): model roles and retrieval modes.
- [Core programming](https://github.com/HKUDS/LightRAG/blob/main/docs/ProgramingWithCore.md): custom graphs, context-only mode, context limits and storage. Recheck these capabilities against the pinned version; context-only does not imply no LLM calls.
- [Historical multilingual ADR](../ADR-002-multilingual-retrieval.md): distinguish earlier results from the new trial.
- [Contract v0.2](../CLAIM-CONTRACT-V02.md) and [roadmap](../ROADMAP.md): provenance, conditions and publication limits.
