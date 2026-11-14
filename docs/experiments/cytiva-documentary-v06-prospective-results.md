# Prospective Cytiva v06 acceptance results

On 14 November 2026, both frozen v06 retrieval variants scored **0/8**
on QV01–QV08. Both assembled all listed reference passages for every
scored request. Neither met the 7/8 threshold or any of the four mandatory
behavior checks. QV06 failed the documentary safety gate.

[v06 regression replay](cytiva-documentary-v06-replay-results.md)

The approved prospective protocol is kept with the local experiment records
as `cytiva-documentary-v06-prospective-protocol.md`.

## Scored outcomes

| Case | Observed outcome in both variants | First failure |
| --- | --- | --- |
| QV01 | Generic abstention. Omitted the rinse pH, the solvent-only lower-flow warning, and the limits on both settings. | Proposal did not identify the requested items in the solvent procedure. |
| QV02 | Abstained on both routes despite the available sources. Omitted the common sodium-phosphate formulation and the stronger route's prewash. | Proposal resolved both routes but missed their requested items. |
| QV03 | Asked for the product and procedure. Omitted both chloride salts and concentrations. | Procedure binding failed for the elution buffer formulations. |
| QV04 | Asked for column size on the wash and omitted the elution branch. The two sizes were already given for separate records. | Scope resolution failed to bind each record's size and stage. |
| QV05 | Gave the documented washing flow and warning but selected washing from an unresolved washing-versus-elution record. It supplied neither a buffer choice nor the required stage clarification. | Procedure binding collapsed the two alternatives to washing. |
| QV06 | Cited E120-W and answered the independent MabSelect branch with the lower-flow and backpressure warnings. It also returned Blue Sepharose timing as an answer for sample A without rejecting its stated use. | The family warning check did not cover the mixed-product question. Validation accepted timing alongside the applicable contraindication. |
| QV07 | Asked for the product and procedure. Omitted the conditional direct-use decision for A and the question about non-interference for B. | General documentary scope and the two samples were not resolved. |
| QV08 | Asked for the product and procedure. Omitted both conditional IEX and HIC guidance and the explicit abstention on exact pH. | General documentary scope was not resolved. |

QV06 is a safety failure on all four repetitions per variant. The warning
and its citation are present. The answer still presents operating guidance
for the case that the warning rules out. The independent MabSelect guidance
remains supported. The other missing items and clarifications fail
completeness. Citation metadata and source dependencies matched the
canonical assembled records. E118-I and E121-EQ remained excluded.

## Regressions outside the score

- **VP01–VP08 and PE01–PE08** Both variants retained 8/8 on each set,
  including the VP06 warning and the PE03 procedure boundary.
- **AD01** Product–procedure answered both solvent branches. Fixed 32
  answered Protein A Sepharose and explicitly abstained for MabSelect.
- **XC06** Both variants separated the common wash from the stronger
  alkali rinse and retained the SuRe/SuRe LX restriction.

All 144 regression requests matched the previous v06 replay in assembled
passages, proposals, decisions, citations, and rendered answers.

## Timing and provenance

Each cell gives the median and range in milliseconds for 24 warm scored
requests per variant. Times exclude index setup and regressions.

| Stage | Fixed 32 | Product–procedure |
| --- | ---: | ---: |
| Retrieval and assembly | 87.112 (68.569–113.172) | 88.773 (74.045–120.805) |
| Proposal | 1.439 (0.455–2.568) | 1.382 (0.410–3.928) |
| Validation | 1.246 (0.393–2.335) | 1.222 (0.337–3.509) |
| Rendering | 0.012 (0.008–0.092) | 0.012 (0.007–0.099) |
| Total | 89.855 (73.564–114.341) | 90.772 (75.167–128.724) |

The run completed 208 local requests and linked each to a unique
metadata-only trace. It made zero generative or paid calls. The outputs,
decisions, and citations were stable across repetitions. The prospective
manifest and its parent chain verified. The 82 protected files matched
their pre-run hashes.

| Record | SHA-256 of file bytes |
| --- | --- |
| Prospective v06 manifest | `f0a5cf2e40fca0ddb65c158e4b0607c9b30499130c38b0e0ecd7eb5b31cfe8e7` |
| Event journal in local run `documentary-v06-prospective-20261114-191848` | `6f15d59c188ab1a1ffb79f3c9e89bb11badb5052d84f46f28df7daa09bbf4d62` |

The prospective result fails the criteria for considering a Chainlit
pilot. The first priority is to enforce the contraindication on the
affected request item while preserving the independent supported branch.
