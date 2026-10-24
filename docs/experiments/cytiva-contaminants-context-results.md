# Cytiva C03-C06: vocabulary and section-context ablation

Executed on 24 October 2026. **Development tuning after inspecting known
failures; not an independent or blind benchmark.** Run A and its code/report
remain unchanged. No answer is generated or evaluated.

## Why the earlier retrieval failed

The [first run](cytiva-contaminants-retrieval-results.md) had six of ten intents
complete in both languages with six hits. The remaining problems were:

| Intent | Observed cause in run A |
|---|---|
| C03 | E119-A ranks 8th in EN and has no positive supporting hit in FR. French contaminant names and the IEX abbreviation do not match the English introduction's full terminology. |
| C04 | E119-A ranks 14th in EN and has no positive supporting hit in FR. Related HIC/Blue advice is retrieved without the section introduction. |
| C05 | General guidance, contaminant context and Blue applicability are dispersed. E118-C ranks 12th in EN and has no positive FR hit; E120-U ranks 16th/14th. French E118-USE is 8th. |
| C06 | E120-A is 7th in EN: retrieved use/warning passages do not automatically retain the introductory product/mechanism paragraph. |

No missing source was due to a token-budget exclusion in run A. The human-reviewed
reference sets were kept intact; required background was not removed to improve
the score.

## Frozen four-arm method

This variant depends on the C01-C10 adapter and its tests from the preceding
adapter lot. It adds the vocabulary/section helper, configuration, ablation
runner and regressions; it does not replace the original adapter or source policy.

All arms use six hits, the same source corpus and BM25 parameters, and the same
2048-token serialized-context limit. The
[new configuration](../../experiments/cytiva/contaminant_context_v02.json) and
[runner](../../experiments/cytiva/contaminant_context_retrieval.py) were frozen
before this first measured ablation. The
[lexical/section helper](../../ingestion/lexical_section_context.py) receives
source passages, query text and declared navigation rules, never reference IDs
from the question set or expected answers.

| Arm | Search vocabulary | Context assembly |
|---|---|---|
| Baseline | Existing bridge | Existing atomic source dependencies |
| Vocabulary | New declared lexical view | Existing atomic source dependencies |
| Section | Existing bridge | Atomic source-section overviews plus existing dependencies |
| Combined | New declared lexical view | Atomic source-section overviews plus existing dependencies |

The new vocabulary maps declared terms and phrases on **both source-index text
and queries**: albumine/albumin, transferrine/transferrin, anticorps/antibody,
related plural forms, and IEX/HIC/SEC with their full technique names. Whole-word
phrase matching avoids arbitrary abbreviation-prefix matches. There is no
translation model, general stemmer, synonym generation or automatic dictionary
tuning. Original source quotes/hashes are retained separately and never rewritten
with the lexical projection. The old vocabulary/module remain unchanged.

The section policy uses source headings and explicit topic/product names. It
reserves the albumin/transferrin introduction, the Blue-product introduction or
the bovine-immunoglobulin introduction as applicable. If no topic is explicit,
it falls back to the highest-ranked source section. Queries with an unknown
contaminant and multiple named techniques also receive general guidance; Blue
conditions are reserved only if that product section is explicitly named.
This is context navigation, not a diagnosis or an answer-status decision.

Overviews are reserved atomically before fitting complete ranked bundles.
Quarantined or over-budget overviews are reported unavailable rather than
partially inserted. Remaining procedural bundles keep their own scope, warning
and footnote dependencies. Source navigation rules are assistant-prepared
experimental policy, not new human approval of source topology or scientific
applicability.

**E118-I and E121-EQ remain pending and unavailable in all four arms.** They
enter neither lexical index statistics nor source contexts. Original preparation
and human decisions remain unchanged.

## Results on all ten reviewed intents

| Metric | Baseline | Vocabulary | Section | Combined |
|---|---:|---:|---:|---:|
| Complete in both languages | 6/10 | 7/10 | 10/10 | 10/10 |
| EN complete | 6/10 | 7/10 | 10/10 | 10/10 |
| FR complete | 7/10 | 8/10 | 10/10 | 10/10 |
| Mean required-source coverage | 87.08% | 90.42% | 100% | 100% |
| Mean context tokens | 1616.45 | 1592.40 | 1725.70 | 1705.35 |
| Maximum context tokens | 1968 | 1834 | 2027 | 2027 |
| Excluded whole bundles | 0 | 0 | 3 | 2 |
| Unavailable overviews | 0 | 0 | 0 | 0 |
| Coverage regressions against baseline | 0 | 0 | 0 | 0 |

Both new factors together restore all required passages for C03-C06 in both
languages. The ablation shows that **section context accounts for most of the
observed improvement**: vocabulary alone fixes C03 but leaves C04/C05 incomplete
in both languages and C06 incomplete in English. Section context alone also
reaches full reference coverage. Other intents retain their required sources.

Compared with baseline, section-only adds 109.25 tokens on average and combined
adds 88.90. Combined therefore has 20.35 fewer tokens on average than
section-only, with the same measured reference coverage. This does not establish
better precision, answer quality or safety. The whole eligible corpus would take
3867 serialized tokens, so these contexts do not simply include every source.

### Budget exclusions retained in the results

- Section-only, C04 EN: E121-B excluded (2064 candidate tokens).
- Section-only, C05 FR: E121-L and E121-W excluded (2319 and 2177 candidate tokens).
- Combined, C04 EN: E118-C excluded (2064 candidate tokens).
- Combined, C05 FR: E121-W excluded (2117 candidate tokens).

These are whole-bundle omissions, not truncated quotations. None is required by
the reviewed reference set for that intent; all omissions remain logged and
`budget_complete` remains false for the affected contexts. Full reference
coverage is not a claim that every retrieved passage was retained. The maximum
actual context stays at 2027 tokens; the 2048 limit does not include a future
answer prompt or generated tokens.

## Preservation, checks and reproduction

New ignored run:

`data/experiments/cytiva/contaminants-pilot-v01/runs/vocabulary-section-20261024-b/`

The run contains a pre-measurement manifest, exact code/config/input snapshots,
source corpus, both lexical-index term inventories, full rankings, ordered
contexts, metrics, exclusions, final manifest and `verification.json`. The same
query/index is used in each context-only pair; assembly does not rerank sources.
Current reviewed decisions are recorded separately from historical pending
preparation flags.

Verified all **80 contexts**, 40 same-ranking section pairs, exact quote and
provenance serialization, atomic dependencies/overviews, token counts and zero
pending-source leakage. The 20 baseline contexts reproduce run A byte-for-byte,
with identical ordered hits and scores within 1e-12 floating-point summation
tolerance. Recomputed metrics match. All 377 earlier tracked/journal/run files,
plus the separately fingerprinted prior adapter/report and run-A files, remain
unchanged. No prior output was overwritten and no method was retuned after run B.

Python networking was guarded, with zero connection/DNS attempts. No LLM/VLM,
embeddings, API, model download or database mutation was used. Same-process
median retrieval/assembly times were 0.84/6.40 ms for baseline, 1.12/5.84 ms for
vocabulary, 0.79/8.71 ms for section and 1.04/9.74 ms for combined. Three repetitions
and rotated arm order exclude initialization; these are not production latency
guarantees or directly comparable with older-run timings.

[Regressions](../../tests/test_contaminant_context.py) cover lexical phrase
equivalence and boundaries, source quote separation, source-section routing,
unknown-contaminant scope, atomic budget rejection, pending-source blocking,
paired-grid checks, reference verification and snapshot integrity.
All 15 new regressions and all 351 main-suite tests pass using existing local
dependency environments; no package installation was required.

```powershell
.\.venv-ingestion\Scripts\python.exe -m unittest tests.test_contaminant_context -v
.\.venv-ingestion\Scripts\python.exe -m experiments.cytiva.contaminant_context_retrieval --output data/experiments/cytiva/contaminants-pilot-v01/runs/vocabulary-section-new
```

This fresh-checkout command measures all four arms without needing the ignored
historical artifacts. When run A is available locally, append
`--baseline-run data/experiments/cytiva/contaminants-pilot-v01/runs/lexical-depth-20261024-a`
to check exact reproduction against that saved run too. Alternatively, create a
fresh baseline with the preceding adapter and pass its directory. An existing
output target is always refused; the historical run-A path is not recreated or
overwritten by this command.

## Practical assessment

Retain section-only as the simpler context candidate and combined as an
alternative with slightly lower average context size here. The dictionary alone
is insufficient for the observed missing-introduction and clarification cases.
Do not replace the existing default based solely on 10/10 on questions used to
design these changes. Check source-selection noise and applicability on separately
prepared questions and additional sections before choosing a default. No actual
answer, numeric refusal, clarification behaviour or scientific correctness has
been tested. The two pending passages remain outside retrieval until separately
reviewed.
