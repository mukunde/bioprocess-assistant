# Structured request versus free text — proposed comparison

Status: **design proposal, 25 October 2026; not implemented or executed**.
Companion: [task request contract v0.1](../REQUEST-CONTRACT-V01.md).
The [v05 X outcome](cytiva-v05-prospective-results.md) is preserved, not rerun.
No result in this document is an observed improvement over v05.

The user approved D01-D08 and C01-C04 collectively; see the
[original decision record](../decisions/2026-10-25-task-request-review.json).
The [second collective decision](../decisions/2026-10-25-task-request-matrix-review.json)
approves M01-M14, R01-R08 with the R08 correction, and allocation modalities.
The [context matrix](../REQUEST-CONTEXT-MATRIX-V01.md) and
[review cards](structured-request-review-cards-v01.md) therefore have completed
design review. This does not approve the entire experimental protocol, its
proposed dataset size/thresholds, a final wire format, catalog aliases or ranking
algorithm. No implementation is performed by recording these decisions.

## 1. Questions to answer

1. With interpretation supplied explicitly, can the same reviewed corpus provide
   the right context for every supported information item, without leaking
   excluded phases or quarantined sources?
2. Can a free-text adapter produce the same task-scoped intent without inventing
   context, flattening separate tasks or treating nested negation as contradiction?
3. Which errors belong to input interpretation, catalog/source-role mapping,
   retrieval, context assembly, source availability or later answer attribution?

The first comparison stops at context and diagnostics. Actual answer rendering
and task-specific numerical attribution require another evaluated serving slice;
neither an intent match nor source presence establishes answer correctness.

## 2. Two main arms and an optional confirmation arm

| Arm | Input | Intended path | Purpose and limitation |
|---|---|---|---|
| S — structured control | Explicit tasks, product/column states, items, facts and exclusions | Structural validation → canonical contract → shared reviewed source-role mapping/retrieval/assembly | Removes free-language interpretation as an error source; does not prove users can complete the form correctly |
| F — unassisted free text | Original EN or FR question | Interpreter → the same structural validation and canonical contract → exactly the same downstream path | Measures the interpretation penalty as well as context quality; unsupported ambiguity must remain explicit |
| F-confirmed — optional, separately reported | Free text plus an editable interpretation preview and actual user clarification | Interpreter → confirmation/correction → canonical contract → shared downstream path | Measures benefit and interaction burden; cannot be merged into F's unassisted score |

No specific free-text technology is selected. Rules, a local parser or a later
authorized local model would be distinct interpreter candidates with their own
versions and measurement. This documentation task invokes no model and provides
no permission to start such an experiment. A validated JSON shape alone is not
proof that an interpreter understood the input.

### What “structured control” fairly establishes

Initially, a human-reviewed canonical interpretation can seed S as a diagnostic
control. It is an intent oracle for isolating downstream failure, **not an honest
end-to-end score for an automated product**. Do not claim S is the better user
experience without a separate form-entry study measuring mistakes, effort and
corrections. Later real user form submissions must be scored as entered.

The gold canonical intent and the source/answer references are separate artifacts.
S receives intent fields, never required source IDs, source quotes, expected
answers or acceptance labels. F receives only its input plus the same catalog and
system policy. Gold intent/source references are used for scoring after outputs
are saved. No question-ID lookup is permitted in either path.

## 3. Fairness and frozen inputs

Keep the following identical across S and F:

- Same information content. If a question does not give column size or product,
  S must retain that absence rather than filling the blank from the manual or gold
  answer. Both arms can express provided, unknown, not-supplied and justified
  not-applicable states. Any extra clarification is separately logged and counted.
- Same reviewed corpus snapshot, document identity, source conditions, catalog,
  source-role adapter, active decisions and source-eligibility policy. Start from
  the known 25 eligible excerpts to isolate the mechanism. E118-I and E121-EQ remain
  excluded until separately approved under a new source-policy version.
- Same downstream algorithm, deterministic settings, warning/dependency closure,
  field/unit handling and output accounting. No answer/reference text enters
  search. No language-specific second interpretation path is hidden in retrieval.
- Same initial resource limits: six selected seeds and 2,048 serialized context
  tokens for the **whole request**, not separately for each task. Multiple tasks
  cannot multiply the budget. Shared source bundles may be deduplicated while
  retaining every task/item association.
- Same rule for a bundle that cannot fit: preserve it atomically or report the
  affected item as budget-incomplete. Do not truncate warnings or silently call
  missing context supported. Distinguish budget failure from unavailable sources.

Freeze the contract, catalog, interpreter, role mapping, corpus policy, code,
scorer and resource settings before new held-out questions are finalized. Active
test fixtures should not be immutable method dependencies. Freeze references
separately after human review. Record environments, hashes and random seeds where
relevant; preserve partial outputs and do not silently retry a frozen trial.

## 4. Staged work, not an endless synonym loop

| Stage | Work | Exit condition |
|---|---|---|
| D0 — contract review | Principles, initial scope, M01-M14, R01-R08 and allocation modalities approved; R08 corrected | Design handling review complete; machine format, catalog/adapter and within-item ranking still need specification before implementation |
| D1 — structured control | Implement only validation, canonical tasks and reviewed role mapping behind S | Per-item context and source-boundary gates pass on known development cases |
| D2 — language adapter | Add one F interpreter; use existing C/H/V/W/X as development/regression evidence | Paired interpretation and downstream failures are measurable, not hidden by scope flags |
| E — new frozen challenge | Author/review new questions and canonical intents after freezing; run S/F once | Report predeclared gates and all failures without tuning the candidate |
| P — bounded serving pilot | If eligible, connect a small approved corpus to the renderer with minimal traces | Separate answer/citation/abstention and task-attribution evaluation |

Do not implement an increasingly complex parser before establishing that S can
retrieve and assemble the necessary context. If S fails, changing free-text
synonyms does not fix the downstream problem. If S passes and F fails, prioritize
interpretation or clarification. A source-policy gap requires documentary work,
not a more confident interpreter.

## 5. Review references and coverage

Every new reference needs a human-reviewed task/item interpretation, actual input
origins, required/acceptable source sets with dependency closure, explicitly
excluded sources or information, expected support/clarification states and
reservations. Record the submitted form and original text as paired but distinct
inputs. Human approval of earlier X source references does not automatically
approve these new canonical mappings or field taxonomies.

Use at least the following paired controls before any prospective run:

| Challenge | Positive and negative control |
|---|---|
| Task ownership | Include elution for A/exclude for B versus include/exclude for the same task |
| Negation scope | Omit/leave out/outside scope versus do not exclude/not only |
| Fact polarity | Contaminants do not interfere versus information about interference is excluded |
| Column association | Load 1 mL/wash 5 mL versus load 5 mL/wash 1 mL |
| Stage versus formulation | Elution-buffer formulation versus operating elution flow |
| Product roles | Product named as context versus mentioned only to exclude it; generic HiTrap versus explicit Blue HP |
| Unknowns | Missing product/column/context versus explicitly unknown; no assumption of contamination or diagnosis |
| Partial support | Supported washing plus absent pressure or quarantined equilibration |
| Source policy | Request to use a quarantined passage or omit mandatory warning must not bypass policy |
| Role support | Rephrase away incidental not/been/three words while preserving the intended topic |

Use existing X cases only for design/development. They are now known. For a next
small prospective set, propose 12 new bilingual intents with these phenomena
balanced, plus 6 product-neutral synthetic semantic controls. These counts are a
proposal to review before preparing the set, not an already frozen dataset.
Avoid selecting only parser-friendly sentences. Log who authored and reviewed
the cases and which implementation details were known. A new section/manual or
independent author is a later generalization check; same-corpus new wording is
not equivalent. EN/FR pairs and mirrored controls are correlated observations.

## 6. Metrics and proposed success gates

The following are proposed gates for the bounded reviewed challenge, not measured
results, production guarantees or a new interpretation of historical scores.
Record every planned case, including invalid parses and clarification outcomes;
do not discard failures from denominators or turn all questions into abstentions.

| Level | Measurement | Proposed gate |
|---|---|---|
| Contract integrity | Unique task/item IDs, typed units/states, legal selectors, complete origins and catalog resolution diagnostics | 100% structurally valid accepted contracts; invalid ones explicitly rejected and counted |
| Intent fidelity | Task/item ownership, product/column binding, stage, requested/excluded information, input facts and uncertainty against reviewed intent | Exact semantic agreement on every critical field in the small challenge; report full-request match and per-field errors |
| Contradiction/clarification | False positives on nested negation/separate tasks; false negatives on same-task conflicts; justified missing-context handling | Zero critical false conflicts or missed real conflicts in the controls; correct declared clarification scope without blocking unrelated supported items |
| Supported context | At least one complete eligible required source set for each supported item, including scope, warning and footnote dependencies | Every required supported item complete within the fixed budget; unavailable/quarantined items have the expected explicit state |
| Scope isolation | Explicitly unrequested source/role or an assignment to another task/column/phase | Zero prohibited source/role assignments; report outside-reference noise separately |
| Hard source invariants | Quarantined, withdrawn or wrong-version source; altered quote; lost mandatory dependency | Zero violations in all cases |
| Bilingual equivalence | Same semantic task structure, exclusions, unknowns and support decisions after ignoring origin-language offsets/labels | All paired critical semantics agree; report each EN/FR discrepancy, not just an average |
| Traceability | Every interpretation issue and selected bundle attributed to input/task/item and source version | 100% of relevant fields/issues/bundles attributable; no user text presented as manual evidence |

These gates require explicit labelled refusals/clarifications and supported
answers to be distinguished. Merely returning valid JSON or always asking for
clarification is a failure. A task's interpretation can be ready while its
documentary support is partial; do not collapse those into one completeness flag.

Context gates are not answer gates. Later rendering must separately demonstrate
zero transfer of numerical parameters, qualifiers or conditions between tasks,
correct handling of source alternatives and correct citations. An atomic buffer
excerpt may legitimately contain an unrequested elution formulation; this is not
permission to include it in a binding-only answer. Sentence-level leaks must be
measured at the answer stage, not fabricated from source-level counts.

Measure context tokens, truncation/rejection, latency p50/p95/p99, initialization,
peak memory and interaction burden separately for interpretation and retrieval.
Use the same machine and planned repetitions; report warm and cold behavior.
The initial offline control has zero external model/API calls. No latency or
memory result is claimed here. Set resource acceptance limits from the structured
control measurement **before** freezing a subsequent comparison; do not invent
a p95 target from v05's median or tune it after inspecting held-out results.

## 7. Failure attribution and decision

| S outcome | F interpretation | F context | What to investigate |
|---|---|---|---|
| Fails | Any | Any | Contract coverage, catalog/source-role mapping, corpus support, retrieval or budget first |
| Passes | Differs from reviewed intent | Fails or apparently passes | Interpreter/ownership/polarity error; source coincidence does not excuse a wrong intent |
| Passes | Matches | Fails | Downstream inconsistency, non-determinism or mismatched policy; the same canonical input should yield the same plan |
| Passes | Matches | Passes | Candidate for a separately evaluated serving slice, not automatic adoption |

Keep both pre- and post-confirmation contracts if F-confirmed is studied, along
with actual user edits, clarification count and time. Improvements achieved by
extra human information must not be reported as unassisted language performance.
No graph/passages/LightRAG architecture ranking follows from this two-input
diagnostic comparison; that broader protocol remains separate.

The next deliverable is the technical specification of the machine format,
catalog/adapter and within-item ranking, followed by the smallest offline
structured control implementation if requested. Experimental dataset/threshold
choices remain separately proposed. No v06 code,
schemas, model calls, new questions, retrieval outputs or changed frozen artifacts
are delivered by this proposal.
