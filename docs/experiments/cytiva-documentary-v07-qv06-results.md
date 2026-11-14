# Cytiva v07 QV06 regression replay

On 14 November 2026, both frozen v07 variants passed the targeted QV06
replay on the same 42-passage corpus. All four repetitions per variant
passed. The v06 prospective score remains **0/8 per variant**.

[v06 prospective results](cytiva-documentary-v06-prospective-results.md) ·
[v06 regression replay](cytiva-documentary-v06-replay-results.md)

## QV06

| Request | Decision in both variants | Citations |
| --- | --- | --- |
| Blue Sepharose for a target similarly hydrophobic to albumin | Abstained on the proposed use and displayed the family-wide contraindication. | E120-W and E120-A, p. 120 |
| MabSelect solvent cleaning | Reported higher backpressure and the recommendation to reduce flow when using 70% ethanol or 30% 2-propanol. Withheld a numerical flow setting. | E167-W, p. 167 |

The assembled passages for QV06 matched v06 for each variant. The change
came from the response layer. Citations matched the canonical records and
their dependencies. E118-I and E121-EQ remained excluded.

## Regressions outside the score

| Cases | Outcome |
| --- | --- |
| VP01–VP08 | Both variants retained 8/8. |
| PE01–PE08 | Both variants retained 8/8. |
| AD01 | Product–procedure answered both branches. Fixed 32 answered Protein A Sepharose and explicitly abstained for MabSelect. |
| XC06 | Both variants kept the common wash separate from the stronger alkali rinse and retained the SuRe/SuRe LX restriction. |

All 144 requests outside the score reproduced the v06 assembled passages,
proposals, decisions, citations, and rendered answers.

## Timing and provenance

Median warm latency in milliseconds across three QV06 requests per variant.
The sample is too small to establish a latency difference.

| Stage | Fixed 32 | Product–procedure |
| --- | ---: | ---: |
| Retrieval and assembly | 78.781 | 67.823 |
| Proposal | 0.503 | 0.648 |
| Validation | 0.357 | 0.508 |
| Rendering | 0.038 | 0.048 |
| Total | 79.843 | 68.759 |

The run completed 152 requests with unique metadata-only traces and zero
paid or generative calls. All 89 protected historical files matched their
pre-run hashes.

| Record | SHA-256 of file bytes |
| --- | --- |
| v07 freeze manifest | `d2e406874a1431bbf3ce83094f941fb4e3dad8145ba3b9a66a53b4a813498c4c` |
| Event journal in local run `documentary-v07-qv06-20261114-205016` | `14736caf28a7158370e8d40f8da6fcd364964597f12f8d7e016bc8a0ab260371` |

This targeted replay measures the QV06 correction. The seven other
prospective QV cases remain unevaluated on v07.
