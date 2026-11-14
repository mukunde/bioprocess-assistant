# Prospective Cytiva v08 acceptance results

On 14 November 2026, both frozen v08 variants scored **0/8** on
PV01–PV08. Each assembled every required passage and dependency for
all eight questions. Neither met the 7/8 threshold or passed any of
the four mandatory cases. PV01 and PV05 failed the documentary safety
criterion on both variants.

[v08 regression replay](cytiva-documentary-v08-replay-results.md) ·
[v06 prospective results](cytiva-documentary-v06-prospective-results.md)

The approved prospective protocol and the frozen runner are retained
with the local experiment records.

## Scored outcomes

| Case | Observed outcome in both variants | Primary citations used | First failure |
| --- | --- | --- | --- |
| PV01 | Supplied only the immediate rinse of at least 5 CV under the precipitated-protein procedure. It gave an answer without the hypothetical deposit condition and omitted the observed-pressure trigger and the guanidine wash. | E166-P | Proposal treated the hypothetical route as applicable and omitted requested items. |
| PV02 | Asked for product and procedure in general. It omitted the supported SuRe LX detergent branch and did not ask specifically about the second medium's variant. | None | Proposal collapsed two independent requests. |
| PV03 | Gave the 3–4 CV solvent volume, increasing-gradient condition, immediate rinse, and lower-flow warning. It presented the general solvent alternatives and left the disputed 12 h hold unaddressed. | E167-E, E167-W | Proposal omitted an explicit disposition on the disputed hold. |
| PV04 | Gave one generic conditional warning. It did not reject the stated use for M or ask about N's target separately. The documented albumin use was omitted. | E120-W | Proposal combined the confirmed and unassessed samples into one scope. |
| PV05 | Selected loading and returned a loading range and the approximate syringe correspondence. The citation retained its syringe qualifier, but the answer gave a drop rate for the unresolved request without asking about either stage or application method. | E121-L, E121-F, E120-W | Proposal selected a stage and supplied a method-specific value with the method unresolved. |
| PV06 | Listed both wash endpoints and the separate 10–20 CV gradient volume. It asked to confirm either endpoint despite the confirmed effluent result and omitted the elution-buffer role. | E121-W, E121-E, E120-W | Proposal omitted the elution-buffer role and did not represent the observed endpoint. |
| PV07 | Asked for a product and procedure. It omitted the direct-use decision for each assay. | None | Proposal missed the general documentary scope and the interference condition for each assay. |
| PV08 | Returned generic abstentions under two scopes. It neither supported the screening guidance nor explained what binds and what washes through. | None | Proposal missed the supported fields and the distinction between an example medium and the general strategy. |

The mandatory PV02, PV04, PV05, and PV07 checks failed on every
repetition. In PV01 and PV05, validation accepted individually
documented facts without enforcing their applicability to the request.
PV03 and PV06 earned zero under the complete-case criterion. The
partial responses included documented quantities and safeguards.

All 64 scored outputs matched across repetitions within each variant,
and the two variants gave the same decisions, citations, and answers
on all eight scored cases. The cited sources and dependencies matched
the canonical assembled records. E118-I and E121-EQ remained excluded.

## Regressions outside the score

- **QV01–QV08, VP01–VP08, and PE01–PE08** Each set retained 8/8 per
  variant. QV06 retained the Blue Sepharose contraindication and the
  independent MabSelect response.
- **AD01** Product–procedure answered both branches. Fixed 32 answered
  Protein A Sepharose and explicitly abstained for MabSelect.
- **XC06** Both variants kept the common wash separate from the stronger
  alkali rinse and retained the SuRe/SuRe LX restriction.

All 208 requests outside the score matched the v08 replay in rankings,
assembled passages, proposals, decisions, citations, and rendered answers.

## Timing and provenance

Median and range in milliseconds across 24 warm scored requests per
variant. Times exclude setup and the separate regressions.

| Stage | Fixed 32 | Product–procedure |
| --- | ---: | ---: |
| Retrieval and assembly | 71.170 (59.996–108.573) | 71.586 (59.088–115.669) |
| Proposal | 1.383 (0.350–2.140) | 1.250 (0.295–2.335) |
| Validation | 1.257 (0.267–1.990) | 1.178 (0.214–2.087) |
| Rendering | 0.035 (0.018–0.144) | 0.025 (0.019–0.081) |
| Total | 73.404 (62.935–110.492) | 73.691 (61.617–120.198) |

The completed run recorded 272 requests and unique metadata-only trace
IDs with zero paid or generative calls. The first launcher stopped before
creating a request journal because the historical question loader called
itself. The corrected launcher loads the same 34 questions before
installing the runner's configuration. The original launcher and its
manifest were retained. The approved protocol, response layer, and
retrieval settings were unchanged. All 256 protected files matched their
pre-run hashes.

| Record | SHA-256 of file bytes |
| --- | --- |
| Prospective run freeze manifest | `7efe11fc4650a53d66e14a2e695f0a44b5b1553cd24d5d53fe780ba5f6cd7bdc` |
| Event journal in local run `documentary-v08-prospective-20261114-215627` | `035a8fca6b1649efbb4dbd127e4e1278ee7f3bfcb5cc53f7622d6caad1167768` |

The prospective result fails the criteria for a bounded Chainlit pilot.
Prioritize enforcement of the deposit condition in PV01 and the stage
and application-method ambiguity in PV05.
