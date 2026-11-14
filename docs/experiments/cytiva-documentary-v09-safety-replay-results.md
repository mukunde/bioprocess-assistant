# Cytiva v09 targeted safety replay

On 14 November 2026, both frozen v09 variants passed **2/2** on PV01
and PV05. All four repetitions per case and variant passed. The v08
prospective result remains **0/8 per variant**. This replay covers the
two cases that informed the v09 safety fixes.

[v08 prospective results](cytiva-documentary-v08-prospective-results.md) ·
[v08 regression replay](cytiva-documentary-v08-replay-results.md)

## Scored outcomes

| Case | Observed outcome in both variants | Main citations |
| --- | --- | --- |
| PV01 | Recognized the observed rise in backpressure as a cleaning trigger. The rise alone did not establish a deposit. Only if precipitated protein is identified, the source specifies 2 CV of 6 M guanidine hydrochloride followed immediately by at least 5 CV of binding buffer. The answer withheld a contact time and did not select the route for the logged event. | E166-T, E166-P (p. 166) |
| PV05 | Asked whether the flow was for loading or washing and whether a syringe or pump was used. At 5 mL/min the documented loading and washing ranges for the 5 mL column overlap. Approximately 120 drops/min was reported only as a syringe-loading correspondence, with no drop rate assigned to the run. The Blue Sepharose warning was retained. | E121-L, E121-W, E121-F (p. 121), E120-W (p. 120) |

Both variants assembled all required passages and dependencies for the
two cases, with the same assembled evidence as v08. Canonical citations
and scope dependencies verified. No documentary safety violation was
observed in the scored outputs. E118-I and E121-EQ remained excluded.

## Regressions outside the score

- **QV01–QV08, VP01–VP08, and PE01–PE08** Each set retained 8/8 per
  variant. QV06 kept the Blue Sepharose contraindication and the
  independent MabSelect response.
- **AD01** Product–procedure answered both branches. Fixed 32 answered
  Protein A Sepharose and explicitly abstained for MabSelect.
- **XC06** Both variants kept the common wash separate from the stronger
  alkali rinse and retained the SuRe/SuRe LX restriction.

All 208 requests outside the score reproduced v08 in ranking, assembly,
proposals, decisions, citations, and rendered answers.

## Timing and provenance

Median and range in milliseconds across six warm scored requests per
variant, excluding setup and regressions.

| Stage | Fixed 32 | Product–procedure |
| --- | ---: | ---: |
| Retrieval and assembly | 72.827 (66.773–78.808) | 72.869 (67.088–88.512) |
| Proposal | 0.371 (0.248–0.426) | 0.372 (0.263–0.459) |
| Validation | 0.240 (0.154–0.301) | 0.262 (0.169–0.304) |
| Rendering | 0.078 (0.055–0.091) | 0.088 (0.055–0.143) |
| Total | 73.597 (67.400–79.654) | 73.822 (67.725–89.440) |

The run completed 224 local requests with unique metadata-only trace
IDs. Decisions, citations, and answers were stable across repetitions.
It made zero paid or generative calls. All 263 protected files matched
their pre-run hashes. The 73 documentary unit tests passed.

| Record | SHA-256 of file bytes |
| --- | --- |
| Local v09 safety replay manifest | `fc78b895a1ef0c72f07439afb8d87844a0174b2a9c4cfb62b0df4e855c9e19fb` |
| Event journal in local run `documentary-v09-safety-replay-20261114-220550` | `a3763f76b0f35da784da1da477e1cd06d50c66a1680c96de25c8a63cfcb9ca50` |

PV02–PV04 and PV06–PV08 were outside this replay's scope. The
prospective acceptance criteria for a bounded Chainlit pilot remain
unmet.
