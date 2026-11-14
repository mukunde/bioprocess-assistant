# Cytiva v08 documentary regression replay

On 14 November 2026, both frozen v08 variants passed **8/8** on
QV01–QV08 and all four mandatory behavior checks. The cases informed
the fixes. The prospective v06 result remains **0/8 per variant**.

[v06 prospective results](cytiva-documentary-v06-prospective-results.md) ·
[v07 QV06 replay](cytiva-documentary-v07-qv06-results.md)

## Scored outcomes

| Case | Observed outcome in both variants | Main citations |
| --- | --- | --- |
| QV01 | Attached pH 7.0–8.0 to the immediate rinse with at least 5 CV of sterile filtered binding buffer. Kept the lower-flow warning with solvent cleaning and withheld a rinse flow and solvent pH. | E167-E, E167-W |
| QV02 | Returned the chosen common wash at 100 mM sodium phosphate, 2 CV, and at least 10 min. Kept the 3 CV binding-buffer prewash with the stronger SuRe/SuRe LX route. | E167-P, E167-S, E167-SH |
| QV03 | Kept both elution formulations separate at pH 7.0 and assigned each chloride salt and concentration to the correct formulation. | E121-B, E120-W |
| QV04 | Kept 1–2 mL/min with the 1 mL wash and 5–10 mL/min with the 5 mL elution. | E121-W, E121-E, E120-W |
| QV05 | Asked which stage was recorded and explained why the identical 1–2 mL/min ranges for 1 mL do not establish which buffer to use. | E121-W, E121-E, E120-W |
| QV06 | Applied the Blue Sepharose contraindication and kept the independent MabSelect solvent warning, with no numerical flow setting. | E120-W, E120-A, E167-W |
| QV07 | Gave conditional direct-use guidance for A and asked about interference with B's intended assay. | E118-USE |
| QV08 | Retained conditional IEX and HIC guidance and withheld an exact IEX pH. | E119-I, E119-H |

Both variants cleared the 7/8 threshold. Review found zero documentary
safety violations in the recorded outputs. Rankings and assembled
evidence matched v06 for every request. The citations and source
dependencies matched the canonical assembled records. E118-I and
E121-EQ remained excluded. Decisions, citations, and rendered answers
were stable across repetitions. QV06 reproduced v07.

## Regressions outside the score

- **VP01–VP08 and PE01–PE08** Both sets retained 8/8 per variant.
- **AD01** Product–procedure answered both branches. Fixed 32 answered
  Protein A Sepharose and explicitly abstained for MabSelect.
- **XC06** Both variants distinguished the common wash from the stronger
  alkali rinse and preserved the SuRe/SuRe LX restriction.

All 144 requests outside the score matched v07 in assembled passages,
proposals, decisions, citations, and rendered answers.

## Timing and provenance

Median and range in milliseconds across 24 warm scored requests per
variant. Times exclude setup and the separate regressions.

| Stage | Fixed 32 | Product–procedure |
| --- | ---: | ---: |
| Retrieval and assembly | 76.078 (63.901–148.855) | 76.970 (64.269–118.990) |
| Proposal | 0.307 (0.178–0.589) | 0.300 (0.206–0.681) |
| Validation | 0.212 (0.113–0.442) | 0.197 (0.133–0.468) |
| Rendering | 0.045 (0.019–0.109) | 0.044 (0.022–0.087) |
| Total | 76.738 (64.524–150.019) | 77.788 (65.016–120.130) |

The completed run recorded 208 requests with unique metadata-only traces
and zero paid or generative calls. The first startup attempt stopped
during the Bolt handshake before the first question. It was retained.
The completed run used the same settings in a new directory after a Bolt
query confirmed readiness. All 100 protected files matched their pre-run
hashes.

| Record | SHA-256 of file bytes |
| --- | --- |
| Local v08 replay manifest | `49b4c0b0c56c31fe04c239f54f67772e2e2d0562c2fa4b2805c7a5a75671dc33` |
| Event journal in local run `documentary-v08-replay-20261114-213649` | `c64205ce1761717e85bcac22fbf34b6225c05c865b14d19bf70dae7ba7249039` |

The replay confirms recovery on the corrected cases. A fresh reviewed
question set is needed to assess transfer before considering a Chainlit
pilot.
