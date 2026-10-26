# Required request context matrix v0.1

Status: **M01-M14 and allocation modalities approved on 25 October 2026;
not implemented**. The [second collective decision](decisions/2026-10-25-task-request-matrix-review.json)
also approves R01-R08 with the R08 sample-volume correction. The earlier
[D01-D08/C01-C04 decision](decisions/2026-10-25-task-request-review.json) is preserved
unchanged as historical review context. Approval is of the design handling rules,
not new scientific facts or an executed algorithm. The
[request contract](REQUEST-CONTRACT-V01.md) remains documentation, not a schema.

## Scope and reading rules

Initial product-specific scope is HiTrap Blue HP, documented 1 mL/5 mL formats,
plus general IEX/HIC/SEC questions needed for existing cases. Do not silently add
other media/products or formats. The current source boundary is the same 25
eligible excerpts on pages 118-121. E118-I and E121-EQ remain excluded.

This matrix separates **context needed to identify a documentary statement** from
**conditions needed to establish that it applies to a real sample**. A user can
ask what the manual states without supplying every real-process property. Preserve
the statement's conditions and warning; do not report applicability as established.
If the user instead asks whether they should carry out an action, unknown material
conditions remain unknown and no real-process authorization is inferred.

For each requested item:

1. Identify its task, product context, stage/topic and information selector.
2. Distinguish supplied values from unknown/not-supplied states. Do not invent
   missing bindings, source approval or a product from a generic label.
3. Resolve same-task inclusion/exclusion overlap before affected operating values.
4. Check documentary eligibility independently of input completeness. More user
   context cannot make a quarantined passage available.
5. Ask only for missing information that affects this item's requested result.
   Do not block unrelated clear items. Do not request extra details when the
   known limitation is source unavailability and those details cannot fix it.
6. Record whether the user asks for a single scoped value or a comparison/list of
   documentary alternatives. Listing supported alternatives does not select one
   for a real process. Explicit comparison of column formats uses separate tasks;
   do not invent a format comparison merely to avoid asking a necessary question.

Source IDs below are **human review references only**. They must not appear in
submitted requests or serve as question-ID shortcuts in a future interpreter.
Numerical documentary values mentioned here are checks on scope, not new advice.

## Approved matrix

The column-dependence statements apply only to the eligible HiTrap Blue HP source
passages, not universally to chromatography products.

| ID | Requested information | Minimum documentary context | Column-size dependence here | Missing-context or source response | Review references |
|---|---|---|---|---|---|
| M01 | General IEX/HIC/SEC separation principle | General-topic intent and technique(s) being discussed | No column/product needed | Return only general principles; no inferred contaminant, technique selection or demand for a confirmed diagnosis | E118-M, p. 118; E118-USE/E118-C may support an explicitly requested general clarification |
| M02 | Sample-application flow | Resolved HiTrap Blue HP product, loading stage and selected 1 mL or 5 mL column task | Yes: documented ranges differ | Clarify size for a single range; an explicitly requested format comparison has two tasks. Preserve optimal-results qualification and linked note | E121-L/E121-F, p. 121 |
| M03 | Washing flow | Resolved product, washing stage and selected column size | Yes | Clarify size for the flow item; unrelated washing endpoints or buffer-role items can remain supported | E121-W, p. 121 |
| M04 | Washing buffer role, quantity expressed in column volumes, or stopping criteria | Resolved product, washing stage and exact information selector | The excerpt gives the same CV guidance/endpoints for both sizes | Do not ask size solely for these items. Keep binding buffer, generally/at-least qualifiers and the alternative endpoints. A requested mL volume is not directly supplied and is not automatically calculated | E121-W, p. 121 |
| M05 | Operating elution flow | Resolved product, elution stage and selected column size | Yes; the stated flow depends on size, not on which of the two documented elution modes is discussed | Clarify size when a single flow is requested; do not require an elution-mode choice solely for this shared flow guidance | E121-E, p. 121 |
| M06 | Operating elution quantity in column volumes | Resolved product and elution stage; either a selected elution mode or an explicit request to list/compare the two modes | The excerpt gives mode-specific CV guidance shared by both sizes | For a single mode-specific quantity, clarify mode; for an explicit documentary comparison, retain separate step/linear alternatives with usually-sufficient qualification. Do not infer a duration or gradient profile | E121-E, p. 121 |
| M07 | Binding-buffer formulations | Resolved product, buffer-preparation item and binding-use facet | No size choice needed for the cited formulations | Clarify buffer use if unspecified and a single formulation role is requested; an explicit comparison can retain both roles separately. Keep alternative formulations and printed nomenclature | E121-B/E121-BH, p. 121 |
| M08 | Elution-buffer formulations | Resolved product, buffer-preparation item and elution-use facet | No size choice needed for the cited formulations | Same buffer-use rule as M07. Do not activate operating elution flow/volumes. No automatic pairing with a binding formulation | E121-B/E121-BH, p. 121 |
| M09 | Approximate syringe-note correspondence | Resolved product and column size to select the documented pair; clarify whether this is note lookup or conversion of an observed flow | Yes; two specific column/flow/drop pairs, not a general formula | Note lookup can repeat its stated flow and approximate drops for the chosen size. A different supplied flow does not authorize interpolation or a universal conversion | E121-F and associated E121-L, p. 121 |
| M10 | Position of albumin removal relative to other purification steps | Resolved HiTrap Blue HP context and workflow-position item | No column size needed for the before/after statement | Do not borrow another task's size or ask for size unnecessarily. Other products named in the same source are not merged into the initial catalog | E120-A, p. 120 |
| M11 | Maximum pressure in bar | Record product/column binding if supplied; exact binding would be necessary for a future scoped value | No eligible pressure value exists to select by size | Report absence only within the 25 eligible excerpts, without inventing bar or computing pressure from flow. Do not solicit size merely to pretend it will unlock a value; retain supported sibling items | Eligible-excerpt registry in the X packet; no numerical pressure source |
| M12 | Equilibration flow, quantity or recipe | Record explicit product/column/stage context | Cannot establish from the current eligible sources | Mark the source unavailable/quarantined under current policy, even if all user fields are supplied. Do not substitute washing or loading parameters | E121-EQ remains excluded; eligible E120-P/E121-PH establish protocol scope only |
| M13 | Cation-exchange pH-versus-pI condition | Record the requested condition and any supplied facts without reconstructing the rule | Not a column-size issue | The specific source remains quarantined; user-supplied pI does not approve it. General charge-separation principles may still be supported | E118-I excluded; E118-M eligible |
| M14 | Any product-specific numeric item with an ambiguous product or unsupported format | Exact product identity and supported format, where relevant | Cannot transfer across identities or unsupported formats | Generic HiTrap is ambiguous: clarify. An explicitly identified different product/unsupported size is outside the initial scope: say so, rather than pretending its identity is missing. Do not infer bed volume from sample volume | Initial C01 scope decision; not a new scientific source claim |

For eligible Blue procedural items, preserve the E120-H heading, E120-W warning,
E120-P cross-page link and E121-PH heading where required by the existing source
policy. E121-BH and E121-F remain attached when required. The matrix cannot remove
these dependencies. A context atom may contain an adjacent column value or elution
formulation; its presence does not authorize rendering it for another task/item.

## Facts, unknowns and applicability

| Situation | Representation and proposed behavior |
|---|---|
| A supplied fact is false | Keep `provided` with Boolean false; do not replace it with unknown or an exclusion |
| The user does not know a property | Keep `unknown`; no assumed hydrophobicity, contaminant or diagnosis |
| A property is not mentioned | Keep `not_supplied`; do not borrow it from the manual, another task or a gold reference |
| A column is irrelevant to a general principle | A justified `not_applicable` state is possible; omission alone does not prove irrelevance |
| Product-specific applicability depends on a supplied property | Evaluate only against an eligible reviewed condition; user statements remain scenario facts, not independently verified science |
| The Blue hydrophobicity warning's applicability is unknown | Retain the warning with a documentary statement; do not say the sample is suitable or the action authorized |
| An input fact and its negation concern the same task | Record a fact conflict separately from a requested-information exclusion; affected applicability stays unresolved |

General direct-use applicability and new symptom-to-cause rules are not added to
the initial implementation by this matrix. Existing documentary experiments stay
available as history. Extending C01's product/topic perimeter needs an explicit
design decision and source mapping, not a conveniently matching excerpt.

## Approved clarification and support handling

Keep interpretation, documentary support and applicability separate, as in the
contract. The handling rules below are approved; the example diagnostic labels
remain descriptive spellings, not an implemented enum:

| Situation | Interpretation | Support / next action |
|---|---|---|
| Unknown column for a requested single washing flow | Needs clarification for that item | `missing_column_binding`; no chosen flow; clear endpoint item may proceed |
| Same task includes and excludes washing parameters | Needs clarification for affected operating items | No affected operating values; no arbitrary last-wins choice |
| Pressure absent from the eligible registry | Ready if the documentary request is understood | Missing source for pressure; report bounded absence and retain supported washing |
| Requested equilibration source quarantined | Ready if the request is understood | Quarantined/unavailable; never borrow values from another stage |
| Resolved request but bundle exceeds global budget | Ready | Budget-incomplete for affected items; not proof of source absence |
| Explicit out-of-scope product | Understood but outside the initial product perimeter | No numerical transfer; do not repeatedly ask the user to identify an already identified product |

## Shared budget and scheduling detail

C04 approved six selected seeds and 2,048 serialized-context tokens per request,
alternation between requested items, shared-source deduplication, atomic dependencies
and explicit unserved-item reporting. The following allocation modalities were
also **approved in the second collective review**:

- Keep tasks in input order and each task's unblocked, in-scope items in their
  own input order. Interleave the item lists across tasks: A1, B1, A2, B2, and so
  on, skipping exhausted lists. On another candidate round, revisit that same
  interleaved order rather than giving one item all candidates first.
- Count distinct selected seeds globally. Reuse a source bundle without charging
  its serialized content twice, while keeping all task/item associations.
- Admit a candidate only with all eligible dependencies and full serialized
  metadata. Never strip a warning or footnote to fit.
- If an indivisible bundle does not fit, record the affected item and reason;
  continue considering other items that can fit. Do not silently rank a source
  as absent or mark the whole request complete.
- Report the resulting item coverage, size and selection order. Input order can
  affect scarce-budget outcomes; it is observable, not a scientifically justified
  priority. No performance or fairness result has been measured.

Exact candidate ordering within an item and any relevance threshold remain to
be specified and frozen with the future corpus adapter. This document does not
approve an algorithm by merely naming round-robin scheduling.

## Review completion and implementation boundary

Rows M01-M14, R01-R08 and the allocation modalities were validated collectively.
The [eight design cards](experiments/structured-request-review-cards-v01.md) retain
their handling rules, including the corrected distinction between sample volume
and volume actually loaded. This approval came from the new design review, not
from automatic inheritance of X source-reference decisions.

The exact wire format, reviewed product/alias catalog, source-role adapter,
within-item candidate ranking and relevance thresholds still need technical
specification. No new prospective question set or success threshold was approved
by this collective decision. No form, schema, v06 code or retrieval run is included.
