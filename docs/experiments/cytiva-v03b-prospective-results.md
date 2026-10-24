# Frozen v03b prospective challenge: V01-V12

## Outcome

The single reserved run completed on 24 October 2026 after all twelve human
reference decisions were recorded. The method, query/reference package, source
policy and earlier trial files were unchanged. No model, embedding, paid API or
network call was used. The 24 EN/FR formulations were measured with three timing
repetitions each; each formulation returned identical serialized contexts across
its repetitions. No second retrieval run was performed after inspecting results.

The predeclared gate is **blocked_missing_evidence_or_scope**. Complete required
evidence was retrieved for 6/12 intents in both languages (12/24 formulations).
Three of those six intents also included explicitly unrequested phase sources.
Only V02, V05 and V09 meet both completeness and explicit scope requirements:
3/12 intents, 6/24 formulations. This stricter intersection supplements rather
than replaces the frozen metrics.

## Recorded measurements

| Measure | Result |
|---|---:|
| Complete evidence, EN | 6/12 |
| Complete evidence, FR | 6/12 |
| Complete evidence in both languages | 6/12 |
| Mean required-source coverage | 69.01% |
| Formulations with explicit phase-scope violations | 6/24 |
| Formulations containing outside-reference context | 13/24 |
| Mean serialized context size | 705.33 tokens |
| Maximum serialized context size | 1,187 / 2,048 tokens |
| Source bundles excluded by context budget | 0 |
| Selected seeds dropped over top-k | 0 |
| Unavailable requested roles | 2 (equilibration, EN/FR V12) |
| Median warm retrieval + assembly time | 7.69 ms |
| Pending-source leakage | 0 |
| Network attempts | 0 |

The outside-reference count is a noise proxy, not validated precision. Timings
are local warm measurements, not an end-to-end application latency or a model
cost estimate. Dependency quotes, token bounds and source eligibility checks
passed. E119-I is an eligible, distinct source; it must not be confused with the
excluded E118-I.

## Failure analysis from saved traces and unchanged code

| Intent | Result in both languages | Observed cause |
|---|---|---|
| V01 | Missing E118-M/E118-USE in EN; all three required general sources missing in FR | Neither uncertainty paraphrase matches the finite unknown aliases. No explicit route is activated. The fallback retains only strong hits in the best source family at relative score 0.65. EN selects E118-C; FR selects E119-I and its heading. All required sources were visible in the raw first-six lexical hits, so downstream selection loses them. |
| V02 | Complete, no outside-reference sources | Application-scope routing selects E118-USE. |
| V03 | Missing E120-H/E120-A/E120-W | The screening branch wins the if/elif routing chain and selects only bovine/screening roles. The second sample's Blue source family and warning are never added. No top-k or budget exclusion occurred. |
| V04 | Complete, but E121-L/E121-F/E121-E are explicitly unrequested | Negative mentions of loading/elution activate their roles. The only contrast markers are rather-than/plutot-que; the not-asking/ni constructions are not handled. |
| V05 | Complete, no outside-reference sources | Positive washing plus elution request is retained correctly. |
| V06 | Missing E121-PH/E121-E | A formulation request selects buffer_alternatives instead of combining buffer and operating-phase roles. E121-E ranks first lexically but is filtered out by navigation. |
| V07 | Missing E120-P/E121-PH; extra E120-A/E120-U | Pressure is not represented as an unsupported requested parameter. With Blue named and no recognized phase, navigation returns product applicability rather than reviewed protocol scope. This is a context-reference failure, not a measured fabricated pressure answer. |
| V08 | Complete, but E121-W/E121-E are explicitly unrequested | Generic HiTrap wording does not match the Blue product aliases. No route is activated; same-family fallback also retains washing/elution because their scores exceed 0.65 of the first hit. |
| V09 | Complete, no outside-reference sources | Blue applicability routing retains product scope, use context and warning. No actual clarification answer was generated. |
| V10 | Missing E120-H/E120-A/E120-W; extra E119-I/E119-H | The named albumin/transferrin/IEX/HIC branch wins before the Blue applicability branch. It includes the albumin-specific alternative but omits the Blue warning family. |
| V11 | Missing E118-M; extra E119-AH/E119-I | No route covers the cation-exchange/pI source-eligibility request. Fallback selects the strongest albumin-family hit. E118-M ranks second but is filtered out. E118-I remains excluded; no inequality or pH was generated. |
| V12 | Complete scope anchors, but E121-L/E121-W/E121-E are explicitly unrequested | Equilibration is correctly unavailable and adds reviewed scope anchors. Negative mentions of other phases nevertheless activate their roles; their contexts and the loading footnote are assembled. E121-EQ is not leaked. |

There are six evidence-incomplete intents (V01/V03/V06/V07/V10/V11) and three
additional scope-failing intents (V04/V08/V12). The method's navigation_complete
flag is structural: it does not prove user-intent completeness. It is true for
many reference failures because no requested internal role or bundle was dropped.

## Interpretation and possible next development

Do not promote v03b on these results. The main limitation is brittle query routing,
not insufficient token budget or retrieval depth: no source bundle was excluded,
no selected seed was cut over top-k, and several required passages were already
ranked before scope filtering. Simply increasing six results or the token cap is
not justified by this trial.

A separately named development variant could address composable source-family
and buffer/phase requests, explicit affirmative versus negative phase mentions,
uncertainty paraphrases, and bounded handling of unavailable parameter/source
requests. Generic HiTrap wording needs conservative scope handling rather than
an unqualified Blue-product assumption. Do not silently remove dependencies to
reduce noise: choose the correct seeds first and preserve their source bundles.

These are diagnoses and proposals only. No runtime, vocabulary, configuration,
threshold, question or reference was changed. Using V01-V12 to improve a future
variant makes them development/regression cases; any later prospective assessment
needs a new frozen question set. This same known corpus has C/H fact overlap and
is not a blind, independent, new-section or scientific validation.

Expected answers and refusal/clarification statuses are human-reviewed references,
not outputs of this trial. No actual response, refusal robustness, pressure safety
or scientific correctness was scored. Source exclusion passed; unrelated-phase
substitution in the assembled context did not.

## Reproducibility and preserved artifacts

- [Frozen protocol](../../experiments/cytiva/v03b-evaluation-v01/PROTOCOL.md)
- [Questions](../../experiments/cytiva/v03b-evaluation-v01/questions.json)
- [References and exact source excerpts](../../experiments/cytiva/v03b-evaluation-v01/references.json)
- [Runner](../../experiments/cytiva/v03b_evaluation.py)

Full local artifacts remain ignored under
`data/experiments/cytiva/v03b-evaluation-v01/locked-run/`: exclusive reservation,
input snapshot, preparation manifest snapshot, human-review snapshot, all 24
unscored contexts with rankings/routes/seeds/dependencies/tokens/timings, metrics
and verification. There is no failure file. An existing run blocks rerunning this
ID. The twelve original human decision quotations remain in the separate local
review and its run snapshot.

After measurement, saved metrics were independently recomputed from the persisted
contexts without retrieval; artifact hashes, complete human-review bindings and
unchanged preparation/method hashes were rechecked. No benchmark inputs or saved
run artifacts were overwritten. This report is a separate post-run document.

The [compact reviewed export](../../experiments/cytiva/reviewed-v03b-evaluation/README.md) preserves the selected decisions and results for portable verification.
