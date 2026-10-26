# Structured input versus free text: comparison protocol v01

Date: 26 October 2026. **CP01-CP06 and preceding clarifications approved collectively. Case/origin and new interface details remain pending review. No interpreter implemented, no comparison executed and no new source approval.**

The [actual decision record](../decisions/2026-10-26-structured-free-text-protocol-review.json) preserves the original French human message. Approval is a design decision, not permission to implement or execute. This proposal
follows the [completed S01-S12 trial](cytiva-structured-control-s-results.md).
It refines the [25 October design proposal](structured-request-comparison-protocol.md)
without rewriting that historical document or approving its earlier counts.

## 1. Question and boundary

Can an offline free-text interpreter preserve the same request meaning and
obtain the same context/diagnostics as an explicitly structured request, without
inventing context, losing exclusions or suppressing independently answerable items?

The structured control has passed 24 submissions on 12 known bilingual scenarios.
This establishes a downstream diagnostic baseline, not free-language performance,
user-form usability, scientific validity or generated-answer quality. The current
556-test main-suite result is a separate integration check, not 556 new scenarios.

The comparison ends at interpretation, source assignment and context assembly.
It does not generate a natural-language procedural answer. E118-I and E121-EQ
remain excluded; absence of pressure remains bounded to the 25 eligible excerpts.

## 2. Arms and common downstream method

| Arm | Actual input | What is measured |
|---|---|---|
| S: reviewed structured control | Reviewed form snapshot with explicit task/item contexts | Downstream ceiling for this particular reviewed intent, not automatic human form-entry performance |
| F0: unassisted free text | Only the exact EN or FR user text, language and opaque request identifier | Interpreter errors plus the same downstream context/diagnostic performance |
| F1: optional confirmed text | Original F0 result followed by actual user edits/clarifications | Separately measured benefit and interaction burden; never pooled into F0 |

One common downstream algorithm, catalog, schema, source-role adapter, source
review policy, dependencies, tokenizer and resource settings must be used.
S/F budgets are six roots and 2,048 serialized context tokens **per request**,
including bindings. No budget per task, hidden raw-text rerouting, answer lookup
or fallback to a second retrieval method. Mandatory warnings stay atomic.

For this first candidate, the approved boundary is deterministic local interpretation with no
model, API, embedding or database call. This is a design boundary,
not an implementation authorization or a promise that arbitrary prose is covered.
An unsupported construction must remain explicit, with its affected scope.

## 3. Interface must be specified before implementation

The existing runtime accepts structured submissions; it is not already a free-text
endpoint. Before coding F, review its boundary and origin handling:

1. Preserve verbatim UTF-8 text and its SHA-256; never replace it with a translated
   or normalized string. Any normalization keeps a mapping to original offsets.
2. Produce the same task/item concepts and explicit uncertainty states defined by
   the [technical specification](../technical/TASK-REQUEST-TECHNICAL-SPEC-V01.md).
   A text mention is a user assertion, not manual evidence or verified fact.
3. Separate an interpreted submission from its origin/issue ledger. Generated
   form pointers alone are not proof of an origin in the user's text. Store an
   explicit bridge from each derived field to original character spans, to a
   justified `not_stated` record or to application metadata with a policy reason.
4. Do not coerce uncertainty or contradictory assertions into a single convenient
   value. Preserve all competing spans and block only their dependent units.
5. If a language ambiguity or policy restriction cannot be expressed faithfully
   by the existing wire format, retain a pre-planning issue with affected scopes.
   Do not silently drop it or add an unapproved enum to make the JSON validate.
   The adapter between such issues and downstream withholding requires review
   and must be frozen as part of F. Do not change the approved downstream method.

Known IDs such as A/B and arbitrary item IDs can be renamed for comparison, but
only by a single bijection over every occurrence. Task ownership, item order,
scope references and exclusion membership must remain intact. Never sort tasks
to hide a changed allocation order or merge two independent preparations.

## 4. Cases and denominators

The [case cards](structured-free-text-cases-v01.md) propose:

- **P01-P12:** exact known S01-S12 texts, paired with the existing EN/FR form
  snapshots and references. Twenty-four language observations, twelve semantic
  scenarios. These are development/regression anchors, not a new holdout.
  Existing human S approvals remain valid for their original scope; equivalence
  of F meaning/origins and this comparison protocol still needs actual review.
- **G01-G06:** six additional bilingual semantic controls (12 observations):
  nested negation, explicit comparison, fact polarity, sample-versus-bed volume,
  explicitly unresolved owner (clarified G05) and forbidden policy override. Their draft expectations are
  interpretation-only; no new structured form, answer or passage selection is
  approved merely by authoring these cards. G06 is an intentional policy stress
  case; do not describe it as representative everyday wording.

Do not publish a combined 36/36 context score: P has downstream references,
whereas G first tests semantic handling. Report P and G separately, by language,
full request and individual information unit, including every rejected or failed
input. A zero denominator is unavailable, not success. Paired translations are
correlated; there are 18 development intents, not 36 independent examples.

At human review, inspect both actual form and text, all critical slots, task
ownership, exclusion scope, uncertainty and exact source spans. Do not give S a
column size, selected mode, confirmed contaminant or corrected product identity
that F's text does not supply. A full qualified product label can itself state a
size; preserve that origin separately from an unfilled column field.

## 5. Reference layers and scoring

References are maintained outside the runtime input:

- **Intent gold:** tasks/items, requested and excluded information, quantities and
  units, fact roles/polarity, selected versus compared modes, uncertainty,
  conflicting assertions and input-origin spans. It is not a list of answers.
- **Documentary gold:** required and acceptable source sets, dependencies,
  expected interpretation/support states, bindings and reservations. Reuse the
  pinned S references for P only after pair-equivalence review.

Compare intent at two levels. First, literal input fidelity: supplied versus
unknown versus not supplied, explicit decimals/units and each assertion's origin.
Second, resolved meaning using the same catalog: an approved alias can resolve to
the same product without rewriting the user's label. `1.0` and `1` are numerically
equal within the same unit, but original lexemes remain available. No unit
conversion, fuzzy product repair, format inference or product substitution.

Input traceability includes the whole relevant negation/scope expression, not
just a convenient positive noun. A reviewer approves exact spans or explicit
acceptable alternatives; no synthetic offsets are claimed by these draft cards.
Generated identity fields and justified inapplicable defaults are app metadata,
not fabricated user statements. All critical facts require a verifiable origin.

| Dimension | Proposed success criterion for the bounded challenge |
|---|---|
| Structural handling | Every accepted record validates; malformed or unsupported input is retained as an explicit counted outcome |
| Critical intent | Exact reviewed task/item ownership, context, stage, information, exclusions, fact role/polarity and uncertainty for every applicable case |
| Clarification | Expected affected scope only; no invented size, false conflict, missed real conflict or blocking of independent supported siblings |
| Provenance | 100% of substantive fields and issues have valid origins; no text assertion becomes source evidence |
| Documentary context | Every supported unit has a complete eligible required bundle; exact source integrity, binding and aggregate checks pass |
| Withheld units | No source assignment to a blocked unit, including when a supported sibling shares its source atom |
| Hard policy/resources | Zero quarantine leakage, warning/dependency loss, cross-task assignment or budget violation |
| EN/FR | Both pass their own references and have equal critical semantics; equality between two wrong outputs is insufficient |
| Completeness of reporting | Every planned submission appears once; crashes, rejected inputs and invalid JSON remain in denominators |

On P, require all 24 observations and all 12 pairs to meet both intent and
documentary gates. On G, require all 12 observations and all 6 pairs to meet their
reviewed semantic/policy expectations, including positive supported cases so
always asking for clarification cannot pass. These are proposed diagnostic gates,
not statistical estimates or approval for deployment.

Source presence alone is insufficient. For example, E121-F may be included with
loading context but must not be bound to the unsupported 2 mL/min transformation.
Conversely, an atomic passage containing adjacent unrequested values is not by
itself a generated-answer leak. Numerical rendering requires another evaluation.

## 6. Failure attribution

| S versus reviewed intent | F interpretation | F downstream | Classification |
|---|---|---|---|
| S fails | Any | Any | Shared method, source policy, budget or reference issue first; do not fix by synonym tuning |
| S passes | Wrong | Apparently passes or fails | Interpretation failure; coincidentally retrieving the same source cannot rescue it |
| S passes | Correct | Fails | Interface, downstream drift or execution discrepancy; inspect actual serialized handoff |
| S passes | Correct | Correct | Pass for context/diagnostics only |

Separate missing context, input contradiction, unsupported grammar, unresolved
identity, identified out-of-scope product, unsupported adapter mapping, missing
source, quarantine, budget exhaustion and runtime failure. A correct quarantine
or clarification is not a failed answer; refusing an available sibling is a failure.
Report counts and exact affected cases before aggregate percentages.

## 7. Freeze and sequence

1. CP01-CP06 are approved. Complete the remaining review of P pair equivalence,
   G expectations, exact origins and the newly drafted interface details. Record
   actual decisions separately; protocol approval does not fill those reviews.
2. Only after an implementation request, build one minimal F candidate using P/G
   as known development material; no use of case IDs, gold intents, source IDs,
   expected answers or reference scores in dispatch. Case labels are audit data
   only, not runtime input. Keep a separate submission projection and gold store.
3. Pin the shared downstream method and F implementation/configuration,
   normalization rules, language coverage, issue bridge, scorer and environment.
   A necessary shared-method change means a new baseline version and reviewed
   conformance evidence; the old S trial is preserved, never relabelled.
4. After this candidate freeze, author a **new 12-intent bilingual
   prospective set** from the declared coverage families: multi-task ownership;
   stage/formulation; negation scope; facts and uncertainty; numeric roles;
   partial support and policy. Include at least two real ambiguities and two
   partial-support requests. Paired documentary cases must be faithfully
   representable in both arms; unresolved-owner cases without an equivalent
   structured input stay in the separately reported semantic set. Balance
   positive and negative controls; do not
   select only parser-friendly phrasing. Exact forms, origins and references
   receive human review after the method freeze and before any run.
5. Freeze that dataset separately. Execute S and F0 once per approved input,
   fixed scenario order and EN then FR, alternating S/F-first by scenario parity.
   Both use independent request state with the same immutable initialized inputs;
   no conversational memory, online updates or query-result cache. Save all
   outputs before scoring. Retain failed/partial runs; no retry/best-of overwrite.
6. Diagnose failures without edits. Any repair creates another named candidate;
   a set inspected during repair becomes regression material, not fresh evidence.

The new set's count and diagnostic gate are approved protocol choices; its exact cases, forms, origins and references are not prepared or approved yet.
The same author knows the method and corpus: even post-freeze questions are not
blinded independent validation. A stronger later test needs an independent
author or new section/manual and fresh source review.

## 8. Measurements and interactions

Measure F interpretation separately from shared resolution/planning, initialization
and file/provenance overhead; use the same PC and actual serialized payloads.
Record errors, context tokens, roots, input length and hardware/dependency versions.
An error may not reduce measured latency or disappear from timing reports.

The frozen one-pass comparison provides descriptive times only. Do not infer a
p95/p99 service claim from 12 intents or from repeated known translations. If a
performance benchmark is later needed, approve a separate repetition/warm-up
plan before running it, preserve all samples and do not rerun the accuracy trial.
There is no new speed target derived from the S median. External model/API cost
for this proposed deterministic candidate is zero; CPU time and human effort are
still costs and must be reported separately.

F1 is deferred: it requires actual user responses with new versioned input hashes,
pre/post correction results, clarification/edit counts and human time. No
synthetic perfect human response is folded into F0. Form entry time and errors
need a separate user study; oracle S cannot establish usability superiority.

## 9. Approval boundary and next deliverable

CP01 (arms/shared method), CP02 (known P and separate G sets), CP03
(origin/issue bridge), CP04 (strict gates/denominators), CP05 (prospective freeze
sequence and 12-intent count) and CP06 (deterministic candidate and deferred
interaction) are approved collectively, together with the five clarifications
presented in the review. Exact case/origin mappings are still pending. G05 now
states the unresolved A/B owner explicitly; its previous wording is preserved in
the decision record rather than silently treated as equivalent.

The [proposed interface specification](../technical/FREE-TEXT-INTERFACE-V01.md)
defines the ledger, origin bridge, planner projection and whole-request accounting.
FI01-FI06, IF01-IF14 and the six preceding clarifications were subsequently
approved in the [interface decision](../decisions/2026-10-26-free-text-interface-review.json).
The [machine schema choices](../technical/FREE-TEXT-MACHINE-DESIGN-V01.md) were
subsequently approved as MC01-MC06. Refined examples and their origins/conditions
await [grouped review](free-text-interface-group-review-v01.md). The companion metadata pins the unchanged
baseline and records the actual approvals; no candidate is implemented, frozen
or executed.
