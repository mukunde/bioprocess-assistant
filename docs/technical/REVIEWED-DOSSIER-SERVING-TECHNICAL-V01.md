# Reviewed-dossier serving — technical specification v01

Prepared on 2 November 2026 against `main` at `6c8bfe0`. **Technical design only; implementation and activation remain pending.** The user accepted DS01–DS10, RC1–RC4 and CL01–CL04. The [new decision record](reviewed-dossier-serving-decisions-v01.json) preserves the exact message and binds the original three proposal documents. Their old pending labels remain historical. No existing review, source record or v03 artifact is rewritten.

Accepted requirements below are normative. Concrete technical choices marked **proposed** are not retroactively attributed to the user's design approval. In particular, no numerical context budget was selected by that approval.

## 1. Components and boundaries

Proposed files for a later implementation, not created by this specification:

| Component | Responsibility | Forbidden responsibility |
|---|---|---|
| `serving/contracts.py` | Strict request/envelope validation and derived outcome types | Parse unrestricted chat text or accept client-supplied release/source authority |
| `serving/registry.py` | Load approved release, mappings, original bindings and withdrawal inventory into an immutable snapshot | Refresh approved source hashes or rewrite old decisions |
| `serving/adapter.py` | Bind each structured task to the registered complete documentary bundle(s) | Invent product membership, a diagnosis, numerical values or graph paths |
| `serving/renderer.py` | Render escaped stored wording, conditions, reservations and source links | Render model-authored technical prose or hide mandatory warnings |
| `serving/service.py` | Check active authority, allocate complete context, derive statuses and record replay metadata | Call an LLM, write Neo4j or silently fall back to legacy chat |
| `serving/source_view.py` | Resolve only release-registered excerpts and review records | Read arbitrary filesystem paths or redistribute the full PDF |

Start with pure local calls plus an explicit opt-in loopback integration after tests. Proposed future endpoints are `POST /api/reviewed/v1/evaluate` and `GET /reviewed/v1/releases/{release_id}/sources/{source_id}`. Neither endpoint exists yet. A later chat route requires its own activation decision; `agent.py`, `query_graph`, `grounding.render_selection` and frozen v03 keep their existing result types.

## 2. Logical machine contracts

The following tables define the proposed machine shape. Executable JSON Schemas and validators are implementation deliverables after technical review, not supplied as working code here. Reject unknown fields, non-finite numbers and type coercion. The [JSON examples](reviewed-dossier-serving-interface-examples-v01.json) are labelled synthetic shapes; they are not actual release records or executable tests.

### Request: `reviewed_serving_request/v1`

| Field | Type / rule |
|---|---|
| `kind` | Exact discriminator `reviewed_serving_request/v1` |
| `request_id` | Nonempty bounded identifier; tracing only, never a path |
| `language` | `en` or `fr` for deterministic interface labels; source quotations remain original English |
| `tasks` | Ordered nonempty array; proposed maximum eight; unique `task_id` |
| `tasks[].task_id` | Caller-supplied stable ID, unique within the request; no cross-task borrowing |
| `tasks[].product` | Existing identity enum: `unknown`, `family_unknown`, `mabselect`, `sure`, `sure_lx`, `other`, `contradictory` |
| `tasks[].deposit_context` | Existing enum: `unknown`, `precipitated_substances`, `hydrophobic_deposits`, `mixed_other` |
| `tasks[].requested_items` | Explicit nonempty unique item list from the initial target catalogue below |
| `tasks[].excluded_items` | Unique item list, defaults empty; item present in both lists is excluded and remains visible as such in audit |
| `tasks[].input_label` | Optional original user wording, audit/display data only; no routing, alias inference or policy execution |

Procedure/phase is fixed by this release to MabSelect cleaning documentation; the source steps retain their distinct cleaning and follow-up-wash ownership. No phase is guessed from arbitrary input text. Product and category are required structurally; their explicit `unknown` values produce clarification rather than malformed input. `contradictory` preserves the conflict and never picks a winner. Raw labels remain data; no new alias parser is implied. Sources, reviews, release IDs, byte limits, URLs and filesystem paths cannot be supplied as authority by the client. The service generates field origins as JSON pointers into the preserved request; a future text interpreter needs its own occurrence/origin contract.

Initial item catalogue, **proposed**: `cleaning_options`, `restricted_sequence`, `followup_buffer_pH`, `pressure_limit`, `solvent_hold_time`. The first adapter only implements registered documentary purposes; arbitrary selectors are invalid input. Numerical pressure and solvent hold-time requests are deliberate scoped-abstention cases, not authorization to search other products.

### Registered bundle mapping

Use exactly the five bundle keys and indispensable source sets in [contract section 3](REVIEWED-DOSSIER-SERVING-CONTRACT-V01.md). Each mapping records:

- `bundle_key`, mapping version and hash; `review_scope` Q05/Q06/N06/N07/Q09;
- allowed exact products, documentary category and supported request items;
- original source/review artifact bindings, condition predicates and required IDs;
- source role (`scope`, `procedure`, `warning`, `clarification_context`);
- alternative group, sequence identity and mandatory following-wash/warning links;
- permitted already reviewed summaries and reservation visibility requirements.

Condition predicates are finite enum comparisons and AND/OR composition with three-valued evaluation. Preserve unevaluated original source wording separately. No general expression evaluator, user script, fuzzy alias, unit conversion or inferred material property. Map `cleaning_options` to Q05 plus the separate Q06 block for eligible precipitated SuRe/SuRe LX, or N06 and N07 for hydrophobic context. Never interpret those bundle combinations as a combined procedure. `restricted_sequence` on plain MabSelect abstains on scope, without a general sodium-hydroxide ban. Narrower item selection must still carry every indispensable source and reservation.

### Response: `reviewed_documentary_bundle/v1`

| Field | Meaning |
|---|---|
| `kind`, `contract_version` | Explicit documentary discriminator and contract version, never a legacy symptom/cause/action result |
| `request_id`, `release_id`, `authority_digest` | Bind response to request and the exact approved active snapshot |
| `status` | Derived aggregate: `supported`, `partial`, `needs_clarification`, `abstained`, `unavailable` |
| `items[]` | Ordered task/item outcomes with `task_id`, requested item, state, reason, field origins, selected/withheld keys and clarification targets |
| `items[].state` | `supported`, `needs_clarification`, `abstained`, `quarantined`, `unavailable`, `excluded` |
| `context` | Complete delivered bundles plus deduplicated source and review objects, referenced by stable release-local IDs |
| `context.bundles[]` | Product/category binding, original force/wording, alternative/sequence/step ownership, mandatory conditions/warnings, reservations and original review references |
| `context.passages[]` | PDF hash, corpus/item ID, printed/PDF page distinction, extraction version, text hash, exact quote/offset interval and exact quote hash |
| `context.reviews[]` | Original review identity/status/date, original human message, evidence-record bindings, exact reservations and artifact hash |
| `citation_refs` | Application-created relative source-view URLs from the active immutable registry; no raw client URL |
| `coverage` | Derived item counts by state and task ownership; never model-declared support |
| `context_measure` | Canonical serialization convention, delivered byte count and configured byte limit |
| `limits` | Documentary support only; diagnosis false, suitability not established, operational authorization false, bounded corpus absence |

Never label a caption, summary or policy sentence as a verbatim handbook quotation. Preserve decimal quantities as original text initially; any future parsed numerical annotation needs its own source association and documentary validation. Do not invent percent basis, interpolation, pressure, duration or exact pH targets.

Global malformed requests produce a validation error before retrieval and no documentary answer. Release/authority errors produce `unavailable` with empty technical context. For task-level failures preserve independent valid items. Unknown or changed authority cannot be downgraded to ordinary source absence.

## 3. Local release, authority and withdrawal

The user is the withdrawal validator (CL01). The initial register must be **explicitly empty**, identified and bound to the first release; absent or unreadable is not equivalent to empty. Acceptance of this design does not create or activate that release.

Proposed local file layout:

```text
serving-data/
  active.json
  releases/<release_id>/release.json
  releases/<release_id>/mapping.json
  releases/<release_id>/withdrawals.json
  releases/<release_id>/source-index.json
```

Each artifact has a schema version and a declared hash convention. The release manifest binds its complete dependency closure, adapter/renderer versions, original scoped review artifacts and the new design record; it is excluded from its own hash. Original artifact hashing follows the recorded LF-normalized conventions; exact quoted text is never normalized before quote hashing. Keep source-record digests distinct from quote digests.

`active.json` identifies the locally approved release and manifest digest. `withdrawals.json` records its version, validator, decision reference and entries targeting versioned bundles/reviews/source identities. New withdrawal/reinstatement decisions create new immutable versions and require a reviewed release; never edit old approval records. Proposed first implementation uses a user-controlled local registry rather than external trust/signature infrastructure. Hash checking alone does not authenticate arbitrary replacement files: the service's configured authority root and explicit activation decision remain the trust boundary, outside client payloads.

At startup verify the entire release and review closure. At every request re-read/hash the small active pointer and withdrawal authority; do not rely only on mtime or a cached startup flag. If either changed, invalidate the loaded snapshot before selection, reload and revalidate a complete approved release. Never continue silently with stale authority. A pointer digest mismatch, missing register, unknown activation decision or invalid authority gives `unavailable`.

For concurrent changes, proposed implementation serializes local activation and lookup snapshot acquisition, writes pointer replacements atomically and checks the authority again before returning a response. If it changed during assembly, discard the response and return `unavailable: authority_changed`; do not silently retry a technical answer against another release. An already returned response remains bound to its old release and is rechecked on any later interaction. No promise of retroactively retracting already displayed browser text is made.

Revoked/unresolved admitted support is `quarantined` for the affected bundle. Corruption of a global release or authority blocks all tasks. Local reload failures must not fall back to an older release or to model prose. Activation and rollback both require an explicit reviewed local release reference (CL04); no automatic graph/public/default-chat activation.

## 4. Source-view resolution

Source IDs resolve through the release index only. The service verifies dependency hashes before delivering the excerpt. The view exposes exact original quotation, PDF identity, page indices/printed label, offsets/hash convention, scope and full linked review/reservation metadata. No user path, arbitrary file URI, raw HTML or injected URL is executed.

The source view must work from a fresh checkout plus the explicit local release artifacts, without an ignored audit directory or full PDF. The page must say whether the original PDF is available; that fact does not invent a visual check. Original document edition metadata remains inherited where originally recorded. A source view for an older release must check its current withdrawal authority and display a hold rather than imply that withdrawn support remains admissible. It must not redirect silently to a new edition's same-looking passage ID.

## 5. Context budget and allocation

CL03 accepted a configurable full-bundle budget but **did not choose its numerical value**. Proposed initial setting for technical review: **65,536 UTF-8 bytes** of canonical delivered `context`, configurable only on the service side. This is a byte/storage ceiling for the model-free handoff, not a tokenizer budget, cost estimate or reuse of frozen v03's 2,048-token experimental limit. A later model prompt needs a separate token budget.

Canonical proposed serialization: UTF-8 JSON, Unicode preserved, keys sorted, compact separators, no NaN/Infinity. Do not normalize quote text. Count bundles, full conditions/warnings/reservations, exact source objects and original review messages. Deduplicate only byte-identical versioned source/review objects and retain all task/option references. Transport framing, the budget field itself and small administrative outcomes are excluded from the context count; HTTP request/response size limits are separate.

Proposed allocation is deterministic in original task/item order, not relevance or chemical ranking. Tentatively add the complete dependency closure of the next independently deliverable item. If the resulting context fits, admit it; otherwise withhold that item as `unavailable: context_budget_incomplete` and consider the next independent item. Never remove only a warning, following wash or reservation. For `cleaning_options`, the set of alternatives required by that response is one atomic delivery item, so fitting one alternative does not license hiding the others. The order is allocation order only, never a recommended treatment order.

Additional proposed resource limits: eight tasks and a 32,768-byte request body. These are implementation defaults to review, not accepted source facts or constraints inherited from the scientific manual. User-requested budget overrides are rejected.

## 6. Outcome calculation

Apply exclusions first and keep their audit entries. They do not increase support counts. Evaluate each requested item within its own task using the states in the accepted contract. Never transfer values between tasks or suppress an independent supported task because another task needs clarification.

Aggregate the nonexcluded requested items: all supported → `supported`; at least one supported and at least one nonserved item → `partial`; none supported and any integrity/service failure → `unavailable`; otherwise any unresolved clarification → `needs_clarification`; remaining cases → `abstained`, retaining per-item quarantine. If all requested items are excluded, proposed result is `abstained: no_requested_item` with no technical context. Do not treat a request with only out-of-scope/quarantined items as an empty successful answer.

A numerical pressure or hold-time absence is limited to admitted selected excerpts. A missing required warning/review dependency is an integrity failure, not scientific absence. A user condition classified unknown cannot become true because another alternative is available. UI interface wording is deterministic; source technical quotations and original messages remain original-language data.

## 7. Conformance and implementation order

Preserve SC01–SC14 as accepted design coverage, not newly approved scientific reference labels. Proposed implementation checks:

| Check | Requirement |
|---|---|
| ST01 | Strict request schema, unique IDs, explicit unknowns, no coercion of supplied false/zero into unknown; invalid selector types are rejected, no policy/source authority overrides |
| ST02 | Five mapping keys retain exact scope and indispensable Q/N source/review sets |
| ST03 | Original approval replay and every immutable dependency verified; no global passage approval inferred |
| ST04 | Empty vs missing withdrawal register; revoked and reinstated versions preserve original decisions |
| ST05 | Startup and per-request authority validation; concurrent pointer change invalidates in-flight answer |
| ST06 | Product/context clarification, plain vs restricted block, no diagnosis or cross-product transfer |
| ST07 | Original quantities, alternatives, ordered washes, pH ownership, warnings and full reservations |
| ST08 | Source URLs resolve on the registered release and fresh excerpt inventory; corrupt/unavailable mandatory view blocks serving |
| ST09 | Task-local exclusions/conflicts, partial outcomes and derived counts; no fabricated extra task |
| ST10 | Budget equality, one-byte overflow, duplicate-source accounting and atomic alternatives; no warning truncation |
| ST11 | Malicious source text is escaped; unknown selected IDs or client URLs cannot reach renderer/filesystem |
| ST12 | Local staging verification has no model/API/Neo4j call and cannot activate itself; v03 and historical records unchanged |

Implementation order after technical review: strict machine schemas and registry fixtures → pure adapter → outcome/budget validation → typed renderer/excerpt view → SC/ST regressions → a staged local release with a concrete inventory and test report → user review before activation. No prefilled activation is permitted. New behavior needs fresh checks later; these known-corpus conformance cases are not a new generalization score.

## 8. Technical points still proposed

| ID | Concrete proposal | Approval boundary |
|---|---|---|
| TS01 | 65,536-byte context ceiling; request limit 32,768 bytes; maximum eight tasks | Numerical defaults were not fixed in the accepted design |
| TS02 | Initial five request items and existing product/category enums; no unrestricted parser | Check coverage against SC01–SC14 before coding |
| TS03 | Versioned local files, atomic active pointer and explicit user-reviewed activation | No Neo4j/public/default-chat activation |
| TS04 | Canonical UTF-8 byte measurement, shared-object deduplication and atomic `cleaning_options` allocation in input order | No model token budget or chemical ranking implied |
| TS05 | Logical request/response shapes and source-view endpoint names above | Machine schemas remain to generate and test; shape examples are synthetic |
| TS06 | Recheck authority before response delivery; discard on mid-request change, without hidden retry | Already delivered text cannot be retroactively erased by this contract |

DS/RC/CL choices are already accepted; these technical defaults are presented separately for efficient review. The original proposals remain immutable and the new decision record is the authority for their accepted design status.
