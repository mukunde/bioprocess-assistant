# Frozen section-only challenge: H01–H10

Executed on 24 October 2026 after ten separately recorded human decisions.
**One frozen candidate; no tuning, method change, query rewrite or repeat run.**
This is a prospective same-corpus challenge on reviewed pages 118–121. Known facts
and related C-series intents were disclosed before the run; this is not a blind,
unseen-section or statistically independent generalization benchmark.

## Method and preserved evidence

The [frozen package](../../experiments/cytiva/section-evaluation-v01/PROTOCOL.md)
selects the earlier ablation's section-only arm: six BM25 hits, original small
bilingual bridge, unchanged section overviews and atomic source dependencies,
2,048 serialized context tokens, no new vocabulary projection. Source status,
quotations, reservations and old experiments remain unchanged. No LLM, VLM,
embeddings, model downloads, paid API or database mutation was used. The frozen
Python/tokenizer environment and PYTHONHASHSEED=0 were verified.

Raw outputs are in the new ignored directory:
`data/experiments/cytiva/section-evaluation-v01/locked-run/`.
They retain the reservation, exact human-review snapshot, pre-run configuration,
all twenty unscored contexts with hits/timings/overviews/exclusions, metrics and
verification. Contexts were saved before reference scoring. There was one
measurement invocation; the frozen helper performs its declared three timing
repetitions per formulation without selecting the best repetition.

Separate `analysis-v01/` stores diagnostic full rankings, missing-source causes,
the exact eligible corpus, a summary, frozen code/input snapshots and artifact
hashes. Post-measurement ranking inspection did not change contexts or scores.
Preflight/postflight raw hashes confirm **1,222 earlier files unchanged**, including
prior experiments and review journals. Python network/DNS attempts were zero;
this guard is not an OS firewall. Artifact hashes establish consistency, not
independent scientific validation.

## Results

| Intent | EN required sources | FR required sources | Bilingual complete |
|---|---:|---:|---|
| H01 | 1/1 | 1/1 | Yes |
| H02 | 2/2 | 1/2 | No |
| H03 | 3/3 | 3/3 | Yes |
| H04 | 3/3 | 3/3 | Yes |
| H05 | 4/4 | 4/4 | Yes |
| H06 | 3/3 | 3/3 | Yes |
| H07 | 7/7 | 7/7 | Yes |
| H08 | 5/5 | 5/5 | Yes |
| H09 | 2/3 | 1/3 | No |
| H10 | 4/4 | 4/4 | Yes, context/eligibility only |

**8/10 bilingual intents complete; EN 9/10, FR 8/10, or 17/20 formulations.**
Mean per-formulation required-source coverage is 92.5%; that aggregate does not
remove the three incomplete formulations. The predeclared pilot gate is
`blocked_incomplete_evidence`; no adoption or default change follows this trial.
FR/EN are paired formulations, not twenty independent observations. These source
presence results are not answer correctness, diagnostic accuracy or precision.

Mean context: **1,578.65 tokens**; maximum: **2,000**, below the fixed 2,048 cap.
All twenty section overviews were included. Two whole bundles were excluded,
both on H04: EN E121-E would require 2,127 tokens; FR E119-I would require 2,203.
Neither is indispensable for H04; both exclusions remain logged. No quotation or
condition was truncated, and no required-source failure was a budget exclusion.

## Failure diagnosis, without correction

### H02 French — weak lexical match and cutoff

The general contaminant-characteristics paragraph **E118-C is ranked ninth**,
outside six hits. Its only matching indexed query term is `purification`.
The frozen original bridge does not align French `albumine`, `transferrine`,
`immunoglobulines` or `bovines` with those English source terms. E118-M is retrieved,
but the section overview reserves E119-A, not the missing general E118-C paragraph.
There is no budget rejection for this formulation. The explicit bovine phrase
rule also does not match the noncontiguous wording about host or bovine
immunoglobulins. This is measured lexical/cutoff and overview-coverage failure,
not missing or quarantined source data.

### H09 English — generic request lacks method-selection context

**E118-M is ranked twelfth**, below six hits. Its sole lexical overlap is the
incidental word `see`; this is not semantic evidence of relevance. The generic
unknown-contaminant overview requires a configured unknown marker and at least
two named methods. This query names no methods, so it does not trigger. Fallback
selects the albumin/transferrin section from a source hit instead of the needed
general selection passage. E118-USE and E118-C are present; E118-M is not.
No bundle was excluded for budget, although the actual context is already at
2,000 tokens. Increasing depth is not demonstrated here as a safe or sufficient
fix within the same cap.

### H09 French — no positive hits for two indispensable sources

**E118-M and E118-USE have no positive supporting lexical hit.** Only six sources
have positive scores, and their overlap is the generic `purification` token.
The original bridge does not translate the query's antibody, affinity or
uncertainty wording. No methods are named, so the general overview is not
triggered; fallback selects the bovine section. E118-C is present, while the
application/interference and general selection passages are missing. There is no
budget exclusion. A larger top-k alone cannot return zero-score sources under
this frozen search rule.

## Context noise and source-boundary limits

Nineteen of twenty contexts contain IDs outside the pre-annotated acceptable
context. This is a reference-dependent noise proxy, not a validated precision
score or proof those extra facts are false. H01 EN, for example, retrieves the
required E118-USE but also reserves bovine context and retains unrelated
procedural material: its complete context is 1,729 tokens. Completeness alone
therefore masks substantial irrelevant or unnecessary context. Fallback to the
first hit associated with a configured section deserves separate future study;
it has not been modified here.

**E118-I and E121-EQ remain excluded from index statistics and every context.**
H10 passes only the reviewed protocol-scope presence and leakage checks. Its
context also contains loading, washing and elution information, so this result
does not show that an answering model would correctly withhold equilibration
numbers or explain the review-status limit. Likewise H09 does not evaluate actual
clarification behaviour. The source-only serializer does not itself carry a
complete review-status inventory; a future serving adapter must preserve these
eligibility limits explicitly rather than infer authorization from retrieval.

## Operational checks and next decision

Same-process medians were 3.33 ms for retrieval and 29.88 ms for
assembly, using the frozen three-repetition helper. Initialization is saved
separately. This small local measurement is not a production latency guarantee;
it should not be compared causally with earlier timings on another process.

Recomputed metrics match the saved results. All twenty contexts pass exact
quote/provenance serialization, token, dependency, deduplication and quarantine
checks; diagnostic rankings reproduce every measured top-six prefix. The frozen
manifest and human decisions retain their original hashes. No candidate code or
reference was changed after results.

**Keep this failed gate and its artifacts as the baseline.** A later authorized
development variant may study general-context routing for underspecified queries,
lexical coverage or context noise, but it must retain this trial and use different
prospective questions for a fresh evaluation. Do not rerun H01–H10 and label a
post-fix score independent. A constrained end-to-end prototype can remain an
engineering experiment; this trial does not authorize adopting the candidate as
the default or claim scientifically validated advice.
