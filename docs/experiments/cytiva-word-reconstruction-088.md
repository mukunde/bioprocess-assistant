# Cytiva page 88: deterministic reconstruction from PDF words

Date: 2026-10-21. Historical preparation status: **targeted technical checks passed; review was pending at creation**.
The subsequent [human review](cytiva-page-088-human-review.md) is complete with
nine validations with reservations. New reconstructions still start pending;
approval of a frozen result is never copied to a newly generated packet.
This is a separate candidate following the [cell-matching ablation](cytiva-cell-matching-ablation-088.md),
under the [visual validation protocol](cytiva-conversion-chunking-protocol.md).
It does not modify or approve the previous Docling conversions, publish claims,
or replace the production ingestion pipeline.

## Result

All four “Available formats” cells are complete and assigned to the correct
product. All four velocity values and units are in their correct columns:

| Product | Formats | Operating mobile velocity | Source word IDs: formats / velocity |
|---|---|---|---|
| MabSelect | Complete, independently read | 500 cm/h | 193–205 / 106–107 |
| MabSelect Xtra | Complete, independently read | 300 cm/h | 206–218 / 108–109 |
| MabSelect SuRe | Complete, independently read | 500 cm/h | 219–231 / 110–111 |
| MabSelect SuRe LX | Complete, independently read | 500 cm/h | 232–244 / 112–113 |

Each format cell contains its own 13 words from two source lines. The four texts
are identical in the manual, but their source IDs and coordinates are disjoint.
No text is copied from another cell. The velocity row's superscript marker 4
remains in the label's source words, separate from the four value cells.

The 24 previously frozen targeted checks pass: four headers, four formats, four
velocities, four capacities with units/note markers, four particle sizes/units
and four CIP reagent associations. These are development checks, not an
exhaustive gold reference or a whole-manual accuracy score.

## Inputs and method

- Manual SHA-256:
  `a6fd949e904ec0bafbcc7d85a3be1660f2bea8949098e86c57ae43d06492946a`.
  The full original PDF hash and the frozen page-88 excerpt/source map match.
- The native Docling PDF parser exports 356 word cells, including source text,
  stable export IDs, top-left bounding boxes and the original/excerpt page map.
  No OCR, layout model, TableFormer, LLM, embedding or API is used.
- [Page-specific layout](../../experiments/cytiva/page088_table_spec.json) records
  an assistant-selected table region, header band, four repeated header anchors,
  one unlabeled description row and six labeled rows. These are explicit visual
  layout assumptions that were pending confirmation at preparation; the configuration contains no
  expected format string or numerical answer.
- [Reconstruction code](../../experiments/cytiva/word_table.py) locates the four
  aligned `MabSelect` header words. Before each header start, it finds a vertical
  whitespace interval that no table word crosses, then places a separator inside
  that interval. Row boundaries similarly use whitespace before the description
  and row-label bands. This avoids treating the full velocity textline as one cell.
- A word is assigned only if its entire rectangle fits exactly one cell region.
  Cross-boundary or ambiguous words are reported; missing separators stop the
  reconstruction. Within a cell, vertical overlap forms lines, then x coordinates
  order words. Only spacing between original words/lines is serialized.

The resulting column boundaries are approximately x=75, 393.81, 756.99, 1115.57,
1474.15 and 1840 on the 1920-wide page. The eight row bands produce an 8×5 grid:
38 nonempty cells and two genuinely empty first-column cells (header/description).
All **206 table words are assigned exactly once**, with 206 resolvable JSON
pointers back to the frozen export, zero ambiguous assignments and zero words
crossing the declared table boundary. Non-table words remain in the source export.

## No-fill and provenance checks

A separate in-memory probe removes only the 13 format words belonging to
MabSelect Xtra. Its reconstructed format cell stays empty, with no source IDs;
the other three format cells are unchanged. The actual PDF and frozen word export
are never edited. This demonstrates that the matching text is not a template,
forward-fill or copy-from-neighbour rule.

Source IDs, text and coordinates of every assigned word are compared against the
frozen export. Replaying identical inputs produces an identical table object.
The new manifest binds the word-export, layout and implementation hashes.
All 125 previous experiment files checked before the run retain their hashes.

## Notes and limits

The five footnotes remain verbatim in the raw word/textline export. The velocity
marker 4 is retained in the row label, and the original page was visually checked
including its AxiChrom conditions. This original reconstruction stage did **not** attach typed
footnote/applicability objects to reconstructed cells. CSV/HTML flatten superscript
formatting; they are inspection artifacts, not instructions ready for retrieval.
The later note-binding stage adds those links and conditions; a production adapter
must still enforce them before serving facts.

This is a bounded repair candidate for one inspected, born-digital, flat table.
The manually specified table region, expected layout and left-aligned headers
limit generality. Merged cells, multiline row labels, other pages, scanned PDFs
and multipage continuation remain untested. Missing or ambiguous geometry must
remain visible; it does not permit imputation. Human documentary confirmation
and scientific validation are separate from these technical results.

## Timing and verification

Measured PDF-parser imports: 33.48 seconds; page parsing: 0.10 seconds.
Reconstruction of the frozen word export: 0.042 seconds, excluding Python startup
and output rendering. These are a single run with prepared local dependencies,
not a controlled speed benchmark or a claim about full-manual throughput.
Model-inference calls, LLM calls, API calls and recorded network attempts: zero.
Local CPU/electricity costs were not measured.

Eight new model-free regression tests cover independent provenance for repeated
text, missing cells staying empty, marker/value separation, absent whitespace,
partial-region quarantine, source/page/coordinate/filling rejection, deterministic
replay and preservation of existing output directories. The existing seven
conversion-runner tests also remain applicable; no external model is needed.

## Local artifacts and reproduction

Local ignored directory:
`data/experiments/cytiva/visual-validation-v01/deterministic-table-088-20261021-a/`.
It contains `words.json`, `validation.json`, the previous-artifact hash inventory,
`word-boundaries-overlay.png` and `reconstruction/` with table JSON/CSV/HTML/PNG
and a manifest. Source text, images and full table outputs remain local.

From the repository root, with the frozen local word export available, choose a
new output directory:

```powershell
& '.\.venv-ingestion\Scripts\python.exe' -m experiments.cytiva.word_table --words 'data/experiments/cytiva/visual-validation-v01/deterministic-table-088-20261021-a/words.json' --spec 'experiments/cytiva/page088_table_spec.json' --output 'data/experiments/cytiva/visual-validation-v01/word-reconstruction-NEW'
& '.\.venv-ingestion\Scripts\python.exe' -m unittest tests.test_word_table tests.test_visual_validation -v
```

The source-parsing script and validation/rendering scripts are retained with
hashes beside the local run. Reconstruction itself uses the standard library;
the separate export step requires the installed native PDF parser. The command
never overwrites an existing directory. Each new candidate starts pending review,
with `publication_allowed: false`; the original Docling output quarantine is not lifted.

## Subsequent footnote preparation

The [separate note-binding and human-review packet](cytiva-table-088-notes-review.md)
adds all five notes and their conditions to an annotated copy. It preserves this
initial reconstruction and its artifacts unchanged; no human approval is inferred.

## Portable identities for new preparations (2026-10-22)

New manifests retain `spec_sha256` for exact original bytes and add
`spec_canonical_sha256` using sorted-key, compact, UTF-8 JSON. LF/CRLF, indentation
and key ordering do not change that identity; a changed field does. Word-export
hashes remain byte-strict. The reconstruction suite now has nine tests, including
a CLI regression comparing LF and CRLF inputs and their separate raw digests.

The notes preparator accepts a new parent's canonical layout identity. Legacy
manifests without that identity remain byte-strict: replay them with their exact
frozen inputs. Do not rewrite an old manifest or replace a reviewed source hash
to make an altered file pass. Create a new reconstruction for a portable run.
