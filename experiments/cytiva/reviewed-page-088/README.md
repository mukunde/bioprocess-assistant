# Cytiva page 88: reviewed table 3.6

Completed on 21 October 2026: **9 cards validated with reservations, 40 cells,
5 notes, 12 product-cell note bindings, no pending decision**.

This selected export preserves the deterministic reconstruction, documentary
provenance and original human decisions. It is not independent scientific
validation, an exhaustive extraction benchmark or authorization for graph
publication. `publication_allowed` remains false.

| File | Purpose |
|---|---|
| `packet.json` | Frozen preparation, compactly serialized without changing any JSON value; 40 cells, source words/coordinates, notes, conditions, anchors and hash-bound cards |
| `review.json` | Final cumulative decisions and original French messages; all reservations retained |
| `events.json` | Original pending review and nine unchanged decision events, allowing offline replay of intermediate review states |
| `manifest.json` | Package hashes, original local byte hashes, lineage, source-page mapping, counts and excluded-artifact limits |

The packet's historical pending flags remain unchanged. Current decisions are in
`review.json`, where `human_approved: true` is scoped to documentary review with
reservations only. Never infer publication permission from that field alone.
Source PDF, full-page conversion, native full-page word export, images, model
weights, personal filesystem paths and credentials are not included. Short source
passages and table words needed for the selected review are included.

## Verification

From the repository root with Python 3.10 or later; standard library only:

```powershell
python -m experiments.cytiva.verify_page088_package
python -m unittest tests.test_page088_package -v
```

The verifier checks package files, every card digest and cell assignment, decision
scope, original messages, reservations, the nine-event chain and replayed review
state hashes, notes and exact condition-evidence spans. It does not rerun PDF
parsing, inspect the omitted images, authenticate reviewer identity or execute
operating instructions. Hashes establish consistency, not authenticity of the
manual's scientific claims.

Package file digests normalize CRLF to LF for Windows Git checkouts. Canonical
JSON digests ignore whitespace; source-artifact digests retain original bytes.
Journal replay explicitly reconstructs the original UTF-8, indent-2, CRLF format,
independently of the operating system used to check this export.
Do not replace a reviewed object or change its hash to approve a modified result.

See the [review summary](../../../docs/experiments/cytiva-page-088-human-review.md)
for all retained limits and the [targeted visual method](../../../docs/visual-document-review.md)
for future source-versus-render reviews. The earlier defective Docling tables stay
quarantined; only this page-specific reconstruction was reviewed.
