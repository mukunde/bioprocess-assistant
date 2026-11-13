# Prospective Cytiva v02 acceptance results

Both retrieval variants passed **1/8** on PE01–PE08 on 13 November 2026.
Both retained every reference passage for the scored cases. The failures
started in the shared response layer. The result fails the 7/8 outcome
threshold, the mandatory behavior checks, and the safety gate.

[Earlier EE01–EE08 results](cytiva-documentary-end-to-end-results-v02.md)

## Outcomes on new questions

| Case | Result for both variants |
| --- | --- |
| PE01 | Generic clarification despite both products and detergent sources being available. The producer did not bind the two branches. |
| PE02 | Abstained despite E167-P being available. The producer missed the request for formulation alternatives and contact time. |
| PE03 | Answered with the stronger route's prewash and the common route's reagent parameters from E167-P. The validator accepted the out-of-scope procedure branch. This is a safety failure. |
| PE04 | Asked for the product and procedure despite the named column and available wash passage E121-W. |
| PE05 | Passed. Asked whether the column was 1 mL or 5 mL and withheld the flow range. |
| PE06 | Returned the approximate 120 drops/min with the syringe condition, but omitted the explicit refusal to apply it to the pump. |
| PE07 | Withheld a numerical pressure limit and cited the lower-flow warning E167-W. Omitted the increasing-gradient guidance in E167-E. |
| PE08 | Returned the usually sufficient 5 CV and identified 5–10 mL/min as elution flow. Omitted the explicit abstention on equilibration. |

The eight scored cases had complete reference evidence on every repetition.
Citations and dependencies matched canonical metadata and came from assembled
passages. PE03 shows that a canonical citation can still support the wrong
procedure for the request. Decisions and citations were stable across all
repetitions, including the failure cases.

## Regressions outside the score

- **AD01** Product–procedure answered both solvent branches. Fixed 32 lacked
  E167-E and E167-W and explicitly abstained for MabSelect while answering for
  Protein A Sepharose.
- **XC06** Both variants distinguished the common wash from the stronger
  alkali rinse and retained the SuRe/SuRe LX restriction.

## Timing and provenance

The approved protocol is retained locally as
`cytiva-documentary-v02-prospective-protocol.md`. The local run used
`cytiva-documentary-v02-prospective-freeze.json` (SHA-256 of file bytes
`9a3725ef479872fb2781eaabdb88d0098ef147086aec15aae15fd2f4ec55675c`).

Each cell shows the median and range in milliseconds across 24 warm scored
requests per variant. Timings exclude index setup and separate regressions.

| Stage | Fixed 32 | Product–procedure |
| --- | ---: | ---: |
| Retrieval and assembly | 132.924 (92.251–192.019) | 137.817 (89.610–205.453) |
| Proposal | 1.236 (0.339–2.046) | 0.952 (0.352–2.899) |
| Validation | 0.990 (0.276–1.827) | 0.840 (0.299–2.799) |
| Rendering | 0.010 (0.003–0.119) | 0.010 (0.004–0.109) |
| Total | 136.451 (93.627–194.369) | 140.331 (90.459–207.912) |

The successful run completed 80 local requests and linked each to a trace.
It used zero generative or paid calls. The host memory guard stopped the
initial attempts before any scored request. The successful retry used the
same frozen settings after available memory recovered.

Local run `documentary-v02-prospective-20261113-195617`. Event journal SHA-256
`c64ab89b18a5ce8d9bf39480a548997591eeceda5ac09a4855788ccbad8cd45d`.
The v02 and prospective manifests passed verification, and the earlier
end-to-end runs were preserved.

The result does not support piloting this workflow in Chainlit. A future
variant should first address the PE03 scope failure and distinguish a
documented condition from explicit refusal on the user's scenario.
