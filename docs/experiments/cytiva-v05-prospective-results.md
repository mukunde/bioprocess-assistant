# Frozen v05 prospective challenge: X01-X12

## Outcome

The single reserved run completed on 25 October 2026 after all twelve human
reference decisions had been recorded. Its reservation timestamp is
`2026-10-25T00:39:34.905548+00:00`. The frozen method, aliases, configuration,
questions, references, source exclusions and previous results were not modified.
No second retrieval run followed inspection. No LLM, embedding, paid API,
download or network call was used.

The predeclared gate is **blocked_missing_evidence_scope_or_diagnostics**.
Required evidence is complete for **7/12 intents in both languages**; only
**X02, X05 and X09** also satisfy explicit source scope and diagnostic criteria
in both languages. That supplementary intersection is 3/12 intents and 8/24
formulations: both languages of X02/X05/X09, plus English X06 and X10. It does
not replace the frozen metrics.

## Recorded measurements

| Measure | Result |
|---|---:|
| Complete required evidence, English | 8/12 |
| Complete required evidence, French | 7/12 |
| Complete required evidence in both languages | 7/12 |
| Complete formulations | 15/24 |
| Mean required-source coverage | 79.17% |
| Explicitly unrequested context present | 9/24 formulations |
| Outside-acceptable-reference context present | 11/24 formulations |
| Required diagnostic criteria failed | 6/24 formulations |
| Mean serialized context size | 757.92 tokens |
| Maximum serialized context size | 1,187 / 2,048 tokens |
| Source bundles rejected by token budget | 0 |
| Selected seeds dropped over six-result cap | 0 |
| Unavailable-source entries | 3: two equilibration entries and one unsupported general-family entry |
| Median warm retrieval and assembly time | 10.95 ms |
| Pending-source leakage / network attempts | 0 / 0 |

The 24 formulations each had three timing repetitions, for 72 measurements.
All serialized runtime outputs, including navigation and diagnostic metadata,
were identical within each formulation's repetitions; no best-repeat selection
was used. Timings are local warm measurements, not application or model latency.
Outside-reference context is a noise proxy, not validated precision. Recorded
token sizes describe context serialization, not paid model consumption.

No answer was generated. Numerical answer accuracy, scientific suitability,
actual clarification wording and assignment of generated statements to separate
samples were not evaluated. Expected answer/clarification labels remain human
reference labels, not observed response classifications.

## Analysis from saved traces and unchanged code

| Intent | Saved outcome | Cause supported by traces and implementation |
|---|---|---|
| X01 | Both languages miss E118-USE/E118-C/E118-M entirely; bovine-family passages are returned instead | The open-question/unchosen-assay wording does not match the finite uncertainty signals. No explicit route is activated. Same-family fallback starts from E119-BI and applies the 0.65 relative cutoff, selecting E119-BI in EN and E119-BI/E119-B/E119-X in FR, with their heading. E118-C appears among the raw first-six hits in both languages and E118-USE in EN, but this selection filters them out. This is both uncertainty recognition and overly restrictive fallback scope. |
| X02 | Complete, no outside-reference sources or diagnostic failures in either language | Direct-use applicability selects E118-USE. This verifies context availability, not a generated answer distinguishing the two interference conditions. |
| X03 | Complete evidence, but EN adds E121-L/E121-F/E121-E and FR adds E121-E, all explicitly unrequested | Omit/omet is not an exclusion rule. English sample application and elution both become positive phase mentions. The French application-de-l'echantillon wording is not a loading alias, so only elution is additionally activated. The French question's original Omet spelling is retained unchanged; even the standard omets in X12 is unsupported. |
| X04 | Complete evidence, but E121-E is explicitly unrequested in both languages | Instead of/au lieu is not a supported contrast marker. Loading and elution both become positive roles. |
| X05 | Complete, clean context in both languages | Buffer formulations and loading are composed; the recognized leave-out construction excludes washing/elution. Whole buffer and loading/footnote atoms remain intact, as required by the reviewed references. |
| X06 | Complete in both languages; EN is clean, FR adds explicitly unrequested E121-E | Do not turn is handled through English not. French ne transforme aucune is outside the finite negative patterns, so the elution mention becomes positive. No task-specific numerical answer was generated. |
| X07 | Both miss E121-W/E121-E and fail navigation_complete/clarification_required criteria | A negated exclusion is treated as an ordinary exclusion: not asking ... exclude and ne ... pas d'exclure create negative elution mentions alongside positive ones. The global conflict flag falsely requests clarification and withholds both operating roles, returning protocol anchors only. |
| X08 | Both miss E119-A/E119-I/E119-H; E119-BL and the Blue applicability family are added | Ruled out of this question/est exclu du perimetre are not recognized postposed product exclusions. Blue remains positive. Discuss/presente also do not match the finite method-explanation aliases, so the albumin branch selects only the Blue-specific alternative and the Blue branch adds product applicability instead of the requested IEX/HIC explanation. |
| X09 | Complete, clean context; pressure-limit diagnostics pass in both languages | The planner composes loading/washing with maximum-pressure source limitations. This preserves the supported requests without leaking a pressure value; no actual pressure answer was generated. |
| X10 | EN is complete; FR misses E118-M. Expected pending-source diagnostics pass in both | Both plans recognize conditional IEX and request general method_selection plus washing/equilibration. French retrieval has no positive lexical hit in any general-family passage, so its family-support guard rejects that route and records no_positive_scope_hit. Equilibration is separately unavailable as expected. The route vocabulary and retrieval vocabulary disagree. |
| X11 | Both miss E120-A/E121-E and fail navigation_complete/clarification_required criteria | Positive elution for A and excluded elution for B are merged into request-wide positive/negative sets without task ownership. A false global conflict suppresses operating and applicability roles, retaining only scope anchors. Separate tasks are not represented strongly enough to distinguish this case from a real same-task contradiction. |
| X12 | Scope anchors are complete, but E121-W is explicitly unrequested; all three required conflict diagnostics fail in both languages | Omit/omets is not recognized, so the second washing instruction is also positive. The actual same-task contradiction is missed; navigation_complete is true and clarification_required false. |

### X10: lexical support is not semantic support

Pure lexical normalization of the saved X10 question and general-family quotes
was inspected with search/planning blocked; no second retrieval or planner call
was performed. There are no shared indexed terms between E118-M itself and
either language's question. English nonetheless passes the general-family guard
through incidental overlaps: `not` in E118-USE and `been`/`three` in E118-C.
French shares no indexed term with any of those three general passages.

The English E118-M success therefore does not establish a reliable bilingual
semantic bridge. The guard accepts any positive family hit, then selects the
requested role from that family; it does not require role-relevant lexical
support. This explains the asymmetry visible in the saved unavailable entries.

### What did not cause these failures

No source bundle was rejected by token budget and no selected seed was dropped
by the result cap. Enlarging those limits does not address the failures observed
here. Structural navigation_complete/source_support_complete flags do not prove
that the user's request was understood: X01 can report both true while missing
every required reference source.

The main limitations are finite phrase recognition, compositional negation,
task ownership, product polarity and disagreement between routing and lexical
support. Adding another isolated alias for each failed sentence would not by
itself resolve those architectural limits.

## Preservation and verification

All 48 run files remain under the ignored local directory
`data/experiments/cytiva/v05-evaluation-v01/locked-run/`. They include the
exclusive reservation, original review snapshot, frozen input snapshots,
pre-run manifest, all 24 unscored contexts and timings, metrics and verification.
No result or input was overwritten.

The retained preparation manifest and method-lock LF-normalized SHA-256 values
are respectively:

- `10ec2b9d37ed231be5f586e64c0056bc51c3589df32e13c73aadcc40dd143541`
- `fc309ddad6cc4d205ae0855a3a315423eaa3e601ef1a780934a84f8b76015ece`

Independent post-run checks recomputed frozen scores from saved contexts only,
with BM25 search and planning blocked. Every recomputed field matches the
recorded metric. Native result hashes match, the review snapshot is byte-identical
to the completed review, and all 1,588 protected earlier file hashes match.
The frozen verifier passes. Execution checked exact source serialization,
dependency closure, eligible sources and token bounds. E118-I and E121-EQ remain
excluded; E119-I is a different, eligible excerpt.

The preparation's pending flags and preparation-era verification remain
historical. Completed decisions and this later reserved run establish the current
review/execution state without rewriting those historical files. No automatic
adoption or application-default change occurred.

## Interpretation and next priority

This is a prospective wording/composition challenge on the same known 25 excerpts,
with known-code authorship and correlated EN/FR forms. It is not a new manual,
independently authored benchmark, scientific validation or answer-generation test.
The v05 development W score of 12/12 is known-case evidence; it did not generalize
to all X formulations. The X score must not be compared directly with v04's W
score as if they were the same test set.

Before authorizing another variant, prioritize explicit task-scoped roles and
compositional polarity over request-wide keyword sets. Align the routing and
retrieval vocabulary, and distinguish meaningful role support from incidental
word overlap. A structured task/phase/product request representation would also
make unsupported or ambiguous interpretations visible for clarification.
These are proposals, not changes made in this run. Any implementation belongs
to a new version; X then becomes development/regression evidence, with a new
reviewed challenge reserved before testing generalization again.
