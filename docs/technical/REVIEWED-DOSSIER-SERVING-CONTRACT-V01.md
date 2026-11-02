# Reviewed dossiers → response service: proposed contract v01

Prepared on 2 November 2026 against merged `main` at `6c8bfe0`. **Proposal awaiting user review.** No adapter, renderer, graph publication, API call or new runtime freeze is implemented by this document. This contract does not retrospectively expand any human approval.

## 1. Objective and initial boundary

Transfer a complete, admissible documentary bundle to a response service without losing product scope, conditions, quantities, alternative/sequence logic, warnings, original citations or human reservations. The first proposed implementation is a local deterministic adapter and typed renderer on the already reviewed MabSelect bundles, with no model, paid API or database write. Serving within an explicit local release is separate from publishing records to Neo4j.

The current [graph tool](../../tools.py) returns symptom/cause/action paths and [grounded renderer](../../grounding.py) renders selected graph facts. A procedural instruction does not establish a symptom, cause, capability or cleaning trigger. The new payload is a distinct `reviewed_documentary_bundle/v1` result; it MUST NOT be disguised as a legacy graph path, silently accepted by `render_selection`, or converted into new cause/action edges. A future opt-in chat integration needs a separate typed dispatch, selection validation and tests before activation. Legacy chat and frozen v03 remain unchanged.

Initial corpus: the [MabSelect dossier](mabselect-cleaning-sources-v01.json), exact [approved application contract](mabselect-cleaning-approved-contract-v01.md), original [MS/C review](mabselect-cleaning-review-v01.json), and their original Q/N evidence and review dependencies. The [design verifier](../../experiments/cytiva/verify_mabselect_design.py) and existing [MabSelect selector](../../demo/mabselect.py) are references, not a new serving release. Other reviewed extractions (r2 claims, tables, diagrams), newer products and comparative cleaning procedures are out of the first release. They require their own explicit mapping and validation; being reviewed somewhere is insufficient.

This is documentary support, not diagnosis, treatment selection, laboratory authorization, GxP qualification or proof that a selected method suits a process. Deposit context is a user-selected category to explore, not a required confirmed diagnosis.

## 2. Review, admissibility and release are different gates

1. **Preserve source state.** Pending preparation flags in archived evidence remain untouched. Later scoped Q/N reviews may authorize documentary reuse only within the exact recorded question/context, complete required source set and retained reservations. Do not relabel the whole passage or PDF as universally approved.
2. **Validate original review binding.** Require known document and edition, source artifact and review digests, exact quote hash and offsets, complete evidence set, decision identity/status and original reservations. Distinguish the review's evidence-record digest from `quote_sha256`; these are different bindings and MUST NOT be interchanged. Reuse the recorded hash conventions, including LF normalization for artifact hashes and exact UTF-8 quote hashing without whitespace repair.
3. **Admit a registered mapping.** Each serving bundle names the original review scope, approved product/context and the portions it may render. Comparative/refusal precedents do not authorize independent single-product recipes. New derived numerical/formulation annotations require explicit documentary checks and review before use; otherwise render the already reviewed wording without inventing typed values.
4. **Require an explicit serving release.** A proposed release manifest binds the corpus version, registered bundle mappings, source/review dependencies, renderer/adapter versions and allowed execution mode. Contract acceptance and a later explicit release decision are separate from MS01–MS08/C1–C4 design approval. No record is served merely because a model emits `approved=true`.
5. **Keep unresolved or revoked support out.** A quarantine, conflicting review or revocation blocks the affected bundle. No current decision or ambiguity can be silently overridden by an older snapshot. An initial release must specify how withdrawal is checked and must be withheld if that authority cannot be established. New evidence, edition or changed wording requires a new version and explicit revalidation, not refreshed source hashes to make old approval fit.

No automatic write to the serving graph, public release or default chatbot activation follows from these gates. The first release is local and opt-in; Neo4j migration is a later approved action with its own rollback contract.

## 3. Immutable units and request identity

The minimal admissible unit is a **reviewed bundle**, not an isolated quote or retrieval chunk. Each option carries its entire required source set and review reservations. A source snippet may be displayed for convenience but cannot authorize a procedure independently of its scope heading, required condition, follow-up step or warning.

A request has explicit, stable task IDs. Each task records the exact product identity or `unknown`, edition/corpus scope, procedure/phase requested, context assertions and origins, requested information, and exclusions. Column format is recorded only when supplied and relevant; it is never inferred by eliminating another format. An absent value differs from supplied zero/false. Unresolved conflicting values remain conflicts, with both origins retained. Do not borrow one task's product, phase, format, parameters or exclusions for another task.

The existing [request contract](../REQUEST-CONTRACT-V01.md), [claim contract](../CLAIM-CONTRACT-V02.md) and frozen v03 retain their own definitions. This proposal does not rewrite their schemas or accept unrestricted free text. The v1 adapter takes validated structured tasks; converting chat text to those tasks is a separately evaluated step.

### Bundle catalogue for the first proposed release

These are proposed serving keys, not new claims or implemented IDs. Every source ID below is scoped to the dossier's exact PDF and corpus version.

| Bundle key | Original review scope | Indispensable source IDs | Allowed role |
|---|---|---|---|
| `mabselect.precipitated.general` | Q05 | E167-H, E167-PH, E167-P | Four alternative formulations with the shared contact minimum and immediate following wash |
| `mabselect.precipitated.restricted` | Q06 | E167-H, E167-PH, E167-SH, E167-S | Separate three-step block; SuRe/SuRe LX only, precipitated/denatured context |
| `mabselect.hydrophobic.detergent` | N06 | E167-H, E167-LH, E167-D | Nonionic-detergent example and immediate following wash |
| `mabselect.hydrophobic.solvent` | N07 | E167-H, E167-LH, E167-E, E167-W | Ethanol OR 2-propanol, immediate following wash and two distinct precautions |
| `mabselect.context.clarify` | Q09 plus approved application clarification policy | E166-H, E166-T, E166-PH, E166-LH, E167-H, E167-PH, E167-SH, E167-LH | Separately labelled contextual headings only; never a selected cleaning recipe |

Use the original reviews' reservations in full. A serving key is not a global passage approval. Excluded comparison precedents remain excluded unless their full reviewed comparison bundle is mapped and approved separately.

## 4. Applicability and uncertainty

Maintain separate fields for **documentary applicability**, **user context** and **operational suitability**. Suitability remains `not_established`. A supported documentary response means that the source describes this requested scope; it does not authorize execution.

Conditions use three-valued evaluation (`true`, `false`, `unknown`): AND within each condition group, OR between groups, retaining original negation, force and qualifications. Explicitly false applicability blocks that option. Missing data never becomes true. If a required condition is unknown but can be clarified, ask only for that condition. If a condition cannot be represented faithfully, retain its exact source wording and an unevaluated status; do not promote it to a computable rule.

For initial MabSelect serving, exact plain MabSelect/SuRe/SuRe LX plus an explored supported deposit category select documentary bundles under the already approved conservative policy. A generic family label, unknown context, conflicting labels or mixed category cannot select a recipe. Ask for the exact label or a single category to explore without demanding a confirmed scientific diagnosis. Product outside the edition-bound catalogue yields scoped abstention, not a compatibility prohibition.

All four general formulations remain distinct alternatives, not a ranking or sequence. The SuRe/SuRe LX block is separately scoped, never a fifth formulation or automatic successor. Detergent and solvent are alternatives; ethanol OR 2-propanol is not a mixture. Immediate following washes, order, examples, approximations, minimum/maximum comparators, ranges, material and denominator/units remain attached to the relevant step.

No automatic CV→mL/time conversion, pressure limit, pH adjustment, dosage, contact time, concentration basis (e.g. v/v when unspecified), naming correction, replacement detergent or regeneration/CIP equivalence may be inferred. In particular, pH 7.0–8.0 belongs to the following binding-buffer wash. The selected MabSelect sources do not grant the page-166 12-hour hold or Protein A/G backpressure cleaning trigger.

## 5. Proposed handoff and response envelope

This is a field-level contract for review, **not an executable JSON schema**. A machine schema and adapter follow accepted decisions.

| Object | Required information and invariant |
|---|---|
| Envelope | `contract_version`, immutable `release_id`, request/task IDs, corpus identity, result type; no user-supplied source/review/release overrides |
| Bound request | Exact product/phase/context selectors and their input origins; explicitly requested parameters and exclusions; unresolved conflicts |
| Selection | Serving key, original review scope, registered dependency IDs, role (`procedure`, `warning`, `scope` or `clarification_context`); relevance scores never determine admission |
| Applicability | Recorded source condition groups, per-condition outcome and reason, origin of the user assertion; suitability remains unestablished |
| Documentary option | Original force and wording, alternative group/sequence identity, ordered steps, quantities with exact source text and step ownership; no unsupported computed value |
| Provenance | PDF identity/hash and edition metadata origin, printed label vs 1-based PDF page vs 0-based index, source/corpus/item IDs, extracted-text locator/version and hashes, exact quote, character interval and quote hash; bounding box only if actually recorded |
| Review binding | Review artifact/version/hash, question/event identity, decision, date, original human message and all scoped reservations; record-digest vs quote-digest semantics explicit |
| Rendering support | Full original required passages including scope and warnings; already reviewed summaries distinguished from exact quotations and from application policy; safe localized interface labels |
| Outcome | Per-task state/reason, clarification targets or absence scope, eligible and withheld bundle IDs; independent aggregate derived from those outcomes |

The full original human messages and review metadata must remain available in the audit view. The ordinary answer must visibly carry applicable reservations and limitations; a collapsed provenance panel cannot hide a condition or warning needed to interpret a procedure.

Quotes stay in original English. French UI labels may be deterministic; new technical translations or paraphrases are not silently treated as reviewed facts. Quotes and names are escaped as data, never interpreted as HTML, Markdown instructions, executable links or model instructions.

### Citation contract

Each displayed option/step/quantity points to its supporting passage(s), with the complete required bundle available from the same answer. A warning link alone does not replace the warning in the answer. UI labels identify product scope and PDF page, and show printed-page ambiguity if present. Exact quote offsets are Unicode code points, start-inclusive/end-exclusive, within the recorded extracted page text; they are not byte offsets or verified visual positions. A quote hash verifies text identity, not semantic correctness or completeness.

A source link targets a service-owned, versioned source view resolvable from a fresh checkout/release. Do not rely on the operator's `C:/...` PDF path, private audit directory or a temporary local server. The first release must include the permitted original excerpt view and review metadata; full PDF redistribution is not required or implied. If the PDF is unavailable, say so; reviewed excerpt access remains usable. If a mandatory excerpt or review binding cannot be resolved, withhold the affected procedure as unavailable. No fabricated URL or claim of pixel-level visual verification is allowed.

## 6. Clarification, abstention and integrity failure

| Per-task state | Meaning | Permitted output |
|---|---|---|
| `supported` | All prerequisites, registered scope and complete required support are present | Reviewed documentary option(s), conditions, full warning/reservations and citations; no suitability claim |
| `needs_clarification` | Necessary product/context/phase/ownership is missing or contradictory and can be asked for | Specific unresolved fields and available distinctions; no recipe based on the missing field |
| `abstained` | Requested fact is absent from the admitted selection or the product/request is outside the release | State what cannot be answered and bound the absence to this corpus/bundle; do not imply global absence or incompatibility |
| `quarantined` | Affected required evidence is explicitly held or conflicts remain unresolved | Explain the scoped hold and do not leak the held content as usable support |
| `unavailable` | Hash/version/review validation, required dependency loading or service execution fails | Retryable/service-integrity message as appropriate; never call it documentary absence, an intentional refusal, or a diagnosis |
| `excluded` | The user excluded this item or did not request it | No delivery or support count for that item; exclusions remain task-local |

Clarification asks only unresolved fields. Do not ask again for a known exact product or force a deposit diagnosis. An absence request for a numerical pressure value in an otherwise supported solvent task yields a supported explanation plus abstention on the number, not a fabricated number and not suppression of all supported content.

For multiple independent tasks, preserve order, task identity and exclusions, and allow partial service. Within one procedure, never truncate an indispensable condition, warning or following wash to claim partial success. An unreadable global release or corrupted shared authority makes the whole request unavailable; an isolated affected bundle may fail while independently validated tasks remain served. No fallback to unreviewed model prose, a neighbouring product, a newer edition or a legacy graph route may conceal failure.

Aggregate response state is derived, never model-declared: all requested in-scope items supported → `supported`; a mix with served independent items → `partial`; none served and an integrity failure → `unavailable`; otherwise unresolved clarification → `needs_clarification`; remaining nonserved cases → `abstained`, with quarantine still explicit per item. Report counts by state and preserve each original reason. A response containing a selected recipe's missing warning is never `supported`.

Budget limits are checked on the full serialized bundle with conditions, reviews and citations. A bundle that cannot fit is withheld as unavailable (`context_budget_incomplete`), without deleting reservations or relabelling that as source absence. Other complete independent tasks may still be served.

## 7. Deterministic enforcement and future model boundary

Validation order: release/inventory integrity → original scoped reviews and source bindings → structured task validity → registered eligibility/applicability → complete bundle assembly → budget → typed rendering → citation-resolution check and derived outcome counts. Record request/release/adapter versions and admitted/withheld IDs for replay. User inputs cannot supply overriding schema, review state, source text, policies, credentials or new release paths.

The v1 handoff is deterministic. If a later model selects bundles, it may choose only already admitted IDs for the correct task. Application code validates task ownership, complete dependency sets, conditions, alternative groups and exclusions, then renders stored reviewed material. It must reject unknown IDs, duplicate or cross-task selections and partial sequences. No free model prose becomes the technical response. No Text2Cypher execution or arbitrary query tool follows from this contract.

Future graph storage may represent documents, scoped reviews and procedure/option/step records separately. It must not flatten a conditional procedure into a `Cause` or remove n-ary product/context/phase scope. A later model/schema review decides graph mapping; no Neo4j migration is authorized or implemented by this proposal.

## 8. Acceptance before implementation/release

The user reviews [DS01–DS10](REVIEWED-DOSSIER-SERVING-REVIEW-V01.md) and the [representative cases](REVIEWED-DOSSIER-SERVING-CASES-V01.md). No approval is prefilled. Implement a minimal machine schema, registered mapping and deterministic renderer only after those decisions. Before a local serving release, verify each registered bundle's scope, exact quotes/quantities, original reviews and the cases, with tamper/missing-warning/budget tests and replayable outcomes.

No question-level review is promoted to a universal passage licence; no source review is replaced by an LLM judge. Initial release tests establish conformance on known reviewed sources, not independent recall or generated-answer quality. Later answering evaluations, OpenTelemetry/Ragas/Promptfoo and graph/passages/LightRAG comparisons remain separate roadmap work.
