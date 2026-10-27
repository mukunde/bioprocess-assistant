# Frozen EN/FR versus structured comparison: FT01-FT12

## Outcome

The one-pass frozen comparison completed on 26 October 2026 after all twelve
actual human approvals. All 48 raw arm outcomes were saved before scoring. No
retry, candidate adjustment, reference amendment or case removal was performed.

| Gate | Result |
|---|---:|
| Structured documentary control S | 24/24 language observations |
| Free text F0: exact intent and documentary equivalence | 12/24 |
| Free text EN | 8/12 |
| Free text FR | 4/12 |
| Complete bilingual pairs | 4/12 |
| Execution exceptions | 0/48 |

The four fully successful pairs are FT01, FT05, FT06 and FT09. EN also passes
FT03, FT07, FT08 and FT12. All other observations remain failures in the declared
denominators. Successful structured outputs include the expected scoped
clarifications, missing-source states and quarantine; success does not imply all
requested parameters exist or that an answer is scientifically validated.

The frozen acceptance criterion (all 24 observations and all 12 pairs pass) is not
met. The structured control works on this reviewed set; the free-text interpreter
is not an equivalent replacement on these inputs.

## Failure analysis from preserved outputs and static code inspection

| Case | Failed language | Observed behavior and cause |
|---|---|---|
| FT02 | EN, FR | EN identifies both flow requests but rejects the clause containing `I need` through its residual-text coverage gate. FR does not recognize `il me faut` as a command and loses E's loading-flow unit. In both languages the unresolved clause blocks the recognized sibling requests too. |
| FT03 | FR | Both units are recognized, but the wording `le volume de lavage en volumes de colonne` is not completely consumed by the closed residual grammar. The entire request is preblocked. EN passes. |
| FT04 | EN, FR | `List` / `Liste` is absent from the command grammar, so the elution-buffer request is missing. FR also leaves `séparément` unresolved. The recognized washing endpoint request is then globally blocked. The failure occurs before a faithful distinction between buffer preparation and operating-elution exclusion can reach the engine. |
| FT07 | FR | The facts, owners and requests are recognized, but the French sample statement leaves substantive residual text. Global blocking suppresses the independently answerable SEC principle as well. EN preserves the expected scoped clarification and serves E. |
| FT08 | FR | The scope regex interprets `son` as task ID `S` followed by the allowed scope marker `on`, creating a third, unrequested task and duplicating the column assertion. This violates the reviewed inventory and projection meaning. D still receives clarification and E remains served; this is not evidence of a released contradictory flow value. EN passes. |
| FT10 | EN, FR | The natural question `What loading flow does the manual give...` / `Quel débit de chargement le manuel indique-t-il...` has a recognized selector but fails residual coverage. FR also rejects part of the available-sample statement. No structured projection is dispatched. The natural questions are retained unchanged. |
| FT11 | EN, FR | The interpreter carries washing forward to `maximum pressure` and merges it into the washing item. The reviewed meaning requires a separate general `operating_limits` item. The engine consequently reports `unsupported_selector` instead of the reviewed bounded `missing_source` state. Washing flow and the independent IEX principle are still served; no pressure value is invented. |
| FT12 | FR | All three units are recognized, but the residual coverage check rejects the accented/apostrophe construction in the equilibration/loading clause. All three units are blocked, including the supported loading and independent binding-buffer requests. EN correctly keeps equilibration quarantined and serves the other two. |

The nine incomplete-inventory observations make zero core calls. The other three
failed observations (FT08 FR and FT11 EN/FR) reach the engine with incorrect
interpreted structure. F0 makes 15 core calls in total, at most one per observation.
These counts come from the saved bridge outcomes, not another interpretation run.

`F0_context.failures = ["execution_error"]` in failed score rows is the frozen
scorer's default when intent does not pass and documentary comparison is not
entered. It does **not** mean an execution exception occurred: all 48 raw `error`
fields are null, and F0 `failure` / `rejection_audit` fields are null. This reporting
limitation is documented here without changing the frozen scorer or its output.

## Integrity, exclusions and resources

- Method/data locks, all review bindings and prior decision-record hashes verify
  after execution. The historical preparation/review-completion snapshots remain
  unchanged and still describe their earlier, pre-execution checkpoint.
- All 39 emitted core contexts (24 S and 15 F0) were inspected. Neither E118-I nor
  E121-EQ appears as an admitted passage or selected root. Quarantine is preserved;
  FT12 FR nevertheless fails availability because of the global grammar block.
- The largest emitted context is 1,439 serialized tokens and two selected roots,
  below the frozen limits of 2,048 tokens and six roots.
- The 16 older local notes are byte-identical to their recorded SHA-256 values.
  All previously tracked files and the Git index remain unchanged.
- The runner records no network attempt. No model, paid API, commit or push was
  used. The 48 outcomes, attempt record, completion record and scores are retained
  in the original exclusive run directory.

Initialization took about 619 ms. Recorded arm elapsed medians were approximately
26 ms for S and 119 ms for F0; sums were 0.98 s and 3.38 s respectively. These are
descriptive measurements of this local run, including blocked requests. They are
not matched successful-workload benchmarks or p95/p99 estimates.

## Interpretation and next priority

The main obstacle is faithful parsing and local scope management, rather than
retrieval depth on this set. Retain the structured input as the reliable control.
A future separately named candidate should prioritize preventing phantom owners,
keeping operating limits separate from adjacent stages, and improving bounded
EN/FR clause coverage. Any proposal to localize blocking must preserve conservative
handling when unresolved text can change the owner or scope; globally ignoring
unknown words would not be justified by these results.

FT01-FT12 are now development/regression evidence for any such repair. A new
candidate needs its own freeze and fresh prospective questions. No repair or
second run is included in this experiment. This same-author, code/source-aware
set is not blinded independent validation and evaluates no generated answer.

## Artifacts

- [Integrity audit, raw-output hashes and unresolved-clause evidence](free-text-comparison-v01-results-checks.json)
- [Frozen method](../../experiments/cytiva/free-text-comparison-v01/METHOD.md)
- [Human review summary](../../experiments/cytiva/free-text-comparison-v01/REVIEW-SUMMARY.md)
- Local retained run: `data/experiments/cytiva/free-text-comparison-v01/locked-run/`
  (`FT01-en-S.json` through all 48 arm records, `attempt.json`, `completion.json`,
  `scores.json`). These raw artifacts remain local; this report does not publish
  or authorize versioning them.
