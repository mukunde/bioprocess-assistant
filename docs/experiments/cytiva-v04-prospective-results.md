# Frozen v04 prospective challenge: W01-W12

## Outcome and preserved execution

The single reserved run completed on 25 October 2026 (Europe/Paris), after all
twelve human decisions were recorded. Its reservation timestamp is
`2026-10-24T22:34:32.926068+00:00`. No second retrieval run followed inspection.
The 24 English/French formulations each had three timing repetitions, with
identical serialized runtime results across repetitions. No LLM, embedding,
paid API or network call was used.

The frozen gate is **blocked_missing_evidence_scope_or_diagnostics**. Required
evidence is complete for 8/12 intents in both languages, but only **W10 and W11**
also meet the explicit scope and diagnostic criteria in both languages.
This supplementary intersection is 2/12 intents and 5/24 formulations
(W07 English, W10 English/French and W11 English/French). It does not replace
the frozen scoring rules. W07 English still contains outside-reference noise.

The local output directory is
`data/experiments/cytiva/v04-evaluation-v01/locked-run/`. Its 46 files retain
the reservation, human-review snapshot, frozen input snapshots, pre-run
manifest, all unscored contexts, timings, metrics and final verification.
These raw artifacts remain outside Git under the project policy.

## Measurements

| Measure | Result |
|---|---:|
| Complete required evidence, English | 8/12 |
| Complete required evidence, French | 8/12 |
| Complete required evidence in both languages | 8/12 |
| Mean required-source coverage | 83.06% |
| Explicitly unrequested context present | 13/24 formulations |
| Outside-acceptable-reference context present | 15/24 formulations |
| Diagnostic criteria failed | 2/24 formulations |
| Mean serialized context size | 813 tokens |
| Maximum serialized context size | 1,741 / 2,048 tokens |
| Bundles excluded by token budget | 0 |
| Selected seeds dropped over six-result cap | 0 |
| Unavailable requested roles | 2: equilibration, W11 EN/FR |
| Median warm retrieval and assembly | 8.70 ms |
| Pending-source leakage / network attempts | 0 / 0 |

Outside-reference context is a noise proxy, not validated precision. The two
unavailable roles are an expected source-boundary signal, not leakage. Timings
are local warm measurements, not application or model latency. No answer was
generated: answer quality, numerical answer accuracy and actual clarification
behavior were not evaluated.

## Failure analysis from saved traces and unchanged code

| Intent | Observed result | Cause supported by traces and code |
|---|---|---|
| W01 | EN misses E118-M/E118-USE; FR misses E118-C/E118-M/E118-USE and includes E119-AH/E119-I | The uncertainty paraphrases do not activate a general route. Same-family lexical fallback at relative score 0.65 retains only E118-C in English and E119-I with its heading in French. All required IDs appear among the raw first-six hits in French; E118-M lies below those six in English. The downstream fallback further restricts retrieval. |
| W02 | Both miss E118-USE, despite its first-place lexical rank in English | The general direct-use branch is guarded by absence of a Blue mention. Naming Blue for the separate second preparation suppresses the first preparation's applicability route. Only Blue applicability roles are assembled. |
| W03 | Complete evidence, but E121-W is explicitly unrequested in both languages | Postposed scope exclusion (washing outside scope) is not recognized; washing and elution both become positive phases. |
| W04 | Complete evidence, but E121-L/E121-F/E121-E are explicitly unrequested in both languages | Imperatives exclude/écarte are absent from the negative patterns. Loading and elution become positive roles alongside washing; the loading footnote follows its parent. |
| W05 | Complete evidence, but E121-E is explicitly unrequested in both languages | Postposed not-requested wording does not negate the preceding elution mention. Buffer alternatives and washing are correctly retained, but operating elution is added. The reviewed whole buffer-formulation excerpt is allowed by the reference; the separate operating-phase excerpt is the violation. |
| W06 | Complete evidence, but E121-W/E121-E are explicitly unrequested in both languages | Leave out/laisse de côté is not recognized. All three phases are selected rather than loading and its scoped note alone. |
| W07 | Complete in both languages; E119-B/E119-BI are extra in both; French additionally includes E121-E/E121-PH and violates explicit scope | The screening route always adds source-context and method-alternative roles, creating avoidable noise. English buffer-name normalization removes the elution phase mention; French coordinated tampons de liaison et d'élution leaves an elution mention, which activates operating parameters. |
| W08 | Both miss E119-A/E119-I/E119-H and include Blue sources outside scope | Product matching ignores negative polarity. Naming Blue in a not-asking clause activates Blue applicability and the albumin-specific Blue alternative. The finite method-explanation aliases do not recognize Explain/Explique, so the requested IEX/HIC explanation roles are omitted. |
| W09 | Both miss E121-W; maximum-pressure limitation diagnostics pass | The pressure branch selects protocol scope anchors and records the source limitation, but bypasses composition with the positively requested washing role. Source-boundary handling works; the supported part of the combined request is lost. |
| W10 | Complete, clean context; diagnostics pass in both languages | Conditional-IEX boundary routing returns the approved general method excerpt and flags the unapproved condition. E118-I remains excluded. This does not validate a generated response. |
| W11 | Complete, clean context; diagnostics pass in both languages | Washing is retained while equilibration is explicitly reported unavailable. Protocol anchors are added without E121-EQ or substitution from other steps. |
| W12 | Scope anchors complete, but E121-E is explicitly unrequested; both diagnostic checks fail | Exclude/exclus is not recognized, so both elution mentions are positive. The synthetic contradiction is not recorded, and navigation_complete is incorrectly true for this request. No operational answer was generated. |

No missing evidence was caused by token-budget rejection or the seed cap in this
run. The dominant defects are finite phrase coverage, negation polarity,
cross-task composition and overly broad role selection. The structural
`navigation_complete` flag is not proof of user-intent completeness: W01/W02,
for example, can have missing reference evidence while this flag is true.

## Integrity and interpretation

The preparation manifest and method-lock LF-normalized SHA-256 values remain:

- Manifest: `98f15737e8d04f691ba5c2b09fd0ebcb9fef45d079778179f1419a75343b606d`.
- Method lock: `972a46be1668fbbe941502a2fc579f3be6786e8675a0be89095ce21e9259ab08`.

Post-run verification independently recomputed scores from saved contexts only,
without invoking search or planning. Scores match the saved metrics; native
context/metric hashes and all 1,488 protected earlier file hashes match.
The human-review snapshot is byte-identical to the completed review record.
Exact source serialization, source eligibility, dependency closure and token
bounds passed during execution. E118-I and E121-EQ remain excluded; E119-I is a
different, eligible excerpt.

The preparation verifier still reports its original twelve pending references:
that immutable preparation state is historical. Execution approval comes from
the separate twelve completed decisions and their question/reference hash
bindings, checked before the run and preserved in its snapshot.

This is a prospective wording/composition challenge on the same known 25-excerpt
corpus, with known-code question drafting, not an independent corpus benchmark.
The 8/12 score must not be compared directly with v03b's 6/12 as if the questions
were identical, nor with v04's successful development results on known V cases.
No automatic adoption is justified. Frozen code, configuration, questions,
references, exclusions and previous results have not been changed.

## Next priority, not implemented in this run

Review these failures before authorizing another variant. A bounded next design
should represent separate tasks, requested roles, exclusions and contradictions
explicitly; apply polarity to product names as well as phases; compose supported
roles with unavailable-parameter diagnostics; and separate buffer formulations
from operating instructions consistently in both languages. Avoid treating each
failed sentence as another isolated alias to add. Any follow-up implementation
should use a new version, retain W as development/regression evidence, and reserve
a new human-reviewed challenge before evaluating generalization.
