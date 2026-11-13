# Cytiva end-to-end documentary response results

On 13 November 2026, the corrected v02 response layer passed all eight
reviewed cases with both retrieval variants. The initial v01 run passed
five cases per variant. Both runs used the same 42-passage corpus.
Local protocol and expected outcomes: `cytiva-documentary-end-to-end-protocol-v01.md`.

## EE01–EE08

| Measure | Fixed 32 | Product–procedure |
| --- | ---: | ---: |
| Complete outcomes, initial v01 | 5/8 | 5/8 |
| Complete outcomes, corrected v02 | 8/8 | 8/8 |
| Reference passages retained in the final context, v02 | 8/8 cases | 8/8 cases |
| Warm end-to-end latency, median (min–max) | 157.84 ms (114.16–241.20) | 161.00 ms (111.83–271.92) |
| Warm retrieval median | 155.53 ms | 157.72 ms |
| Warm proposal median | 1.20 ms | 1.19 ms |
| Warm validation median | 1.05 ms | 1.22 ms |
| Warm rendering median | 0.04 ms | 0.04 ms |

The v02 run met the 7/8 threshold for each variant and preserved all
complete fixed-32 outcomes. Each latency column uses 24 warm requests
and excludes index setup and the two regressions. The protocol sets no
latency threshold.

| Corrected case | Observed behavior in both variants |
| --- | --- |
| EE02 | Separated 2 CV of nonionic detergent from the 3–4 CV solvent alternatives. Kept the gradient and lower-flow guidance with the solvent route. `E167-D`, `E167-E`, `E167-W` (p. 167). |
| EE04 | Returned the 12 h hold in 70% ethanol and the subsequent rinse with at least 5 CV of binding buffer. Preserved the lower-flow warning and withheld a numerical flow rate. `E166-E`, `E166-W` (p. 166). |
| EE05 | Returned 1 mL/min for loading and 2 mL/min for washing as the upper bounds for the 1 mL column. Kept the approximate 30 drops/min note with syringe loading and preserved the Blue Sepharose warning. `E120-W`, `E121-L`, `E121-F`, `E121-W` (pp. 120–121). |

EE03 asked for the MabSelect variant, EE08 asked for column size, and
EE06 explicitly applied the Blue Sepharose contraindication. Across all
80 requests, the citation and dependency checks passed. Decisions,
rendered outputs, and citations were stable across repetitions. Review
found zero unsupported actionable claims, scope transfers, or missing
mandatory warnings in this run.

## Separate regressions

| Case | Fixed 32 | Product–procedure |
| --- | --- | --- |
| AD01 | Answered Protein A Sepharose and explicitly abstained on the MabSelect solvent branch. The final context lacked `E167-E` and `E167-W`. | Retained both passages and answered both product branches with their own solvent options and warnings. |
| XC06 | Kept the common wash (`E167-P`) and stronger alkali rinse (`E167-S`) separate. Preserved the SuRe/SuRe LX restriction (`E167-SH`) and withheld eligibility for an unspecified column. | Preserved both branches and the same restriction. |

AD01 and XC06 are outside the 8/8 score.
[Reviewed AD01](cytiva-neo4j-adaptive-depth-protocol-v01.md#ad01) ·
[Reviewed XC06](cytiva-expanded-heldout-questions-v01.md#xc06)

## Provenance and limits

The successful run used one scored request and three warm repetitions
per case and variant, with alternating variant order. It completed
80 local requests and linked each to a metadata-only OpenTelemetry
trace. It made zero generative or paid calls.

The local journals are under
`data/experiments/retrieval/cytiva-feasibility-v01/`. The manifests,
launchers, raw journals, and traces used here are local artifacts.
The journal digests below identify the preserved runs.

| Record | Local run or artifact | SHA-256 of file bytes |
| --- | --- | --- |
| Corrected v02 journal | `documentary-e2e-v02-20261113-163416/events.jsonl` | `39f35198ada8beaed24f72fa156259a5f281d8613ca96d7f6d57d62a224b1316` |
| Initial v01 journal | `documentary-e2e-v01-20261113-011532/events.jsonl` | `e5474b3773c6b02ffe9bcd39210bd3368c57ee1d7e8d6eca6fcd780f4356e080` |
| v02 manifest copied into the run | `cytiva-documentary-end-to-end-freeze-v02.json` | `1afe02792113de5148ed8aff82ef830358387dda3092ac9e96a79b95a7632f44` |

The eight questions had already guided the three corrections. The v02
score measures regression recovery on this corpus. Prospective
generalization and Chainlit integration remain outside this evaluation.
