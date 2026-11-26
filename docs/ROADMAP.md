# Roadmap for evidence-grounded bioprocess assistance

Help bioprocess engineers inspect source-backed troubleshooting guidance.
Keep source review, documentary previews, and operational decisions separate.

## What works today

| Area | Available now |
| --- | --- |
| Graph chat | Chainlit supports Claude Sonnet 4.6 via the Anthropic API by default and local Ministral 3 3B Instruct 2512 through Ollama on opt-in. Both select Neo4j result IDs. The app validates the selection and renders graph facts with citations. [Grounding decision](ADR-001-knowledge-graph-grounding.md) · [Local mode](LOCAL-GRAPH-CHAT.md#use-ministral-on-the-host) |
| Local demo | Guided and bounded English and French requests use reviewed Cytiva excerpts. The Windows setup has same-PC evidence. [Demo guide](DEMO-FIRST.md) |
| MabSelect | The guided Chainlit mode uses an approved local registry. Citations and withdrawal checks follow the current registry authority. [Operator guide](CHAINLIT-MABSELECT.md) |
| Protein A/G Sepharose | The merged candidate provides a separate Chainlit preview with scoped sources, clarification, and simulated withdrawals. Release v03 was verified in one approved local installation. The public recording shows the preview; it does not provide access to that installation. [Candidate guide](CHAINLIT-SEPHAROSE-CANDIDATE.md) · [PR #91](https://github.com/mukunde/bioprocess-assistant/pull/91) |
| Evidence preparation | Local Docling Graph extraction and a separate reviewed model extraction have produced development evidence. [Ingestion guide](INGESTION.md) · [Reviewed extraction](../experiments/cytiva/reviewed-r2/README.md) |
| Observability | The local OpenTelemetry viewer shows request, Anthropic, and Neo4j timing, token counts, and estimated model cost. The benchmark links each result to its trace and enforces a spending reserve. The registry UI has its own local metadata traces and read-only summary. [Graph chat traces](LOCAL-GRAPH-CHAT.md#optional-local-traces) · [Benchmark protocol](GRAPH-CHAT-MEASUREMENT.md) · [Registry trace demo](REGISTRY-TRACE-DEMO.md) |

The [README thumbnail](../README.md#watch-the-demo) opens the
[1080p graph chat demo](https://mukunde.github.io/bioprocess-assistant/graph-chat/).
Browser verification confirmed that the 27-second video plays inline at
1920 × 1080 without signing in or downloading the file.
[Published player and attribution](https://github.com/mukunde/bioprocess-assistant/actions/runs/43712108704)

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

### Local Ministral result

The merged local mode passed four known cases in an authenticated Chainlit
session with disposable Neo4j. G02 gave a sourced answer with French
headings and five citation entries. G03 abstained without a search. G04
abstained after a below-threshold lookup. Neither abstention displayed
citations. M01 returned both symptom paths and ten citation entries.
[Acceptance results](LOCAL-GRAPH-CHAT.md#local-acceptance-results)

A separate M01 benchmark measured the effect of compact context with
Ministral already loaded. All six runs made the same two Neo4j searches
and produced the same JSON selection and citation-bearing output. One
pair was excluded from timing because Windows entered sleep during the
full-context run. Medians use the two remaining runs per variant.

| M01 measurement | Full context | Compact context |
| --- | ---: | ---: |
| End-to-end median | 79.97 s | 30.96 s |
| Final JSON selection median | 65.89 s | 14.87 s |
| Input tokens for final selection | 2,046 | 632 |

The 61% latency reduction applies to this question on the test machine.
The Chainlit acceptance replay checked functional behavior separately.

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

### v08 regression replay

The frozen v08 scored **8/8 per variant** on QV01–QV08 with fixed 32
and product–procedure retrieval. Both variants passed all four mandatory
checks, and review found zero documentary safety violations. Rankings
and assembled passages matched v06. QV06 reproduced the v07 correction.
The cases informed the v08 fixes. The v06 prospective score remains
**0/8 per variant**.
[v08 replay results and provenance](experiments/cytiva-documentary-v08-replay-results.md)

Outside the score, VP01–VP08 and PE01–PE08 each retained 8/8 per variant.
On AD01, product–procedure answered both branches, while fixed 32
answered Protein A Sepharose and abstained for MabSelect. On XC06,
both variants kept the common wash separate from the stronger alkali
rinse and retained the SuRe/SuRe LX restriction. All 144 requests
outside the score reproduced the v07 outputs.

### Prospective v08 and targeted v09 results

The frozen v08 scored **0/8 per variant** on PV01–PV08. Both variants
assembled every required passage, but all four mandatory behavior
checks failed. PV01 presented a rinse without enforcing the deposit
condition. PV05 returned a syringe drop-rate correspondence without
clarifying the stage or application method. Both failed the documentary
safety criterion.
[v08 prospective results](experiments/cytiva-documentary-v08-prospective-results.md)

The frozen v09 scored **2/2 per variant** in the targeted PV01 and PV05
replay. It kept the deposit-specific procedure conditional, clarified
the stage and application method, and withheld a drop rate for the
logged run. No safety violation was observed in these scored outputs.
The six other PV cases were outside this replay.
[v09 safety replay and provenance](experiments/cytiva-documentary-v09-safety-replay-results.md)

In both runs, QV01–QV08, VP01–VP08, and PE01–PE08 each retained 8/8 per
variant outside the score. On AD01, product–procedure answered both
branches. Fixed 32 answered Protein A Sepharose and abstained for
MabSelect. On XC06, both variants kept the common wash separate from the
stronger alkali rinse and retained the SuRe/SuRe LX restriction. All 208
out-of-score requests in v09 reproduced their v08 prospective outputs.

### v10 regression replay

The frozen v10 scored **8/8 per variant** on PV01–PV08 with fixed 32 and
product–procedure retrieval. Both variants passed all four mandatory
checks. Review found zero documentary safety violations in the recorded
outputs. Rankings and assembled passages matched v08, and PV01 and PV05
reproduced the v09 safety results. These cases informed the fixes. The
v08 prospective score remains **0/8 per variant**.
[v10 replay results and provenance](experiments/cytiva-documentary-v10-replay-results.md)

Outside the score, QV01–QV08, VP01–VP08, and PE01–PE08 each retained
8/8 per variant. AD01 and XC06 kept the outcomes described above.
All 208 out-of-score requests reproduced the v08 prospective regressions.

### Prospective v10 and v11 regression replay

The frozen v10 scored **0/8 per variant** on TV01–TV08. Both variants
assembled all required passages, and the first failures were in
proposal. The frozen v11 scored **8/8 per variant** when replaying the
same questions and passed all four mandatory checks. No documentary
safety violation was observed in the replay. Transfer to new questions
remains unmeasured for v11.
The detailed v10 and v11 records are pending publication.

Outside the score, PV01–PV08, QV01–QV08, VP01–VP08, and PE01–PE08
retained 8/8 per set and variant. AD01 and XC06 reproduced their prior
outcomes. All 272 historical requests matched the v10 outputs.

## Guided pilot milestone

The public showcase and local guided Chainlit pilot closed on 16 November
2026. One participant completed **GC01–GC04 without help on the successful
attempts**. GC01 and GC02 required retries. The tested interface exposes
one current submit button and opens cited excerpts directly in the chat.

After the UI and documentation merges, a fresh Windows clone of `main`
at `7fc251f` matched all seven interface hashes. The documented launcher
started MabSelect and both Sepharose previews with disposable data. All
three responded and their data snapshots passed validation.
[Operator results](FINALIZATION-PLAN.md#independent-operator-results) ·
[Closure verification](FINALIZATION-PLAN.md#closure-verification) ·
[Windows setup](CHAINLIT-GUIDED-PILOT.md)

## Windows CPU graph chat milestone

The Windows CPU graph chat milestone closed on 24 November 2026.
[PR #147](https://github.com/mukunde/bioprocess-assistant/pull/147) added the
PowerShell launcher with Ministral on CPU by default and Iris Xe on request.

On the reference Windows PC, the launcher confirmed CPU-only inference and
Chainlit responded on loopback from merged `main` at `6e343fb`. Available RAM
was 1,338 MiB after model load and 2,130 MiB with the full stack ready, above
the 1,024 MiB startup threshold. An earlier run paused at the memory gate.
The launcher validation also covered exact citations on M01, abstention on
ML06, model import into an empty Ollama store, and restart on the same ports
after Ctrl+C. The Iris Xe check confirmed GPU offload and stopped at the
memory gate before opening Chainlit.
[Setup and validation](LOCAL-GRAPH-CHAT.md#windows-launcher-verification)

### Published graph chat recordings

[PR #152](https://github.com/mukunde/bioprocess-assistant/pull/152) added the
[Ministral CPU recording](https://mukunde.github.io/bioprocess-assistant/ministral/)
below the main [Claude Sonnet 4.6 showcase](https://mukunde.github.io/bioprocess-assistant/graph-chat/).
Both thumbnails in the public README opened their GitHub Pages players.
Chrome verified 1080p playback and seeking on both recordings.
[Pages deployment](https://github.com/mukunde/bioprocess-assistant/actions/runs/45852692904)

## Next priority

Check the gaps in the existing graph chat tests and cover them with a short
offline replay. Use fixed Neo4j results and simulated model responses to
exercise the chat path in French and English. Cover a sourced answer, a
two-symptom answer with distinct citations, an unsupported pressure limit,
and invalid JSON or an unknown result ID. Provide one rerunnable command.
This checks application behavior without loading a model or starting Docker.
[Existing tests](../tests/test_graph_chat_ministral.py)

## Pending validation

[PR #149](https://github.com/mukunde/bioprocess-assistant/pull/149) added the
[pinned CPU protocol](validation/WINDOWS-GRAPH-CHAT-SECOND-PC.md) and its
[blank results sheet](validation/windows-graph-chat-second-pc-results.md).
The run is pending until a second physical Windows PC is available. Run the
eight checks and record CPU residency, memory at startup, citation and
abstention behavior, and restart on the same ports.

The frozen LX01–LX12 comparison of Ministral, Qwen, and Gemma remains pending
until the full stack can meet the protocol's memory requirement. It has its own
acceptance criteria.

## Follow-up work

If broader documentary free text becomes a release requirement, compare
the same new requests in two forms using the same evidence. Run the original text through interpretation and compare
it with manually structured tasks. Use the difference to decide
whether to improve interpretation or the response layer. Before a
free-text pilot, retain the prospective threshold of 7/8 per variant,
all mandatory behavior checks, and zero documentary safety violations.

| Work | When it is ready to advance |
| --- | --- |
| Model-free Cytiva demo portability | Run its separate Windows protocol when a second physical PC is available. [Cytiva demo protocol](validation/WINDOWS-SECOND-PC.md) |
| Held-out answer evaluation | Define a held-out set for new evidence or behavior. Cover missing context, conflicting sources, negation, and unsupported quantities. Record false acceptances, abstentions, latency, and cost. [Evaluation guide](../eval/README.md) |
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
