# Roadmap: evidence-grounded bioprocess assistance

## Direction

Keep Neo4j as the published knowledge store. Add a separate PDF ingestion job,
review extracted claims before publication, and measure both answer quality and
cost. Adopt useful KAG principles incrementally; do not migrate to OpenSPG yet.
The reliability baseline is implemented. Ingestion/review and local passage
retrieval have been exercised on selected real-manual examples; the reviewed
extraction is not yet served by the legacy chatbot. A separate model-free guided
demo serves 25 reviewed passages through frozen v03. A merged, separate
Protein A/G Sepharose backpressure journey now reuses scoped cleaning reviews
and original citations, without a model or database. Portable telemetry, independent
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

## Current checkpoint — 31 October 2026

Phase numbers identify workstreams and acceptance gates, not a completed linear
sequence. Documentary work advanced before telemetry; manifests and timings do
not complete phase 1. The legacy chatbot still uses its curated graph; the
separate local guided/text demo serves a bounded set of 25 reviewed passages.
The first product/context troubleshooting journey is now merged and independent
of that frozen interpreter; it does not change the legacy chat graph.

| Workstream | Merged/observed | Remaining gate |
|---|---|---|
| 0 — Reliability | Constrained rendering, error handling, additive graph loading and offline regressions | Live end-to-end deployment evaluation |
| 1 — Observability | Experiment manifests, context/token accounting and descriptive local timings | OpenTelemetry export, call/retry/cost accounting and enforcement |
| 2 — Model and references | Minimal ontology/claim contract and reviewed extraction/questions; S, FT and FV deliveries merged | Independent evaluation, exhaustive coverage and actual answer quality; documentary review is not scientific validation |
| 3 — Ingestion/chunking | Docling Graph route, separate reviewed Docling → GPT extraction, selected table/figure reviews and repairs | Full lifecycle, real-manual precision/recall and serving migration |
| 4 — Retrieval/interpretation | BM25 trials, structured control, FT/FV comparisons, corrected opt-in v03, its runtime freeze, corrected local demo, Windows installer and launcher merged; same-PC fresh-clone setup verified; bounded Protein A/G backpressure journey merged | Product-specific scope extension, second-machine setup/walkthrough and independent serving/answer evaluation |
| 5 — KAG decision | Deferred; LightRAG remains a separate comparison candidate | A measured need beyond simpler retrieval and bounded reasoning |

Current merged baseline: `main` at `7d6b9c2`, including
[PR62](https://github.com/mukunde/bioprocess-assistant/pull/62) (bounded
backpressure journey) and [PR63](https://github.com/mukunde/bioprocess-assistant/pull/63)
(documentation digest repair). The exact merged files passed the full
**800-test suite: 799 passed, one optional PDFium preview dependency skipped,
no failures or errors**. Twenty affected-package checks passed again after merge.
These regressions do not validate diagnosis, operational use or generated answers.

The historical 27 October baseline is `main` at `4b2bfa5`, including
[PR51](https://github.com/mukunde/bioprocess-assistant/pull/51) (v03 runtime freeze),
[PR52](https://github.com/mukunde/bioprocess-assistant/pull/52) (demo and usability fixes)
and [PR53](https://github.com/mukunde/bioprocess-assistant/pull/53) (Windows launcher),
followed by [PR55](https://github.com/mukunde/bioprocess-assistant/pull/55)
(isolated Windows installation and verified tokenizer setup).
The full maintained suite passed **790/790 tests** on that integrated baseline,
with no errors, failures, skips or external connection attempts. Earlier 556,
603, 667, 757 and 780 checkpoints remain historical. This is neither clean-OS
certification nor a generated-answer benchmark. Separate installation evidence
comes from a fresh clone on the same PC, not a second physical machine.

### Merged evidence, runtime freeze and demo

- **Merged:** the [v05 X export](../experiments/cytiva/reviewed-v05-evaluation/README.md)
  preserves its blocked outcome. The [structured S export](../experiments/cytiva/reviewed-structured-control/README.md)
  passes 24/24 reviewed submitted forms and 12/12 pairs; it does not establish
  free-text understanding.
- **Merged:** CP/FI/MC decisions, machine schemas, actual GR01–GR04 approvals and
  the bounded EN/FR interpreter/bridge with IF conformance. Earlier documents
  describing pending examples/unimplemented runtime are historical checkpoints.
- **Merged:** [FT01–FT12](../experiments/cytiva/free-text-comparison-v01/README.md),
  with twelve approvals and 48 retained outcomes: S 24/24, F0 12/24 observations,
  4/12 bilingual pairs. The freeze was not retuned. Consulted FT inputs became
  [opt-in v02](technical/FREE-TEXT-CANDIDATE-V02.md) development regressions; v02
  passes 57 targeted checks but is not the default runtime or chat route.
- **Merged in PR48:** the
  [FV01–FV12 package](../experiments/cytiva/free-text-v02-comparison-v01/README.md)
  freezes v02 before new wording, preserves twelve human approvals (including
  one collective FV05–FV12 message) and all 48 native outcomes. Official gates:
  **S 22/24, F0 17/24, EN 10/12, FR 7/12, 7/12 pairs**. Acceptance remains blocked.
  FV04 collapses distinct buffer-use items; FV07/FV11/FV12 expose FR phase
  association failures. FV06 fails only a shared aggregate flag in both arms:
  individual states/bindings match, and no adjusted score is substituted.

- **Merged in PR49/PR50:** the coverage contract separates eligible context from
  whole-request support. Corrected v03 preserves buffer occurrences, rejects
  unrepresented coordination, retains inherited French phase origins and checks
  contradictory counts. Its 76 checks use known development inputs; historical
  FT/FV gates and scores are unchanged.
- **Merged in PR51:** the [v03 runtime freeze](../experiments/cytiva/free-text-v03-freeze-v01/README.md)
  pins 36 engine/shared dependency, policy and environment files. Runtime integrity
  does not supply a new prospective score or change the legacy chat default.
- **Merged in PR52:** the user-selected [guided Cytiva demo](DEMO-FIRST.md)
  serves the 25 eligible excerpts without a model or Neo4j. The browser walkthrough
  covers citations, clarification, partial service and quarantine. Corrections
  make stale results, missing-format recovery and source/result navigation explicit;
  quote highlighting preserves the original text.
- **Merged in PR53:** the Windows launcher starts the demo in one command after
  checking Python, 12 dependency versions, offline tokenizer integrity and all
  36 frozen files. It installs/downloads nothing and does not establish that a
  fresh machine can reproduce the prepared environment. No new trial was run.

The [historical delivery inventory](experiments/free-text-v02-reviewed-package.md)
keeps raw outputs and the 16 older S preparation/review notes outside the lot.
Original decisions, reference reservations, locks and results remain unchanged.
No experimental interpreter or retriever is activated by this documentation.

**Merged in PR55:** an explicit Windows setup command creates
an isolated `.venv-demo`, installs the 12 frozen dependencies from a wheel-hash
lock and prepares the verified tokenizer cache. Installation and the guided
walkthrough were exercised in a fresh local clone, with no old project environment
or tokenizer copied into it. Package downloads could use the workstation's pip
cache. This is same-PC reproducibility evidence, not a second physical-machine or
clean-OS certification. Ten installer regressions and seven browser/HTTP scenarios
passed; all five displayed source quotations matched their returned text exactly.
The launcher readiness check passed again on merged main. See the
[installation review](experiments/cytiva-demo-installation-review.md). v03 is unchanged.

**Published on 29 October 2026:** the human-approved 34-second onboarding v05
package (PR58), README integration (PR59) and GitHub Pages player (PR60) are merged.
The [video](https://mukunde.github.io/bioprocess-assistant/) plays from the README
poster without a manual download. The [successful deployment and public check](CYTIVA-VIDEO-HOSTING.md)
concern media delivery, not hosted interactive assistance, answer quality or
second-PC installation. Frozen v03 and all prior experiment results are unchanged.

### Merged bounded troubleshooting journey

[PR62](https://github.com/mukunde/bioprocess-assistant/pull/62) adds the
[Protein A/G Sepharose backpressure journey](validation/CYTIVA-TROUBLESHOOTING-DEMO.md).
It reuses the reviewed cleaning source pool (17 excerpts on PDF pages 166–167),
selecting the complete required bundle for each reviewed branch. Users choose
an exact product and a context to explore; this selection establishes no cause.
Unknown product/context yields clarification, hydrophobic treatments remain
separate alternatives and the ethanol pressure precaution stays attached.
MabSelect is explicitly outside this first journey. The local response retains
original quotations, PDF identity, page/offset/hash provenance and reservations.

The four agent browser scenarios and 17 journey/demo regressions passed. The
long context label now has a complete wrapping summary, and clarification sources
are explicitly labelled as context/headings rather than a selected recipe.
These checks do not create new human scientific approval, an independent
retrieval benchmark, a v03 prospective score or operational authorization.
Frozen v03, historical scores and E118-I/E121-EQ quarantine remain unchanged.
The existing onboarding video shows the earlier guided route, not this new UI.

### Next delivery priorities

1. **Scope and review one adjacent product-specific journey.** Collect a short
   usability response to the merged Protein A/G route, then prepare a bounded
   MabSelect cleaning journey from already reviewed sources. Before coding, agree
   exact product identities, deposit-context categories, source bundles, conditions,
   alternatives, warnings and clarification/outside-scope cases. Require no recipe
   from pressure alone, no Sepharose recipe transfer and no SuRe/SuRe LX-only
   condition applied to other products. Reuse the existing deterministic renderer
   and preserve the current journey and frozen v03; do not start another broad
   parser-tuning or whole-manual review campaign. This is a proposed next scope,
   not an implemented or scientifically approved product route.
2. **Run second-PC Windows validation in parallel when available.** Use a fresh
   clone, separately installed CPython 3.13.0 x64 and a newly prepared environment
   and tokenizer cache. Record readiness versions/hashes, citations/warnings,
   missing-format clarification, partial service and quarantine using the existing
   walkthrough. A physical second PC remains a separate portability gate; it does
   not block scoping the next bounded journey.
3. **Keep serving migration separate.** Define an explicit reviewed-record adapter
   contract before enriching the legacy Neo4j chatbot. The local documentary
   journey does not publish new graph records or provide generated advice.

4. **Instrument and evaluate the actual answering path incrementally.** Add OpenTelemetry spans,
   call/retry/cost accounting and budget enforcement. Evaluate generated answers,
   citations and abstentions with deterministic checks, calibrated local Ragas
   and Promptfoo attacks with benign controls; these integrations remain pending
   and do not block the model-free demo. Use fresh reviewed holdouts for future
   behavior changes; do not overwrite the current freeze or historical results.
5. **Compare architectures after prerequisites.** Run graph/passages/LightRAG on a
   common corpus and budget. Benchmark local answering separately; keep KAG and
   fine-tuning conditional on failures simpler approaches cannot address.

No additional representative-page review is required by default. Reopen conversion
only for a new format, measured failure or required source gap. Optional pages
53/86/142 are untested extensions, not a whole-manual review queue.

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
| [Merged free-text interface](technical/FREE-TEXT-MACHINE-DESIGN-V01.md) | CP/FI/MC and GR01–GR04 reviewed; interpreter/bridge and IF checks implemented | Bounded offline interface; no default chat activation |
| [FT01–FT12](../experiments/cytiva/free-text-comparison-v01/README.md) | Merged S 24/24, F0 12/24, 4/12 pairs | Gate blocked; now v02 development material, not discarded failures |
| [Opt-in v02](technical/FREE-TEXT-CANDIDATE-V02.md) | Merged candidate, 57 targeted tests pass | FT repair results do not establish independent generalization |
| [FV01–FV12](../experiments/cytiva/free-text-v02-comparison-v01/README.md) | Merged reviewed one-pass run: S 22/24, F0 17/24, 7/12 pairs, maximum 1,674 tokens | Gate blocked; shared FV06 aggregate mismatch is separate from parser failures; no rescoring or method repair |

The original Q/N/C series contains 28 intents with paired FR/EN formulations,
not 56 independent observations. H/V/W/X/FT/FV add same-corpus challenges with known-code
authorship; inspected failures become development inputs. Required-source presence
is not answer correctness, refusal quality or measured precision. Section-only
was a historical ablation preference. The frozen v05 X run remains blocked;
no candidate becomes the chat default through these experiments. W and X use
different questions and their aggregate scores are not a controlled v04/v05
comparison. The FT and FV scores also use different question sets and do not measure a controlled gain. None is a new-section/manual or independently authored benchmark.

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
has no general-family lexical hit. The task-scoped contract, structured control, EN/FR interpreter/bridge and opt-in v02 are merged. FT and the merged FV trial remain blocked. A passing structured trial does not establish unrestricted free-text understanding; FV06 additionally exposes a shared coverage-contract mismatch.

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
