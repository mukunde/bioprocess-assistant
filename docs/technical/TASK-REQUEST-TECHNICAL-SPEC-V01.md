# Task request technical specification v0.1

Status: **T01-T08 and TC01-TC04 approved as technical design; not implemented**,
25 October 2026. See the [collective technical decision](../decisions/2026-10-25-task-request-technical-review.json).
The declarative files in this directory are specification artifacts. No existing
application, schema validator service, retriever or v06 code loads them. No model,
embedding, retrieval/planning experiment or paid API was used to prepare them.

## 1. Authority, artifacts and scope

Approved design basis:
[D01-D08/C01-C04](../decisions/2026-10-25-task-request-review.json),
[M01-M14/R01-R08 and allocation](../decisions/2026-10-25-task-request-matrix-review.json),
[contract](../REQUEST-CONTRACT-V01.md) and
[context matrix](../REQUEST-CONTEXT-MATRIX-V01.md).
Those earlier approvals did not automatically approve the wire format, aliases,
role metadata, ranking or thresholds. The separate T01-T08/TC01-TC04 collective
review now approves this technical design; it does not activate runtime code,
approve new scientific facts or establish measured performance.

| Artifact | Role |
|---|---|
| [task-request-v01.schema.json](task-request-v01.schema.json) | Design-approved JSON Schema 2020-12: public structured submission, internal canonical envelope and context-plan definitions |
| [task-request-catalog-v01.json](task-request-catalog-v01.json) | Design-approved exact product labels, explicit qualified-label aliases and technique vocabulary |
| [task-request-source-adapter-v01.json](task-request-source-adapter-v01.json) | Design-approved corpus bindings, role candidates, eligibility, ranking and resource policy |

Initial S control: HiTrap Blue HP 1 mL/5 mL and the reviewed general IEX/HIC/SEC
topics. Preserve the exact existing 25 eligible excerpt identities; E118-I and
E121-EQ stay excluded. The adapter exposes only the relevant initial roles, not
every possible question that the 25 excerpts could support. Other products and
advanced topic-specific procedures are not silently added. No source review,
publication state, scientific applicability or real-process authorization changes.

## 2. Public machine input and internal records

### Public submission

The schema root accepts only `structured_submission`, version
`task-request-0.1-tech-proposed`, with `input_mode=structured`, language EN/FR and
one or more tasks. All objects reject undeclared properties. Earlier contract
examples were conceptual illustrations, not instances of this wire format.
The preimplementation IDs ending in `tech-proposed`/`proposed` are retained for
traceability; the approval status and decision record are authoritative. They do
not mean pending human review and do not identify a deployed API.

Each task has task ID, optional sample label, intent, product/column states,
facts, information items and task/item-scoped exclusions. Each item has ID,
stage, information selectors, answer mode, technique context and facets.
The initial stage/information combinations are exactly those represented by
M01-M13; M14 is a product/format resolution gate rather than an information item.

| Field group | Format and meaning |
|---|---|
| Product | State plus stated label; no caller-supplied canonical identity or approval |
| Column | State plus a decimal-string bed volume and unit; no inference from a sample volume |
| Facts | Scoped quantity/Boolean/text slot, with user-observation, user-assumption or documentary-scenario role |
| Information | Closed selector list; no numerical answer, source IDs or expected response in a request |
| Answer mode | `single_context` or `compare_documented_alternatives`; the latter must be explicit |
| Technique context | State plus literal IEX/HIC/SEC/cation-exchange labels resolved by the same catalog |
| Facets | Buffer use, selected elution mode, and syringe-query mode as explicit state/value slots |
| Exclusion | Owner task and optional owner item, plus typed stage/information/product selector |

`single_context` does not mean selecting one of a source's alternative endpoints
or mixing alternative buffers: documented logic/qualifiers always survive. For
M06, it requires a selected elution mode for one mode-specific quantity; explicit
comparison keeps both documented modes. Disabled/inapplicable form fields can be
represented as `not_applicable` with a matrix-derived reason and application-origin
trace, not an invented user observation. A genuinely unmentioned relevant value
remains `not_supplied`.

Known slots require a value. `unknown` and `not_supplied` require JSON null.
`not_applicable` also requires a reason. Numeric values are decimal strings, not
JSON floats: initial quantities use mL or mL/min and no conversion. Numeric zero
is not missing; a zero bed volume is a semantic invalid value, whereas a genuinely
observed zero flow can remain a supplied observation. Units must fit the field:
bed/sample/loaded volume use mL, observed flow uses mL/min. A supported product
with a different positive bed volume is an unsupported format, not a missing size.

### Structural validation versus semantic validation

JSON Schema checks shape, field names, types, null/state branches, legal enum
values and forbidden extra fields. It cannot establish source fidelity or every
cross-field rule. A future implementation must additionally check:

- Unique task IDs and globally unique item/exclusion IDs; every scope reference
  resolves to its enclosing task/item. A consistent task has one assertion per
  fact key. Preserve duplicate/conflicting raw assertions and their input pointers;
  emit `conflicting_input` and block affected units, never overwrite a value.
  Separate tasks only for explicitly distinct samples/scenarios. Never repair a
  same-scenario contradiction by automatically splitting it (TC03).
  No hidden inheritance across tasks.
- Units and numerical domain; consistent explicit size in a qualified product
  label and column field. Do not overwrite either side of a conflict.
- Allowed stage/information/facet combinations and justification for not-applicable
  fields; selected mode versus requested comparison is coherent.
- Product resolution, required-context checks M01-M14, inclusion/exclusion
  intersections, fact contradictions and mandatory warning policy.
- Every substantive normalized value has a real origin; offsets/pointers resolve
  against the preserved input. A schema-valid claim of origin is not itself proof.

Malformed structure is rejected before planning with field paths. A well-formed
same-task contradiction is represented as `needs_clarification`, not silently
repaired, discarded, or treated as missing documentary support. An understood
out-of-scope product and an ambiguous product have distinct diagnostics.

### Internal canonical request

`#/$defs/canonical_request` is an application-produced record, never an accepted
public submission type. It preserves the submitted task fields and input snapshot,
binds schema/catalog/adapter/corpus versions, attaches catalog resolutions,
field origins and issues. The downstream stage uses these typed fields/resolutions;
it must not independently route from the original free text.

For structured input, `input_sha256` hashes the saved input object serialized
with sorted keys, compact separators, UTF-8, `ensure_ascii=false`, no NaN and no
Unicode normalization. It is a reproducible content digest, not the original HTTP
byte hash or a claim of RFC canonicalization. Future free-text input hashes its
verbatim UTF-8 bytes. The schema reserves that internal snapshot type but does not
implement or expose a free-text public endpoint.

Origins are form JSON pointers, original-text `[start,end)` Unicode character
spans, explicit `not_stated` references to the input digest, or application-assigned
metadata with a reason. No fabricated span for an absent field, no offset into a
translation, and no user phrase treated as manual evidence. Preserve original
column state separately from an effective value explicitly present in a qualified
product label; the alias/catalog version and that input origin explain the value.

## 3. Catalog and aliases

Normalize labels with NFKC, casefold and collapsed whitespace. Do not remove
punctuation, accents, tokens or size qualifiers, and do not use substring/fuzzy
matching or a lexical similarity threshold for identity resolution.

| Input | Approved design resolution |
|---|---|
| HiTrap Blue HP | Exact label for `product:hitrap_blue_hp`; size still separate |
| HiTrap Blue HP 1 mL / 5 mL | Explicit catalog alias to the same product, carrying that stated size and its input origin |
| HiTrap, Blue, Blue HP, Blue Sepharose | Ambiguous; the small active catalog does not make a partial name unambiguous |
| Blue Sepharose 6 Fast Flow or the listed SuRe/SuRe LX/Phenyl/Selection Kit labels | Identified label outside initial scope, never an alias for Blue HP |
| Unlisted spelling | Unresolved; no automatic typo repair or best-score identity |

The catalog's `reviewed_alias` rows are approved as technical catalog design
under T03. This neither activates runtime resolution nor approves a new source.
Canonical IDs are design identifiers, not new graph nodes or altered ontology IDs.
IEX/HIC/SEC labels have explicit EN/FR entries. Cation exchange retains its subtype
and an IEX-family link; the link cannot supply a withheld pH/pI condition.
Catalog lookup applies to typed labels, not a scan of an entire question that
would activate a product merely mentioned in an exclusion.

## 4. Corpus adapter and source-role assignments

The adapter pins the current evidence registry, source-review manifest, document
identity and inherited source/dependency policy by hash. Its policy-file pointer
imports eligibility and dependencies, not the old v05 routing algorithm. Raw
historical pending flags do not approve sources; the active reviewed corpus
manifest and exclusions remain authoritative. Fingerprints include pages,
quote hashes and text offsets for all source records, including blocked ones;
retaining a blocked ID's metadata does not make its text selectable.

| Approved matrix topic | Approved design candidate roots | Support/dependency distinction |
|---|---|---|
| M01 principle | E118-M | General method principle only; no product recipe |
| M01 explicit general clarification | Joint E118-USE + E118-C + E118-M | A joint candidate, not three interchangeable one-source answers; counts three distinct roots |
| M02 loading flow | E121-L | E121-F and all scope/warning dependencies retained |
| M03/M04 washing information | E121-W | Same atom can serve different permitted information units |
| M05/M06 elution flow/mode/quantity | E121-E | Mode and size conditions remain item-specific |
| M07/M08 formulations | E121-B | Binding/elution-use facet controls permission to use adjacent content |
| M09 syringe note | E121-L, with E121-F as direct note support | Choosing L retains the reviewed loading association and F dependency; no separate invented note procedure |
| M10 workflow position | E120-A | Includes multiple named products in the quote; binding is limited to the resolved supported product |
| M11 pressure | No candidate | Bounded missing-source result over exactly 25 eligible excerpts |
| M12/M13 | No eligible candidate | E121-EQ/E118-I remain quarantined; supported sibling items remain independent |

Eight distinct content roots are exposed by this initial interface. All 25 eligible
excerpts retain their existing identity/policy, but unrelated bovine or detailed
albumin procedures do not become candidates because they share words. Compute
dependencies only for the chosen roots and declared guards, not by appending an entire source family.
The workflow-position candidate additionally requires E120-W and its closure as
an approved role-level guard. This preserves the existing warning without changing
the historical dependency policy or promoting a source. Other protocol bundles
already inherit that warning through E120-P.
No hardcoded question IDs, expected answers or evaluation-required sets enter
input interpretation. Source IDs occur only in the versioned, reviewed corpus
adapter and trace metadata.

This is deliberately a small **reviewed-role navigation control**, not a scalable
unrestricted RAG system. Most roles currently have one candidate. Its diagnostic
value is to isolate interpretation from source assembly; do not advertise a
new semantic-retrieval benchmark result or compare directly with old v05 scores.
Some old X wording includes generic/out-of-scope product names; new canonical
references must respect C01 and be reviewed rather than silently reusing old labels.

## 5. Ranking and numeric thresholds

Split an item's requested information into separately accounted units, retaining
task/item ownership and facet context. This permits unknown size to block washing
flow while stopping criteria remain supported. The scheduler still visits items,
not a flattened global list of unrelated units.

Apply hard eligibility/scope/context gates **before** lexical ranking:

| Gate | Approved design value/rule |
|---|---|
| Identity | One exact catalog label entry; explicit ambiguous/out-of-scope/unresolved states do not pass as a guessed product |
| Source eligibility | Every transitive bundle member eligible, correct version and intact; zero quarantine bypass |
| Role/scope | Registered reviewed role, compatible product/method, required size/mode/facet context; no unknown-scope candidate |
| Useful support | At least **1** not-yet-covered, unblocked requested information unit directly supported by the candidate |
| Minimum raw BM25 score | **None** (`null`); zero is admissible only after direct reviewed-role support passed |
| Relative lexical cutoff | **None** (`null`); no 0.65-style best-family fallback |
| Global resource limits | **6** distinct admitted roots; **2,048** serialized context tokens |

Order admissible candidates lexicographically by:

1. Number of newly covered requested units, descending. Extra unsolicited facts
   contribute no coverage and no ranking bonus.
2. Product specificity: explicit single-product support (2), explicit reviewed
   multi-product support containing the product (1); unknown (0) is ineligible.
   A genuinely product-free general topic uses a neutral value, not a guessed identity.
3. Column specificity: exact documented format (2), explicitly documented set
   containing the format (1); unknown required size is ineligible. If size is not
   required by the matrix, use a neutral value and do not reward guessing it.
4. BM25 tie-break score, descending, then sorted root-ID tuple ascending.

Specificity annotations must be documented in the reviewed adapter; they are not
inferred from a source's lexical title. The present excerpts share product/column
scope, so many grades will be equal. These grades are not diagnostic confidence.

BM25 uses k1=1.2, b=0.75 and inherited dependency-context indexing over the
inherited **eligible searchable** records, not just the eight interface roots.
Index original English quotes plus dependencies without the old vocabulary
projection or bilingual token aliases. Build its query from positive canonical
role/product/method/stage/information lexemes, not original question words,
exclusion text or gold answers. Missing root lexical hits contribute zero.
The adapter pins the existing lexical primitive/stop list and BM25 equation by
file hash, with bilingual aliases disabled. Use one common positive query per item
visit, built from all its mapped ready roles and resolved canonical labels/codes,
with sorted unique tokens. Extra guard sources affect assembly, not BM25 statistics.
The old search cutoff and old assembler are not the specified planner.
For a multi-root candidate take the arithmetic mean of root scores; round this
tie-break score to 12 decimal places with decimal ROUND_HALF_EVEN, retaining the
raw score in audit. No ranking execution or score calibration is claimed here.

There is no lexical fallback to an unmapped family. A missing role mapping is
`unsupported_selector`/adapter gap, not evidence that the manual lacks the fact.
The positive reviewed mapping replaces the old unrelated-word family gate; no
embedding threshold or self-reported model confidence is introduced.

## 6. Joint scope, unavailable data and item completion

Resolve exclusion intersections per task/item/stage/information, not request-wide
word sets. A product used as context is not a request for all its procedures.
Buffer formulation and operating elution are separate stage kinds. For an explicit
comparison of binding and elution formulations, use two preparation items in the
same task, with scalar `buffer_use=binding` and `buffer_use=elution` respectively
(TC02). Retain their separate identities even when both bind to E121-B. This does
not authorize pairing formulations or activate operating-elution parameters. A same-task
include/exclude overlap blocks affected units; separate-task scopes do not conflict.

`unit_result` preserves independent `interpretation_state`,
`documentary_support_state`, scoped canonical `issue_ids` and a complete
`diagnostics` list with interpretation/documentary-support/assembly dimensions
(TC01). Its existing `state` remains a presentation summary, never the sole
diagnostic or a replacement for these dimensions. In the supported case it must
agree with ready interpretation, eligible support and complete admission.

Assess support independently only where the relevant role is identifiable
without guessing missing context. Otherwise use `not_assessed`; do not infer
source absence. A known Blue HP equilibration request with unknown column size
may retain both a missing-context interpretation diagnostic and quarantined
support. Clarifying the size cannot lift the quarantine. Do not solicit a size merely to
imply it would unlock unavailable support; retain the diagnostic without an
unnecessary clarification question. An ambiguous product
that prevents a reliable role assessment must not be forced onto that source.
Do not claim a budget failure for a blocked unit that was never assembled.

All canonical issue references must resolve and match the unit scope. A blocked
unit has no admitted source IDs or context binding. A source shared with a ready
sibling unit can still be present, bound exclusively to that permitted sibling.
Diagnostic codes are machine identifiers with nonempty details; their messages
are not evidence or scientific validation.

Context lookup and summary result statuses are separate:

- `supported`: complete eligible support for this unit admitted with all dependencies.
- `needs_clarification`: unresolved input binding/conflict, not source absence.
- `missing_source`: specifically the reviewed absence case, such as M11 pressure.
- `quarantined`: relevant known source unavailable under active policy.
- `out_of_scope`: understood but outside initial product/topic/format perimeter.
- `unsupported_selector`: legal vocabulary used in a combination without a reviewed role.
- `unsupported_transformation`: an unapproved calculation/interpolation rather than quoted lookup.
- `budget_incomplete`: eligible useful support exists but did not fit.

For the syringe facet, `note_lookup` repeats a documented approximate reference.
`reference_flow_check` can only repeat a literal reference pair for the chosen
column and exactly matching supplied flow/unit; otherwise report unsupported
transformation. It never computes drops for a new flow. This design-approved facet is
not a new scientific calibration or a general conversion rule.

An item with several units may be partially served. The internal plan records
all units and reasons, not one ambiguous complete flag. `all_requested_units_accounted_for`
means each requested unit has an explicit outcome, not that every answer exists.
`all_supported_ready_units_covered` requires all units classified as eligible and
unblocked to have admitted support; it cannot excuse missing adapter mappings.
Also report interpretation issues and unserved units. Applicability to a real
sample remains a separate unevaluated/unknown decision unless reviewed conditions
and supplied facts establish it; no laboratory authorization follows.

## 7. Scheduling, budget and output trace

Use the approved item order A1, B1, A2, B2, etc., preserving task-local order.
Each visit considers one next candidate for uncovered ready units. Recompute
marginal coverage against existing associations; skip zero-use candidates. Revisit
the interleaved order for further candidates, considering each candidate at most
once per item. Stop when supported units are covered or queues exhausted.

Admit a candidate only if its complete joint roots and inherited dependency
closure plus mandatory guard closure fit both global limits. A joint three-root bundle costs three distinct
root slots; dependencies do not consume another root slot merely by being present.
Deduplicate roots and source atoms across tasks but retain every permitted binding.
An over-budget candidate consumes no admitted-root slot: record it and continue
other candidates/items. A source already present costs no new root slot, but its
additional binding still consumes context tokens and must fit. Never truncate
quotes, warnings, footnotes or source metadata; do not give each task a new budget.

`#/$defs/context_envelope` has two fields: `source_passages` and `bindings`.
Passages retain the exact original ID, PDF page/index, scope, quote/hash and text
offsets. Bindings associate each permitted information unit with task/item,
resolved product, column state, stage, facets and supporting source IDs.
They are not generated numerical answers or scientific approvals.

Count the **entire actual context envelope**, including bindings, using the pinned
local cl100k_base asset and tiktoken identity in the policy. Serialize compact JSON
with top-level source_passages then bindings; passage keys follow the schema's
declared order; source atoms follow first admission order, using depth-first traversal in declared
root/dependency order (dependencies before root), then declared guard closures; bindings
follow request/task/item/information order. Facet keys follow the declared schema
order. Preserve Unicode text unchanged, use UTF-8, no ASCII escaping or NaN.
Tokenizer assets are never downloaded on failure. Audit-only logs are outside
the context; if later sent to a model, their tokens must be counted too. Future
user prompts/answers remain separate from this context cap.

`#/$defs/plan_result` defines the internal summary layout. Audit must additionally
record input/catalog/adapter/corpus hashes, origin references, resolution choices,
all candidate gates and score components, rejected bundles, marginal token costs,
selection order and per-unit outcomes. Startup corruption/hash mismatch is an
operational error, not an invented missing-source result. If no supported unit
exists, keep an empty context and explicit diagnostics rather than padding it.

## 8. Illustrative public submission

This R04-shaped example requests washing flow and stopping criteria while the
column size is explicitly unknown. It is specification data, not an executed
request or a new human-approved machine mapping.

```json
{
  "document_kind": "structured_submission",
  "contract_version": "task-request-0.1-tech-proposed",
  "input_mode": "structured",
  "language": "en",
  "tasks": [{
    "task_id": "A",
    "sample_ref": null,
    "intent": "documentary_procedure_lookup",
    "product": {"state": "provided", "value": "HiTrap Blue HP"},
    "column": {"state": "unknown", "value": null},
    "facts": [],
    "items": [{
      "item_id": "A-wash",
      "stage": {"kind": "operating_phase", "code": "washing"},
      "information": ["flow_rate", "stopping_criteria"],
      "answer_mode": "single_context",
      "techniques": {"state": "not_applicable", "value": null, "reason": "Product-specific documentary lookup"},
      "facets": {
        "buffer_use": {"state": "not_applicable", "value": null, "reason": "No formulation request"},
        "elution_mode": {"state": "not_applicable", "value": null, "reason": "Washing item"},
        "syringe_query_mode": {"state": "not_applicable", "value": null, "reason": "No syringe-note request"}
      }
    }],
    "exclusions": []
  }]
}
```

Expected design behavior: clarify size for the flow unit, retain supported endpoint
context for the other unit, never assign a flow to the unknown column. The atom
can contain both documented flow ranges without authorizing either in the answer.

| Conformance example | Structural expectation | Later semantic expectation |
|---|---|---|
| Submission above | Valid | Partial handling as described, not an observed result |
| Add a caller `source_ids` field | Invalid | No source-policy override path |
| Replace decimal-string bed volume with JSON number | Invalid | No silent type/unit conversion |
| Qualified product label says 5 mL, explicit column says 1 mL | Can be shape-valid | Conflict, never last-wins |
| Same task includes/excludes washing flow | Can be shape-valid | Scoped clarification; no affected values |
| Internal canonical_request submitted to the public root | Invalid | Only the application creates that record |

## 9. Approved review and implementation boundary

The actual collective human message approves T01-T08 and TC01-TC04; its original
French wording and the pre/post clarification artifact hashes are preserved in
the [technical decision record](../decisions/2026-10-25-task-request-technical-review.json).
It is one collective approval, not twelve independent exchanges.

| Decision | Approved technical meaning |
|---|---|
| T01 | Strict versioned public submission, separate application-produced canonical record; no caller source-policy override |
| T02 | Four explicit slot states, decimal-string quantities, units, no automatic conversion |
| T03 | Explicit catalog aliases; ambiguous/out-of-scope/unresolved identities remain distinct |
| T04 | Reviewed source-role navigation with task/stage/information/facet ownership |
| T05 | Atomic support/context/guard bundles; joint clarification sources and mandatory warning preserved |
| T06 | Coverage, product specificity, column specificity, then BM25 tie-break; no raw/relative lexical cutoff |
| T07 | Per-information partial outcomes, with all blocking reasons retained |
| T08 | Count the full context including bindings; six roots and 2,048 tokens globally |
| TC01 | Independent interpretation and documentary-support states, all scoped diagnostics; clarification cannot lift quarantine |
| TC02 | Two preparation items for a binding/elution formulation comparison, no inferred pairing |
| TC03 | Preserve same-scenario contradictions; split only explicitly distinct scenarios |
| TC04 | Deterministic conformance checks before freezing implementation or preparing a new prospective evaluation |

### Required future conformance checks (TC04)

These are implementation acceptance requirements, **not tests executed against
a planner**. All checks must pass before the method is frozen. JSON-shape checks
alone do not establish semantic behavior or research performance.

| Check | Required behavior |
|---|---|
| CF01 States and types | Preserve unknown versus not-supplied, false and zero; reject undeclared public fields, numeric JSON values where decimal strings are required and forged public canonical records |
| CF02 Unit roles | Detect wrong volume/flow units and invalid bed-volume domain; no automatic conversion |
| CF03 Identity and format | Qualified 5 mL label versus supplied 1 mL column is a conflict; generic HiTrap remains ambiguous; known other product/unsupported size stays out of scope |
| CF04 Exclusions and ownership | Same-task overlapping inclusion/exclusion blocks affected units only; no context transfer across tasks, stages or formulation/operation kinds |
| CF05 Contradictory facts | Opposing assertions concerning one scenario remain in the input snapshot with origins, produce scoped conflicting-input issues, and are neither overwritten nor split automatically |
| CF06 Partial support | Unknown washing column blocks flow, while eligible stopping criteria remain independently servable without assigning either adjacent flow range |
| CF07 Concurrent diagnostics | Known quarantined equilibration support and unresolved column context coexist; clarification does not remove the quarantine, and no blocked-unit binding is admitted |
| CF08 Missing versus unassessed | Bounded pressure absence refers only to the 25 eligible excerpts; a role that cannot be resolved is not falsely classified as source absence |
| CF09 Buffer comparison | Two preparation items bind separately to binding/elution-use roles, preserve alternatives, and never pair recipes or activate operating-elution values |
| CF10 Atomic sources and guards | Keep original quotes, provenance, dependency order and warnings; joint clarification counts three distinct roots; excluded E118-I/E121-EQ never enter context |
| CF11 Ranking and traces | Eligibility precedes ranking; direct mapped zero-score support remains admissible; no unmapped lexical fallback; ordering and scoped rejection traces are reproducible |
| CF12 Global allocation | Check exact six-root and 2,048-token boundaries including bindings, round-robin item order, deduplication, no truncation, continuation after an oversized bundle, and explicit budget-incomplete outcomes |

The next bounded implementation can cover structural/semantic validation, the
catalog, the offline structured control and its trace/conformance checks, when
requested. No free-text interpreter, Chainlit interface, graph migration, new
scientific rule, real-process authorization or answering model is included here.
Documentary conditions remain distinct from established real-sample applicability.

Only after conformance passes should the implemented versions be frozen and new
canonical intent/source references reviewed for a prospective comparison. No new
prospective dataset, performance threshold or measured success is approved by this
technical decision. Most initial roles have one candidate; this control isolates
interpretation and source assembly, not unrestricted whole-manual retrieval.
Historical evidence, decision records and frozen v05 results remain unchanged.
Earlier records describing technical review as pending remain historical statements
at their original decision date; this separate decision supersedes that status.
