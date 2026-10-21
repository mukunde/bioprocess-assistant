# Methodology review — archive of 18 October 2026

Archive of reasoning and alternatives discussed. The single active plan is [ROADMAP.md](../ROADMAP.md); this document is not a second roadmap to maintain.

Status: working proposal adjusted to Gaël's answers. Primary use: troubleshooting with symptoms, possible causes and actions. Career objective: AI/LLM engineer and data/knowledge engineer. Exclusively local operation by default; private cloud may be considered if guarantees and cost are acceptable. Declared maximum budget: below EUR 10, interpreted as monthly because the question asked about a monthly budget. Availability: free on weekdays, with as much project time as necessary; no overall five-hour weekly limit. No hosting or purchase is initiated.

## What the review reveals

The existing [roadmap](../ROADMAP.md) correctly planned instrumentation (phase 1), then the domain model and annotated reference (phase 2), before ingestion (phase 3). Execution anticipated phase 3 without meeting prerequisites. The ontology was therefore not absent from the plan; it was insufficiently defined before use. Synthetic tests checked technical contracts, not actual extraction quality.

The real test remains useful: 29 entities, no domain relation, 13 blocked cards, 55 min 49 s. It invalidates the current default configuration without proving Docling Graph or the local model generally unsuitable. One trial cannot select an architecture or establish a reliability rate.

Retain separation of ingestion/application, immutable sources, human review, deterministic checks, bounded answer rendering and no automatic publication of extractions.

## Critique of scope and assumptions

- Three objectives are mixed: a useful assistant, a graph-ingestion platform and a regulated-sector demonstrator. Choose one primary user scenario; the others become constraints or extensions.
- The graph and Neo4j are imposed before comparison with a simple documentary baseline. Keep the existing approach as a candidate, not an experimental conclusion. KAG should not be an objective independent of user need.
- A troubleshooting model need not represent every manual object. Figures, buffers and markers must not be forced into the five available classes. A partial graph can be correct if scope is explicit and passages remain accessible.
- Symptom→Cause→Action can imply stronger causality than sources state. Distinguish possible cause, described effect, recommended action and applicability conditions. An instruction to clean when pressure increases does not justify inventing an intermediate cause.
- Lack of an expert does not prevent manual-fidelity checks, but prevents calling them validation for an industrial process. Replace this inaccessible prototype prerequisite with explicit documentary validation and an ambiguous/not-evaluated category. Expertise remains necessary for any eventual operational use.
- A cited source and deterministic rendering eliminate neither selection errors, incorrect conditions nor graph errors. Replace absolute zero-hallucination promises with measurable criteria and limitations.
- Historical embedding conclusions concern six symptoms and a development set. They do not establish that vector passage retrieval is useless. Evaluate retrieval similarity separately from answer/refusal decisions.
- Publication produces a separate evidence graph not yet consumed by the chatbot. Connecting approved knowledge to user answers must become an explicit milestone. Plan version activation and revocation; stored snapshots alone cannot withdraw serving knowledge.
- Review time may dominate token cost. Compare assisted manual annotation with automatic extraction on the same batch. Do not invest in automation if corrections cost more than entry for the intended volume.

## Alternatives to compare

| Approach | Value | Cost/limitation | Proposed decision |
|---|---|---|---|
| Passage retrieval + sourced answer/abstention | Simple documentary-question baseline | Relations and conditions must be checked in passages | Mandatory baseline; start lexical and extend only if needed |
| Small manually populated graph with evidence | Reliable targeted-troubleshooting reference; predictable initial effort | Limited maintenance capacity and coverage | Mandatory baseline for selected facts |
| Section-assisted extraction + review + graph | Measures automation's actual benefit | Corrections may cost more than manual entry | Main candidate after both baselines |
| Combined graph and passages | Uses validated relations and restores context | Extra routing, consistency and evaluation work | Possible target if benefits are measured |
| Full KAG, extensive rules and inference | May serve multi-step reasoning questions | High modeling and operational cost | Defer until a concrete question demonstrates need |

Retain Docling conversion in trials. Compare bounded-context direct extraction with compact dense extraction; these are variants, not commitments. The domain ontology must remain independent of the extraction library.

## Revised sequence and acceptance gates

| Milestone | Deliverable | Acceptance gate |
|---|---|---|
| 0 — Use and budget | Primary scenario, user, corpus, answer limits; separate interactive-latency, ingestion and review budgets | Choices explicit with Gaël; criteria fixed before comparison |
| 1 — Questions and minimal ontology | 10–15 proposed representative questions, class/relation definitions, examples/counterexamples, conditions, identity and provenance | Every concept serves a need; PDF examples checked; ambiguities flagged |
| 2 — Reference and measurements | Small annotated batch independent of model outputs; OTel traces and minimal execution budget | Reproducible measurement of missed facts/relations, errors, review time and resources |
| 3 — Baselines | Passage retrieval and manual graph on identical scope | Observed scores/costs; refusals/clarifications tested; explicit limits |
| 4 — Experimental extraction | CIP micro-test then varied pages; source→facts→evidence→review | Measured gain versus manual entry; no publication without evidence/review; critical errors analyzed |
| 5 — Useful complete slice | A question uses approved facts from a precise snapshot and displays evidence | Publication, activation, recovery, correction and revocation tested; incomplete contexts handled |
| 6 — Evaluation and demonstration | Held-out set, calibrated Ragas, regression attacks, quality/latency/cost report, reproducible startup | Current-system results; justified architectural choices; no old score presented as new |

Question counts are a starting proposal, not a statistically sufficient sample for industrial reliability. Performance thresholds and budgets still depend on usage; do not invent accepted precision or latency targets.

## Experimental method

1. Define questions the ontology/system must answer: which action the manual recommends for this symptom/product, under which conditions, and what the passage does not support concluding.
2. Annotate expected facts before inspecting model answers. Check facts absent from extraction too: reviewing proposals alone does not measure recall.
3. Separate development and test by section or question family; avoid paraphrases of the same fact on both sides. With one manual, explicitly state generalization limits.
4. Use identical sources, model, context and budgets for the first method comparison, then change one factor at a time. Repeat finalist variants and separate cold start from warm operation.
5. Measure conversion, extraction, location, semantic validation, retrieval and answering separately. Aggregate scores alone cannot attribute regressions.
6. Evaluate relation types, direction, conditions and evidence; explicitly count number, unit, negation and product errors. Measure expected-fact coverage rather than total nodes.
7. Record duration, calls, available tokens, RAM, review minutes and cost per accepted fact. Unknown tokens stay unknown; local resources are not cost-free.
8. Set stopping rules: budget overrun, schema failure, truncation or unresolved citation yields an observable incomplete/failed state, never silent success. Preserve targeted resumption.

## Role of selected tools

- **OpenTelemetry:** before the next benchmark, add spans at conversion/extraction/validation/retrieval/answer boundaries, version IDs and errors. Start with simple local export; OTLP/Collector and a two-backend demonstration follow. Portable transport does not guarantee portable dashboards or cost calculations.
- **Ragas:** retained for retrieval/answers with prepared contexts and references. Add extracted-relation fidelity measures. Calibrate judges on reviewed cases; do not define success through one faithfulness score, especially when the current renderer copies graph facts.
- **Red-teaming:** start with reproducible fixtures and deterministic checks: document injection, wrong resin, negation, missing conditions, false evidence, altered numbers and exhausted budgets. Add Promptfoo orchestration after stabilizing the application contract; include benign cases to detect excessive refusal.
- **Local models:** retain the installed model to isolate schema/orchestration effects first. A stronger model on public text can be a comparator if Gaël authorizes it, not ground truth. Defer fine-tuning until recurring errors and sufficient annotations exist.
- **Ontology and visualization:** versioned definitions and relation examples suffice initially. OWL/Protégé becomes relevant when reasoning or interoperability warrants it; observed-graph diagrams do not define permitted relations.
- **Employability:** prioritize a complete demonstrable slice, independent evaluation, failure diagnosis and measured choices. Tool count is secondary.

## Documentation corrections identified at this historical checkpoint

Update `docs/ROADMAP.md` and `docs/INGESTION.md` to reflect known hardware, the first real trial, insufficient quality, imperfect provenance and missing instrumentation/reference. Distinguish implemented, fixture-tested, measured on a manual and accepted. Revise README promises and retain old scores only as history. Do not declare phase 0 fully deployment-validated before required live checks.

## Confirmed choices and consequences

- **Product:** documentary troubleshooting assistant for Protein A capture. It presents possible causes and sourced actions, requests necessary conditions and distinguishes documentary recommendation from established diagnosis.
- **Portfolio:** two dimensions in one product. Knowledge engineering: versioned ontology, facts/evidence, conditions, review, publication and revocation. AI/LLM engineering: measured extraction, retrieval, context management, abstention, traces and evaluations.
- **Execution:** conversion, models, retrieval, storage, review and evaluation local in the reference path. At this historical checkpoint the Claude/AuraDB application did not satisfy this constraint: preserve it as history and explicitly plan a complete local path. Examine component licences and limits before distribution.
- **Private cloud:** a later conditional option. A remote API or cheap shared GPU is not a private environment. Evaluate isolation, access, storage, retention, region and full costs before proposing it. Success does not depend on free GPU hosting.
- **Budget:** no paid service needed for the next milestone. Local API fees may be zero, but hardware/electricity remain real costs. Any remote benchmark or hosting requires a later explicit choice; below EUR 10/month is a ceiling, not a spending target.
- **Time:** Gaël is available on weekdays and can devote as much time as needed. Advance by milestones without a weekly cap or imposed hourly allocation. Still measure review/machine time to compare methods and avoid unnecessary work.

## Proposed first cycle: four stages without imposed duration

Stages follow dependencies and may proceed once criteria are met. They are not calendar weeks. Quality criteria take precedence over speed; machine time is measured separately.

| Stage | Priority work | Deliverable |
|---|---|---|
| 1 | Scope 2–3 symptoms, prepare about 10 questions; define relations and check a small fact batch | Minimal ontology and reviewed documentary examples, including ambiguities |
| 2 | Make facts locally accessible without requiring automatic extraction; prepare tests/minimal traces | A question yields a sourced answer or clarification on a known snapshot |
| 3 | Instrumented extraction micro-test reusing conversion; compare manual-entry time | Reasoned choice between assisted extraction and manual entry for this scope |
| 4 | Evaluate held-out cases including incorrect conditions, negations and injections; document results | Reproducible local demonstration and limitations report |

If a milestone fails, narrow scope or extend the cycle rather than adding tools. Retain Ragas as supplementary local evaluation once references exist and judge cost is measured. Multi-platform OTel export and extensive automated red-teaming follow later.

### Ontology decisions to prepare before the next test

Define Symptom, PossibleCause, RecommendedAction and product/phase context; allow Symptom→Action recommendations where no intermediate cause is sourced. Separate domain concepts from Document, Version, Evidence and Claim provenance concepts. Document final names and mappings to the existing schema. Define unknown conditions, contradictions and claim withdrawal. Prepare examples before requesting Gaël's review.

### First-cycle success criterion

A small troubleshooting assistant works entirely locally on a few verified facts and exposes the exact evidence and conditions behind answers. Its report distinguishes tested, measured, reviewed and unknown aspects. The graph may initially be small and manually populated; adopt automation only when its value is measured.

Sources: local roadmap/guides read on 18 October 2026; [Cytiva extraction diagnostic](../experiments/cytiva-local-extraction-diagnostic.md). Primary documentation consulted: [Ragas metrics](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/), [OpenTelemetry GenAI conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) and [Docling Graph dense extraction](https://github.com/docling-project/docling-graph/blob/main/docs/fundamentals/extraction-process/dense-extraction.md).
