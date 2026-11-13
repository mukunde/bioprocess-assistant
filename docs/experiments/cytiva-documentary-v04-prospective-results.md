# Prospective Cytiva v04 acceptance results

On 13 November 2026, both frozen v04 variants scored **1/8** on VP01–VP08.
Both retained every required passage for every scored request. The
response layer missed the 7/8 outcome threshold and three mandatory
behavior checks. VP06 omitted the applicable contraindication, which
fails the documentary safety criterion.

Local protocol and references: `cytiva-documentary-v04-prospective-protocol.md`.

[v04 regression replay](cytiva-documentary-v04-replay-results.md)

## Scored questions

| Case | Observed behavior in both variants | First failure |
| --- | --- | --- |
| VP01 | Abstained despite having both passages. It omitted the 2 CV of 6 M guanidine hydrochloride and the detergent example that supplies the 1 min duration. | Proposal missed the requested facts after resolving the precipitated-protein route. |
| VP02 | Correctly gave the 3 CV prewash and the SuRe/SuRe LX restriction. It omitted the post-reagent rinse that carries pH 7.0–8.0. | Proposal selected only the prewash. |
| VP03 | Correctly gave the sodium-phosphate binding formulation, along with its potassium-based alternative. It omitted the sodium-phosphate elution formulation and its 2 M sodium chloride. | Proposal selected only the binding formulations. |
| VP04 | Asked for the product and procedure. It omitted both elution volumes and the 1–2 mL/min elution range for the 1 mL column. | Procedure binding failed. |
| VP05 | Asked for the product and procedure. It withheld the flow range but did not ask whether the column was 1 mL or 5 mL. | Procedure binding failed before the size check. |
| VP06 | Asked for the product and procedure. It gave no operating method but omitted the explicit contraindication from E120-W. | Procedure binding failed before the applicability check. |
| VP07 | Asked for the product and procedure. It omitted both conditional direct-use guidance and the scoped abstention on a numerical cutoff. | Product resolution failed. |
| VP08 | Gave the 0.5–5 mL/min loading range and Blue Sepharose warning, then asked whether the other medium was MabSelect SuRe or SuRe LX. The loading footnote appeared only as a source dependency. | Passed. |

Citation metadata and dependencies matched the canonical assembled
sources. No excluded passage, unsupported actionable instruction, or
cross-procedure parameter transfer was observed. The missed warning in
VP06 recurred on all four repetitions of both variants. All case-level
decisions, citations, and rendered outputs were stable across repetitions.

## Regressions outside the score

- **PE01–PE08** Both variants preserved 8/8 and reproduced their prior
  decisions, citations, and rendered answers, including the corrected
  PE03 procedure boundary.
- **AD01** Product–procedure answered both branches. Fixed 32 answered
  Protein A Sepharose and explicitly abstained for MabSelect.
- **XC06** Both variants separated the common wash and stronger alkali
  rinse and preserved the SuRe/SuRe LX restriction.

All 80 regression requests reproduced their prior assembled passage
lists, decisions, citations, and rendered answers.

## Timing and provenance

Median and range in milliseconds across 24 warm scored requests per
variant. Times exclude index setup and regressions.

| Stage | Fixed 32 | Product–procedure |
| --- | ---: | ---: |
| Retrieval and assembly | 82.184 (64.985–126.418) | 83.232 (62.529–115.376) |
| Proposal | 0.882 (0.272–3.480) | 0.815 (0.309–2.860) |
| Validation | 0.704 (0.209–3.695) | 0.715 (0.226–2.916) |
| Rendering | 0.007 (0.006–0.039) | 0.007 (0.006–0.033) |
| Total | 83.402 (65.661–127.246) | 84.027 (63.307–116.442) |

The run completed 144 local requests with 144 unique metadata-only
traces, zero paid or generative calls, and no execution errors. E118-I
and E121-EQ remained excluded. The earlier freezes and trials were preserved.

| Record | SHA-256 of file bytes |
| --- | --- |
| Prospective v04 manifest | `196718b9f2b9246001846ea82317564e707d4f85a487413bf2e24062ccadd93a` |
| Event journal in local run `documentary-v04-prospective-20261113-223118` | `66ef7ff21717a208655207b4906521878695a240469c999c24e86605171c3095` |

The prospective result does not support a Chainlit pilot. The first
priority is to detect the Blue Sepharose contraindication across named
Blue media even when the narrower procedure remains unresolved. The
other failures concern item selection, procedure binding, and general
documentary scope.
