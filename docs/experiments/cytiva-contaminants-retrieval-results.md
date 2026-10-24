# Cytiva C01-C10: first top-five/top-six retrieval comparison

Executed on 24 October 2026. **New-section development measurement; no generated
answers or human validation of benchmark results.** The original review package,
source preparation and all earlier experiments remain unchanged.

## Adapter and frozen method

The [adapter](../../experiments/cytiva/contaminant_retrieval.py) verifies the
[reviewed reference package](../../experiments/cytiva/reviewed-contaminant-questions/README.md)
before loading the cached tokenizer or measuring anything. It binds each result
to the verified review decision and separately retains the original preparation
status. The source-only runtime interface accepts query text, index and budgets;
it receives no question ID, expected answer or required-evidence set.

Both arms use the same 27 source records, index, BM25 k1=1.2/b=0.75, existing FR/EN
vocabulary bridge, transitive source dependencies and **2048-token serialized
context limit**. Only the lexical result limit changes from five to six. The
source policy was declared before this first measurement and has not been tuned
after seeing the results. No new translation, stemming, reranker or vocabulary
alias was introduced.

This adapter uses the generic atomic assembler on the new page-118/121 topology.
It does not apply the cleaning-specific pressure/flow expansion from pages
166–167. It tests transfer of the shared retrieval/context method and result
depth, rather than claiming unchanged reuse of every cleaning-specific policy.

### Pending passages remain excluded

`E118-I` and `E121-EQ` remain **pending individual validation**. A runtime copy of
the verified source policy marks them ineligible and removes them from searchable
seeds. Original evidence, annotations and review flags are never overwritten or
promoted. Their quotations remain only in the frozen corpus for provenance;
neither their text nor their terms enter the BM25 index or assembled contexts.
Any child depending on a pending passage is also ineligible.

There are **25 eligible source records and 18 searchable seeds**. Headers and
footnotes are included through source dependencies. Both arms preserve complete
quotations, applicability warnings, cross-page scope and the loading footnote.

## Results

| Metric | Five results | Six results |
|---|---:|---:|
| Questions complete in both languages | 5/10 | 6/10 |
| English formulations complete | 6/10 | 6/10 |
| French formulations complete | 6/10 | 7/10 |
| Mean required-source coverage, all formulations | 85.42% | 87.08% |
| Mean serialized context | 1372.20 tokens | 1616.45 tokens |
| Maximum serialized context | 1673 tokens | 1968 tokens |
| Excluded bundles due to budget | 0 | 0 |
| Pending-source leakage | 0 | 0 |

All 20 formulations receive additional context with six results, averaging
**244.25 extra tokens** (about 17.8%). There is no coverage regression in the
paired run. More complete source presence is not a measured precision gain or
proof of safer/more faithful answers.

| Question | Five results, EN / FR | Six results, EN / FR | Missing with six |
|---|---|---|---|
| C01 | Complete / incomplete | Complete / complete | None; FR restores E119-BI at rank 6 |
| C02 | Complete / complete | Complete / complete | None |
| C03 | Incomplete / incomplete | Incomplete / incomplete | E119-A in both languages |
| C04 | Incomplete / incomplete | Incomplete / incomplete | E119-A in both languages |
| C05 | Incomplete / incomplete | Incomplete / incomplete | EN: E118-C, E120-H, E120-U, E120-W; FR: E118-C, E118-USE, E120-U |
| C06 | Incomplete / complete | Incomplete / complete | EN: E120-A |
| C07 | Complete / complete | Complete / complete | None |
| C08 | Complete / complete | Complete / complete | None |
| C09 | Complete / complete | Complete / complete | None |
| C10 | Complete / complete | Complete / complete | None |

### Failure analysis retained from the first run

- **C03/C04:** the required introductory passage E119-A ranks 8th/14th in English.
  In French it has no positively scored supporting seed. The existing vocabulary
  bridge does not map `albumine`/`transferrine` to `albumin`/`transferrin`, and this
  source paragraph spells out the techniques rather than including IEX/HIC
  abbreviations. The specific advice passages do not automatically include that
  introductory paragraph through their current source dependencies.
- **C05:** broad clarification evidence is dispersed across the general guidance
  and Blue-product applicability. E118-C ranks 12th in English and has no positive
  supporting hit in French; E120-U ranks 16th/14th. The earliest English supporting
  bundle for the Blue scope/warning is 7th, outside both cutoffs. French E118-USE
  ranks 8th. The current lexical method does not assemble the whole clarification
  context from this broad question.
- **C06 EN:** E120-A ranks 7th. The indication and warning can be present without
  all source records in the reviewed reference set. Keep the recorded reference
  failure; do not weaken the approved source set or infer a successful answer.

These misses are caused by lexical matching/ranking and the frozen source
dependency policy, not budget truncation or leakage from pending sources. No
question-ID exception, retrospective reference change or score adjustment was
made. The raw ordered rankings and per-missing-source supporting-seed diagnostics
are saved with every result.

## Verification and operations

The new ignored run is:

`data/experiments/cytiva/contaminants-pilot-v01/runs/lexical-depth-20261024-a/`

It contains a pre-measurement manifest, exact code/config/input snapshots, the
frozen corpus/index inventory, full rankings, ordered contexts, results, metrics,
final manifest and `verification.json`. Existing output directories are refused.
Recorded review/preparation benchmark flags remain historical; only this new
run's final manifest records the executed benchmark.

Verified all **40 paired contexts and 20 ranking prefixes**, exact serialized
quotations/provenance, dependency closure, source uniqueness, actual token counts
and zero pending-source leakage. Recomputed metrics match. Twenty frozen
code/input hashes and **350 pre-existing tracked files, journal files and run
artifacts** remain unchanged. Source PDF, raw pages, images and runtime assets
remain outside this change.

Python networking was guarded; zero connection/DNS attempts were recorded. No
LLM/VLM, embeddings, paid API, model download or database mutation was used.
Median assembly took 3.62 ms with five results versus 5.01 ms with six; retrieval
medians were 0.60/0.57 ms. Three same-process repetitions, alternating arm order,
exclude initialization and are not a production-latency benchmark.

[Adapter regressions](../../tests/test_contaminant_retrieval.py) cover pending
source exclusion, indirect dependency blocking, exact context/budget checks,
paired-grid integrity, reviewed-input binding before tokenizer loading,
snapshot integrity and refusal to overwrite a run.
All **11 adapter regressions and 336 main-suite tests pass** with the existing
local dependency environments; no packages were installed.

```powershell
.\.venv-ingestion\Scripts\python.exe -m unittest tests.test_contaminant_retrieval -v
.\.venv-ingestion\Scripts\python.exe -m experiments.cytiva.contaminant_retrieval --output data/experiments/cytiva/contaminants-pilot-v01/runs/lexical-depth-new
```

## Decision and next experiment

Six results offer a small recall improvement here at a measurable context cost;
they do not establish a generally sufficient cutoff. Retain this first run and
the four remaining incomplete intents. The references were prepared before
measurement, but their author knows the method; this is a prospective new-section
development probe, not an independently blind benchmark.

A separate next variant could compare a declared bilingual lexical bridge and
source-section introductory context, frozen before measuring. Broad clarification
queries deserve their own coverage checks. Any new tuning should retain this
baseline and be checked on additional questions. Neither change is implemented
in this run. E118-I/E121-EQ remain pending and unavailable until separately
reviewed; source coverage does not validate an answer, refusal, clarification or
scientific applicability.
