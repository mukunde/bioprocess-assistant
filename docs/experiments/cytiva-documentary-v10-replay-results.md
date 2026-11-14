# Cytiva v10 documentary regression replay

On 15 November 2026, both frozen v10 variants scored **8/8** on
PV01–PV08 and passed all four mandatory behavior checks. These cases
informed the v09 and v10 fixes. The v08 prospective result remains
**0/8 per variant**.

[v08 prospective results](cytiva-documentary-v08-prospective-results.md) ·
[v09 targeted safety replay](cytiva-documentary-v09-safety-replay-results.md)

## Scored outcomes

| Case | Outcome in both variants | Primary citations |
| --- | --- | --- |
| PV01 | Recognized the observed cleaning trigger. Kept the 2 CV of 6 M guanidine and immediate rinse of at least 5 CV conditional on identifying precipitated protein. Withheld a contact time. | E166-T, E166-P (p. 166) |
| PV02 | Gave the SuRe LX detergent wash and immediate rinse. Asked for the second column's variant and withheld stronger alkali settings. | E167-D, E167-SH (p. 167) |
| PV03 | Gave 3–4 CV of 70% ethanol, the conditional increasing-gradient guidance, the lower-flow warning, and the immediate rinse. Withheld the disputed 12 h hold and numerical settings for flow and gradient. | E167-E, E167-W (p. 167) |
| PV04 | Applied the Blue Sepharose contraindication to M and asked about N's target hydrophobicity. Kept both decisions separate from the general albumin-use guidance. | E120-U, E120-W (p. 120) |
| PV05 | Asked about stage and application method separately. Kept the loading and washing ranges conditional and withheld a drop rate for the specific run. | E121-L, E121-F, E121-W (p. 121), E120-W (p. 120) |
| PV06 | Recognized the confirmed effluent endpoint. Kept the binding-buffer wash separate from the usually sufficient 10–20 CV of elution buffer for linear-gradient elution. | E121-W, E121-E (p. 121), E120-W (p. 120) |
| PV07 | Withheld direct use for the assay with confirmed interference and gave conditional direct-use guidance for the other assay. | E118-USE (p. 118) |
| PV08 | Preserved screening across media of different hydrophobicities. Kept Phenyl HP scoped to the example and explained the HIC strategy in which the antibody can bind and the contaminants wash through. | E119-S, E119-X, E119-H (p. 119) |

Both variants cleared the 7/8 threshold. Review found zero documentary
safety violations in the recorded outputs. Rankings and assembled
evidence matched v08 on every request. All required passages were
present. Citations and listed dependencies matched canonical assembled
records. E118-I and E121-EQ remained excluded. Both variants gave the
same scored answers, and the outputs were stable across repetitions.
PV01 and PV05 reproduced the v09 targeted replay.

## Regressions outside the score

- **QV01–QV08, VP01–VP08, and PE01–PE08** Each set retained 8/8 per
  variant. QV06 kept the contraindication and the independent MabSelect
  response.
- **AD01** Product–procedure answered both branches. Fixed 32 answered
  Protein A Sepharose and explicitly abstained for MabSelect.
- **XC06** Both variants kept the common wash and stronger alkali rinse
  separate and retained the SuRe/SuRe LX restriction.

All 208 requests outside the score matched the v08 prospective
regressions in rankings, assembled passages, proposals, decisions,
citations, and rendered answers.

## Timing and provenance

Median and range in milliseconds across 24 warm scored requests per
variant. Times exclude setup and the separate regressions.

| Stage | Fixed 32 | Product–procedure |
| --- | ---: | ---: |
| Retrieval and assembly | 76.312 (63.437–124.356) | 78.965 (61.337–101.920) |
| Proposal | 0.321 (0.194–0.538) | 0.351 (0.227–0.494) |
| Validation | 0.207 (0.119–0.584) | 0.234 (0.160–0.400) |
| Rendering | 0.064 (0.042–0.149) | 0.070 (0.048–0.179) |
| Total | 77.116 (64.054–124.973) | 79.900 (62.376–102.622) |

The run completed 272 local requests with unique metadata-only trace
IDs and zero paid or generative calls. All 270 protected files matched
their pre-run hashes. The 81 documentary unit tests passed.

| Record | SHA-256 of file bytes |
| --- | --- |
| Local v10 replay manifest | `b1adab81413f7d3644bce3db3747dc05cc5a2c8bf1440dc161d0e4b45339f9b5` |
| Event journal in local run `documentary-v10-replay-20261115-002032` | `6c9f42c968f13cba909a184b2f39d56bf2730f52d80d5f8fb45aba6b6156f9f4` |

A prospective evaluation on independently reviewed new questions is
still required before considering a bounded Chainlit pilot.
