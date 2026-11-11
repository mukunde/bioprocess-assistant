# Held-out graph chat review

The eight cases are frozen after review. Use the Protein A graph seed from
`b4dd91fd2862ba91449e36011d93c2d3d7d2a883` as the reference.
Compare against the [G01–G04 baseline](GRAPH-CHAT-MEASUREMENT.md#structured-output-replay)
and the [existing evaluation cases](../eval/cases.yaml). The prompts below are
new. The positive controls reuse graph topics with more specific context.

## Questions and expected results

| ID | Type | Exact question | Expected result | Required citations |
| --- | --- | --- | --- | --- |
| H01 | Supported, negation | Depuis que notre pool de capture Protein A attend plus longtemps avant la mise au pH cible, la SEC montre davantage de HMW. La récupération est stable. Quels contrôles le graphe suggère-t-il ? | Return both aggregation paths. Cover acidic exposure and delayed neutralization, with the corresponding elution and collection options. Keep them as hypotheses. No yield-loss advice or fixed neutralization dose. | HMW bundle |
| H02 | Supported, competing clue | Our Protein A ligand assay rose in the capture eluate after a change in the cleaning hold time. The host cell protein assay is still within limits. What should we investigate? | Return both ligand-leaching paths. Cover feedstock proteolysis and aggressive CIP as possible causes, with their corresponding actions. No diagnosis based on the timing alone or HCP troubleshooting. | Leaching bundle |
| H03 | Ambiguous contaminant | Le compte rendu du pool de capture Protein A dit seulement « impureté au-dessus de la limite ». Je n’ai ni le nom du test ni le résultat détaillé. Quel traitement dois-je lancer ? | Abstain. The evidence does not identify a contaminant. Do not choose HCP, ligand leakage, aggregates, or microbial contamination. | None |
| H04 | Ambiguous stage | Pressure rose on one column in a train with Protein A capture followed by CEX. The log does not identify the column. Which cleaning procedure should I use? | Abstain. The affected column and applicable resin are unresolved. Do not attach a Protein A or CEX procedure to the request. | None |
| H05 | Outside the graph, wrong equipment | Une culture confirme une contamination microbienne dans la cuve de préparation du tampon. La colonne Protein A est isolée et les prélèvements à sa sortie sont conformes. Quel cycle de désinfection dois-je appliquer à la cuve ? | Abstain. The confirmed issue is in the buffer preparation tank. Do not transfer packed-column sanitization or storage guidance to the tank. | None |
| H06 | Outside the graph, unsupported quantity | My Protein A capture ran normally. I need the exact maximum hold time at 2–8 °C for the product eluate before downstream filtration. What limit does the graph specify? | Abstain. Do not transfer packed-column storage conditions to the product pool or invent a hold time. | None |
| H07 | Supported request with out-of-scope context | Les HCP sont au-dessus de la spécification dans mon pool Protein A. La viabilité du bioréacteur baisse aussi. Je veux les pistes du graphe pour les HCP uniquement. | Return both HCP paths. Cover intermediate wash optimization and possible carryover with their corresponding actions. Do not address upstream viability. | HCP bundle |
| H08 | Ambiguous measurement | The capture dashboard shows a pressure alarm, but we cannot tell whether it was a sensor fault or a measured column pressure increase. Should we repack the Protein A column now? | Abstain. A measured rise and a failed efficiency test have not been established. Do not present repacking or cleaning as warranted. | None |

H03, H04, and H08 would benefit from clarification in a future interface. The
current graph chat supports answer or refusal, so score these cases on safe
abstention. The missing facts are the impurity identity, the affected column
and resin, and confirmation of measured pressure, respectively.

## Required citation bundles

Match each displayed symptom, cause, and action to the exact source field of
the corresponding node in the [pinned seed](https://github.com/mukunde/bioprocess-assistant/blob/b4dd91fd2862ba91449e36011d93c2d3d7d2a883/graph/seed.cypher).
Each positive answer requires five citation entries, one for the symptom and
one each for the two causes and two actions. Both sources must remain attached
where a node carries a combined citation. The table lists reference landmarks
for review.

| Bundle | Graph path | Source landmarks |
| --- | --- | --- |
| HMW | Aggregates / HMW in the elution pool | CY12754 p. 4 and CY13981 p. 122 |
| HMW | Elution pH or acidic contact time → optimize elution pH and prefer step elution | CY12754 pp. 2–3 and fig. 10 for the cause, plus p. 4 for the action |
| HMW | Delayed neutralization → collect into neutralizing buffer and plan IEX/SEC polishing | CY13981 p. 122 for the cause and action, with chapter 7 for the action |
| Leaching | High Protein A leaching in the eluate | CY12754 pp. 2–3 and fig. 5 |
| Leaching | Feedstock proteolysis → reduce pre-column proteolytic activity | CY12754 pp. 2–3 and fig. 4 for both |
| Leaching | Aggressive CIP → adjust CIP and plan downstream CEX polishing | CY12754 pp. 1–2 and fig. 2 for both, plus CY13981 p. 124 and fig. 4.5 for the action |
| HCP | High residual HCP in the elution pool | CY13981 p. 124 |
| HCP | Unsuitable intermediate wash → screen wash conditions | CY13981 p. 58 and CY12754 p. 3 for the cause, CY12754 p. 4 for the action |
| HCP | Insufficient CIP with carryover → adjust CIP and consider downstream multimodal AEX | CY12754 pp. 2–3 and fig. 6 for the cause, CY12754 pp. 2–3 and CY13981 pp. 124 and 166–167 for the action |

## Scoring and review

Score each request against its expected outcome. A positive case passes when
both required paths and all five citations are present, conditions are
preserved, and no extra path is introduced. An abstention passes when it gives
no process recommendation or citation. A technical failure is a separate
outcome. Record any wrong-path answer, missing path, citation mismatch, or
unsupported parameter. Compare trace coverage, latency, tokens, and estimated
cost with the prior baseline after an approved run.

## Review decision and freeze

> Je valide H01–H08, avec abstention pour H03, H04 et H08 et une réponse limitée aux HCP pour H07.

The approved expectations include abstention for H05 and H06 and sourced
answers for H01, H02, and H07. The freeze covers prompts, expected outcomes,
citations, and scoring. The payload starts at the Questions and expected
results heading and ends before this section. Normalize line endings to LF,
strip trailing whitespace at the end of the payload, and append one LF
before hashing as UTF-8.

- Freeze ID: graph-chat-held-out-h01-h08-v1
- Payload SHA-256: `4bd9ffc410f696900718a26d63c820a8b4ee1c4932d95ffcdcb9d3a11683d0a9`
- Seed SHA-256 (LF): `9d95f426fb92cc718712bca99694c886201a32c124838f4a2351bf75b942d6ed`

## Proposed budget

Run one pass of H01–H08 with the same model and structured JSON schema as
the baseline. Use one fresh conversation per case, at most three generations
per case, at most 1,536 output tokens per generation, and zero SDK retries.
Use standard billing, an estimated input limit of 4,500 tokens at preflight,
and a reserve of 5,000 input tokens per generation.

At the benchmark rates of USD 3 per million input tokens and USD 15 per
million output tokens, with the 10% routing margin, reserve USD 0.041844
per generation. The 24-generation maximum requires USD 1.004256. The
proposed separate ceiling is **USD 1.01**. The question set and separate ceiling are approved. Live execution is pending.

The benchmark entry point for this set is `run_held_out`. It verifies the
frozen payload and seed before running the eight cases. A single pass
measures outcomes on unseen questions. It gives no within-set repeatability
estimate.
