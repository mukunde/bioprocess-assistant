# Roadmap: evidence-grounded bioprocess assistance

## Direction

Keep Neo4j as the published knowledge store. Add a separate PDF ingestion job,
review extracted claims before publication, and measure both answer quality and
cost. Adopt useful KAG principles incrementally; do not migrate to OpenSPG yet.
The reliability baseline is implemented. Ingestion/review and local passage
retrieval have been exercised on selected real-manual examples; the reviewed
knowledge is not yet served by the chatbot. Portable telemetry, independent
answer evaluation and the common-corpus retrieval comparison remain pending.
See [the ingestion guide](INGESTION.md) for the separate local pipeline.

2026-10-19 extraction decision: provisionally retain GPT-6.1 Sol (medium) for rare
strong-model extraction. Claim contract v0.2 and per-claim quarantine are implemented. The earlier-prompt
100–102 package remains archived. The local `pages-100-102-v02-r2` package is
reviewed after one subscription generation on 59 source elements: 33 final claims,
19 validated and 14 validated with reservations (20 October 2026). See the
[curated review package](../experiments/cytiva/reviewed-r2/README.md).
Publication, scientific validation and migration into the existing UI remain pending.
The 97–99 comparison remains a development result, not a general model ranking.
Migration from the legacy dense template/review database is still pending.

## Agreed constraints and current state

- Prioritize troubleshooting: symptoms, possible causes and actions. Demonstrate
  both AI/LLM engineering and data/knowledge engineering.
- Budget below EUR 10/month; local processing by default. Subscription-interface
  experiments on the public manual are explicitly authorized. No API purchase is
  implied. The user is available during weekdays; there is no global five-hour
  weekly limit.
- The user can verify documentary fidelity without an external domain expert.
  Operational suitability is a separate claim and is not established here.
- The local Ministral dense extraction produced 29 entities and no semantic
  relations in approximately 56 minutes. The subscription comparison on pages
  97–99 led to provisional selection of GPT-6.1 Sol; see
  [the fidelity review](experiments/cytiva-v01-fidelity.md).
- Contract v0.2 separates purpose/conditions, force, quantities and source
  quarantine. The archived 100–102 package contains 59 Docling items from the earlier prompt;
  it is unexecuted. The corrected-prompt `pages-100-102-v02-r2` package has completed
  generation and per-claim human documentary review (33 final claims, none pending).
  This development review is not an exhaustive gold benchmark or a causal retrieval
  evaluation. Reviewed cleaning and contaminant sources/questions now extend the
  procedural sample; their retrieval results are summarized below. Next: preserve
  decisions/reservations in the serving adapter and measure coverage independently.
- The earlier [methodology review](decisions/2026-10-roadmap-review.md) is an
  archive of the reasoning, not a second plan to maintain.

## Current checkpoint — 26 October 2026

Phase numbers identify workstreams and acceptance gates, not a completed linear
sequence. Documentary work advanced before telemetry; local manifests and timings
do not complete phase 1.

| Workstream | Merged/observed | Remaining gate |
|---|---|---|
| 0 — Reliability | Constrained rendering, error handling, additive graph loading and offline regressions | Live end-to-end deployment evaluation |
| 1 — Observability | Experiment manifests, context/token accounting and descriptive local timings | OpenTelemetry export, call/retry/cost accounting and enforcement |
| 2 — Model and references | Minimal ontology/claim contract, reviewed extraction and Q/N/C/H/V/W/X records; S01-S12 decisions/export merged | Exhaustive coverage, independently authored evaluation and actual answer quality; documentary review is not scientific validation |
| 3 — Ingestion/chunking | Local Docling Graph route, separate reviewed Docling → GPT extraction, targeted table/figure reviews and repairs | Full lifecycle, real-manual precision/recall and serving migration |
| 4 — Retrieval/interpretation | BM25 experiments and blocked v03b/v04/v05 results preserved; reviewed structured control and passing S trial merged | Refined free-text fixture review, interpreter/bridge implementation, new frozen S/F trial, serving adapter and answer evaluation |
| 5 — KAG decision | Deferred; LightRAG remains a separate comparison candidate | A measured need beyond simpler retrieval and bounded reasoning |

The merged baseline is `main` at `1b852f4`, after
[PR #39](https://github.com/mukunde/bioprocess-assistant/pull/39) (reviewed X trial),
[PR #40](https://github.com/mukunde/bioprocess-assistant/pull/40) (request contract/spec),
[PR #41](https://github.com/mukunde/bioprocess-assistant/pull/41) (corrected control),
and [PR #42](https://github.com/mukunde/bioprocess-assistant/pull/42) (reviewed S trial).
The maintained suite passed **556/556 tests**, none skipped, on this integrated
baseline with external connections blocked and loopback tests allowed. Earlier
463/483 checkpoints remain historical, not the current test count. This is not
fresh-install certification or a generated-answer benchmark.

### Completed versus prepared locally

- **Merged:** the [v05 X review/export](../experiments/cytiva/reviewed-v05-evaluation/README.md)
  preserves its blocked outcome: 7/12 intents evidence-complete in both languages;
  only X02/X05/X09 meet completeness, scope and diagnostic criteria. Its 9/24
  scope and 6/24 diagnostic failures are not rewritten.
- **Merged:** the [structured S01-S12 export](../experiments/cytiva/reviewed-structured-control/README.md)
  preserves twelve actual approvals, the S01 form amendment and all 24 saved
  outputs. All 12 paired scenarios pass their reviewed context/diagnostic gate;
  E118-I/E121-EQ stay excluded. The [outcome report](experiments/cytiva-structured-control-s-results.md)
  records limitations and the 348–1,504-token contexts. This is an intent-supplied
  control, not evidence of free-text understanding or scientific suitability.
- **Local, not merged or implemented:** [CP comparison protocol](experiments/structured-free-text-comparison-v01.md),
  [FI interface](technical/FREE-TEXT-INTERFACE-V01.md), three [MC machine schemas](technical/FREE-TEXT-MACHINE-DESIGN-V01.md)
  and actual collective decision records. CP01–CP06, FI01–FI06/IF01–IF14 and
  MC01–MC06 with their clarifications are approved design choices.
- **Local, still pending human review:** sixteen refined machine examples and
  three invalid caller inputs, organized into [GR01–GR04](experiments/free-text-interface-group-review-v01.md).
  Precise origins, absence/default reasons, externally supplied boundary conditions,
  injected errors and rejection audit are prepared and statically checked.
  Those checks do not execute the interpreter or establish IF conformance.

The [proposed design delivery](experiments/free-text-design-package-v01.md)
lists the exact files; the sixteen older local S preparation/review notes remain
outside it. Original historical preparation flags, raw runs and decisions are
preserved. No experimental method is activated in the chat by these updates.

### Next delivery priorities

1. **Complete the four fixture groups, then implement the bounded language interface.**
   Keep origin and policy issues separate from the unchanged structured core.
   Preserve every requested unit, including blocked/unresolved ones, in the global
   outcome. Declare EN/FR coverage and pass IF01–IF14 before candidate freeze.
   Do not start another generic specification cycle unless an actual gap appears.
2. **Freeze and evaluate S versus unassisted free text.** Use known P01–P12 and
   G01–G06 for development, with separate documentary/semantic denominators.
   After freezing the candidate, author twelve new bilingual intents and review
   exact inputs, origins and references before one saved S/F trial. Retain all
   failures without retuning. Unrepresentable owner ambiguities remain semantic-only;
   post-confirmation human corrections are a separate arm, not F0 performance.
3. **Build a bounded serving slice.** Connect eligible reviewed v0.2 records to
   the renderer; retain versions, conditions, reservations and quarantine.
   Exercise clarification/refusal, correction, revocation and rollback. Do not
   silently promote blocked retrievers or expand the legacy seed's scope.
4. **Instrument and evaluate the real answering path.** Add OpenTelemetry spans,
   provider usage/retry/cost accounting and budget checks. Evaluate generated
   answers, citations and abstentions with deterministic checks, calibrated local
   Ragas and Promptfoo attacks with benign controls. All three integrations are pending.
5. **Compare architectures after prerequisites.** Run graph/passages/LightRAG
   against a common corpus and resource budget. Benchmark local answering under
   a separate approved experiment; keep KAG and fine-tuning conditional on failures
   that simpler approaches do not address.

No additional representative-page review is required by default. Reopen conversion
only when a new format, measured failure or required source exposes a gap. Optional
pages 53/86/142 are untested extensions, not a whole-manual review queue.

## Phase 0 — Reliability baseline (implemented; deployment gate separate)

- Reject unverified free-form model answers. The model selects retrieved result
  IDs; application code renders graph facts and their sources.
- Keep French/English headings and refusals. Technical facts remain verbatim in
  their canonical English until reviewed translations are available.
- Fail evaluations on unexpected refusals, incorrect symptom selection, missing
  verdicts and invalid judge output. Separate lexical English retrieval from the
  bilingual end-to-end contract.
- Make seed import additive, publish seed changes atomically, and wait for the
  full-text index before serving queries. Remove automatic domain-wide deletion.
- Preserve zero thresholds and reject negative/non-finite thresholds.
- Add offline regression tests; no live database or paid API needed.

Exit: offline regression tests pass. Live Neo4j/Anthropic evaluation remains a
separate required check before deployment. Historical scores are not scores of
this revised pipeline.

## Phase 1 — Portable observability (pending; next integration prerequisite)

Use a provider-neutral call wrapper with an optional Langfuse sink. Record a
trace ID, operation (chat / extraction / judge), model, prompt/schema version,
latency, status, provider request ID, attempts, and provider-reported token usage.
Separate uncached input, cache reads, cache writes and output tokens. Retain a
versioned price configuration, currency and effective date; label calculated
amounts as estimates and reconcile them with provider billing.

Do not log prompts, PDFs, credentials or user identifiers by default. Keep the
assistant working when telemetry is unavailable. Add per-run extraction budgets,
explicit retry limits and spend alerts; monitoring alone is not budget enforcement.
Instrument agent, judge and future extraction calls, not just the chat endpoint.

Exit: one trace per workflow with linked calls; successful, failed and retried
calls are accounted for; unknown pricing is reported as unknown, never zero.
Validate usage and cost accounting on fixed fixtures including cache usage.

## Phase 2 — A versioned domain model and a reference extraction set

Status: [minimal ontology](ontology/v0.1.md), [claim contract v0.2](CLAIM-CONTRACT-V02.md)
and scoped human references are implemented. The 33 extraction claims and reviewed
Q/N/C (28 intents), H (10) and V (12) series are documentary/development references
with overlapping facts. W and X each add twelve reviewed same-corpus intents; S adds twelve reviewed structured diagnostic scenarios. These do not establish
exhaustive extraction recall, independent authorship or a held-out answer benchmark.
The target model and acceptance gate follow;
the implemented subset is summarized above.

Add stable domain IDs independently of display names. Model Document,
DocumentVersion, Evidence (page, block/table/cell, exact quote), Claim,
Symptom, Cause, Action, Resin, ProcessStep and ApplicabilityCondition.
Capture units, ranges, negations, resin-specific restrictions and document date.
Use separate Evidence for each factual claim and each causal relationship.
Keep source statements separate from expert interpretations and inferred claims.

Curate a reference set from a few representative Cytiva pages (paragraphs,
troubleshooting tables, footnotes, scans). Have the user check documentary fidelity
against the source, including numerical recommendations; mark uncertainty rather
than assuming operational validity. Domain expertise remains a separate requirement
before an operational industrial use is claimed.

Exit: schemas, stable IDs and reference annotations reviewed; every published
claim has a traceable source and an applicability context.

## Phase 3 — Docling Graph ingestion into staging

Status: isolated local conversion/extraction/review and optional separate evidence
publication exist. The GPT-6.1 Sol subscription extraction is a distinct reviewed
route, not evidence that the local model achieves the same quality. Neither
route feeds the existing chat. End-to-end acceptance criteria below remain open.

PDF registry + SHA-256/version -> Docling conversion -> schema-constrained
Docling Graph extraction -> validation -> staging -> human review -> publication
into Neo4j. Run outside the interactive Chainlit container and pin the ingestion
runtime separately. Verify the chosen release's Python/backend compatibility.

Use Pydantic templates for domain objects, an adapter into our domain schema, and
explicit provenance validation. Docling Graph exports are not automatically our
production schema. Verify page/quote grounding on the reference set; schema-valid
JSON does not establish scientific truth. Never execute model-generated Cypher.
Use parameterized publication queries, stable IDs, content hashes and checkpoints.
Re-importing the same approved version must not duplicate or remove knowledge.

Exit: extraction precision/recall on annotated claims and relations; complete
verified provenance for published claims; rejection of unsupported numbers;
reviewed contradictions; idempotent import, resume and rollback exercised.
Measure cost per PDF/page and per approved claim, including retries/review rejects.

### Completed targeted reviews — tables, captions and diagrams

The [conversion/chunking protocol](experiments/cytiva-conversion-chunking-protocol.md)
was exercised without extraction LLMs or paid APIs on pages 77, 88, 104 and
152–153. T0/T1 conversion and K0/K800 tests preserve historical outputs; later
repairs and reviewed annotations are new artifacts. Table recognition was
**disabled in the earlier r2 extraction**, so these are separate experiments.

| Reviewed example | Completed scope | Retained limits |
|---|---|---|
| [Page 77](../experiments/cytiva/reviewed-page-077/README.md) | Ten cards: species/header scope, pH, seven remarks and observed chunk conservation | Source blanks stay blank; some applicability context is in a different chunk; no production retrieval approval |
| [Page 88](../experiments/cytiva/reviewed-page-088/README.md) | Nine cards: deterministic coordinate reconstruction, 40 cells, five notes and 12 cell-note bindings | Original available-formats conversion defect remains historical; reconstruction is specific to this table, not a general converter fix |
| [Page 104](../experiments/cytiva/reviewed-page-104/README.md) | Six cards: image/caption, five paths, alternative, applicability, VH3 and K0/K800 conservation | Reviewed paths are human readings, not extracted directed edges; automatic text-only diagram semantics remain quarantined |
| [Pages 152–153 v1](../experiments/cytiva/reviewed-pages-152-153/README.md) and [v2](../experiments/cytiva/reviewed-pages-152-153-v2/README.md) | Six initial decisions plus one v2 conservation decision: HiTrap/HiScreen repair, continuity, note scope and integrated annotations | Three ambiguous rows remain physically quarantined; no complete property-cell or production retrieval approval |

Current scoped decisions are in each package's review record. Historical pending
flags in frozen preparation artifacts stay unchanged. Reservations, source
provenance and original human quotations remain part of the accepted record.

These examples validate observed conversion/chunk conservation and documentary
readings with reservations. They do not establish automated diagram reasoning,
optimal chunk size, retrieval completeness, full-manual correctness or scientific
applicability. K600/K1400 and optional pages 53/86/142 remain untested; broadening
the matrix requires a concrete need rather than a default page-by-page review.

## Phase 4 — Contextual retrieval and bounded reasoning

### Implemented development baseline

Local BM25 retrieval and atomic context assembly use exact reviewed passages,
source dependencies, immutable run manifests and a 2,048-token serialized-context
cap. No LLM, embedding model or paid API was needed for these trials. The cap does
not include a future answer prompt or output. Earlier trials/configurations are
preserved and no experiment silently changes the chat default.

| Reference series | Observed result | Interpretation |
|---|---|---|
| [Q01–Q10 and N01–N08](experiments/cytiva-retrieval-depth-results.md), cleaning pp. 166–167 | Six hits preserve 10/10 Q and improve N from 7/8 to 8/8 with complete required evidence in both languages | N05's sixth-ranked passage and dependent heading are recovered; greater context size is not proven better precision |
| [C01–C10 first run](experiments/cytiva-contaminants-retrieval-results.md), contaminants pp. 118–121 | Five → six hits improves bilingual completeness from 5/10 to 6/10 | Ranking/vocabulary and missing section introductions remain measurable failures |
| [C01–C10 ablation](experiments/cytiva-contaminants-context-results.md) | Baseline 6/10, vocabulary 7/10, section 10/10, combined 10/10; section/combined maximum 2,027 tokens | Context of section explains most gain; combined saves 20.35 mean tokens versus section-only in this sample |
| [Frozen H01-H10 section-only run](../experiments/cytiva/reviewed-section-evaluation/README.md) | 8/10 intents complete in both languages (EN 9/10, FR 8/10) | Gate blocked; later inspected failures became development inputs |
| [Frozen v03b / V01-V12](../experiments/cytiva/reviewed-v03b-evaluation/README.md) | 6/12 complete in both languages, but only 3/12 also respect explicit scope; all 24 contexts retained | Merged blocked result; no source leakage, but omissions and unrequested phase context prevent promotion |
| [v04 development A-D](../experiments/cytiva/compositional-navigation-v04-results/README.md) | Final known-case evidence coverage V12/12, H10/10, C10/10 in both languages; V has zero unrequested/outside-acceptable context | Merged opt-in development variant after failure inspection, not an independent evaluation or default change; one optional V03 seed is still dropped at six seeds |
| [Frozen v04 / W01-W12](../experiments/cytiva/reviewed-v04-evaluation/README.md) | 8/12 complete in both languages; only W10/W11 satisfy completeness, explicit scope and diagnostics | Merged blocked trial: 13/24 explicit scope failures, 2/24 diagnostic failures; no generated answers |
| [v05 development A-B](../experiments/cytiva/polarity-navigation-v05-results/README.md) | Final known-case W12/12, V12/12, H10/10, C10/10; intermediate C02 failure retained | Merged development result, not generalization; missing H/C scope annotations remain unavailable |
| [Frozen v05 / X01-X12](../experiments/cytiva/reviewed-v05-evaluation/README.md) | EN 8/12, FR 7/12, both 7/12 complete; only X02/X05/X09 satisfy all reference criteria | Merged reviewed packet; gate blocked by scope/diagnostic failures; no method tuning after results |
| [Structured S01-S12](../experiments/cytiva/reviewed-structured-control/README.md) | 24/24 submitted forms and 12/12 bilingual pairs pass context/diagnostic checks; 348–1,504 tokens | Merged structured control on known code/corpus; no free-text or generated-answer validation |
| [Local free-text design](technical/FREE-TEXT-MACHINE-DESIGN-V01.md) | CP/FI/MC decisions approved, machine artifacts prepared, GR01–GR04 pending | No interpreter/bridge implementation or S/F execution; exact case/origin approval remains separate |

The original Q/N/C series contains 28 intents with paired FR/EN formulations,
not 56 independent observations. H/V/W/X add same-corpus challenges with known-code
authorship; inspected failures become development inputs. Required-source presence
is not answer correctness, refusal quality or measured precision. Section-only
was a historical ablation preference. The latest frozen v05 X run is blocked;
no candidate becomes the chat default through these experiments. W and X use
different questions and their aggregate scores are not a controlled v04/v05
comparison. Neither is a new-section/manual or independently authored benchmark.

On V, frozen v03b averaged 705.33 context tokens (maximum 1,187); final v04 known-V
development averaged 663.75 (maximum 1,220). Frozen v04 W averaged 813 (maximum
1,741), while v05's known-W development averaged 684.83 (maximum 1,109). The later
frozen X run averaged 757.92 (maximum 1,187). These are recorded serialized-context
sizes under the 2,048-token cap, not future prompt/answer tokens or paid usage.
No X source bundle was rejected by budget and no selected seed exceeded the cap;
larger context/result limits do not explain or solve the observed X failures.

E118-I and E121-EQ remain pending and excluded from indexes and contexts,
including indirect dependencies. Validating W10/W11 or X10 does not approve them;
E119-I is separately eligible. W09/X09 pressure absence is bounded to the 25
eligible excerpts. W12 and X11/X12 are labelled synthetic scope controls, not
contradictions in the manual. No generated answer is scored in these trials;
metadata flags do not certify actual clarification or correct sample attribution.

The X traces identify finite exclusion/uncertainty vocabulary, nested negation,
request-wide conflict sets without task ownership, and routing/lexical mismatch.
For X10, English family support even relies on incidental words while French
has no general-family lexical hit. The task-scoped request contract and structured control are now merged; their separate S trial passes. Free-text interpretation and its bridge remain unimplemented. A passing structured trial is not an implemented v06 language fix.

### Remaining product and reasoning requirements

Retrieve multiple candidates, preserve negations and distinguish multiple symptoms.
Ask for missing resin, phase or operating context before proposing conditional
procedures. Separate text relevance from diagnostic confidence. Index source
passages alongside graph facts; expose evidence to the user.

Adopt KAG principles: explicit ontology, concept alignment, graph-to-passage links,
and bounded rule evaluation. Start with a small set of expert-reviewed rules over
Neo4j and record premise IDs, rule version and derived conclusions. Unknown
conditions produce unknown/clarification, not an assumed truth.

Exit: independent held-out bilingual and adversarial cases covering near-domain
misses, contradictory manuals, negation, multiple symptoms, missing context,
invalid instructions and unsupported numerical claims. Compare with phase 0 on
accuracy, false acceptances, refusal quality, latency and cost.

### Candidate evaluation: LightRAG versus simpler retrieval

LightRAG is a candidate for evaluation, not an adopted dependency or a replacement
for the v0.2 contract, manual review, quarantine or Neo4j service graph. Follow the
[three-arm retrieval protocol](experiments/retrieval-comparison-protocol.md):
current lexical/graph retrieval family, simple passage retrieval, and LightRAG on
the same reviewed corpus and canonical passages. Keep the unchanged legacy app
as a separate coverage witness; do not rank its six-symptom seed directly against
a larger indexed manual.

First compare retrieval alone, then use a common answer model and validated
renderer only after the required adapters exist. Freeze questions, input hashes,
chunking, context budgets and configurations; measure evidence quality, refusal,
conditions/quantities, latency, tokens and RAM on the local PC. Use local models
with zero additional API spend. Compare chunking/extraction variants separately.
Only consider adoption if the measured gain over the simpler alternatives survives
resource, provenance and quarantine checks. The three-arm comparison and LightRAG
integration remain unexecuted. Existing
BM25 trials are a lexical baseline/ablation; they do not implement the protocol's
simple multilingual-vector arm or its common-corpus graph and LightRAG adapters.
Reconcile the separately tested six-hit candidate with the protocol's five-passage
limit by declaring and freezing one shared comparison policy before measurement.

## Phase 5 — Decide whether an OpenSPG KAG experiment is justified

Only if representative tasks require multi-hop reasoning beyond the bounded
Neo4j approach, run an isolated OpenSPG KAG comparison on the same held-out set,
sources and model budget. Include indexing/operations cost and evidence quality.
Do not replace the production store unless the measured gain justifies migration.
Neither a graph nor KAG guarantees absence of hallucinations or GxP suitability.

## Reference documentation (consulted 2026-10-17)

- Docling Graph: https://github.com/docling-project/docling-graph
- Graph/provenance management: https://github.com/docling-project/docling-graph/blob/main/docs/fundamentals/graph-management/index.md
- OpenSPG KAG: https://github.com/OpenSPG/KAG
- KAG paper: https://arxiv.org/abs/2409.13731
- Langfuse usage/cost: https://langfuse.com/docs/observability/features/token-and-cost-tracking
- Background article supplied by the user: https://sergeyvasiliev.substack.com/p/rag-vs-graphrag-vs-kag


## Design decisions from the observability/provenance discussion (2026-10-17)

These are design requirements, not integrations implemented in phase 0.

### Portable tracing

Instrument application boundaries with the OpenTelemetry SDK, export OTLP to an
OpenTelemetry Collector, and configure backend exporters independently. Use GenAI
semantic conventions pinned to a documented version plus a small bioprocess.*
namespace. Keep backend-specific mappings in collector configuration or an adapter.
Prove portability by sending one fixture trace to two backends and checking parent
links, timings, errors, usage and retrieval metadata. Transport compatibility does
not guarantee equivalent dashboards, evaluation storage or price calculations.

Record graph/document snapshots, model/prompt/schema versions and immutable result
references. Keep large source payloads in controlled artifact storage rather than
span attributes. Export metadata only by default; full-context capture is explicit.

### Ragas and adversarial evaluation

Use Ragas alongside deterministic contracts, with explicitly configured judge and
embedding providers (local for offline mode). Serialize graph evidence into source
contexts while retaining IDs. Evaluate answer relevance, context usefulness and
reference-based correctness; do not rely on final-text faithfulness alone, since
our renderer already reproduces graph facts. Extend evaluations to PDF-to-claim
fidelity and relation direction. Judge scores are not manual approval.

Use Promptfoo as the initial red-team harness against the complete application,
with generation, grading and any embedding calls configured locally for offline
runs. Add direct and document-borne injection, fake citations, wrong resin/operation,
negation, unit changes, missing conditions and budget-exhaustion cases. Keep a
balanced benign set to detect an always-refuse regression. Use deterministic
checks for schema/IDs/sources/budgets and calibrated judges for semantic errors.
Store minimal attack fixtures and regression outcomes, not unreviewed malicious
content in the published graph. Garak is an optional second tool for model-level
probes, not an additional mandatory dependency.

### Claim-level evidence contract

Docling Graph's detailed provenance is a starting point. Its verbatim match can
locate an entity identifier without proving every property or relation. Preserve
the full provenance ledger and distinguish exact, approximate and unresolved
anchors. Build an application Evidence record for every atomic claim, including
relations and numerical properties:

- immutable PDF SHA-256 and document version;
- conversion, extraction schema/model and chunking configuration versions;
- PDF page index (explicitly zero-based) and optional printed page label;
- Docling item references and geometry with coordinate-system metadata;
- exact source quote, text hash and offsets into an immutable text artifact;
- table/row/column/footnote references when applicable;
- subject, predicate, object/value/unit, polarity and applicability conditions;
- explicit source statement vs derived interpretation;
- localization check, semantic judge verdict, manual review and reviewer/date.

Code resolves artifact IDs to registered paths (never arbitrary model-supplied
filesystem paths). Deterministic checks verify file identity, page/item existence,
quote/span alignment and supported numeric/unit conversions. A text match proves
location, not general semantic entailment. An optional judge reads only the cited
passages plus required headers/notes and returns supported / contradicted /
insufficient, with evidence IDs. Publication remains manually reviewed. Never
upgrade approximate anchors or judge scores to manual approval.

Provide a review screen linking each claim/relation to highlighted PDF passages,
with approve/reject/edit actions and an append-only review record. The user can
validate documentary fidelity even without access to a domain expert; that is
not the same as validating a procedure for a particular industrial process.

### Chunking experiments

Separate extraction windows from retrieval/evidence units. Start with Docling's
structural chunks and preserve heading trails, product/resin scope, warnings,
footnotes, table headers and continuation links. An extraction unit should keep a
troubleshooting row (symptom, cause, remedy) together. Split oversized tables by
rows with repeated headers/context; do not cut a value away from its unit or note.
Cross-page sections may stay together while retaining exact per-item page anchors.

Compare structural section/row windows against the whole small document baseline
and bounded token-budget windows (initial experimental values: 600/1000/1400,
counted with the actual model tokenizer). These values are hypotheses, not chosen
optima. Overlap should repeat required context, not indiscriminately copy text.
Deduplicate by evidence identity. Compare missing relations, incorrect cross-row
links, numeric errors, provenance quality, review effort, latency and tokens.

### Latency and local inference experiments

The current query is fixed parameterized Cypher, not LLM-generated Cypher. Trace
cold-start/connection time, database execution and fetch, each LLM call and retry,
serialization size, and rendering independently. Neo4j does not consume LLM tokens;
resubmitting graph results to the model does. Benchmark warm and cold separately.

Compare the current loop with: (a) deterministic bilingual symptom selection;
(b) one constrained local classification/extraction call followed by a parameterized
query and deterministic rendering, without returning long graph descriptions to
the model; (c) the existing hosted model baseline. Preserve negation and scope
checks and evaluate false acceptance before adopting a faster route.

For a small static dataset, compare an immutable JSON adjacency map or SQLite FTS
snapshot with Neo4j. Include snapshot/version consistency and publication updates;
retain Neo4j unless measured benefits justify another serving representation.

Start local model trials with Ministral-3-3B-Instruct-2512 GGUF Q4_K_M; compare
Qwen3.5-4B with thinking disabled for short structured tasks. Pin exact artifacts
and runtimes. No fine-tuning until held-out errors show a stable learnable problem;
fine-tune routing/extraction format, not mutable handbook facts. Hardware fit and
answering latency remain to be benchmarked on the known reference PC: Intel
i5-1135G7 (4 cores/8 threads), 16 GB RAM and Intel Iris Xe, without a CUDA GPU.
The earlier 56-minute extraction does not measure interactive answering latency.

### Visualization and portfolio deliverables

Use Neo4j Browser/Query for instances and schema exploration. Use local Protege
only if an explicit OWL ontology adds value; an observed Neo4j schema is not a
formal ontology. Initially document allowed types, predicates and constraints in
a versioned schema rather than maintaining unnecessary duplicate representations.

Portfolio evidence: reproducible local startup, reviewed source-linked examples,
held-out evaluation and red-team reports, measured cost/latency comparisons,
portable telemetry export, a brief demo, and candid limitations. CI is a future
proposal, not an instruction to publish or bypass user validation.

### Additional primary references

- OpenTelemetry GenAI: https://opentelemetry.io/docs/specs/semconv/gen-ai/
- Langfuse OTLP compatibility: https://langfuse.com/integrations/native/opentelemetry
- Docling Graph provenance: https://github.com/docling-project/docling-graph/blob/main/docs/fundamentals/graph-management/provenance.md
- Docling chunking: https://github.com/docling-project/docling/blob/main/docs/concepts/chunking.md
- Ragas metrics: https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/
- Promptfoo local generation configuration: https://www.promptfoo.dev/docs/red-team/configuration/
- Ministral GGUF: https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512-GGUF
- Qwen3.5 4B: https://huggingface.co/Qwen/Qwen3.5-4B
- Neo4j Browser: https://neo4j.com/docs/browser/
- Protege: https://protege.stanford.edu/software/


## Implementation update: first ingestion/review slice

Implemented an isolated, pinned Docling Graph dense adapter using native hybrid
chunking and detailed provenance, Pydantic entity/relation templates, immutable
source/conversion/ledger artifacts, deterministic quote localization, manual
approve/reject decisions, correction into a new run, and approved snapshot export.
A loopback UI displays extracted passages and PDFium-rendered source pages.
Optional parameterized Neo4j publication creates a separate reviewed evidence
snapshot; the chatbot's existing graph is not automatically enriched.

Initial validation covered synthetic fixtures and the upstream configuration
contract. Subsequent real-manual conversion/chunking reviews and passage-retrieval
experiments are summarized above; the initial local extraction's limitations are
retained in [its diagnostic](experiments/cytiva-local-extraction-diagnostic.md).
Selected table repairs and conservation checks do not complete phase 3 extraction
precision/recall, lifecycle or publication acceptance. Ragas, OpenTelemetry,
Promptfoo execution and the reviewed-record serving adapter remain unimplemented.
See [INGESTION.md](INGESTION.md) for local commands and route-specific limitations.
