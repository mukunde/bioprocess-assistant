# Frozen opt-in v02 comparison: FV01-FV12

## Recorded result

The one-pass comparison completed on 27 October 2026 after the twelve actual human
pair approvals. All 48 raw arm outcomes were saved before scoring. The method,
references and original scores were not edited, retried or filtered.

| Frozen gate | Passed / total |
|---|---:|
| Structured S documentary observations | 22/24 |
| F0 intent observations | 19/24 |
| Complete F0/paired observations | 17/24 |
| Complete EN observations | 10/12 |
| Complete FR observations | 7/12 |
| Complete bilingual scenarios | 7/12 |

Both languages pass FV01, FV02, FV03, FV05, FV08, FV09 and FV10. EN additionally
passes FV07, FV11 and FV12. Neither language passes FV04 or FV06 under the frozen
gates. Acceptance requires all 24 observations and 12 pairs; it is not met.

S fails FV06 EN/FR only on the expected aggregate flag, not on unit states, source
bindings or intent. That shared failure must not be attributed to the interpreter.
The results remain 22/24 and 17/24; no adjusted or replacement score is published.

## Failure analysis: saved evidence and static code inspection

| Scenario | Language | Finding |
|---|---|---|
| FV04 | EN and FR | Binding-buffer and elution-buffer formulations both receive the item ID `P-buffer_preparation`, because the interpreter generates IDs from task plus stage only. The bridge groups by this ID and rejects the repeated `buffer_formulation` selector. Both formulation units are present, but they cannot remain distinct through projection. A handled `projection_error` is recorded; the core is not called and the otherwise independent washing unit is also unserved. The negated exclusion remains inactive. |
| FV06 | EN and FR, S and F0 | Individual results match the reference: P washing-specific pressure is `unsupported_selector`, Q general pressure is `missing_source`, and Q loading is supported. Both arms also agree semantically. The engine deliberately sets `all_supported_ready_units_covered=false` whenever any unsupported selector exists; the reviewed reference expects true because all eligible/ready units are covered. This is a definition mismatch between the shared indicator and the reference, not a retrieval failure. |
| FV07 | FR only | The stopping-criteria selector contains the phrase `critères de fin du lavage`, but its unit is incorrectly assigned to `sample_application` from the preceding loading request. The remaining unconsumed washing phase triggers incomplete-inventory handling and globally preblocks all three units, including Q HIC and the size-independent endpoints. EN has the correct scoped clarification and serves the supported siblings. |
| FV11 | FR only | After `débit d’équilibrage`, the second `débit d’élution` inherits equilibration. The phase-selection rule does not recognize the French `d’` construction as the explicit right-hand phase connector, so it prefers the preceding phase. This creates two equilibration-flow units and leaves elution unconsumed, preblocking the full request, including Q loading. EN correctly distinguishes both phases and preserves quarantine. |
| FV12 | FR only | General maximum pressure is assigned to the previous equilibration phase. In French the flow selector precedes its phase word, so the pressure rule's preceding-window logic sees that phase as an attachment even across the comma. The engine therefore emits `unsupported_selector` for pressure rather than the reviewed general `missing_source`. Equilibration remains quarantined; P washing and Q SEC are still served. EN routes pressure correctly. |

The FV04 cause is visible in `free_text_interpreter_v02.py` (task/stage-based item
IDs) and `free_text_bridge_v02.py` (grouping and repeated-selector guard). The
FV07/FV11/FV12 causes are in selector-to-phase association, rather than missing
manual passages. The old phantom task S is not reproduced in these saved outputs;
FV08 passes in both languages. Buffer/operating separation and P-only exclusion
also pass in FV03.

### FV06: retain the result, clarify the indicator later

The structured engine first calculates coverage over eligible, ready units, then
intentionally overrides it to false if any unsupported selector appears. Its
comment states that an unmapped selector must not masquerade as complete coverage.
The reference instead distinguishes eligible-unit coverage from overall service,
which is already false through `has_unserved_units=true`.

This experiment cannot settle that contract by changing code or gold afterwards.
A future reviewed change must explicitly decide the meaning of eligible-unit
coverage versus whole-request service and update separate indicators if needed.
No retrospective reference amendment, rescoring or trial rerun is performed here.

### Errors versus scorer placeholders

All 48 top-level raw `error` fields are null: no exception escaped an arm call.
There are nevertheless two recorded bridge projection failures (FV04 EN/FR), so
this must not be described as an entirely error-free execution. FV07 FR and FV11
FR are intentional preblocks after incorrect interpretation, not thrown failures.

The frozen scorer leaves `F0_context.failures=["execution_error"]` when intent
fails and documentary comparison is not entered. For FV07/FV11/FV12 this label
does not identify a runtime exception. The raw bridge/core records above provide
the actual failure dimension. The scorer itself remains unchanged.

## Preservation, sources and resources

The [post-run audit](free-text-v02-comparison-v01-results-checks.json) binds all 48
raw outcome hashes, native scores and completion record. All 551 files in the
pre-run preservation inventory remain byte-identical, including previously
tracked files, the original FT trial, FV method/data/review material and the 16
older local notes. The Git index and tracked working tree are unchanged.

All 44 emitted contexts (24 S and 20 F0) were checked for original source fields,
quote/page provenance and exact serialized token accounting. Neither E118-I nor
E121-EQ appears in an admitted passage, binding or selected root. No source
approval changed. Maximum context use is 1,674 tokens and three selected roots,
within the frozen 2,048-token/six-root limits. No budget failure explains the
observed differences. F0 made 20 core calls and four observations made none.

Initialization took about 854 ms. Descriptive recorded elapsed medians were
approximately 41 ms for S and 219 ms for F0; arm sums were 1.60 s and 5.37 s.
These include blocked/error cases, are not matched successful-workload benchmarks
and do not establish p95/p99. There were no network attempts, LLM calls or paid API
calls, and no commit or push.

The native run remains local at
`data/experiments/cytiva/free-text-v02-comparison-v01/locked-run/`, including every
`FVxx-language-arm.json`, `attempt.json`, `completion.json` and `scores.json`.
The earlier pending/pre-execution documents remain historical snapshots; this
report records the later completed comparison separately.

## Conclusion and next priority

The frozen candidate does not meet the complete-equivalence gate. Fixing item
identity for distinct buffer uses and local phase attachment is the main parser
priority. FV06 requires a separate explicit contract decision for the shared
coverage flag before any new freeze. Those are proposals, not changes made here.

Do not compare 17/24 directly with the old FT result of 12/24 as a measured gain:
the question sets differ. This source/code-aware prospective set is diagnostic
evidence, not blinded independent validation. It evaluates no generated answer
or scientific suitability. Any future repair turns FV01-FV12 into development
evidence and requires a new candidate/freeze plus fresh reviewed questions.
