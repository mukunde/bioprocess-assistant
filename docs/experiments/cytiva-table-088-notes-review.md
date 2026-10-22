# Cytiva page 88: footnote bindings and human review

Date: 2026-10-21. Historical preparation status: **prepared and technically verified; nine human decisions pending at creation**.

The subsequent [completed human review](cytiva-page-088-human-review.md) records
nine validations with reservations. The preparation packet described below remains
frozen; current decisions are held separately in the human-review progress log.
This follows the [word-coordinate reconstruction](cytiva-word-reconstruction-088.md)
and retains the original PDF, word export and reconstructed table unchanged.
No inference, API, publication or runtime graph update occurs.

## Association map

| Note | Printed anchor | Product cells receiving the note | Role and retained context |
|---|---|---|---|
| 1 | Capacity values for MabSelect and MabSelect SuRe | Two capacity cells | Measured at 10% breakthrough by frontal analysis, 500 cm/h, 20 cm bed, 2.4 min residence time |
| 2 | Capacity value for MabSelect Xtra | One capacity cell | Same measurement method and 10% breakthrough; 250 cm/h, 10 cm bed, 2.4 min |
| 3 | Capacity value for MabSelect SuRe LX | One capacity cell | Same measurement method and 10% breakthrough; 100 cm/h, 10 cm bed, 6 min |
| 4 | Recommended operating mobile velocity row label | Four velocity cells | AxiChrom 300 column, 20 cm bed, pressure `< 0.2 Mpa` with source parentheses `(2 bar, 29 psi)`, 25°C |
| 5 | Particle size row label | Four particle-size cells | Defines the reported `d 50v` as median particle size of the cumulative volume distribution |

There are **six printed marker anchors and twelve product-cell bindings**. Including
the velocity and particle-size row labels, fourteen cells carry note references.
Row-wide associations are explicit links from a printed label marker; no cell value
is filled or copied. Empty product cells would receive no fabricated value or
value binding, and would remain visible in a separate review card.

The measurement velocities in notes 2 and 3 (250 and 100 cm/h) remain distinct
from the recommended operating velocities for those products (300 and 500 cm/h).
Context fields are namespaced as `capacity_measurement.*` versus
`recommended_velocity_context.*`; no note silently overwrites a table value.
Note 5 is a definition, not a numerical operating condition.

## Text, conditions and provenance

The [binding module](../../experiments/cytiva/table_notes.py) consumes the frozen
word export, reconstructed table and [explicit notes specification](../../experiments/cytiva/page088_notes_spec.json).
It locates the five original textlines inside a declared footer region, requires
an exact word-to-textline reconstruction and recognizes strict source patterns.
Unexpected wording, missing notes/markers, inconsistent properties or changed
source references stop preparation instead of producing inferred content.

Each note retains:

- its exact source textline and source JSON pointer;
- every original word, ID, top-left rectangle and word-export pointer;
- typed conditions with lexical values, source units, operators and roles;
- exact condition quotations and Unicode character offsets in the source textline;
- printed superscript evidence, source cell, binding kind and target cells.

The 110 note words and 22 condition/definition evidence spans resolve to the frozen
export on original/printed page 88 (excerpt page 1). All 206 original table words
and all forty cell texts are unchanged. The new packet is bound to original PDF,
excerpt/page map, word-export, layout, parent-table, notes-specification and source
image hashes. The five note quotations are preserved in English as printed.

The pressure operator remains strictly `<`. The source unit spelling `Mpa` is
retained without silent normalization. Parenthetical bar/psi values are recorded
as printed representations, with no calculated conversion or assertion of exact
equivalence. This context is not promoted into a universal equipment pressure
limit. These interpretations were subsequently human-reviewed with reservations
for the frozen page-88 package; new packets require their own decisions.

## Review packet

Frozen historical preparation directory:
`data/experiments/cytiva/visual-validation-v01/table-088-notes-20261021-a/review-v3/`.
Earlier local preparation revisions are preserved separately. Full source text
and renderings remain ignored local artifacts.

| Artifact | Purpose |
|---|---|
| `packet.json` | Annotated table, notes, conditions, anchors, bindings, source hashes and review cards |
| `human-review.md` | Sequential review with product names, values, exact note quotations and conditions |
| `review.html` | Read-only linked table; superscript links jump to notes; original page rendering is available |
| `original-page-088.png` | Local Poppler rendering checked against the source page |
| `review.json` | Nine hash-bound pending decisions; reviewer, date and original human message remain null |
| `manifest.json` | Input/implementation/file hashes and zero-call metadata |

The preparation does not record any human decision. Read the cards and reply with
an ID, decision and any reservation. Future decisions must preserve the original
human wording verbatim and bind to both the packet and the reviewed card hash.
The HTML has no approval action or external resource; following a source link
does not change review status. The completed documentary review is recorded in
the separate progress log and compact package, not by changing this preparation.
It does not authorize publication, laboratory use or a pipeline integration.

## Nine review cards

| Card | Check |
|---|---|
| P88-layout | Manual/table identity, headers, descriptions, row labels, both source-empty cells and geometry |
| P88-N1 | Two capacity values with measurement note 1 and its scope |
| P88-N2 | Xtra capacity with note 2; distinguish measurement velocity from recommended operation |
| P88-N3 | SuRe LX capacity with note 3; preserve its different residence time |
| P88-N4 | Four recommended velocities, shared row-marker scope and all note-4 conditions |
| P88-N5 | Four particle sizes and the metric definition, without invented thresholds |
| P88-row-4 | Four CIP-reagent cells and product-family associations |
| P88-row-5 | Four ligand cells and their distinctions |
| P88-row-7 | Four complete format cells, each supported by its own source words |

Together these cover all forty cells exactly once. Context evidence can be reused
across cards, but no approval is inferred from another card. Every decision starts
`pending`; `human_approved` and `publication_allowed` remain false.

## Verification and reproduction

Nine new model-free regressions exercise direct versus row-label scope, measurement
versus operating contexts, pressure operators/units, exact evidence spans, missing
values, missing/changed source material, ordinary digits versus superscripts,
hash-bound pending review coverage and protection of existing output directories.
The combined note, word-table and conversion-runner suites pass **24 tests**.
All 140 earlier experiment files checked retain their hashes.

Source preflight checks original/word/layout bindings and replays the deterministic
parent reconstruction before making an annotated copy. For a new preparation,
choose new output directories and supply the frozen local word export. Create a
new reconstruction first so that its manifest carries a portable specification
identity; exact historical inputs remain unchanged:

```powershell
& '.\.venv-ingestion\Scripts\python.exe' -m experiments.cytiva.word_table --words 'data/experiments/cytiva/visual-validation-v01/deterministic-table-088-20261021-a/words.json' --spec 'experiments/cytiva/page088_table_spec.json' --output 'data/experiments/cytiva/visual-validation-v01/word-reconstruction-NEW'
& '.\.venv-ingestion\Scripts\python.exe' -m experiments.cytiva.table_notes --table-run 'data/experiments/cytiva/visual-validation-v01/word-reconstruction-NEW' --words 'data/experiments/cytiva/visual-validation-v01/deterministic-table-088-20261021-a/words.json' --layout 'experiments/cytiva/page088_table_spec.json' --notes-spec 'experiments/cytiva/page088_notes_spec.json' --source-image 'data/experiments/cytiva/visual-validation-v01/table-088-notes-20261021-a/review-v3/original-page-088.png' --output 'data/experiments/cytiva/visual-validation-v01/table-088-notes-NEW'
& '.\.venv-ingestion\Scripts\python.exe' -m unittest tests.test_table_notes tests.test_word_table tests.test_visual_validation -v
```

This is a page-specific development preparation, not a general footnote resolver.
Other layouts, multiline footnotes, scanned pages and automatic evaluation of
operational applicability remain outside this test. The source table and reviewed
r2 claims are not altered or automatically admitted into chatbot knowledge.

## Portable specifications and preserved history (2026-10-22)

The versioned notes specification now includes `layout_canonical_sha256`. Its
legacy `layout_sha256` is retained as historical byte provenance, not used as the
portable content identity when the canonical field is present. New reconstruction
manifests similarly retain raw bytes and add a canonical identity. The note
preparator verifies both canonical bindings and records `specification_identities`
alongside the actual input byte hashes in each new packet. Word exports and
legacy specifications remain byte-strict; genuine content changes are rejected.

Three additional regressions cover JSON reformatting/LF/CRLF acceptance, unchanged
legacy byte-strict behavior and rejection of altered layout/source/bindings. The
note suite now has twelve tests; note, reconstruction and launcher suites total
30. Historical packets, original specifications inside local artifacts and all
nine human decisions remain unchanged. New pending candidates are not promoted
by matching an old card digest.
