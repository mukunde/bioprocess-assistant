# Cytiva table A1.7 import preview

Replay the reviewed table as a local graph preview. The command builds JSON
in memory, checks the recorded output hashes, and writes to a new directory.
The project’s Neo4j graph requires no connection for this experiment.

```powershell
python -m experiments.cytiva.pages152153_import_preview --output tmp/cytiva-table-152-153-preview
python -m unittest tests.test_pages152153_import_preview -v
```

Use Python 3.10 or later. The reviewed v1 and v2 packages supply the portable
inputs. `--pdf` checks the original handbook against its recorded SHA-256.
`--artifacts` replays the historical annotations and K0/K800 inputs under the
local `visual-validation-v01` directory. The verification JSON records which
optional checks ran.

## Verified scope

| Evidence | Result |
| --- | --- |
| Pages 152–153 | One logical table, two separately cited segments, and ten repeated headers. Continuation carries no inherited note scope. |
| Page 152, HiTrap/HiScreen | Keep HiTrap rows 19–20 grouped and the row 20 product cell blank. HiScreen stays on row 21. |
| Page 152, note 1 | One MAbTrap Kit cell. Preserve the approximate count, supplied buffer stocks, and syringe wording. The review grants no reuse authorization. |
| Page 152, note 2 | Two marked Protein G and Protein A Mag Sepharose Xtra product cells. The note describes the material. |
| Page 153, note 3 | Twelve marked capacity cells across four PreDictor groups. Preserve `N/A` as printed. |

The local rehearsal verified the original PDF and inspected its rendered pages.
Marked cells and notes retain original page numbers, references, geometry, and,
for note text, character spans. Each note link retains its review decision and
reservations.

`import_preview.json` contains 62 staged nodes and 75 relationships, including
the 15 cell-to-note links. Its 40 table rows provide documentary context.
`quarantine.json` retains the unresolved aggregate rows 1, 9, and 13 of the
page-152 segment. These are HiTrap Protein G HP, HiTrap Protein A HP, and HiTrap
rProtein A FF. They have no connections to the graph preview.

The [recorded hashes](../../experiments/cytiva/pages152153_import_preview_manifest.json)
bind the preview and quarantine to the
[reviewed v2 package](../../experiments/cytiva/reviewed-pages-152-153-v2/README.md).
The preview is marked `publication_allowed: false` and `production_ready: false`.
