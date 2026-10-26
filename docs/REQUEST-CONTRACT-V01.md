# Task request contract v0.1 — design proposal

Status: **D01-D08, C01-C04, M01-M14, R01-R08 and allocation modalities approved
on 25 October 2026; not implemented**. R08 includes the approved sample-volume
correction; wire format, catalog and within-item ranking remain to be specified.
This document defines an intended request representation, not an executable
schema, an approved new ontology, a v06 implementation or a measured improvement.
No interpreter or retrieval experiment was run to prepare it.

The [decision record](decisions/2026-10-25-task-request-review.json) preserves the
actual collective human approval and its exact original French quotation.
Approval concerns the twelve named decisions, not every illustrative mapping or
field name in this document. The initial implementation perimeter is HiTrap Blue
HP 1 mL/5 mL plus needed general IEX/HIC/SEC questions; other product identities
must not be silently added. Offline structured cards and a readable per-task
preview precede Chainlit and free-text integration. No form is implemented here.

Approved detailed artifacts: the [required-context matrix](REQUEST-CONTEXT-MATRIX-V01.md)
and [eight representative cards](experiments/structured-request-review-cards-v01.md).
The [second collective decision](decisions/2026-10-25-task-request-matrix-review.json)
records their validation and allocation handling. These approvals do not validate
the complete wire-format example, every earlier X mapping or the experimental
protocol's proposed future dataset size and thresholds.

The [frozen v05 X report](experiments/cytiva-v05-prospective-results.md) motivates
the design: exclusions and nested negations remain fragile, separate tasks become
false global conflicts, and routing vocabulary disagrees with lexical support.
The existing [claim contract](CLAIM-CONTRACT-V02.md) remains the contract for
documentary assertions. A request describes what the user asks; it cannot create
claims, approve sources, establish real-process suitability or authorize action.

## 1. Decision and minimum scope

Use one canonical request representation for a structured form and for interpreted
free text. The retrieval/assembly stage receives that representation rather than
independently reinterpreting the original text with another set of routing rules.
Keep the original input for audit, not as a second hidden decision path.

A **task** owns one product context, one column context and zero or more requested
information items. Split tasks when the user supplies different column sizes or
product scopes; several tasks may still refer to the same sample. Two phases on
the same product/column can be two items in one task. A task is a request scope,
not a chromatography step, a sample identity or a causal assertion.

Minimum concepts:

| Concept | Purpose | Example |
|---|---|---|
| Request | Original input and a list of tasks | Compare two independent preparations |
| Task | Ownership of context, observations, items and exclusions | A: loading a 1 mL column; B: washing a 5 mL column |
| Product | Exact stated product, separately resolved against a versioned catalog | HiTrap Blue HP; generic HiTrap remains ambiguous |
| Column | Explicit column attributes, not sample volume or flow | Bed volume 1 mL |
| Information item | Stage/topic and requested information, with a stable local ID | A-load: sample application, flow range |
| Exclusion | A typed selector scoped to a task or item | B only: exclude operating elution information |
| Input fact | User-supplied scenario/observation and its uncertainty | Minor contaminants interfere: false for A, true for B |
| Ambiguity/conflict | An unresolved interpretation with affected scopes | Same task both includes and excludes washing flow |

Canonical codes used below are **proposed design vocabulary**, not newly approved
graph identifiers. Catalog definitions, aliases and mappings need review before
implementation. The initial contract does not add a graph database or dependency.

## 2. Required fields and meaning

### Request envelope

| Field | Intended content |
|---|---|
| `contract_version` | `task-request-0.1-draft`; future incompatible changes get a new version |
| `request_id` | Application-assigned identity, not a question-reference ID used for routing |
| `input` | `mode`, language, verbatim text for free text or submitted form snapshot, UTF-8 content hash |
| `tasks` | Ordered scopes with unique task IDs; order preserves presentation, not procedural sequence |
| `interpretation_issues` | Ambiguities/contradictions with affected task/item IDs and input origins |

The application separately binds the catalog, interpreter, corpus, active source
review and execution-policy versions. Users cannot set source approval flags,
override quarantine, insert gold source IDs or raise hard resource limits through
this contract. Request IDs must not select reference answers or expected passages.

### Task and item fields

| Field | Intended content and constraint |
|---|---|
| `task_id` | Local immutable identity used by every item, exclusion and later result |
| `sample_ref` | Optional label supplied by the user; shared label does not merge tasks |
| `intent` | Initial choices: documentary procedure lookup, procedure comparison, mechanism explanation, documentary applicability or context clarification |
| `product` | Input state, stated label, catalog resolution and origin; a negative mention is not a positive product selection |
| `column` | Input state and explicitly supplied attributes; initial numeric attribute is bed volume |
| `facts` | Scoped scenario facts with origin, value/state and wording; none inferred from source selection |
| `items` | Unique `item_id`, stage/topic, information selectors, optional facets, input origins |
| `exclusions` | Unique exclusion ID, task/item scope, typed selector and input origin |

Each item belongs to its enclosing task. Do not permit an item to silently
redeclare a different product or column; create another task instead. For an
ambiguous pronoun such as “use that flow for the other one,” retain an issue
rather than inventing a task binding.

### Supplied, unknown and absent are different

Product, column and relevant facts carry one of these states:

| State | Meaning |
|---|---|
| `provided` | Explicitly supplied by the user; not scientifically verified |
| `unknown` | The user explicitly says they do not know |
| `not_supplied` | The input does not state it |
| `not_applicable` | This documentary question has no such context requirement, with an explicit reason |

Only `provided` carries a substantive value. A false Boolean is a real supplied
value, not missing data. A `not_applicable` classification must be justified by
the information item; it cannot bypass context needed for numerical instructions.
Uncertainty about contaminants does not require a confirmed diagnosis before
asking useful clarifying questions or retrieving general principles.

Product resolution is separate from input state: `exact_label`, `reviewed_alias`,
`ambiguous` or `unresolved`. An unambiguous abbreviation may resolve only through
a reviewed catalog mapping, never through a best lexical score alone. Do not
merge HiTrap Blue HP with Blue Sepharose 6 Fast Flow, SuRe with SuRe LX, or every
HiTrap with Blue. Shared source support does not make product identities equal.

### Column quantities

Use decimal strings with explicit units for supplied quantities, for example
`{"bed_volume":{"value":"1","unit":"mL"}}`. Keep the original representation
and its origin. Bed volume, available sample volume, volume actually loaded,
flow and column volumes are different concepts. A stated sample volume does not
establish that it will all be loaded. Do not infer column size from sample volume,
flow or drops.
A size explicitly present in the complete product name may be extracted with
that text span as origin. Missing or contradictory units require clarification
where the requested information depends on them; no automatic conversion is
introduced by this proposal.

## 3. Separate stage from requested information

| Stage kind / code | Typical information selectors |
|---|---|
| `operating_phase / sample_application` | `flow_rate`, `application_method`, `syringe_correspondence` |
| `operating_phase / washing` | `buffer_role`, `flow_rate`, `column_volumes`, `stopping_criteria` |
| `operating_phase / elution` | `buffer_role`, `flow_rate`, `column_volumes`, `elution_mode` |
| `operating_phase / equilibration` | `buffer_role`, `flow_rate`, `column_volumes` |
| `preparation / buffer_preparation` | `buffer_formulation`, with facet `buffer_use=binding` or `elution` |
| `general_topic / method_selection` | `principle`, `method_alternatives` |
| `general_topic / product_applicability` | `applicability`, `relative_position_in_workflow` |
| `general_topic / operating_limits` | `maximum_pressure` |

These are the smallest proposed selectors needed for current cases; their names
are not numerical answers. Selecting `flow_rate` requests a documented value;
it does not place a value in the request. A supplied observed flow belongs in
task facts, separately from the requested parameter.

**An elution-buffer formulation is not an elution procedure.** Its stage is
buffer preparation and its facet is elution use. It does not request elution
flow, gradient settings or operating volumes. Likewise, mentioning a phase in
a comparison or exclusion does not make it positively requested.

The meaning of a selector must be shared by input interpretation, source-role
mapping and result accounting. Maintain one versioned mapping rather than letting
routing recognize a concept that lexical retrieval cannot represent. Such a
mapping must be reviewed; it must not hardcode question IDs or reference source
IDs in the interpreter. Source-role mapping belongs to the reviewed corpus adapter.

## 4. Exclusion and conflict rules

An exclusion has an explicit owner and selects a product, stage, information
type or all operating information in that scope. Resolve phrases such as “B only”
before applying polarity. No implicit cross-task inheritance is allowed in the
first version. A request-wide exclusion is expanded to explicit affected scopes
while retaining its original origin; unclear scope remains an issue.

1. Retain both positive and negative assertions; never silently apply last-wins.
2. A conflict exists when an inclusion and an exclusion overlap in the **same
   task, stage/topic and information scope**, after resolving ownership.
3. A broad exclusion of washing overlaps washing flow and quantity requests.
   It does not overlap a buffer-preparation item merely containing the word
   elution. Product context alone is not a positive request for every procedure.
4. “Do not exclude elution” is a negated exclusion, not a request to omit elution.
   Preserve the original wording and normalized relation; do not count keyword
   occurrences as independent contradictory instructions.
5. Inclusion for A and exclusion for B is not a conflict. Contradictory scopes
   for the same task require clarification before supplying affected parameters.
6. Block only affected items when ownership is clear. An unresolved task binding
   can block every dependent item. Do not discard unrelated supported requests
   because another item lacks a source or needs clarification.
7. Distinguish request negation from a fact: “contaminants do not interfere” is
   a scoped scenario fact, not an exclusion of interference information.
8. User exclusions cannot strip mandatory warnings, dependencies or quarantine
   checks. If the requested presentation is incompatible with mandatory scope,
   withhold that procedural item and explain the limitation; do not omit safeguards.

The design must represent contradiction rather than suppress it. The source
manual is not declared contradictory merely because the user's request is.

## 5. Origins and three separate decisions

Every normalized substantive field, item and exclusion needs an input origin:
a form JSON pointer, or `[start,end)` offsets into the unchanged original text
using Python Unicode character indexing. Preserve the original text and its
UTF-8 SHA-256 before normalization. Record normalization/catalog versions and
the basis for an alias mapping. Do not manufacture offsets in a translated string.

Input origins explain **what was asked**. Manual citations, document hashes,
page labels and quote offsets explain **what supports an answer**. Keep these
two provenance systems separate; user wording is not scientific evidence.

| Decision | States and consequence |
|---|---|
| Interpretation | `ready`, `needs_clarification`, `invalid`; evaluated per affected scope |
| Documentary support | Initially `not_checked`, later `supported`, `partial`, `missing` or `quarantined`; attributed to items |
| Applicability of a documentary condition | `not_evaluated`, `satisfied`, `not_satisfied`, `unknown` or `conflicting`; depends on supplied facts and reviewed conditions |

A valid request can ask for an unavailable pressure value. Its interpretation
is ready, its pressure item lacks support, and supported washing information
remains available. A source-backed warning can still have unknown applicability
to the actual sample. None of these decisions authorizes a real laboratory action.
No uncalibrated interpreter confidence score substitutes for these checks.

At output time, associate every selected source bundle and later answer fragment
with its task/item IDs, conditions, column and phase. Keep unavailable/excluded
items explicit; do not silently call the whole request complete. Atomic source
bundles, warnings and footnotes remain intact even when adjacent information is
not requested. An allowed context atom is not permission to render all its values.
Quarantined E118-I/E121-EQ remain unavailable under the current corpus policy.

## 6. Illustrative structured input

Paired free-text input for this illustration:

> For preparation A, compare step and linear-gradient elution on HiTrap Blue HP
> 1 mL: report flow and column volumes. For preparation B, say only whether HiTrap
> Blue HP albumin removal can occur before or after other purification steps;
> exclude operating elution information for B.

The following is a **submitted-form example**, not normalized output, an executed
request or an approved new reference. The final wire format still needs review.
Form field pointers provide input origins when a future adapter creates the
canonical contract. Catalog resolution, issues and support decisions are added
by the application, not asserted by this submitted payload.

```json
{
  "contract_version": "task-request-0.1-draft",
  "input_mode": "structured",
  "language": "en",
  "tasks": [
    {
      "task_id": "A",
      "sample_ref": "preparation-A",
      "intent": "documentary_procedure_lookup",
      "product": {"state": "provided", "value": "HiTrap Blue HP"},
      "column": {"state": "provided", "value": {"bed_volume": {"value": "1", "unit": "mL"}}},
      "facts": [],
      "items": [
        {
          "item_id": "A-elute",
          "stage": {"kind": "operating_phase", "code": "elution"},
          "information": ["flow_rate", "column_volumes", "elution_mode"]
        }
      ],
      "exclusions": []
    },
    {
      "task_id": "B",
      "sample_ref": "preparation-B",
      "intent": "documentary_applicability",
      "product": {"state": "provided", "value": "HiTrap Blue HP"},
      "column": {"state": "not_supplied", "value": null},
      "facts": [],
      "items": [
        {
          "item_id": "B-position",
          "stage": {"kind": "general_topic", "code": "product_applicability"},
          "information": ["relative_position_in_workflow"]
        }
      ],
      "exclusions": [
        {
          "exclusion_id": "B-no-elution",
          "scope": {"task_id": "B"},
          "selector": {"kind": "operating_phase", "code": "elution", "information": "all"}
        }
      ]
    }
  ]
}
```

Expected interpretation: A requests operating elution information; B requests only
workflow position. B's exclusion does not conflict with A. Missing B column size
must not trigger a needless clarification for a general workflow-position item,
nor borrow A's size if a later B-specific numerical item is added.

| Input variation | Structured meaning | Expected interpretation |
|---|---|---|
| Load a 1 mL column; wash a different 5 mL column | Two tasks with their own column and phase | Keep both contexts; never transfer a range between them |
| List the elution-buffer formulations, without operating elution settings | Buffer-preparation item with elution-use facet; exclude operating-phase elution | No contradiction; no operating elution flow/volumes requested |
| Same task: give washing flow, but omit all washing parameters | Include washing flow and exclude all operating washing information in that task | Clarification required for the affected item |
| Product is unknown; explain general method-selection principles | Explicit unknown product; general-topic item | General documentary context may be supported without inventing a product or demanding a confirmed diagnosis |

## 7. Candidate mappings for known X cases

These mappings are **new design examples pending review**, not extra human
decisions or a rewrite of the frozen X references. They are development examples,
not an unseen evaluation set. Original wording and reference decisions remain in
the [frozen X packet](../experiments/cytiva/v05-evaluation-v01/questions.json).

| Case | Candidate interpretation | Expected boundary |
|---|---|---|
| X01 | General clarification; residual identity explicitly unresolved; downstream application not chosen | Retrieve general principles; no assumed bovine contaminant, automatic technique choice or confirmed-diagnosis requirement |
| X02 | Two tasks with separate provided interference facts: A false, B true | No transfer of A's condition; B does not imply a general prohibition or mandatory further purification |
| X03 | Blue HP, 5 mL; include washing buffer/flow/quantity/endpoints; exclude loading and elution | No unwanted operating phase, including loading footnote unless independently required |
| X04 | Blue HP, 1 mL; include loading flow; exclude operating elution | Instead-of relation narrows the item; required approximate footnote remains context, not universal conversion |
| X05 | Blue HP, 5 mL; buffer preparation with binding-use facet, plus loading flow | Formulation is not operating elution; preserve alternatives, printed nomenclature and dependency scope |
| X06 | Separate tasks for loading 1 mL and washing 5 mL | No column/phase crossover or elution instruction |
| X07 | Same task positively requests washing and elution; negated exclusion does not negate elution | No false contradiction; no duration or gradient profile inferred |
| X08 | General IEX/HIC explanation with Blue as an excluded product mention | Product name in exclusion cannot activate the Blue route; conditional statements stay conditional |
| X09 | Separate loading/washing tasks plus a pressure-limit item whose exact product/column binding is recorded or clarified | State the bounded absence if unsupported; retain supported flows and do not invent pressure |
| X10 | Independent general-IEX, Blue 5 mL equilibration and Blue 1 mL washing scopes | General approved principles/washing remain available; no reconstructed pH/pI or equilibration values |
| X11 | Separate A-elution and B-workflow-position scopes | No request-wide conflict; no transfer of A settings to B |
| X12 | Same-task include/exclude overlap on washing parameters | Clarify that scope before affected operating values; not a contradiction in the manual |

X09's original question leaves the pressure item's column association unspecified.
Do not invent one in the canonical contract. Because the current eligible corpus
has no pressure value at all, a bounded documentary absence can be reported
without guessing a size; any later product/size-specific value needs the binding
resolved. This design detail was not measured by the previous context-only scorer.

## 8. Non-goals and review checklist

No schema implementation, UI, v06 parser, new model, embedding, retriever, graph
schema, scientific rule or application integration is included. In particular,
the examples do not silently approve product aliases or convert quarantined data
into active claims. Existing frozen experiments and their scores remain unchanged.

The matrix/card and allocation review is complete. Before implementation, specify
the machine format, catalog/alias mappings, corpus role adapter, and exact candidate
ordering/thresholds within an item. Preserve the accepted context dependencies,
task ownership and support distinctions; source approval remains separate. The proposed
[structured versus free-text protocol](experiments/structured-request-comparison-protocol.md)
defines the comparison and acceptance gates before another version is written.
