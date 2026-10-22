# Cytiva pages 152–153: reviewed tables, notes and chunk conservation

Review completed on **23 October 2026**: six cards validated with reservations,
none pending in this inspected scope. The package preserves the HiTrap/HiScreen
reconstruction, documentary table continuation, 15 cell–note links and observed
K0/K800 conservation. It approves no scientific performance, complete property
audit, graph publication or production retrieval.

| File | Contents |
|---|---|
| `cards.json` | Six unchanged review cards; selected table text/spans, 30 reconstructed cells with glyph coordinates, eight native text items, frozen context and exact derived K0/K800 XML/metadata |
| `events.json` | Original initial state and six unchanged decision events, including the original French messages verbatim |
| `review.json` | Exact final six-card state, approved scopes, 15 unique note bindings and retained reservations |
| `manifest.json` | Portable package/support digests, original local JSON byte hashes, source page mapping, counts and lineage |

Frozen cards/chunks still have their historical pending flags. Current decisions
are separate review records. The final global `human_approved: false` deliberately
means **no blanket dataset approval**; the six card decisions are each
`validated_with_reservation` and approved only for their recorded documentary scope.

The second HiTrap MabSelect product cell stays blank. Its two-variant grouping is
a separate annotation. The two native tables stay distinct; page 153's caption
context is a reviewed continuation annotation, not a printed title. Note 1
belongs to MAbTrap Kit; note 2 to the two marked Mag Sepharose Xtra entries; note 3
to exactly twelve marked PreDictor capacity cells. Preserve approximate counts,
capacity units, N/A and blanks. No reuse authorization, protocol or zero capacity
is inferred.

Three table-0 rows remain quarantined for per-variant interpretation: 1 (HiTrap
Protein G HP), 9 (HiTrap Protein A HP), 13 (HiTrap rProtein A FF). The **43 derived
data rows** are not 46 independently reconstructed physical variant lines.

The opt-in format is **structural-table-xml v1, not DocLang/OTSL**. K0 has 3579
tokens. K800 has seven fragments (six table blocks plus text inventory), token
counts **212, 782, 794, 547, 659, 661, 720** and total **4375**. The cap applies to
serialized chunk text, not a complete future prompt or assembled query. Repeated
caption/notes are context, not cell applicability. Human-approved bindings have
not been propagated into those frozen chunks or the production pipeline. The
inventory is a preservation unit, not an evaluated retrieval unit.

## Offline verification

From the repository root, Python 3.10+; **standard library only**:

```powershell
python -m experiments.cytiva.verify_pages152153_package
python -m unittest tests.test_pages152153_package -v
```

Optional comparison against the exact original local derived document:

```powershell
python -m experiments.cytiva.verify_pages152153_package --source-document data/experiments/cytiva/visual-validation-v01/repaired-152-153-20261022-c/document.json
```

The verifier checks package inventory, source/card/event bindings, six replayed
states, retained reservations, scopes, note coordinates, source glyph consistency,
all 430 table data-grid positions, exact XML structure, cell spans, whole groups,
header/caption/note context, source page metadata and original text fingerprints.
It verifies the recorded token counts against the frozen audit; it **does not
re-tokenize**, render the source PDF, re-extract content, prove reviewer identity
or measure retrieval quality. Source image hashes are references, not fresh visual
validation. Optional source replay checks the exact byte-bound derived JSON and
selected table/text evidence, not the original PDF itself.

Package and supporting-file digests normalize CRLF to LF for portable checkouts.
Canonical JSON digests are distinct from historical local byte hashes. Historical
JSON bytes are reconstructed from UTF-8, indent 2, insertion order and CRLF to
verify their original event/state links. Approval is not transferable to changed
source evidence by updating file digests.

No PDF, image, embedded image data, full converted document, model weight,
personal absolute path or credential is included. The complete local history
remains under the ignored experiment directory.

## Proposed versioning scope

This **17-file proposal** includes seven review/context documents, five package
files, the offline verifier and its tests, and three existing local reproduction
files. No unrelated project files are included.

| Group | Repository-relative paths |
|---|---|
| Review/context (7) | `docs/experiments/cytiva-table-152-153-protocol.md`, `docs/experiments/cytiva-table-152-153-results.md`, `docs/experiments/cytiva-table-152-153-results.csv`, `docs/experiments/cytiva-table-152-153-review.csv`, `docs/experiments/cytiva-table-152-153-repair.md`, `docs/experiments/cytiva-table-152-153-human-review.md`, `experiments/cytiva/pages152153_table_spec.json` |
| Compact package (5) | `experiments/cytiva/reviewed-pages-152-153/README.md`, `cards.json`, `events.json`, `review.json`, `manifest.json` in that same directory |
| Verification (2) | `experiments/cytiva/verify_pages152153_package.py`, `tests/test_pages152153_package.py` |
| Local reproduction (3) | `experiments/cytiva/repair_table152.py`, `ingestion/table_chunking.py`, `tests/test_table_chunking.py` |

The reproduction files are needed by the commands already documented in the
repair report. They are experimental and opt-in; this proposal changes no
production ingestion default. The offline package verifier does not execute or
import them. Historical pending/preparation statuses in the original probe CSV,
specification and diagnostic reports are retained; the completed human review
and this package state the later decisions.

Proposed commit message:

```text
feat(ingestion): preserve reviewed Cytiva tables and row-safe chunking
```

See the [completed review](../../../docs/experiments/cytiva-table-152-153-human-review.md),
[repair report](../../../docs/experiments/cytiva-table-152-153-repair.md),
[original diagnostic](../../../docs/experiments/cytiva-table-152-153-results.md)
and [protocol](../../../docs/experiments/cytiva-table-152-153-protocol.md).
