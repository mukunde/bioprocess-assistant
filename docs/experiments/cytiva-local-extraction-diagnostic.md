# Diagnostic of the first Cytiva extraction

Analysis of existing files, without a new extraction or changes to review decisions.

Run: `bioprocess-assistant-review/data/ingestion/a325aff86fd8-5bb7c2d10264`.
Original pages 97–99, pages 1–3 of the excerpt. Local Ministral 3B Q4 model, i5 CPU, 16 GB RAM.

## Results and causes

29 entities, no semantic relations. Native metadata reports `skeleton_path_counts = {"": 1, "entities[]": 29}`. No `relations[]` node exists at discovery time. `merge_orphans_dropped = 0`, with no truncation or failed discovery batch. The adapter does not filter relations: it takes those returned by the model. The 27 native edges are structural links, not domain relations.

The schema puts relations in a list of standalone models with five identity fields (types and names of both endpoints, and predicate). Dense discovery requests short identifiers copied from the document, prohibits filling properties and says relations will be handled later. Filling is then launched only for paths actually discovered; its subschemas remove child lists. This combination explains the structural blockage and provides a strong hypothesis for the model's omission, rather than proving a general limitation of Docling Graph.

The model extracted no Symptom/Cause despite explicit text in `#/texts/77` (fouling, blockage, increased back pressure, decreased flow rate) and `#/texts/78` (clean when back pressure increases). These passages are in the CIP chunk, so their absence from conversion is not the cause. Extracted objects are often mistyped: a buffer as Resin, distilled water as ProcessStep, molecular-weight markers as Resin. The Entity and Relation schemas have no classification docstrings; the discovery guide does not transmit type and predicate enums. The root docstring is truncated to 240 characters. Chunking preserves the CIP section, but local headings such as Lane replace product context; the start of the document is repeated as global context, potentially favouring the experimental example on page 97. This last influence remains untested.

## Citations: 13 cards, 29 failed occurrences, 26 distinct texts

The current check searches for a quotation within one Docling item or one table row/cell, tolerating whitespace differences only. This verifies location, not the meaning of an assertion.

- Six occurrences become exact within-item matches after removing tags alone. Example: `<text>(B) SDS-PAGE analysis</text>`. This diagnostic does not change results or approvals.
- Four more become exact substrings of a global concatenation after tag removal (Elution buffer and System, twice each). Concatenation is diagnostic only: accepting it as evidence could incorrectly connect different pages or columns.
- The remaining 19 occurrences have potentially combined causes: PDF control characters rendered as `[U+0003]`/`[U+0007]`, separate label and value, a serializer-added list marker, case changes, paraphrasing or omitted words.

Verified examples:

- `Column:` is `#/texts/4`, its value is `#/texts/6`; they are not one contiguous item, and `Sample:` intervenes in reading order.
- Sodium phosphate actually contains U+0003 in `#/texts/9`. Copying displayed text or its escaped representation no longer matches the raw text.
- `Pool eluted human MAb` differs from `Pool eluted purified human MAb` in `#/texts/48`.
- `backpressure` differs from `back pressure` in `#/texts/77`.
- One figure quotation removes `(SDS gel, lane 3)` before the final full stop.
- `<ldiv><marker>1.</marker></ldiv>LMW markers` contains a serializer-added list number; simply stripping tags retains `1.`, which does not exist in `#/texts/46`.

The 13 cards should therefore neither be labelled hallucinations nor accepted through approximate matching. The 16 cards without location errors still require semantic and condition review.

## Breakdown of 55 min 49 s

| Stage | Observed time |
|---|---:|
| Initialization before the native pipeline starts | ~1 min 39 s |
| Conversion and chunk preparation | ~46 s |
| Initial discovery, 4 batches | ~14 min 08 s |
| Coverage review, 1 batch | ~1 min 49 s |
| Filling, 30 sequential jobs | ~37 min 27 s |

Filling accounts for approximately 67% of total time. `dense_fill_nodes_cap=1` requires one call per node, plus the root. Logs show five discovery batches including coverage, followed by thirty filling jobs. Dense coverage is distinct from direct gleaning: `gleaning_enabled=false` does not disable it. Metadata shows neither truncation nor failed discovery batches.

Conversion is not the main bottleneck. One snapshot showed only 0.5 GiB of free RAM; memory pressure is plausible, but its contribution was not measured. No specific duration can be attributed to swapping or hardware gain promised. Per-call token counts and prompt/generation durations are missing, preventing separation of these costs.

## Proposed corrections, in priority order

1. **Evidence references instead of regenerated quotations.** Preserve raw `document.json` and its hashes. Produce a model-facing text view with item IDs, paragraphs/sentences and offset mappings back to raw content. Limit, document and log serialization-control cleanup. The model selects IDs and, where needed, segments; code reconstructs exact quotations and coordinates. Multi-item evidence keeps segments and their roles separate. Do not arbitrarily concatenate labels/values or cross table rows. A valid reference proves location only; human review remains mandatory.

2. **Extract facts and relations in the same small context.** Retain Docling conversion and HybridChunker structure. For this flat schema and small model, test direct extraction per bounded semantic subsection against node discovery followed by individual filling. Each output contains the symptom, explicitly cited cause/action, conditions and evidence references. An adapter assigns IDs and constructs canonical entities/relations. This requires section orchestration, not merely replacing `dense` with `direct` on the entire PDF. A 2048-token output budget may be insufficient for the whole document.

3. **Compact ontology and instructions.** Define every class and predicate in descriptions actually transmitted to the model. Exclude figures, instruments, markers and buffers from domain classes that do not describe them; do not add classes without a retrieval need. A target for manual verification is increased back pressure → cleaning, or symptom → fouling → cleaning where passages actually support those links. A cleaning instruction must not become a certain diagnosis. Explicitly decide whether a Symptom→Action relation is useful: the current schema does not allow it directly. Preserve figure/protocol condition differences, particularly pH 7.4 versus 7.2.

4. **Keep document-based/hierarchical chunking.** Attach parent product/section and relevant conditions to each chunk without repeating the entire opening figure. Keep warnings with associated steps, and tables with headers and spatial relationships. Detect product boundaries, particularly MabSelect SuRe LX at the end of the page. Calculate token limits for the entire request with output headroom, rather than text alone and a cl100k proxy. Do not blindly increase chunk size.

5. **Limit and measure calls.** Reuse immutable conversion; finish the conversion process before loading the extraction model to release OCR/layout weights. Cache by PDF hash + versions + conversion + schema + instructions + model + parameters. Limit call count, total time and tokens; report explicit errors and support resuming missing sections. Trace each call's total, loading, prompt and generation durations, tokens, throughput, section, attempt and validation. Distinguish zero local API fees from resource consumption. Initially retain one CPU worker.

6. **Minimal dense comparison if needed.** Test `dense_fill_nodes_cap=3`, scoped context and corrected descriptions on reduced input. With exactly the same 29 entities and one root, this gives 11 filling jobs instead of 30, approximately 16 total jobs if the five discovery batches remain unchanged. This is job arithmetic, not a duration prediction: outputs will be longer, contexts may grow and truncation must be checked. It does not alone fix relation discovery. Avoid LLM deduplication and parallelism as first optimizations on this PC.

## Validation protocol before another full extraction

Start with the two CIP paragraphs on original page 99, reusing existing conversion. Establish a small human reference with every expected fact/relation and its exact evidence. Automatically prepared proposals remain unvalidated until confirmed by the reader.

Compare the current mode, compact dense mode and structured direct extraction by section using the same model, context and reference. Instrument every call and set an explicit budget, such as at most three calls and ten minutes for this micro-test, stopping on overrun. Check relation precision/recall, types, directions, conditions, irrelevant entities, resolved-reference rate, tokens and duration. All evidence for approval candidates must be located; speed gains cannot compensate for lost fidelity. An LLM-as-a-judge/RAGAS can supplement checks but is not this extraction's ground truth.

Only then compare all three pages, including figures, buffers and conflicting conditions. No duration gain has yet been measured for these proposals; no guaranteed reduction to a specific number of minutes can be claimed.

## Verified sources

- Local sources: `ingestion/schema.py`, `ingestion/pipeline.py`, `ingestion/evidence.py`, `extraction.json`, `document.json`, `provenance.json`, native metadata and `tmp/cytiva-first-extraction.log`.
- Installed dependency code, pinned revision: `docling_graph/core/extractors/contracts/dense/{catalog,prompts,orchestrator}.py` and `docling_graph/config.py`.
- Official documentation for general context; the installed version takes precedence: [dense extraction](https://github.com/docling-project/docling-graph/blob/main/docs/fundamentals/extraction-process/dense-extraction.md) and [configuration](https://github.com/docling-project/docling-graph/blob/main/docs/reference/config.md).
