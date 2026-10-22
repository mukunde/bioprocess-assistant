# Cytiva page 104: reviewed figure, applicability and chunk conservation

Completed on 22 October 2026: **six cards validated with reservations; none pending**.
This package preserves documentary decisions on figure 3.29, five recommended
paths, KappaSelect's alternative role, paragraph applicability, the VH-subscript-3
representation and observed K0/K800 text conservation. It approves neither
scientific applicability nor an automated diagram interpretation or production use.

| File | Purpose |
|---|---|
| `cards.json` | Six unchanged reviewed cards, selected native text/geometry, source-image hashes, human-readable source paths and exact K0/K800 text/metadata |
| `review.json` | Final cumulative state, six original French user messages and all reservations |
| `events.json` | Initial pending record, six unchanged events and minimal metadata to reconstruct progressive review states |
| `manifest.json` | Portable package/supporting-file digests, original artifact byte hashes, source mapping, counts and review lineage |

Historical pending flags remain in the frozen cards and preparation specification.
Current human decisions are in `review.json`; they do not retroactively change
technical experiment results. Final `human_approved: true` is restricted to
this exact documentary and diagnostic scope. Automatic text-only diagram semantics
remain `quarantined`; publication, production retrieval and actual model image
attachment are not validated.

The five paths and alternative are an approved source reading, not native
extracted directed edges. The three Capto L occurrences keep separate scopes.
KappaSelect is not a mandatory next process step. Preserve conditional applicability,
kappa/lambda Fab constant-region wording and the general-guide qualification.
Display `VH₃` and plain-text alias `VH3` apply only to verified page-104 occurrences;
raw `VH 3 .` and diagram child order remain unchanged. No normalizer is implemented.

K0 has 392 tokens; K800 contains one 316-token chunk. All 28 converted text items,
including 25 picture text children, are retained. The size difference reflects
formatting/serialization, not measured compression. Image payload and branch
geometry/relations are absent from serialized text; the image remains recoverable
through the exact conversion's picture reference. Three direct chunk anchors
reach 29 native items through children/caption, not 29 direct chunk spans. This
one-chunk trial does not test secondary splitting or cross-chunk applicability.

## Offline verification

From the repository root, Python 3.10 or later; standard library only:

```powershell
python -m experiments.cytiva.verify_page104_package
python -m unittest tests.test_page104_package -v
```

The verifier checks card/decision binding, reservations, source path/alternative
scope, raw subscript representation, text conservation, chunk fingerprints,
source mapping, quarantine flags and all six reconstructed event/state hashes.
It also checks the accompanying protocol/results/reference files in the repository.
This selected package is an offline repository artifact; supporting documents
must accompany it. Nothing downloads a model or calls a service.

Package/supporting-file SHA-256 values normalize CRLF to LF for portable Git
checkouts. Original local JSON byte hashes are reconstructed from UTF-8,
indent-2 and CRLF; canonical JSON card digests are separate. Updating hashes does
not transfer an approval to a new source or newly generated result.

Optional comparison against the exact original local T1 document:

```powershell
python -m experiments.cytiva.verify_page104_package --source-document data/experiments/cytiva/visual-validation-v01/convert-104-20261022-a/p104/T1/document.json
```

This compares selected native items, caption/picture provenance, child order and
text conservation to the byte-bound original conversion. It does not render the
PDF, re-extract content, recount tokens or prove reviewer identity. Token counts
retain the cached local audit; text fingerprints and recorded counts are checked.
Source-image hashes are audit references, not visual revalidation on a fresh clone.

The package contains selected page text/coordinates and relative historical local
artifact paths. It excludes PDFs, images, embedded image data, the full native
conversion, model weights, personal absolute paths and credentials. Original
local artifacts and decisions remain unchanged.

See the [completed review](../../../docs/experiments/cytiva-page-104-human-review.md),
[trial report](../../../docs/experiments/cytiva-figure-104-results.md) and
[protocol](../../../docs/experiments/cytiva-figure-104-protocol.md).
