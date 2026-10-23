# Cytiva pages 152–153: reviewed v2 annotations and physical quarantine

Completed on **23 October 2026**: `P152-153-annotated-chunking` is validated with
reservations for **observed conservation and correct annotation placement**.
No decision is pending for this card. The six earlier documentary decisions
remain unchanged in the [v1 package](../reviewed-pages-152-153/README.md).

This is an incremental repository package: v1 is a verified dependency, not a
second copy of its six decisions. The v2 package retains the single new decision,
its original French message, reviewed annotation provenance and exact new XML.
It does not approve scientific performance, complete property-cell correctness,
graph publication or production retrieval.

| File | Contents |
|---|---|
| `cards.json` | Unchanged v2 review card; integrated annotations and their five approval sources; exact primary/quarantine K0 and K800 text/metadata; historical artifact/chunk manifests |
| `events.json` | Original initial pending state and unchanged conservation-decision event, with the original human quotation verbatim |
| `review.json` | Exact final scoped review, eight reservations and remaining quarantine |
| `manifest.json` | Portable package/support/dependency digests, source and event lineage, counts and original local byte hashes |

The initial card and output manifests keep their historical pending flags. The
later `review.json` supplies the scoped approval. Global `human_approved`,
`production_ready` and `publication_allowed` remain false; the single accepted
card has `human_approved_for_observed_conservation: true`.

## Retained scope

- **g1:** HiTrap MabSelect rows 19–20 remain together; the second product cell
  stays blank. No source product text or native rowspan is manufactured.
- **c1:** page 153 continues logical table A1.7 through a reviewed annotation;
  two source tables and exact original/excerpt page anchors remain distinct.
- **n1/n2/n3:** exactly **15 cell–note links** (1 + 2 + 12) retain their approved
  source cells, text, geometry, note refs, original messages and reservations.
  Unmarked rows sharing a fragment inherit no note applicability. N/A is not
  expanded or replaced with zero, and no reuse permission or protocol is inferred.
- **Primary:** 40 derived rows; K0 **3952 tokens**; eight K800 fragments including
  one source-text inventory. Token counts **212, 695, 765, 630, 758, 703, 759, 708**;
  total **5230**, maximum **765**.
- **Quarantine:** table-0 rows **1, 9, 13** (HiTrap Protein G HP, HiTrap Protein A
  HP, HiTrap rProtein A FF), physically separate in both controls. K0 **446 tokens**;
  one K800 fragment, **425 tokens**, no approved note links. Aggregate values
  remain unresolved for per-variant use.

All 43 derived rows are conserved; this does not assert 46 independently
reconstructed physical variant lines. The inventory preserves eight native text
items but is not a retrieval result or applicability rule. The 800-token cap
covers XML alone, not a complete future prompt or assembled context. Full
reservations and provenance remain in the hash-bound sidecar; concise limitations
are also present in XML. The format is experimental structural XML v2, not DocLang.

## Offline verification

From the repository root, Python 3.10+; **standard library only**:

```powershell
python -m experiments.cytiva.verify_pages152153_v2_package
python -m unittest tests.test_pages152153_v2_package -v
```

The verifier first validates the v1 package and its six-event chain, then checks
the inherited annotation/quotation/reservation scope, v2 artifact lineage,
original decision replay, source cells/spans, explicit note-link placement,
physical quarantine, full XML fingerprints and source page mapping. It checks
the recorded token audit and metadata; it does **not re-tokenize**, render a PDF,
prove reviewer identity, or run a retrieval or scientific evaluation.

Optional replay against the exact original local artifacts:

```powershell
python -m experiments.cytiva.verify_pages152153_v2_package --annotated-run data/experiments/cytiva/visual-validation-v01/annotated-152-153-20261023-b --chunks-run data/experiments/cytiva/visual-validation-v01/chunks-annotated-152-153-20261023-b
```

Package, supporting-file and v1 dependency hashes normalize CRLF to LF for Git
portability. Canonical payload digests are separate. Historical local JSON hashes
reconstruct UTF-8, indent 2, insertion order and CRLF; copied v1 repository files
retain their historical formatting with CRLF. This preserves original approvals
and lineage without rewriting reviewed records. Source-image SHA values are audit
references, not a visual revalidation on a new checkout.

No PDF, image, embedded image data, full converted document, model weights,
personal absolute path or credential is included. Complete source artifacts
remain local under ignored experiment directories. No LLM/API or paid service is
used by verification.

## Proposed versioning scope

Exactly **12 files**:

1. `docs/experiments/cytiva-table-152-153-annotations.md`
2. `docs/experiments/cytiva-table-152-153-annotations-human-review.md`
3. `experiments/cytiva/apply_reviewed_tables.py`
4. `ingestion/reviewed_table_chunking.py`
5. `tests/test_reviewed_table_chunking.py`
6. `experiments/cytiva/verify_pages152153_v2_package.py`
7. `tests/test_pages152153_v2_package.py`
8. `experiments/cytiva/reviewed-pages-152-153-v2/README.md`
9. `experiments/cytiva/reviewed-pages-152-153-v2/cards.json`
10. `experiments/cytiva/reviewed-pages-152-153-v2/events.json`
11. `experiments/cytiva/reviewed-pages-152-153-v2/review.json`
12. `experiments/cytiva/reviewed-pages-152-153-v2/manifest.json`

The reproduction and serializer files are the existing local, opt-in v2 work.
The proposal changes no production default and does not recommit v1 files.
Historical pending preparation flags are distinct from the completed human review.

Proposed commit message:

```text
feat(ingestion): preserve reviewed Cytiva v2 annotations and quarantine
```

See the [completed review](../../../docs/experiments/cytiva-table-152-153-annotations-human-review.md),
[integration experiment](../../../docs/experiments/cytiva-table-152-153-annotations.md)
and [earlier documentary review](../../../docs/experiments/cytiva-table-152-153-human-review.md).
