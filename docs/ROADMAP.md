# Roadmap for evidence-grounded bioprocess assistance

Help bioprocess engineers inspect source-backed troubleshooting guidance.
Keep source review, documentary previews, and operational decisions separate.

## What works today

| Area | Available now |
| --- | --- |
| Graph chat | Anthropic selects curated Neo4j results. The app validates the model's structured JSON selection and renders graph facts with citations. [Grounding decision](ADR-001-knowledge-graph-grounding.md) |
| Local demo | Guided and bounded English and French requests use reviewed Cytiva excerpts. The Windows setup has same-PC evidence. [Demo guide](DEMO-FIRST.md) |
| MabSelect | The guided Chainlit mode uses an approved local registry. Citations and withdrawal checks follow the current registry authority. [Operator guide](CHAINLIT-MABSELECT.md) |
| Protein A/G Sepharose | The merged candidate provides a separate Chainlit preview with scoped sources, clarification, and simulated withdrawals. Release v03 was verified in one approved local installation. The public recording shows the preview; it does not provide access to that installation. [Candidate guide](CHAINLIT-SEPHAROSE-CANDIDATE.md) · [PR #91](https://github.com/mukunde/bioprocess-assistant/pull/91) |
| Evidence preparation | Local Docling Graph extraction and a separate reviewed model extraction have produced development evidence. [Ingestion guide](INGESTION.md) · [Reviewed extraction](../experiments/cytiva/reviewed-r2/README.md) |
| Observability | The local OpenTelemetry viewer shows request, Anthropic, and Neo4j timing, token counts, and estimated model cost. The benchmark links each result to its trace and enforces a spending reserve. The registry UI has its own local metadata traces and read-only summary. [Graph chat traces](LOCAL-GRAPH-CHAT.md#optional-local-traces) · [Benchmark protocol](GRAPH-CHAT-MEASUREMENT.md) · [Registry trace demo](REGISTRY-TRACE-DEMO.md) |

The [README thumbnail](../README.md#watch-the-demo) opens the
[1080p graph chat demo](https://mukunde.github.io/bioprocess-assistant/graph-chat/).
Browser verification confirmed that the 27-second video plays inline at
1920 × 1080 without signing in or downloading the file.
[Pages deployment](https://github.com/mukunde/bioprocess-assistant/actions/runs/42224594186)

The [Chainlit Sepharose recording](https://mukunde.github.io/bioprocess-assistant/sepharose/)
remains available separately.

Find dated test results and design decisions in the [documentation index](README.md)
and the [history of this roadmap through 5 November 2026](https://github.com/mukunde/bioprocess-assistant/blob/6be6ce24ce7e0da547a93de9042826dc3cbe818a/docs/ROADMAP.md).

## Latest graph chat result

Two structured-output passes of G01–G04 matched all eight expected outcomes.
G01 and G02 returned sourced answers, and G03 and G04 abstained. All 20
displayed citation entries matched the seed. G05 passed offline with an
injected Neo4j outage. The live replay had a median request latency of 3.97 s
and an estimated total model cost of USD 0.089622.
[Replay results](GRAPH-CHAT-MEASUREMENT.md#structured-output-replay)

The targeted pressure validation matched all six expected outcomes. H08 and
two new alarm cases abstained, and the three reported or measured increases
returned both pressure paths with their citations. Median request latency was
3.89 s, and estimated total model cost was USD 0.075246.
[Pressure validation](validation/GRAPH-CHAT-PRESSURE-VALIDATION.md#live-result)

## Cytiva retrieval results

The frozen XC01–XC12 comparison used the same 42 reviewed passages for
expanded Neo4j, vector passage search, and LightRAG. All 432 local requests
completed. Full coverage means the final context contains every required
passage for a question.

| Method | Full coverage at 16 and 32 | Median total latency at 16 and 32 | Median evidence tokens at 16 and 32 |
| --- | ---: | ---: | ---: |
| Expanded Neo4j | 11/12 → 12/12 | 26.75 → 71.28 ms | 1,295 → 2,720.5 |
| Vector passage search | 10/12 → 12/12 | 28.32 → 75.89 ms | 1,242 → 2,597.5 |
| LightRAG | 9/12 → 11/12 | 77.81 → 137.17 ms | 1,183.5 → 2,579 |

At 32 passages, LightRAG still lost one required passage for XC06 during
assembly. The experiment measured evidence retrieval. The historical
comparison with the narrower Neo4j projection remains non-conclusive.
[XC results and provenance](experiments/cytiva-expanded-heldout-results-v01.md)
· [Reviewed questions and evidence](experiments/cytiva-expanded-heldout-questions-v01.md)

## Neo4j adaptive-depth result

On AD01–AD10, fixed 16 covered 8/10 questions. Fixed 32 and adaptive 16→32
each covered 9/10. The adaptive rule expanded on 10/10 questions against
a limit of five. Its median total latency rose from 87.37 to 118.58 ms
relative to fixed 32. Both returned a median of 2,705.5 evidence tokens.
The separate XC06 regression recovered both missing passages after
expansion. [Adaptive-depth results](experiments/cytiva-neo4j-adaptive-depth-results-v01.md)

## Product and procedure retrieval result

Fixed 32 and product–procedure retrieval both covered 8/8 SP questions
on the same 42 passages. Median warm total latency was 125.07 ms for
fixed 32 and 129.83 ms for the candidate, within the 1.25 ratio limit.
Both returned 2,661.5 median evidence tokens.

In separate regressions, the candidate recovered the MabSelect solvent
passage and warning missing from fixed 32 on AD01. Both variants covered
XC06, and the candidate preserved the distinction between the common wash
and the restricted SuRe/SuRe LX option.
[Results and regressions](experiments/cytiva-neo4j-product-procedure-results-v01.md)

## Offline answer-layer result

The replay passed all 50 checks. Both variants passed AR01–AR06 with
full evidence and with paired retrieval snapshots. Each produced three
answers, one clarification, and two abstentions on the paired snapshots.
Both also passed all seven fault groups, covering 11 subcases each.

On AD01, fixed 32 answered for Protein A Sepharose and abstained for
MabSelect. Product–procedure retrieval supported both branches. On XC06,
both variants preserved the SuRe/SuRe LX restriction. The replay measured
validation and rendering of reviewed proposals.
[Offline replay results](experiments/cytiva-answer-layer-offline-results-v01.md)

## End-to-end documentary response result

The corrected v02 passed 8/8 reviewed EE cases with both retrieval variants,
up from 5/8 each in the initial run. Both used the same 42 reviewed passages.
Warm median latency was 157.84 ms for fixed 32 and 161.00 ms for
product–procedure retrieval. The run used zero paid calls.

In separate regressions, product–procedure retrieval answered both AD01
branches. Fixed 32 answered Protein A Sepharose and abstained on MabSelect
because its context lacked E167-E and E167-W. Both variants kept the common
wash and stronger alkali rinse distinct in XC06, with the SuRe/SuRe LX
restriction. The EE cases informed the v02 corrections and measure regression
recovery on this corpus.
[End-to-end results and provenance](experiments/cytiva-documentary-end-to-end-results-v02.md)

## Documentary response evaluations

The frozen v02 scored 1/8 per variant on PE01–PE08, below the 7/8
threshold. Both variants assembled every required passage. On PE03,
the shared response layer accepted common-wash parameters for the
stronger MabSelect alkali route.
[Prospective v02 results](experiments/cytiva-documentary-v02-prospective-results.md)

The v03 correction passed PE03 on all four repetitions per variant.
The frozen v04 then passed 8/8 per variant on the full PE01–PE08
regression replay, including all mandatory PE05–PE08 checks. The review
found no unsupported actionable claims, scope transfers, or missing
mandatory warnings in the recorded outputs. The PE questions informed
the v04 corrections, so the 8/8 measures regression recovery on the same
42 passages.
[Targeted v03 replay](experiments/cytiva-documentary-v03-pe03-results.md) ·
[v04 replay and provenance](experiments/cytiva-documentary-v04-replay-results.md)

AD01 and XC06 met their separate criteria and stayed outside the scores.
On AD01, product–procedure retrieval answered both branches. Fixed 32
answered Protein A Sepharose and abstained on MabSelect because it
lacked E167-E and E167-W. On XC06, both variants kept the common and
stronger rinses separate and retained the SuRe/SuRe LX restriction.

### Prospective v04 and targeted v05 results

The frozen v04 scored 1/8 per variant on the new VP01–VP08 questions,
below the 7/8 threshold. Both variants assembled every required passage.
The response layer missed three mandatory behavior checks, including
the Blue Sepharose contraindication on VP06. The omitted warning failed
the documentary safety criterion.
[v04 prospective results](experiments/cytiva-documentary-v04-prospective-results.md)

The targeted v05 replay restored the E120-W contraindication on all four
VP06 repetitions for each variant. Both variants rejected the proposed
media switch under the stated hydrophobicity condition. The prospective
v04 score remains 1/8 per variant.
[v05 VP06 results](experiments/cytiva-documentary-v05-vp06-results.md)

PE01–PE08 retained 8/8 as regressions. AD01 and XC06 also met their
regression criteria. All 80 regression requests in the v05 replay
reproduced their v04 passages, decisions, citations, and responses.
These ten cases stayed outside the prospective and targeted scores.

### v06 regression replay

The frozen v06 scored 8/8 per variant on the VP01–VP08 replay and passed
all mandatory VP05–VP08 checks. Review found no documentary safety
violations in the recorded outputs. The questions informed the v06
corrections. The prospective v04 result remains 1/8 per variant.
[v06 replay results and provenance](experiments/cytiva-documentary-v06-replay-results.md)

All 80 requests on PE01–PE08, AD01, and XC06 matched the v05 replay.
PE01–PE08 retained 8/8. On AD01, product–procedure retrieval answered
both branches. Fixed 32 answered Protein A Sepharose and abstained on
MabSelect. On XC06, both variants kept the common and stronger rinses
separate and retained the SuRe/SuRe LX restriction. These ten cases
were outside the VP01–VP08 score.

### Prospective v06 and targeted v07 results

The frozen v06 scored **0/8 per variant** on QV01–QV08. Both variants
assembled every required passage. They missed the 7/8 threshold and all
four mandatory behavior checks. On QV06, the response cited the Blue
Sepharose contraindication while still giving operating guidance for the
affected request.
[v06 prospective results](experiments/cytiva-documentary-v06-prospective-results.md)

The frozen v07 passed QV06 in all four repetitions per variant. Both
variants abstained on the contraindicated Blue Sepharose use and answered
the independent MabSelect request. The same passages were available in
v06 and v07. The other seven QV cases remain unevaluated on v07.
[v07 QV06 replay](experiments/cytiva-documentary-v07-qv06-results.md)

In both runs, VP01–VP08 and PE01–PE08 each retained 8/8 per variant
outside the score. On AD01, product–procedure retrieval answered both
branches. Fixed 32 answered Protein A Sepharose and abstained for
MabSelect. On XC06, both variants kept the common wash and stronger
alkali rinse separate and retained the SuRe/SuRe LX restriction.

## Next priority

Fix the seven remaining QV failures in a separate response-layer candidate.
Bind each request to its product, procedure, and column size. Preserve
unresolved procedure alternatives and handle general documentary questions
with their conditions intact. Keep the QV06 contraindication and independent
MabSelect response as regression checks.

Replay QV01–QV08 with VP01–VP08, PE01–PE08, AD01, and XC06 outside the
score. Before considering a bounded Chainlit pilot, evaluate the corrected
candidate on a fresh, independently reviewed question set. Require at
least 7/8 per variant, all mandatory behavior checks, and zero documentary
safety violations.

## Follow-up work

| Work | When it is ready to advance |
| --- | --- |
| Windows portability | Run the pinned protocol on a second physical PC and record the mandatory checks and any retries. [Second-PC protocol](validation/WINDOWS-SECOND-PC.md) |
| Independent acceptance | Define a held-out set for new evidence or behavior. Cover missing context, conflicting sources, negation, and unsupported quantities. Record false acceptances, abstentions, latency, and cost. [Evaluation guide](../eval/README.md) |
| Wider model observability | After the chat baseline, apply the same metadata and budget rules to extraction and judge calls. [Tracing guide](REGISTRY-TRACING.md) |
| Generated-answer evaluation | Calibrate Ragas judges and run Promptfoo attacks with benign controls once the corresponding answering path is in scope. |
| Evidence publication | Measure extraction precision and recall on annotated claims. Check source identity, quotations, quantities, and applicability. Exercise review, idempotent import, and rollback before publishing claims to Neo4j. [Claim contract](CLAIM-CONTRACT-V02.md) · [Ingestion guide](INGESTION.md) |
| Retrieval integration | Use the end-to-end acceptance results to choose a serving approach and verify it in the intended interface. [Three-arm protocol](experiments/retrieval-comparison-protocol.md) |

Consider OpenSPG KAG only if measured reasoning failures justify a separate
comparison. Consider fine-tuning only after an evaluation identifies a gap it
could address. Reopen document conversion when a new format, a required source,
or a measured failure calls for it.

## Scope of validation

The current evidence supports bounded documentary and software checks.
Operational use requires separate scientific validation and approval.
