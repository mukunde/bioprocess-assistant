# Cytiva N05: retrieval cutoff diagnosis and top-six candidate

Executed on 23 October 2026. **Offline development experiment; no answer generation or production default change.**

## Diagnosis

N05 asks whether the 100–500 mM sodium hydroxide sequence for MabSelect SuRe LX
can be treated as the Protein G Sepharose cleaning procedure. Both reviewed
language formulations require seven source excerpts, including the distinct
Protein A/G precipitated/denatured-protein block on page 166.

The full BM25 ranking has the same source order in English and French:

| Rank | Source excerpt | Role |
|---|---|---|
| 1 | E167-S | SuRe/SuRe LX stronger-alkali sequence |
| 2 | E167-P | MabSelect precipitated/denatured-substance alternatives |
| 3 | E166-T | General Protein A/G cleaning indication |
| 4 | E166-D | Protein A/G detergent example |
| 5 | E166-W | Protein A/G solvent warning |
| 6 | E166-P | Protein A/G guanidine/binding-buffer sequence |

The existing limit is five lexical hits. E166-P therefore never reaches the
assembler, although it is eligible and its complete bundle would fit. Its
parent heading E166-PH is included only through the source dependency
`E166-P → E166-PH → E166-H`; that heading is consequently absent too.

This is a lexical ranking/cutoff failure, not an absent source, quarantine,
conversion loss or budget rejection. Procedure-specific sodium hydroxide and
SuRe LX terms favour the MabSelect sources. The page-166 guanidine block has
little matching procedural vocabulary, while other shorter page-166 bundles
match inherited product headings and general cleaning terms. The existing
section policy does not trigger because N05 has no pressure/flow/threshold term.

Required source content remains separate:

- **E166-PH:** “To remove precipitated or denatured proteins:”
- **E166-P:** “1. Wash the medium with 2 column volumes of 6 M guanidine hydrochloride.
  2. Immediately wash with at least 5 column volumes of binding buffer.”
- E167-S retains its own SuRe/SuRe LX applicability heading, sequence, quantities
  and contact time. Retrieval of both blocks establishes neither equivalence nor
  a general prohibition; no conditions are transferred between them.

Exact source strings, including line breaks, hashes and page offsets, remain in
the unchanged reviewed evidence and the new run's corpus/context snapshots.

## Proposed correction and alternatives

Use the opt-in [v05 configuration](../../experiments/cytiva/cleaning_source_context_v05.json)
with **six hits**, keeping the same BM25 index, vocabulary bridge, source
topology, section policy and **2048-token serialized-context limit**. The
[paired launcher](../../experiments/cytiva/retrieval_depth.py) checks that
retrieval depth is the only methodological difference. No question-ID exception,
gold-reference expansion, inferred fact or truncated quotation is added.

The v03 default and earlier launchers/configurations remain unchanged. This is
a pilot-specific candidate, not a universal claim that six hits suffice.

An exploratory explicit-family/category counterpart policy was also tested in
run E. It recovers N05 and changes fewer contexts, but needs an additional
manually curated category mapping with pending human review. Its complete code,
configuration, tests and results remain frozen in that run's input snapshots;
it is not added to the maintained runtime. The simpler top-six candidate is
preferred at this stage because it achieves the same evidence coverage without
another source-navigation maintenance task. Category-aware diversification or
a local reranker remain alternatives if broader testing exposes noise or new
cutoff failures. Neither alternative was validated on independent material here.

## Paired results: new run F

| Reviewed reference set | v03 top five | v05 top six | Maximum context, five → six |
|---|---:|---:|---:|
| Q01–Q10, complete in both languages | 10/10 | 10/10 | 1618 → 1654 tokens |
| N01–N08, complete in both languages | 7/8 | 8/8 | 1604 → 1604 tokens |

For **N05 EN and FR**, required evidence presence rises from **5/7 to 7/7**.
The original five hits keep exactly the same order and scores within the paired
run; the added sixth hit is E166-P. Atomic dependency assembly restores E166-PH.
N05 context grows from **1322 to 1552 tokens**, with no excluded bundle.

The change is not free of context overhead: 14/20 Q formulations and 14/16 N
formulations receive a changed context. Mean added context is 164.75 tokens for
Q and 177.94 for N; the largest increases are 515 and 344 respectively. Extra
source presence is not evidence of improved precision or final answer quality.

No evidence-coverage regressions or budget exclusions occur in this sample.
All 72 paired contexts preserve exact quotations, metadata, product scopes,
dependency closure and unique source IDs. All remain below 2048 tokens.
Assembly medians on the same process rise from 3.48 to 4.57 ms for Q and 3.67 to
4.40 ms for N. Three repetitions on this small development corpus exclude
initialization; these are not production latency guarantees.

## Preservation and checks

Earlier runs A–D, inputs and reviews remain unchanged; 125 pre-existing file
fingerprints were checked. Run F also records and verifies every pre-existing
run file, including exploratory run E. The 36 v03 baseline contexts reproduce
run D byte-for-byte, with identical ordered hits. Historical floating-point
scores differ only in last-bit summation order and compare within 1e-12.

New runs use fresh output directories and refuse an existing target before
network guarding or tokenizer loading. Both reviewed reference packages are
verified; code/config/source/review snapshots and hashes are saved before
measurement. Token counting uses the validated local cl100k cache under the
Python network guard. **Zero LLM/API calls and zero network attempts.**

[Ten new regressions](../../tests/test_retrieval_depth.py) cover bilingual N05
recovery, the unchanged index/configuration, quarantine, atomic budget refusal,
exact provenance/dependency preservation, no-match queries, paired-grid checks,
reference preflight, snapshots and refusal to overwrite earlier output.
All 55 focused retrieval tests and all 311 tests in the main suite pass. The
main suite uses the existing application integration environment with the local
ingestion dependencies added to its import path; no packages were installed.

Local ignored artifacts:

- `data/experiments/cytiva/retrieval-pilot-v01/runs/cross-family-context-20261023-e/`
- `data/experiments/cytiva/retrieval-pilot-v01/runs/retrieval-depth-20261023-f/`

Run F contains `manifest-before-run.json`, input snapshots, corpus, full diagnostic
rankings, exact contexts, results, metrics, final manifest and `verification.json`.
No source PDF, model weights or raw experiment directories are proposed for Git.

```powershell
.\.venv-ingestion\Scripts\python.exe -m unittest tests.test_retrieval_depth tests.test_section_context tests.test_local_passage_retrieval -v
.\.venv-ingestion\Scripts\python.exe -m experiments.cytiva.retrieval_depth --output data/experiments/cytiva/retrieval-pilot-v01/runs/retrieval-depth-new
```

## Limits and next decision

The correction was chosen **after inspecting N05**, on the same 17 curated
source excerpts and 18 known bilingual development intents. This is not an
independent or whole-manual benchmark. Human documentary approval of references
does not validate these measured retrieval results, scientific applicability,
answer/refusal quality or publication. No answer was generated or scored.

Retain v05 as the simple candidate for human review. Before integrating it into
the assistant, test broader source sections and independently prepared comparison
questions, including cases where the missing source ranks below sixth place.
Track context noise, product mixing, budget exclusions and final response
faithfulness separately; complete reference presence alone cannot certify them.
