# Cytiva page 104: completed human documentary review

Date: 2026-10-22. Status: **six cards validated with reservations; none pending**.

The user approved `P104-image-caption` for documentary visual fidelity and the
exact native caption link. Original user decision:

> Je valide P104-image-caption avec les réserves indiquées. Enregistre ma décision et passons à la revue des cinq chemins du schéma. Aucun appel LLM ni API payante, aucun commit ni push.

## Image/caption decision: retained reservations

- The output is a retained image, not a reconstructed semantic graph; automatic
  text-only branch/alternative interpretation remains quarantined.
- Crop margins differ. The caption is separate from the image crop and explicitly
  linked to it. No missing diagram content was observed in the reviewed image.
- Identical T0/T1 results on this page do not approve other conversions.
- This decision does not approve branch claims, VH3 text serialization, image
  attachment to a model, scientific applicability or production retrieval.

## Source-path and alternative decisions

The user approved `P104-paths` with its reservations. Original decision:

> Je valide P104-paths avec les réserves indiquées. Enregistre ma décision et passons au rôle d’alternative de KappaSelect. Aucun appel LLM ni API payante, aucun commit ni push.

The five recommended-product paths in original/printed page 104, figure 3.29,
are approved as a documentary source reading, not five native extracted relations.
They describe a general selection guide, not guaranteed binding or sequential
laboratory operations. Keep the three Capto L occurrences in their respective
source branches. VH3 is the domain-antibody heavy-chain subtype, with a source
subscript; serialization remains separate. The automatic text-only semantic
quarantine remains in place, and publication/production are not authorized.

The user approved `P104-alternative` with its reservations. Original decision:

> Je valide P104-alternative avec les réserves indiquées. Enregistre ma décision et passons aux conditions d’applicabilité du paragraphe. Aucun appel LLM ni API payante, aucun commit ni push.

KappaSelect is approved as the depicted alternative on the Fab/Kappa branch,
not as a subsequent process step. Retain the contextual lack of Capto L affinity
and kappa-Fab constant-region wording. Do not transfer the alternative to the
Lambda, scFv or domain branches, infer absence of other applications, universal
interchangeability, an affinity threshold or a sequential two-support protocol.
This remains documentary review, without scientific validation or release of
text-only semantic quarantine.

## Paragraph applicability and VH3 representation decisions

The user approved `P104-applicability` with its reservations. Original decision:

> Je valide P104-applicability avec les réserves indiquées. Enregistre ma décision et passons à la représentation textuelle de VH₃. Aucun appel LLM ni API payante, aucun commit ni push.

Retain the conditional complementary-media context, distinct kappa/lambda Fab
constant-region statements, possible MabSelect use associated with VH3 affinity,
and the general-guide qualification. No affinity threshold, switching algorithm,
operating parameters or universal capture rule may be added. Approval concerns
documentary fidelity, without independent scientific validation or release of
automatic text-only semantic quarantine.

The user approved `P104-VH3` with the representation and reservations. Original
decision:

> Je valide P104-VH3 avec la représentation et les réserves indiquées. Enregistre ma décision et passons à la revue du chunking K0/K800. Aucun appel LLM ni API payante, aucun commit ni push.

Display `VH₃` and plain-text alias `VH3` are approved for these verified page-104
occurrences, with original source references retained. The 3 is a subtype
subscript, not a dose, step number or independent node. Raw paragraph `VH 3 .`
and separate diagram children remain unchanged; their ordering limitation was
already present in native source text. No global rewrite rule, normalization
adapter or corrected serialization is implemented, and the text-only semantic
quarantine remains in place.

## Chunking conservation decision

The user approved `P104-chunking` for observed conservation with reservations.
Original decision:

> Je valide P104-chunking pour la conservation observée, avec les réserves indiquées. Enregistre ma décision et fais le bilan final de la revue de la page 104. Aucun appel LLM ni API payante, aucun commit ni push.

K0 contains 392 tokens; K800 yields one 316-token
chunk with no secondary split. All 28 converted text items, including 25 picture
text children, and the exact XML text-node sequence are preserved. Paragraph,
caption and labels co-occur. The size difference is not a measured compression
or omission rate. Three direct anchors and 29 reachable native items resolve to
excerpt 1 / original and printed 104; caption/child anchors require traversal.
Image payload and directed diagram semantics are absent from serialized text,
even though the stored image is recoverable through the exact conversion.
The approval is limited to observed conservation on this exact result;
cross-chunk context, secondary splitting, actual model input and production
retrieval remain untested.

The raw candidate reference and prior technical result sheet remain unchanged;
the [technical diagnostic report](cytiva-figure-104-results.md) describes their
historical pending status. It does not override later user decisions.

## Local audit trail

Ignored records are under
`data/experiments/cytiva/visual-validation-v01/page104-human-review-20261022-a/`:

- `P104-image-caption.json` and `review-initial.json`: unchanged preparation.
- `001-P104-image-caption.json`: original user quotation, reservations, source
  conversion hash, reviewed-card digest and initial-review byte-hash binding.
- `P104-paths.json`: unchanged reviewed card with source nodes, five paths,
  source geometry and label checks; its historical pending flags remain frozen.
- `review-after-001.json`: approved first decision and pending next decision.
- `verification-after-001.json`: checked digests, quotation and prior-artifact
  preservation. Global approval, publication and production retrieval stay false.

- `002-P104-paths.json`: second user quotation and reservations, linked to the
  previous event and state hashes.
- `P104-alternative.json`: unchanged reviewed card with exact paragraph source item,
  picture label items, source branch/role annotations and explicit limits.
- `review-after-002.json` and `verification-after-002.json`: two approved decisions,
  one pending alternative card, checked quotes/hash chain and unchanged prior files.

- `003-P104-alternative.json`: third original user quotation and reservations,
  linked to the previous event and review byte hashes.
- `P104-applicability.json`: unchanged reviewed paragraph card with five exact source
  excerpts, original image hash and documentary applicability limits.
- `review-after-003.json` and `verification-after-003.json`: three approved cards,
  one pending card, checked source excerpts/hash chain and unchanged prior files.

- `004-P104-applicability.json`: fourth original user quotation and reservations,
  with previous event/state hash links.
- `P104-VH3.json` and `VH3-source-region.png`: unchanged reviewed card and
  source-derived detail crop, with raw paragraph/items, chunk hashes and limits.
- `review-after-004.json` and `verification-after-004.json`: four approved cards,
  one pending card, checked source/chunk fragments and unchanged prior records.

- `005-P104-VH3.json`: fifth original quotation and representation reservations,
  linked to prior event and cumulative-review hashes.
- `P104-chunking.json`: unchanged reviewed card with exact K0/K800 text, metadata,
  metrics, source checks and conservation/anchor limits.
- `review-after-005.json` and `verification-after-005.json`: five approved cards,
  one pending chunking card, checked 28-item sequence and unchanged prior records.

- `006-P104-chunking.json`: sixth original user quotation and retained reservations,
  linked to the prior event and cumulative-review byte hashes.
- `review-after-006.json`: completed cumulative state, six validations and no
  pending card; approval explicitly scoped to documentary fidelity/diagnostics.
- `verification-after-006.json`: all six card/event/state bindings and quotations,
  388 original pre-execution files and 328 pre-final visual-review files verified
  unchanged; source JSON and chunk outputs remain frozen.

Conversion SHA-256:
`887870e70681ecd1171d8d1dff17b515381d52d2ccf35ea66e5c55ce54fbd923`.
No model/API calls, conversion reruns or chunk modifications accompany this review.

## Final scope and retained limits

| Card | Approved documentary scope | Retained limit |
|---|---|---|
| P104-image-caption | Complete retained diagram image and exact native caption binding | Crop margins differ; an image is not a typed graph or validated model attachment |
| P104-paths | Five source-recommended fragment/subtype/product paths | General selection guide; distinct repeated labels, no universal affinity guarantee or sequential process |
| P104-alternative | KappaSelect alternative on the Fab/Kappa branch | No transfer to other branches, automatic substitution rule or two-support protocol; other applications are not ruled out |
| P104-applicability | Conditional context, Fab constant-region scope, possible MabSelect use for stated VH3 affinity | No invented thresholds, operating parameters, guaranteed capture or independent scientific validation |
| P104-VH3 | Source-subscript interpretation; VH₃ display and VH3 plain-text alias for verified occurrences | Raw paragraph/child items unchanged; no global rewrite or implemented normalization adapter |
| P104-chunking | Observed preservation of 28 text items, 25 internal labels and source-anchor resolution in exact K0/K800 | One page/one chunk only; no image payload or typed branch semantics in text; no production retrieval validation |

The final cumulative `human_approved: true` is limited to this documentary and
diagnostic review. `production_retrieval_validated`,
`actual_model_image_attachment_validated` and `publication_allowed` are false.
`automatic_text_only_diagram_semantics` remains `quarantined`. Historical card,
preparation and technical-result flags remain frozen and are not current decisions.
The approved source reading does not mean that Docling automatically extracted
those branch/alternative relations; native typed diagram relations remain absent.

## Compact versionable package

The [review package](../../experiments/cytiva/reviewed-page-104/README.md) preserves
the six unchanged cards, final decisions, original human quotations, reservations
and progressive journal. Its standard-library
[verifier](../../experiments/cytiva/verify_page104_package.py) replays all six
original state hashes, checks source paths/alternative/VH3 scope and exact text
conservation, and optionally compares native items against the original T1 JSON.
Package hashes support LF/CRLF checkouts; original artifact byte hashes remain
separate. Images, PDFs and the full conversion remain local. The export does not
implement typed graph edges, source rewriting or image delivery to a model.

## Next steps

1. Review the compact package before versioning. Its checks establish record
   consistency, not new scientific, retrieval or production validation.
2. Before semantic integration, build and separately verify a provenance-bound
   representation of the approved paths, alternative and applicability conditions.
   Treat VH3 display/alias as explicit source-backed metadata, not a raw rewrite.
3. If visual model input is pursued, test actual image/caption/paragraph attachment
   and budget against the exact stored asset. It has not been implemented or tested.
4. Evaluate retrieval/applicability separately. Extra token budgets or OCR do not
   recover absent diagram semantics; new tests must address a specific open gap.
