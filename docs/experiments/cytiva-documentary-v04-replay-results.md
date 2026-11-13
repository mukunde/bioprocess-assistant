# Cytiva v04 documentary regression replay

On 13 November 2026, v04 passed **8/8** on PE01–PE08 with both retrieval
variants. The frozen prospective v02 run scored **1/8** per variant on
these questions. The questions informed the v04 corrections, so the v04
result measures regression recovery on the same 42 passages.

[Prospective v02 results](cytiva-documentary-v02-prospective-results.md) ·
[Targeted v03 PE03 replay](cytiva-documentary-v03-pe03-results.md)

## Scored cases

| Case | Observed behavior in both variants |
| --- | --- |
| PE01 | Returned both immediate rinses with at least 5 CV each. Kept filtration and pH 7.0–8.0 with MabSelect. E166-D and E167-D. |
| PE02 | Preserved the sulfate and chloride formulations as alternatives and the common-route contact time of at least 10 min. E167-P. |
| PE03 | Kept the stronger-route reagent values and contact time separate from the prewash. Preserved the SuRe/SuRe LX restriction. E167-S and E167-SH. |
| PE04 | Preserved both wash endpoints as alternatives, explained that volume alone is insufficient, and retained the Blue Sepharose warning. E121-W and E120-W. |
| PE05 | Asked which column size was correct and withheld the flow range. |
| PE06 | Explicitly withheld a pump conversion and kept the approximate drop rate under the documented syringe conditions. E121-L, E121-F, and E120-W. |
| PE07 | Withheld a numerical pressure maximum and preserved the lower-flow and increasing-gradient guidance. E167-W and E167-E. |
| PE08 | Returned the usually sufficient 5 CV for one-step elution and withheld the equilibration flow. E121-E and E120-W. |

Both variants exceeded the 7/8 threshold and passed the mandatory PE05–PE08
checks. All required passages were present for the scored requests.
Citations and dependencies matched the canonical records and the assembled
context. Review found zero unsupported actionable claims, scope transfers,
or missing mandatory warnings in the recorded outputs. E118-I and E121-EQ
remained excluded. Decisions and citations were stable across repetitions.

## Regressions outside the score

- **AD01** Product–procedure answered both branches with their own
  precautions. Fixed 32 answered Protein A Sepharose and abstained on
  MabSelect because E167-E and E167-W were absent from the final context.
- **XC06** Both variants kept the common wash and stronger alkali rinse
  separate and preserved the SuRe/SuRe LX restriction.

## Timing and provenance

Each cell shows the median and range in milliseconds across 24 warm scored
requests per variant. Timings exclude index setup and the regressions.

| Stage | Fixed 32 | Product–procedure |
| --- | ---: | ---: |
| Retrieval and assembly | 105.027 (88.666–159.873) | 110.988 (84.451–137.302) |
| Proposal | 1.007 (0.266–2.302) | 1.067 (0.240–2.368) |
| Validation | 0.938 (0.244–2.120) | 0.885 (0.175–2.314) |
| Rendering | 0.039 (0.006–0.118) | 0.034 (0.007–0.083) |
| Total | 107.406 (91.289–164.562) | 113.278 (86.213–142.195) |

The run completed 80 local requests with 80 unique metadata-only traces
and zero paid or generative calls. The v04 manifest and its parent chain
passed verification.

Local run `documentary-v04-replay-20261113-214606`. Event journal SHA-256
`40f16997bd9ded43b77906b7cac5280b680d711fe16aab1e36bb4e4b1b292b82`.
The v04 manifest is `cytiva-documentary-v04-replay-freeze.json`, with
file SHA-256 `48b92eb9ecd7a5cdfeb434d541ef89c92dc30eb78aad1fc7d0a0a5d5dc30ff74`.
