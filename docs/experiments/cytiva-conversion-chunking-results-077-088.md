# Cytiva 77 and 88: first conversion and chunking comparison

Date: 2026-10-21. **Historical technical diagnostic; these converted outputs were not human-approved.** The test follows the [protocol](cytiva-conversion-chunking-protocol.md) on two separate blocks. The assistant transcribed the reference from renderings before conversion and froze it locally; that preparation was not a human decision. Other pages and K600/K1400 were not executed.

The later [page-88 human review](cytiva-page-088-human-review.md) approved a
separate deterministic reconstruction with reservations. It does not approve
these original conversions, the page-77 diagnostic or graph publication.

On 2026-10-22, the separate [page-77 human review](cytiva-page-077-human-review.md)
completed ten validations with reservations for the exact T1 table, adjacent
remarks and observed K800 conservation. It does not approve T0, generalize to
other conversions or validate production retrieval. In particular, a condition
and its potassium-isothiocyanate precaution remain in separate chunks.

## Conclusion

Enabling TableFormer substantially improves structure. **T1 is not globally validated**, however: the “Available formats” row on page 88 is incorrectly grouped into one product cell. The table remains quarantined. At 800 tokens, no additional loss of converted cells or targeted notes was observed on these two pages; this does not repair incorrect conversion.

## Conditions and traceability

- Source: SHA-256 `a6fd949e904ec0bafbcc7d85a3be1660f2bea8949098e86c57ae43d06492946a`, 183 pages. Independent excerpts of 77 and 88; local page 1 maps to the original page in each source map.
- Docling 2.140.0, docling-core 2.101.1, Docling Graph 1.9.1 at the project-pinned commit, tiktoken 0.12.0, pypdf 6.21.1; local Heron layout and TableFormer V1 `accurate` weights, cell matching enabled for T1. CPU, four threads, OCR disabled, images preserved at scale 2.
- T0: structure recognition disabled; T1: enabled. All other profile settings match. Each conversion uses a separate process, counting startup/imports.
- K0: full DocLang; K800: native HybridChunker through Docling Graph, tiktoken `cl100k_base`, `merge_peers=True`, DocLang without geometry in text. Same frozen T1 JSON for diagnosis.
- No LLM extractor, paid API or Neo4j database was called. No downloads: caches checked; zero network attempts in worker logs under a Python guard. This mechanism is not a firewall for native code.

Full local ignored artifacts under `data/experiments/cytiva/visual-validation-v01/`: `reference-20261021/`, `convert-20261021-a/`, `chunks-20261021-a/`, `conversion-checks-20261021.json`, `chunk-checks-20261021.json`, `review-20261021.csv` and versioned conversion reviews. This report does not distribute PDFs, renderings, full cells or outputs.

## Conversion observations

| Check | T0 | T1 |
|---|---|---|
| Page 77, table 3.5 | One cell containing flattened text | 17 rows including the header, 4 columns |
| Page 88, table 3.6 | One cell containing flattened text | 8 rows including the header, 5 columns |
| Both table captions/titles | Present | Present and references resolved |
| Targeted cells, units and notes | Text sometimes present, insufficient structure | Substantial gain, with reservations below |

**Page 77:** 48 fields compared across 16 data rows: 16 subclasses and 32 pH fields. Against the initial authored reference, 46 matched after declared subclass-whitespace normalization and two differed in `n.a.` punctuation. **Source recheck on 2026-10-22:** the PDF itself prints `n.a` without a final stop for Goat IgG2 and the second Guinea pig row. Conversion preserves those spellings; the two discrepancies are errors in the initial reference, not lost punctuation in conversion. The frozen reference and comparison remain unchanged as historical evidence. No numeric value or operator changes were observed in these fields. The 10 empty species cells in continuation rows remain empty: the format supplies no explicit scope relation to each subclass. Do not automatically forward-fill every blank without a reviewed documentary rule. Remarks on the right remain separate text, including the reservation about free protein and coupled material.

**Page 88:** the 12 targeted checks of four capacities with note markers, four velocities and four particle sizes match. All five notes are present and linked to the table by references. CIP reagents for the two families remain distinct in checked cells. However, the last row concatenates all four format texts into the first product's cell and leaves the next three empty: **F01, blocking column-association defect**, found by inspection beyond the initial probes. Cell-box overlays on the rendering confirm the incorrect grouping.

An initial diagnostic note suspected a replacement character in note 4's temperature unit because of console display. UTF-8 and code-point inspection confirms that degree sign U+00B0 is intact. The suspicion is withdrawn in `conversion-review-20261021-v2.json`, retaining a link to the initial version. It does not count as a conversion error.

## Chunking observations

| Measure | Page 77 | Page 88 |
|---|---:|---:|
| K0, full DocLang tokens | 1,469 | 1,003 |
| K800, final chunks | 2 | 2 |
| Total contextualized-chunk tokens | 1,174 | 808 |
| Maximum per chunk | 760 | 793 |
| Secondary text splits | 0 | 0 |
| Table 3.6 notes in its chunk | Not applicable | 5 of 5 |

All 58 converted nonempty cells on page 77 and all 35 on page 88 occur in the chunk containing their table. **This measures conversion preservation, not PDF fidelity:** F01 persists in K0 and K800. Page 77 retains its first applicability reservation in the same chunk as the table. Headers and targeted conditions are present; the two blocks are never merged.

All checked item_refs resolve; page maps and conversion hashes match. All 10 chunk geometry entries for 77 and 8 for 88 resolve to boxes within page dimensions. Cell overlays were inspected. Native text fingerprints use 8-byte BLAKE2b; file identity is tracked separately with SHA-256.

Token differences between K0 and chunks include different serialization/contextualization; they are neither compression rates nor, alone, omission measures. The audit compares cells and notes. Secondary splitting was not exercised; its safety on larger tables remains undemonstrated.

## Time and resources

| Block/profile | Full worker time | Imports/preparation | Conversion, including deferred model loading |
|---|---:|---:|---:|
| 77/T0 | 123.0 s | 89.6 s | 30.6 s |
| 77/T1 | 79.2 s | 48.6 s | 27.9 s |
| 88/T0 | 51.1 s | 36.3 s | 12.8 s |
| 88/T1 | 52.0 s | 32.3 s | 17.5 s |

Total for four conversion workers: **305.3 s**. Sampled process/child peak memory: approximately **1.15 decimal GB**. These initial passes, with evolving system caches and image export, are not a controlled TableFormer overhead measurement: the faster 77/T1 run does not establish that TableFormer accelerates conversion.

Chunking: approximately 79.4 s and 52.3 s including imports; actual processing of both passes (raw chunks and native path) took 0.086 s and 0.040 s. Startup dominates. No API cost. These times **cannot be directly compared to the earlier 56-minute LLM extraction**, which included other processing and calls.

## Historical decisions and next experiment (2026-10-21)

- 11 targeted probes technically examined: 10 satisfied on T1/K800, one ambiguous species-scope probe (V01). The other 21 probes remain unexecuted. F01 is an additional defect outside these 11 probes; their score cannot approve the table.
- No result is a user decision. The local grid remains `pending_user_review`; the versioned CSV template retains its initial pending values.
- Retain 800 as an experimental starting point for these two pages; there is no measured reason to change the global budget yet.
- Next compare cell matching enabled/disabled on page 88 in a **new** run: PDF-cell matching might cause the grouping, but this remains a hypothesis. Do not alter T1 or its outputs.
- Before extracting facts affected by F01, repair and review the row or explicitly retain quarantine. No automatic filling of the three empty cells.
- Handle species grouping and scope separately. Continue with 104 and 152–153; K600/K1400 and secondary splitting belong to a distinct slice. This table trial does not validate figures or their visual relations.

## Runner verification

Six model-free safety tests cover preserved outputs, separate noncontiguous blocks, rejection of uninspected reviews or changed hashes, no implicit human approval, DNS blocking before network access and rejection of another manual before model loading. The main suite with local application/PDF dependencies passed **112 tests**, mocking external models/APIs and using local-only review HTTP servers. Application and ingestion environments are isolated; the complete check reuses installed dependencies and installs no packages.

## Subsequent cell-matching ablation

The [separate page-88 comparison](cytiva-cell-matching-ablation-088.md) is complete.
Disabling matching does not repair F01 and moves the first velocity value into
the row label. The enabled default is retained and both Docling versions of
table 3.6 remain quarantined.
This follow-up preserves the original measurements and artifacts above.
