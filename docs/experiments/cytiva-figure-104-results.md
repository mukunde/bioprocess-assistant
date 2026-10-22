# Cytiva page 104: figure conversion and chunking results

Date: 2026-10-22. Status: **technical diagnostic and six-card human documentary review complete with reservations; automatic text-only diagram semantics remain quarantined**.
This is a development trial against a candidate source reference, not a held-out
benchmark, scientific validation or graph publication approval. No extraction
LLM, VLM, API call or paid service was used. Local layout/TableFormer inference
is document conversion, not language-model extraction.

## Finding

**T0 and T1 preserve the same readable diagram and exact caption, but the current
text path does not represent the diagram's directed branch relations.** K0 and
K800 retain the converted text, including picture children, while omitting the
image payload/URI. K800 keeps a resolvable picture reference in metadata; this is
not automatic image delivery to a model. No extra text loss due to splitting was
observed on this single-page, single-chunk case.

See the [15 technical probe results](cytiva-figure-104-results.csv),
[execution protocol](cytiva-figure-104-protocol.md) and
[candidate source reference](../../experiments/cytiva/page104_figure_spec.json).
The original [preparation sheet](cytiva-figure-104-review.csv) remains unchanged,
with historical `not_run` values. All decisions were pending when these technical
results were recorded. In the later [human review](cytiva-page-104-human-review.md),
the user approved image/caption fidelity, the five source paths, the KappaSelect
alternative, paragraph applicability and VH-subscript-3 representation with
reservations, and completed the K0/K800 conservation review with reservations.
All six human decisions are recorded separately; automatic text-only diagram
semantics remain quarantined, and production/publication are not authorized.

## Source, frozen conversion and inspection

Original/printed page 104, zero-based index 103, Figure 3.29; excerpt page 1.
Original PDF SHA-256:
`a6fd949e904ec0bafbcc7d85a3be1660f2bea8949098e86c57ae43d06492946a`.
One-page excerpt SHA-256:
`2e820737ed56e2f39a258532ae82092dd85c4d3de9880db3d85596f854e9e7b9`.
Both T0 and T1 `document.json` files have the same bytes and SHA-256:
`887870e70681ecd1171d8d1dff17b515381d52d2ccf35ea66e5c55ce54fbd923`.
The chunking metrics bind to this exact conversion; it was not edited or rerun.

Both profiles used local CPU/four threads, image scale 2, OCR off, page/picture
images on, picture description/classification and chart extraction off, remote
services off. T1 enabled TableFormer V1 accurate and cell matching; T0 disabled
table structure. No table was detected, so TableFormer provides no observed
quality gain here. A disabled chart-model configuration appearing in profile
metadata is not an executed model call. The only effective enabled-feature
profile difference was table structure; a supported-engine list for the disabled
chart feature also serialized in a different order across workers.

The full original page, then source crop and actual detected picture crop were
visually inspected. T1's picture PNG is byte-identical to T0's, so the inspected
picture applies to both. A side-by-side comparison is retained locally.
Differences in crop margins do not indicate content loss. All four vertical role
labels' native source glyph bounds fit inside the detected crop, including its
tight top/bottom margins.

| Layer | Observation | Limit |
|---|---|---|
| Image | One readable picture; 14 box occurrences, five recommended paths, eleven logical connections including the alternative visibly retained | These are source-reference/visual observations, not extracted graph edges |
| Labels | All 14 candidate box labels' character inventories located in native child-item geometry; four role labels retained | Generic children are not fourteen typed box nodes; whitespace/order checks do not prove associations |
| Caption | Exact caption; `#/pictures/0.captions -> #/texts/1`, with reciprocal parent link | Paragraph's `Figure 3.29` is a textual reference; the native picture `references` list is empty |
| Paragraph | Capto L condition, constant-region specificity and general-guide wording retained | Scientific applicability and universal product compatibility are not validated |
| Diagram structure | No typed directed branch or alternative-product connections in conversion annotations/metadata | Five paths and eleven source connections cannot be approved for automatic text-only semantic use |
| Typography/order | Image retains VH subscript 3; picture children serialize `VH`, `Heavy chain`, then `3` after other labels | Source native character order already displaced the 3; preserve provenance instead of silently joining or relocating it |

`Lambda` and `FabSelect` also occur as separate picture children, with `FabSelect`
late in the native child order. Their source region still contains both strings.
Treating child sequence as a branch traversal could associate products incorrectly.
No incorrect extracted edge was measured because no branch-edge extraction ran;
the failure is the absent representation required for the intended text-only use.

## K0 versus K800

| Check | K0 | K800 |
|---|---|---|
| Token count, cached `cl100k_base` recount | 392 | 316 in one final chunk |
| Native text items preserved | 28/28 | 28/28, identical text-node sequence to K0 |
| Internal picture text children preserved | 25/25, in native order | 25/25, same order |
| Caption + paragraph + picture-label text together | Yes | Yes |
| Image URI/payload in serialized text (`src`) | Absent | Absent |
| Spatial coordinates in serialized text | Absent, as configured | Absent, as configured |
| Directed branch/alternative representation | Absent | Absent |
| Native retrieval anchors | External conversion/hash control | Three direct refs and geometry entries |
| Secondary text splits | Not applicable | Zero; raw count 1, final count 1 |

The 392-to-316 difference reflects document wrappers and pretty-printing versus
compact chunk contextualization, not a measured compression rate or lost text.
All 28 converted text strings and the exact XML text-node sequence were checked;
paragraph, caption and diagram labels are not separated across chunks in this run.
This does not exercise oversized figures, multi-page/cross-chunk context or
secondary splitting, and says nothing about production retrieval.

K800's three direct refs are `#/texts/0`, `#/pictures/0` and `#/texts/27` (footer).
Traversing native picture children/captions resolves 29 total items (28 text items
plus one picture), all with valid geometry on excerpt page 1 -> original/printed
104. The caption is an **indirect** anchor through the picture; its geometry is
not a fourth direct chunk geometry entry. Picture-level geometry alone does not
locate a specific branch. All original child anchors remain available in JSON.
The picture embedded in JSON was decoded and its pixels match the saved PNG.

The image and its rasterized arrows are preserved in conversion, but image source
and coordinates are omitted by the chosen DocLang text serialization. They have
not been sent through an actual multimodal model or serving adapter. The chunk
metadata can locate the image only when resolved against the correct hash-bound
conversion. A future adapter must explicitly attach it; a `<picture>` containing
labels alone does not carry visual branch semantics.

## Quarantine and next steps

1. **Keep directed diagram semantics quarantined** for automated text-only
   extraction/recommendations: five paths, the alternative role and VH3 branch
   assignment require an explicit reviewed representation. Do not create graph
   claims from label order, nearest product names or the visual arrow as a
   mandatory laboratory process step.
2. Retain the original picture, native caption link, paragraph and child geometry
   for human review. The image itself has no observed missing branch/label; it is
   not globally unusable merely because text-only semantics are unsupported.
3. Before enabling visual interpretation, test an explicit image-and-caption
   attachment path against the exact stored asset, preserving page/hash/region
   provenance and input budget. This is a future test, not implemented here.
4. For this small diagram, a manually reviewed five-path/alternative reference
   is a practical source for a later typed representation. A deterministic
   vector/geometry experiment is also possible but must demonstrate arrow and
   branch associations rather than assume them. No such reconstruction ran here.
5. OCR is not justified by this trial: characters are present. Changing the
   token budget cannot recreate absent arrows/image input. Compare K600/K1400
   only if a new contextualization question warrants it.

The separate conversion review marks this block `quarantined_diagnostic_only`
and permits chunking for diagnosis only. `human_approved` and
`publication_allowed` remain false. No independent scientific validation,
production serving approval, model input validation or graph import occurred.

## Performance and artifacts

| Stage | Import/setup (s) | Conversion incl. lazy model load (s) | Export (s) | Supervised wall (s) | Sampled peak worker+children RSS |
|---|---:|---:|---:|---:|---:|
| T0 | 71.786 | 25.153 | 0.391 | 99.144 | 870.7 MiB |
| T1 | 28.758 | 14.647 | 0.469 | 45.847 | 1084.6 MiB |
| K0/K800 | Included in worker | Not rerun | Included | 54.934 | 660.2 MiB |

The chunk worker took 52.512 s including imports; the measured raw-plus-native
K800 passes took 0.051 s. The supervision totals are about 200 s for both
conversions and chunking, excluding preparation/inspection. Sequential workers
and warm operating-system caches confound comparisons; T1 is not established as
faster than T0. No timeout/resource limit was reached. All recorded worker/network
checks show zero attempted connections; LLM/API calls and API cost are zero.

Ignored local folders under `data/experiments/cytiva/visual-validation-v01/`:

- `convert-104-20261022-a/`: source map, frozen excerpt, exact profiles,
  T0/T1 JSON/Markdown, picture/page PNGs, metrics and worker logs.
- `conversion-review-104-20261022-a.json`: technical quarantine tied to the exact
  T1 hash and inspection report, created after visual inspection.
- `chunks-104-20261022-a/`: frozen review copy, K0 and K800 texts, raw/native
  chunks, geometry, metrics and logs.
- `page104-diagnostic-20261022-a/`: side-by-side image, conversion and node checks,
  exact token/text/anchor checks, completed technical probe sheet and final
  verification manifest.

The preparation reference/sheet and all prior review decisions remain unchanged.
Verification includes all 388 files frozen before this execution, unchanged
conversion outputs after chunking, the preparation manifest, relative links and
runner regression tests. Full PDFs, raster assets and native documents remain
local rather than being added to versioned result documents.
