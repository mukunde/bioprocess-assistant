# Graph chat pressure validation

## Live result

On 11 November 2026, a single live pass matched all six expected outcomes.
H08, P01, and P02 abstained despite matching graph results. G02, P03, and P04
returned both pressure paths and preserved the resin conditions and all five
citations per response. All 15 citations matched their graph node source
fields. The trace records the final abstention without distinguishing the
model's decision from the application check.

The run used Claude Sonnet 4.6, the structured JSON schema, and the pinned
Neo4j seed. All six request traces exported. Each case used two generations
with `tool_use` followed by `end_turn`. No case was truncated or rejected.

| Case | Observed result | Citations | Request (s) | Input tokens | Output tokens | Estimated USD |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| H08 | Abstention | 0 | 4.76 | 3,576 | 76 | 0.011868 |
| G02 | Sourced answer | 5 | 3.86 | 3,562 | 85 | 0.011961 |
| P01 | Abstention | 0 | 3.44 | 3,624 | 80 | 0.012072 |
| P02 | Abstention | 0 | 3.37 | 3,571 | 79 | 0.011898 |
| P03 | Sourced answer | 5 | 3.92 | 3,604 | 81 | 0.012027 |
| P04 | Sourced answer | 5 | 5.11 | 4,505 | 127 | 0.015420 |

The 12 generations used 22,442 input and 528 output tokens. Total estimated
cost was USD 0.075246. The guard reserved USD 0.502128 against the separate
USD 0.76 ceiling. Median request latency was 3.89 s, median generation
latency was 1.67 s, and median Neo4j search latency was 32 ms.

## Proposed targeted run

Run the following six cases once, in order, on the same pinned graph seed.
Use a fresh conversation for each case. H08 and G02 reuse the exact original
prompts. The four variants below were prepared after the correction. Fix their
wording and expectations before the run.

| Case | Exact prompt or source | Expected result |
| --- | --- | --- |
| H08 | [Frozen H08 prompt](../GRAPH-CHAT-HELD-OUT-REVIEW.md#questions-and-expected-results) | Abstain without citations or advice. |
| G02 | [Original G02 prompt](../GRAPH-CHAT-MEASUREMENT.md#question-set) | Answer with both pressure paths and five citations. Use French headings. |
| P01 | Le voyant de surpression s’est allumé pendant la capture Protein A. L’historique ne contient aucun relevé de pression pour cet intervalle. Peut-on décider d’un nettoyage à partir de ce voyant ? | Abstain without citations or advice. An alarm supplies no reading. |
| P02 | The capture skid flagged pressure during a run. The transmitter was disconnected and there is no independent reading. Should we repack the Protein A column? | Abstain without citations or advice. |
| P03 | Pendant la capture Protein A, un manomètre indépendant indique une pression d’entrée supérieure à celle des cycles précédents au même débit. Quelles pistes vérifier ? | Answer with both pressure paths and five citations. Use French headings. |
| P04 | The dashboard alarm was intermittent, but an independent inlet gauge showed a sustained pressure rise during Protein A capture at the same flow rate. What checks does the graph support? | Answer with both pressure paths and five citations. Use English headings. |

For the three sourced controls, expect the bed packing or flow path with an
efficiency check and the fouling path with cleaning scoped to the resin.
Require the exact source field for each of the five nodes in the
[pinned seed](../../graph/seed.cypher). These are CY13981 p. 166 for the
symptom and fouling cause, pp. 162–164 for the packing or flow cause,
pp. 166–167 and CY12754 p. 4 for the cleaning action, and CY13981 p. 164
and CY12754 p. 5 and figure 11 for the efficiency action. Preserve the
conditions and avoid presenting a cause or repacking need as established.

An unexpected answer, abstention, missing path, citation mismatch, or advice
outside the documented conditions fails its case. Record technical errors
separately. The target is six conforming outcomes. Record trace coverage,
lookup outcomes, request and stage latency, reported tokens, and estimated
cost per case. Keep the original run and the targeted run as distinct records.

## Proposed budget

Use a separate ceiling of **USD 0.76** for this six-case run. Keep the
benchmark settings of three generations per request, zero SDK retries,
1,536 output tokens per generation, a 4,500-token input preflight limit,
and a reserve of 5,000 input tokens per generation. At the baseline rates
with the 10% routing margin, the reserve is USD 0.041844 per generation,
or USD 0.753192 for all 18 possible generations.

The six cases and separate USD 0.76 ceiling were approved. The entry point
is `run_pressure_validation`. It verifies the approved prompts and graph
seed before using the client.
