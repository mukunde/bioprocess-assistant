# Cytiva page 77: reviewed table, remarks and chunk conservation

Completed on 22 October 2026: **10 cards validated with reservations, none pending**.
The documentary scope covers table 3.5, seven adjacent remarks and observed K800
conservation/partition. It does not validate scientific applicability, an executable
laboratory protocol, a general chunk budget or production retrieval.

| File | Purpose |
|---|---|
| `cards.json` | Ten unchanged reviewed objects: source cells, six proposed species groups, pH values, original remarks, source coordinates and existing chunk text/metadata |
| `review.json` | Final cumulative review with original French human messages and all reservations |
| `events.json` | Initial pending record, ten unchanged events and minimal metadata needed to replay progressively introduced cards and intermediate states |
| `manifest.json` | Package identities, original local byte hashes, source mapping, counts, review lineage and known context/reference limitations |

The cards retain their historical preparation/pending flags. Current decisions
are in `review.json`. Its `human_approved: true` is explicitly limited to
documentary fidelity and observed diagnostic conservation. Both
`production_retrieval_validated` and `publication_allowed` remain false. A card
approval is not transferred to a modified result merely by updating a hash.

The original species cells stay blank; accepted grouping is separate metadata.
Preserve approximations, inequalities, n.a./n.a. spellings, conditional wording,
alternatives and precautions. In particular, the Rat IgG3 potassium-isothiocyanate
condition is in chunk 0 while its structural/immunological caution is in chunk 1.
Conservation of all text does not ensure that table-only retrieval returns context.

The two apparent punctuation losses in the initial authored reference are reference
errors: the source itself prints n.a without a final stop for Goat IgG2 and the
second Guinea pig row. Historical reference/check artifacts remain unchanged.

## Offline verification

From the repository root with Python 3.10 or later; standard library only:

```powershell
python -m experiments.cytiva.verify_page077_package
python -m unittest tests.test_page077_package -v
```

The verifier checks file identities, ten card/decision links, exact 68-cell
coverage, seven remarks, species scope, reservations, chunk preservation and the
replayed event/state chain. It reconstructs original local UTF-8/indent-2/CRLF
bytes for historical digests, independently of the current operating system.
Package file digests normalize CRLF to LF for Git checkouts. Canonical JSON
digests are distinct from original artifact byte hashes.

Optional source replay requires the exact original local T1 conversion:

```powershell
python -m experiments.cytiva.verify_page077_package --source-document data/experiments/cytiva/visual-validation-v01/convert-20261021-a/p077/T1/document.json
```

This compares selected source cells and remarks against the hash-bound conversion;
it does not parse the PDF, render images, rerun extraction/chunking, recount tokens
or authenticate reviewer identity. Token counts retain the local tokenizer audit;
the standard-library check verifies their consistency and text fingerprints.

The export includes the selected page text and coordinates needed for review.
It excludes PDFs, full-page renderings, the complete conversion document, native
parser exports, model weights, credentials and personal filesystem paths.
Source/decision hashes establish consistency, not scientific validity or a
cryptographic signature of reviewer identity.

See the [review summary](../../../docs/experiments/cytiva-page-077-human-review.md)
and [trial report](../../../docs/experiments/cytiva-conversion-chunking-results-077-088.md)
for retained limits and the corrected reference interpretation. Raw local artifacts
and earlier preparations remain unchanged; this selected export does not replace
their historical status labels.
