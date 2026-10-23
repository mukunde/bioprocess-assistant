# Cytiva pages 152–153: integrated reviewed annotations and isolated quarantine

Date: 2026-10-23. **Documentary annotations integrated; technical conservation
checks pass; new chunk outputs await human conservation review.** This opt-in
experiment uses the [six-card reviewed package](../../experiments/cytiva/reviewed-pages-152-153/README.md).
It does not modify the original conversion, reviewed cards, decisions, v1
serializers/chunks, or production defaults.

## Applied annotations

The [new local launcher](../../experiments/cytiva/apply_reviewed_tables.py)
verifies the existing package and its exact derived source document before
creating a new output directory. It copies the document **byte-for-byte** and
adds an annotation sidecar with scoped approvals and provenance:

- **g1:** the HiTrap MabSelect grouping of derived rows 19–20. Row 20's raw
  product cell remains blank; no source rowspan or printed product text is added.
- **c1:** table `#/tables/1` continues logical table A1.7 from `#/tables/0`.
  Both source objects and page anchors remain distinct. Page 153's repeated
  caption context is explicitly `reviewed-continuation`, not a native caption.
- **n1:** one cell–note link for MAbTrap Kit, with approximate purification count,
  syringe wording and no column-reuse authorization inferred.
- **n2:** two links for the marked Protein G/Protein A Mag Sepharose Xtra entries;
  material description only, without a derived handling protocol.
- **n3:** twelve links for the four PreDictor groups' 6/20/50 µL capacity cells.
  Raw `N/A 3` is preserved without expansion, zero substitution or inferred capacity.

Each approval retains its original human message, reservations, reviewed-card
digest and event digest. Each of the 15 cell links retains native cell geometry,
raw text, grid address, note reference and original/excerpt page numbers. The
source PDF and derived document hashes remain bound to the reviewed package.
Copies of the complete review/events preserve the six-decision history, including
the earlier conservation approval; that approval is not transferred to new chunks.

The artifact-level `annotations_human_validated: true` applies to these unchanged
documentary annotations. Global `human_approved`, `production_ready` and
`publication_allowed` remain false.

## Serialization and quarantine

The [v2 serializer](../../ingestion/reviewed_table_chunking.py) emits explicit
`note-link`, `row-group` and `continuation` elements. Full provenance and original
reservations remain in the hash-bound sidecar; concise scope limitations are also
included in the budgeted XML. Every table fragment retains its full header and
caption context. A note body is included **only when that fragment contains an
explicit cell link to it**, and its scope is `explicit-cell-links-only`.

The source-text inventory separately preserves all eight native text items,
including note 3's native body-text label. It is tagged as a preservation unit,
not a retrieval result; its note bodies do not establish table-row applicability.

Whole native spans and the reviewed HiTrap group stay indivisible. Any quarantine
intersecting such a group quarantines the complete group. An annotated atomic unit
that exceeds the final serialized budget fails instead of being truncated.

The three unresolved aggregate rows are **physically isolated** under `quarantine/`:

| Table-0 grid row, zero-based | Product |
|---|---|
| 1 | HiTrap Protein G HP |
| 9 | HiTrap Protein A HP |
| 13 | HiTrap rProtein A FF |

Their source text remains unchanged in the copied document and quarantine XML.
They are absent from primary K0/K800 table inputs. Primary row identifiers retain
their original numbers, so gaps indicate this deliberate partition. These remain
43 derived rows in total, not 46 independently reconstructed physical variant lines.

## Final local run

| Measure | Primary outputs | Quarantine outputs |
|---|---:|---:|
| Data rows | 40 | 3 |
| Data-grid positions | 400 | 30 |
| K0 tokens | 3952 | 446 |
| K800 fragments | 8: seven table fragments plus inventory | 1 table fragment |
| K800 token counts | 212, 695, 765, 630, 758, 703, 759, 708 | 425 |
| K800 total tokens | 5230 | 425 |
| K800 maximum tokens | 765 | 425 |
| Explicit approved cell–note links | 15, each once | 0 |

Serialization, source/package checks, validation and export took **0.460 seconds**
including imports in this run; process-launch overhead and the separate audit are
excluded. No conversion or model weights were loaded. Annotations and limitations
add text: compared with the [previous v1 experiment](cytiva-table-152-153-repair.md),
token totals must be interpreted with the different format and quarantine partition.
This is not a controlled compression/speed benchmark or evidence of retrieval gains.

The 800-token cap applies to serialized XML alone, not a future complete prompt,
tool schema, assembled multi-chunk context or generated answer. The XML format is
`reviewed-structural-table-xml-v2`, not DocLang/OTSL. K0 uses an inventory-first
layout and segment boundary; it does not reproduce original PDF reading order.

## Verification

**212 tests plus six r2 package tests pass**, including 13 new regressions for
exact note scope, blank preservation, reviewed grouping, continuation, source-page
metadata, physical quarantine, span/group propagation, oversized-unit rejection,
output collision protection and rejection of locally re-signed scope changes.
The original offline review-package verifier still passes.

A separate read-only audit independently parses the new XML, compares all **430
data-grid positions** to the unchanged document, verifies source span anchors,
checks K0/K800 partition agreement, resolves all 15 links back to approved cells,
recounts tokens with cached `cl100k_base`, and confirms no unlinked note body in
table fragments. It verifies that **512 pre-existing experiment files** are
byte-identical. No new human decision is created by these technical checks.

## Reproduce

From the repository root, with the existing ingestion environment and cached
tokenizer, choose new output names on every run:

```powershell
$annotationsPython = '.\.venv-ingestion\Scripts\python.exe'
$annotationsBase = 'data/experiments/cytiva/visual-validation-v01'
$annotationsRun = "$annotationsBase/annotated-152-153-new-run"
$annotationsChunks = "$annotationsBase/chunks-annotated-152-153-new-run"
& $annotationsPython -m experiments.cytiva.apply_reviewed_tables prepare --source "$annotationsBase/repaired-152-153-20261022-c/document.json" --output $annotationsRun
if ($LASTEXITCODE -ne 0) { throw 'Stop: annotation preparation failed.' }
& $annotationsPython -m experiments.cytiva.apply_reviewed_tables chunk --run $annotationsRun --output $annotationsChunks --budgets 800
if ($LASTEXITCODE -ne 0) { throw 'Stop: reviewed chunking failed.' }
& $annotationsPython -m unittest tests.test_reviewed_table_chunking -v
```

Both commands reject existing output directories before processing inputs. The
chunk command re-verifies the original review package, exact document bytes,
artifact hashes and regenerated approved annotation set; changing a local sidecar
and its manifest cannot extend approval or remove the three quarantines.
The existing Python audit guard blocks network connections/DNS and downloads;
it is not an OS firewall. Recorded network attempts and LLM/API calls are zero.

Final ignored artifacts under the experiment base:

- `annotated-152-153-20261023-b/`: unchanged document, annotations, original review
  and events, source-package manifest and artifact manifest.
- `chunks-annotated-152-153-20261023-b/`: primary K0/K800, separate quarantine
  K0/K800, source/annotation/implementation fingerprints and metrics.
- `annotations-integration-audit-20261023-b/`: independent read-only audit,
  checks and final verification record.

The `-a` trial outputs remain preserved. Neither trial changes source approvals,
old artifact bytes or any production pipeline. See the [new regressions](../../tests/test_reviewed_table_chunking.py)
and the [completed documentary review](cytiva-table-152-153-human-review.md).
