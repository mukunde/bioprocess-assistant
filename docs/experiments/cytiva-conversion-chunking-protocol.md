# Cytiva: validating tables, captions, diagrams and chunking

Date: 2026-10-21; status updated 2026-10-22. **Initial T0/T1 and K0/K800 trials executed on 77 and 88.** See the [first trial report](cytiva-conversion-chunking-results-077-088.md). Later documentary reviews approved the exact [page-77 T1 result with reservations](cytiva-page-077-human-review.md) and the separate [page-88 deterministic reconstruction with reservations](cytiva-page-088-human-review.md); they do not approve the defective original page-88 conversion or production retrieval. The [page-104 figure/caption trial](cytiva-figure-104-results.md) has now executed T0/T1 and K0/K800: the image and text are preserved, but diagram semantics remain quarantined for text-only use. Its [six-card human documentary review](cytiva-page-104-human-review.md) is complete with reservations. Other selected pages and K600/K1400 remain untested. No LLM/API calls, Neo4j publication or changes to the r2 package.

## 1. Objective and limitations

Determine what the converter preserves from the PDF, then what the chunker preserves from that conversion. Separate both error sources from LLM extraction errors. This phase does not run `ingestion extract`: that command also triggers semantic extraction, which is unnecessary for this diagnostic.

The r2 trial disabled `do_table_structure` and OCR. It validates neither tables nor illustration interpretation. Its profile remains frozen. The local Docling Graph pipeline has its own conversion path; do not automatically attribute r2 settings to it.

All selected pages are **development** data. Inspection and subsequent tuning prevent presenting them as an independent test. This protocol demonstrates neither industrial suitability nor scientific validity of recommendations. Selected tables concern properties, conditions and products, not a complete symptom/cause/action matrix.

## 2. Source and selection

Local manual: `cytiva_affinity-chromatography-antibodies_hplc_technical-support.pdf`, 183 PDF pages, SHA-256 `a6fd949e904ec0bafbcc7d85a3be1660f2bea8949098e86c57ae43d06492946a`. Reference/version copied from the r2 registry: `CY13981-25Jan21-HB`, `25Jan21`. These are previously recorded documentary metadata, not renewed certification of the edition.

Numbers below are **1-based PDF pages**. Visible printed numbers match on all eight selected pages. Subtract 1 for a zero-based API; retain both fields in the manifest. The structured selection is in [cytiva-visual-validation-selection.json](cytiva-visual-validation-selection.json).

| Batch | PDF / printed pages | Visually checked content | Target difficulty |
|---|---|---|---|
| Initial trial | 77 | Table 3.5 and remarks on the right | Inherited species/subclass, pH ranges, `≤`, `≥`, `Approx.`, `n.a.`, exception and applicability limits |
| Initial trial | 88 | Table 3.6 and five notes | Four adjacent products, units, distinct experimental conditions and superscript references |
| Initial trial | 104 | Figure 3.29 and text on the left | Five fragment → chain subtype → product paths; an alternative distinct from the recommended product |
| Initial trial | 152–153 together | Table A1.7 and notes 1–3 | Actual continuation, repeated headers, 1/5 mL variants, compatibility bullets, empty cells, `N/A` and notes |
| Extension | 53 | Table 3.1, symbol legend and text | `++++`/`++`/`—` scale, subclasses and measurement scope; no invented numeric score |
| Extension | 86 | Figure 3.22, caption and paragraph | Four products, three time series, axis and units; image capture distinguished from reading bars |
| Extension | 142 | Figure 7.1 and text | Two/three-step process, parallel alternatives, order, FT/B/E modes and shared annotation |

Start with the five initial-trial pages. Add the three extensions only after resolving blocking errors. This covers document forms, not a statistically representative sample of the entire manual.

Convert separate blocks: `[77]`, `[88]`, `[104]`, `[152,153]`, then `[53]`, `[86]`, `[142]`. Do not concatenate 77 and 88 as contiguous pages or merge items across blocks. Inspect every full page for reading order; manifest probes are targeted checks, not exhaustive annotation of every cell.

## 3. Human reference before conversion

1. Verify the PDF hash, then open rendered original pages. Use Poppler; inspection images remain local and ignored. Increase resolution if a unit or note is unreadable.
2. For every probe, record the source region and expected values/relations without inspecting conversion. Manifest expectations are **candidates for confirmation**, never already approved user decisions.
3. Identify table cells by semantic headers and row/column coordinates, including merged cells and inherited fields. An empty cell does not default to `false`, `0`, the preceding value or `N/A`.
4. For diagrams, record boxes, labels, directed connections and groups. Keep parallel paths and alternative relations separate. For charts, annotate axes, units, series and legend; do not infer exact values from bar heights.
5. Record ambiguity and contradictions without resolving them through external knowledge. An applicability note is not automatically an attribute of all neighbouring rows.
6. Freeze local references by hash before execution. Later corrections require a new version and rationale; do not alter a reference merely to make a profile pass.

Use [cytiva-visual-validation-review.csv](cytiva-visual-validation-review.csv) as the review-log template. Copy it to a new local directory for each run and fill in run IDs and the frozen reference. Decisions, captures and full text remain under `data/experiments/cytiva/visual-validation-v01/<run-id>/`, outside this protocol's versioned files.

## 4. Preparation and isolation

- Reference PC: i5-1135G7, 16 GB RAM, Iris Xe; CPU, four threads. Freeze Python, Docling, docling-core, docling-graph and installed versions/commits in the run manifest. The historical profile used Docling 2.140.0; the project pins Docling Graph 1.9.1 at the commit in `requirements-ingestion.txt`.
- The **conversion/chunking-only** runner is available: `python -m experiments.cytiva.visual_validation`, with `convert` and `chunk` commands; see the [runner guide](../../experiments/cytiva/README.md#local-table-conversion-and-chunking-no-llm). It rejects existing output directories, source SHA mismatches, missing weights and remote services; tokenizer and serialization are enforced. The historical `prepare_claim_test` command cannot enable tables: its current settings disable them.
- Check options against the installed version. T1 specifies TableFormer V1, `accurate` mode, PDF cell matching enabled; record the actual loaded class and `kind`. Never silently switch to V2, a VLM or a default profile.
- Verify layout **and** TableFormer weights, their hashes and the tiktoken cache. Historical layout preloading does not establish table-weight availability. If anything is missing, stop preflight and identify the files; downloading is a separate step.
- Run locally without network: prepared caches, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HUB_DISABLE_TELEMETRY=1`, `LITELLM_LOCAL_MODEL_COST_MAP=True`, no `DOCLING_SERVE_URL`, remote services disabled. These variables alone do not prove network isolation; enforce it on the process where necessary.

## 5. Conversion: controlled comparison

| Profile | Tables | OCR | Images | Purpose |
|---|---|---|---|---|
| T0, new control | Structure disabled | Disabled | Pages and figures preserved | Replay the ablation on these pages without changing r2 |
| T1, candidate | Structure enabled; TableFormer V1 `accurate`, cell matching enabled | Disabled | Same as T0 | Measure the actual structural gain |
| T2, conditional | Same as T1 | Enabled with explicit engine/version/language | Same as T0 | Only if relevant characters are missing; separate comparison |

T0 and T1 share layout, CPU, page order/blocks, image scale 2, `generate_page_images=True` and `generate_picture_images=True`; image description/classification and LLM enrichments are disabled. Export full document JSON, HTML/CSV tables, Markdown for inspection, cropped figures and references. Markdown alone is not authoritative for merged cells.

A vector figure must remain verifiable: if no usable PictureItem is created, record failed figure detection and retain the rendered page as a manual fallback. Do not count a full page as a correctly detected/cropped figure. Do not conceal conversion loss with a generated semantic description.

For each object, check text/order, headers/cells, operators/units, title/note links, figure/caption, page and geometry. Document coordinates, dimensions and origin; verify with overlays on the rendering. The right number appearing somewhere on a page does not validate its association.

## 6. Chunking: measure loss after freezing conversion

Only chunk blocks whose T1 output has been examined; block incorrect or ambiguous units. Use the **same conversion JSON per block** across variants: no reconversion during comparison.

An incorrect block may be chunked solely to diagnose additional loss, explicitly marked `quarantined_diagnostic_only` with a review tied to the exact JSON hash. This does not make the block eligible for extraction or publication. The runner infers no human approval.

| Variant | Role |
|---|---|
| K0 | Full-block serialization without splitting; preservation control, not an assumed context-compatible LLM input |
| K600 | Structural/hierarchical HybridChunker, 600-token cap |
| K800 | Same settings, 800-token cap; matches the current local budget |
| K1400 | Same settings, 1400-token cap; observe context/size trade-offs |

Keep `merge_peers=True`, **DocLang without geometry in text**, tiktoken `cl100k_base` and the same serialization provider as the pinned local path. These values are hypotheses, not optima. This grid includes 800 for the current diagnostic; it does not replace the separate retrieval-passage budget in the LightRAG protocol.

Test the **actual chunking path**, including Docling Graph's secondary text splitting, not just raw HybridChunker chunks. Record before/after text, contextualized text, tokens, parent/child IDs, headings, item_refs, all pages, geometry, hashes and `resplit_of`. Inherited parent metadata after secondary splitting does not prove that each child contains the stated note, cell or evidence. Verify the exact subpassage and every `prov` entry, not only `prov[0]`.

Check each unit:

- product/species/subclass + property + value/operator/unit + condition remain associated;
- table rows retain headers, notes and scope context; row splitting is acceptable only if links are preserved;
- external notes and titles are not assumed to repeat automatically: inspect native output, then any context assembler separately;
- continuation 152→153 is explicitly linked; no artificial contiguity across blocks;
- figures, captions and referring passages remain linked by IDs; a text chunk omitting the image does not validate transmission of visual relations to an LLM;
- each child resolves to its actual page/region; header duplication is allowed, invented facts and cross-associations are not.

Report **native context** and **reconstructed context** separately. If a parent must be reinserted, preserve explicit references, remeasure the full budget and declare dependency on a future assembler. Chunks collectively containing a note are not equivalent to a model input actually receiving it.

K0 also detects DocLang serialization loss: if JSON is correct but K0 omits cell relations or images, the error precedes splitting. No LLM can guarantee reconstruction of visual information absent from its input.

## 7. Checks, measurements and decision

**Deterministic:** source/artifact hashes; PDF/excerpt/printed-page mapping; item_ref existence/resolution; exact numbers/operators and preserved units; valid explicit links; token counts of actual serialized text; no lost/duplicated rows or cross-block merges. Compare aligned cells to references, not bags of words. All normalization is explicit and reversible; never turn `n.a.` or approximations into exact measurements.

**Manual:** compare converted objects and chunks with rendered pages; row associations, note scope, arrows, groups and ambiguities. An LLM judge is unnecessary here and does not replace these decisions. CSV probes stay `not_run` until execution, then require `pass`, `fail`, `ambiguous` or `not_applicable`, with rationale and reviewer identity/date.

Report numerators and denominators by content type:

- expected objects found / expected objects in the frozen reference;
- correct selected cells (value **and** headers) / selected cells checked;
- correct title/note/figure links / annotated links; visual relations only where a representation path is actually tested;
- intact critical units in final input / critical units examined, plus units requiring reconstruction or quarantine;
- actually resolved anchors / checked anchors, distinguishing parent geometry from child location;
- chunk count, total/maximum tokens, duplication and contextualization overhead;
- separate loading, conversion, serialization and chunking times; sampled process/child peak memory if measurable, otherwise `unknown`; human review time.

Do not call this manual-wide recall: it is a development selection. Count ambiguous and unexecuted probes separately, without silently removing them to improve rates. Report each table/figure even if aggregates look good.

**Blocking criteria for units intended for later extraction:** zero incorrect product/row associations, zero changed numbers/operators/units, zero lost critical notes, zero invented visual relations and 100% of necessary anchors resolvable. Explicit quarantine reduces coverage; it does not validate the configuration globally. Passing probes does not certify unannotated cells.

Stop after 15 minutes per conversion block/profile or excessive memory pressure; record `timeout`/`resource_limit`, not a quality result. These proposed safeguards are not measured performance. Repeat measurements only to distinguish candidates without blocking errors; separate cold start from warm caches. API costs remain zero; report CPU time and memory.

## 8. Deliverables and next steps

In a new local directory: manifest/versions; PDF/excerpts and page maps; renderings; effective profiles/weights; frozen conversions; tables/figures; human references; K0/K600/K800/K1400 outputs; CSV log and defect report. Source PDFs, captures and full corpora remain local artifacts; see [repository instructions](../../AGENTS.md).

First pass: T0/T1 on 77 and 88, then 104 and block 152–153; K0/K800 on reviewed conversions. Only then compare K600/K1400 and add 53/86/142. VLM interpretation of diagrams is a separate experiment with its own references and measurements, outside this preparation.

Possible decisions: retain T1 and a chunking budget; repair context loss in an adapter; use row units with repeated headers; retain a whole page/image for manual support; or quarantine objects. Code corrections require dedicated regression tests. This protocol approves or publishes no claims.
