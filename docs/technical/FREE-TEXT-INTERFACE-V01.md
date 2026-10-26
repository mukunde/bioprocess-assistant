# Free-text interpretation interface v01

Date: 26 October 2026. **FI01-FI06, IF01-IF14 and preceding clarifications approved collectively; not implemented or frozen.**
The [interface decision record](../decisions/2026-10-26-free-text-interface-review.json) preserves the actual human message. Machine-schema details and exact fixtures are a new draft pending review. The comparison protocol CP01-CP06 and five preceding
clarifications were approved collectively; see the
[actual decision record](../decisions/2026-10-26-structured-free-text-protocol-review.json).
That approval does not automatically approve every new field or test below.

Companions: [comparison protocol](../experiments/structured-free-text-comparison-v01.md),
[case cards](../experiments/structured-free-text-cases-v01.md), and
[structured technical specification](TASK-REQUEST-TECHNICAL-SPEC-V01.md).
The current structured runtime, public schema, catalog, source adapter and source
policy remain unchanged. No new public endpoint or executable schema is added.

## 1. Boundary and data flow

Verbatim input -> interpretation ledger -> validated planner projection ->
unchanged StructuredControl.evaluate -> bridge outcome -> reference scoring.

The ledger and bridge are new application-side artifacts, not instances of the
existing `canonical_request` or `plan_result` schemas. Do not insert new states
or nullable task owners into those schemas. The runtime's canonical record and
plan remain unmodified and are stored as its actual output. A proposed wrapper
connects them to the original text and accounts for every omitted unit.

There is at most one shared planner invocation per input, never one per task.
The original six-root/2,048-token budget includes the actual serialized planner
context/bindings. Interpretation and wrapper metadata are outside that context
budget and must be measured separately, not hidden as zero-cost data.

## 2. Input envelope and immutable text

The application assigns an opaque `request_id`. The caller supplies only
language EN/FR and verbatim text; it cannot supply system hashes, source approval,
root IDs or resource overrides. A quoted malicious directive remains user text,
not an authorized system setting. Reference case IDs and answers are never input.

Store the text before any transformation, with SHA-256 over its exact UTF-8 bytes.
Do not normalize Unicode/newlines before hashing. Empty, non-string or invalidly
encoded inputs are rejected explicitly before interpretation. An unrecognized
language is rejected rather than silently translated or guessed.

The first implementation must declare its supported constructions, normalization
and input-size limits before freeze. No unreviewed size limit is selected here.
Normalizing case/whitespace for matching must retain an index map to original
characters. Technical product identity remains catalog-driven, without fuzzy
correction or substring-based identity selection.

## 3. Proposed interpretation ledger

| Field | Required meaning |
|---|---|
| `interface_version` | New wrapper version, distinct from the unchanged structured contract version |
| `request_id`, `language`, `input_text`, `input_sha256_utf8` | Exact immutable input identity |
| `system_identity` | Hashes of schema, catalog, adapter, source review, interpreter, bridge and interpretation policy; populated by application only |
| `assertions` | Ordered literal assertions: original spans, raw lexemes, subject candidates, semantic role and value/state; retain conflicting assertions separately |
| `tasks` | Stable known scopes in original order; each context field links to assertions; no invented split to repair a contradiction |
| `requested_units` | Inventory of positive information requests, including unresolved owners, ordered by occurrence |
| `exclusions` | Owned typed restrictions, their polarity and origins; negated exclusions remain auditable but are not active bans |
| `issues` | Stable issue IDs, reason/category, exact origins, affected units and blocking effect |
| `origins` | Target-to-input links for all substantive values, relations and issues |
| `interpretation_status` | `ready`, `partial`, `needs_clarification` or `rejected`; does not claim documentary support |

Ledger names are proposed design fields, not newly accepted public wire keys.
The closed categories and machine schema need their own implementation review.

Each requested unit has an immutable `unit_id`, occurrence order, optional known
owner or explicit owner candidates, information selector, stage/facets, origins
and issue references. An unresolved owner has no selected owner. Its candidate
set is not permission to create one positive request for every candidate.

A stage whose meaning is itself unresolved is retained as an unresolved fragment,
not labelled as an invented enum. Never create a dummy product, task, information
selector or supplied value merely to satisfy the planner's required fields.

The inventory includes recognizable positive requests before filtering. If a
remaining fragment might contain another positive request that cannot be bounded,
record `inventory_complete=false` and an interpretation issue; the wrapper cannot
claim full accounting. Raw syntactically unsupported text must not disappear.

## 4. Origins and normalization

Offsets are half-open `[start,end)` in Python-style Unicode code points in the
original string, not UTF-8 byte offsets, UTF-16 code units or a translated text.
An origin includes the input hash and quoted exact substring. Several spans can
support one relation; a product span and an exclusion's scope/negation spans must
not be collapsed into just the positive product name.

Origins have three kinds:

- `text_span`: a real original substring and character offsets;
- `not_stated`: relevant field absent from the preserved input, with the input
  hash and checked scope; no fake empty span;
- `application_metadata`: generated IDs or matrix-derived inapplicable/default
  field, with policy identity and reason; never a fabricated user statement.

Retain `provided`, `unknown`, `not_supplied` and justified `not_applicable`.
False and zero are substantive supplied values. Observed sample volume, loaded
volume, column bed volume and flow have distinct roles. A numeric lexeme such as
`1,0` in French may normalize to decimal string `1.0` in the same unit while
retaining its original span; no cross-unit conversion or interpolation is allowed.

A size inside a qualified product label remains an assertion from that label.
Do not pretend that the separate column field was explicitly filled. Preserve a
contradictory explicit column value as another assertion; do not choose last-wins.

## 5. Issue ownership and dispatch

| Situation | Proposed dispatch |
|---|---|
| Fully representable input, including a structurally valid semantic conflict already handled by StructuredControl | Preserve the assertions in a faithful submission; let the unchanged runtime diagnose it |
| Known unit with unresolved owner, as clarified G05 | Retain both owner candidates, pre-block that unit, and do not invent a planner assignment; unrelated known units may proceed |
| Unknown product spelling or explicit unknown size representable by current slots | Pass the literal label/state; the common catalog/context rules diagnose it |
| Unsupported construction with clearly bounded affected item | Pre-block that item and retain its text and issue; independent items may proceed |
| Restriction whose scope could affect several items | Block every possibly affected item until clarification; do not assume it affects only the nearest item |
| Missing or incompletely recognizable inventory | Preserve the fragment, report incomplete accounting; do not manufacture full coverage |
| Mandatory-warning removal affecting A, as G06 | A procedural item is pre-blocked by the presentation-policy conflict; no warning-free procedure is served; independent C remains eligible |
| Attempt to approve E121-EQ through user text | Preserve and reject the policy directive; do not lift quarantine or invent an equilibration request |
| Invalid input envelope or inconsistent internal references | Reject explicitly without planner invocation; retain audit failure |

An unknown fact alone does not prove process inapplicability; no confirmation of
contamination or chemical suitability is invented. Keep language interpretation
issues separate from the runtime's documentary quarantine/missing-source states.
Pre-blocked units have documentary state `not_assessed_by_planner`, not a claim
that their source is absent. The unchanged source-exclusion policy is still shown.

## 6. Planner projection and immutable core result

The adapter constructs a schema-valid `structured_submission` only from units
that can be faithfully represented and are not blocked by unresolved language or
presentation policy. It must preserve task/item order, context assertions, facts,
facets and all applicable active exclusions. Do not prune conflicting but
representable assertions to make a unit pass. If one information selector of an
item is pre-blocked, preserve the other selectors and their relative order.

Maintain explicit mappings from ledger unit/task/item IDs to projection IDs and
JSON pointers, including every occurrence of an exclusion scope. Field origins
link those generated pointers back to the actual text. Planner `form_field`
origins describe the projection only; they never replace this bridge evidence.

If an item has no dispatchable units, omit it from the projection but retain it
in the ledger and wrapper. If a task then has no items, omit its projection task
without deleting its ledger scope. No empty or fabricated task is sent to satisfy
the existing schema. If the projection has no tasks, do not call the planner.

Projection must not weaken an exclusion. If an exclusion targets a removed item,
retain it as an inert ledger restriction with the target and reason, not as a
widened task ban. Task-level exclusions remain on surviving task items. A scope
that cannot be preserved without changing its meaning blocks the dependent
surviving units rather than silently disappearing.

Shared context/facts for a surviving task stay attached even if their first text
mention occurred in an omitted item. Conversely, product names mentioned only
inside exclusions cannot become positive product context. The common scheduler
still interleaves admissible items in preserved task order. This projection-order
property requires a conformance test; do not assert it solely from S01-S12 results.

Store exact projection bytes/hash, validate with the unchanged public schema,
then call `StructuredControl.evaluate` once. No direct call to private `_interpret`
or `_assemble`, monkey patch, post-hoc removal of selected passages, alternate
source lookup or mutation of the returned canonical record/plan is allowed.

## 7. Bridge outcome and complete accounting

The wrapper has separate fields for `interpretation_ledger`, `projection`,
`projection_mapping`, `core_result` (unaltered or null with a reason), `unit_outcomes`,
`request_summary`, and `timings`. It is not labelled an existing `plan_result`.

Every recognizable requested unit appears exactly once in `unit_outcomes`:

- `planner_evaluated`: link to the exact core unit and its interpretation,
  documentary support, diagnostics, binding and assigned sources;
- `preblocked`: own issue IDs, affected scope, unresolved candidates if any,
  documentary state `not_assessed_by_planner`, and **no binding or source IDs**;
- `not_evaluated_due_to_error`: explicit input/interpretation/projection/runtime
  failure. A previously pre-blocked unit retains its original reason as well.

Do not overwrite the core's aggregate flags. They describe only the projection.
The wrapper separately reports known unit count, preblocked/evaluated/failed
counts, inventory completeness, whether every requested unit has an outcome,
whether any unit remains unserved and whether any interpretation issue remains.
An incomplete inventory or pre-blocked unit prevents a full-service claim even
if the projected core plan reports all its eligible units covered.

Successful handling of a required clarification can pass a diagnostic case while
still reporting the request as partly unserved. Evaluation-reference success and
the application's service-completeness status are different fields.

No completion by subtraction: removing a blocked unit cannot improve the score's
denominator. Downstream errors do not erase preblocking decisions. Source
integrity, exclusions and budget invariants remain checked on the actual context.

For a paired S/F documentary case, the structured arm must also express the
reviewed input meaning faithfully. If the unchanged form cannot express a case's
unresolved ownership, do not fill an owner for S or invent a dummy task to enable
the comparison. Keep that case interpretation-only, as G05 currently is, until
a separately reviewed common-interface revision supports it. The future paired
set can use representable ambiguities such as unknown size or contradictory
explicit sizes; an unrepresentable case cannot be silently counted in its
downstream comparison denominator.

## 8. Design examples and required conformance checks

| Check | Design example and acceptance condition; not executed |
|---|---|
| IF01 | Ready washing plus binding formulation: all units dispatch once, origin spans cover both requests, no additional selector |
| IF02 | Same-scenario size conflict as P11: preserve both assertions and pass the representable conflict to the core; no invented split |
| IF03 | Clarified G05: one unresolved washing unit with candidates A/B, no A/B washing binding; independent C SEC unit dispatches |
| IF04 | G06: rejected policy override and A-only presentation conflict; no E121-EQ or E118-I context, no warning stripping, C survives |
| IF05 | One information selector preblocked within a multi-selector item: retain the other units, applicable exclusions and order; denominator unchanged |
| IF06 | All units preblocked: no planner call, no dummy task, empty context, explicit incomplete service |
| IF07 | Negated exclusion G01 and addition G02: no false conflict, no omitted positive item, full polarity/scope origins |
| IF08 | False scenario fact G03 and volume roles G04: exact fact roles/states, no column or loaded-volume inference |
| IF09 | Pointer/UTF-8/code-point mapping on accented French and multi-code-point characters: original substring and input hash verify; no translation offsets |
| IF10 | Ambiguous exclusion scope: no arbitrary nearest-item attachment; independent scopes are preserved only when provably unaffected |
| IF11 | Core exception or projection validation failure: immutable partial audit, explicit outcome for every known unit, no hidden retry |
| IF12 | Equivalent S/F admissible meaning: one global budget, same shared source policy and plan semantics after a single ID bijection; no order sorting or raw-text rerouting |
| IF13 | A generated pointer without a real text/application origin is rejected; an unrecognized possible request prevents complete-inventory reporting |
| IF14 | Removed-item exclusion never widens to a task ban or disappears from the ledger; shared facts remain available to valid sibling units |

These are approved implementation acceptance requirements, not executed test
results. Final input forms, origin annotations and expected wrapper records must
be reviewed before implementation fixtures are finalized. P/G case approval is
not inferred from protocol approval. None of these examples creates source gold.

## 9. Review choices before implementation

FI01 (new wrapper/ledger versus unchanged core schemas), FI02 (verbatim
origin and normalization contract), FI03 (dispatch/preblocking/projection rules),
FI04 (whole-request accounting), FI05 (explicit language perimeter and diagnostics),
and FI06 (IF01-IF14 conformance before candidate freeze) are approved. MC01-MC06
and their clarifications are now also approved; the [machine design guide](FREE-TEXT-MACHINE-DESIGN-V01.md)
describes the refined fixtures awaiting grouped review.

The machine schema choices were approved separately after the interface decision.
Exact refined origins and test conditions now await GR01-GR04 review. No candidate
is frozen and no prospective comparison is authorized by this specification.
