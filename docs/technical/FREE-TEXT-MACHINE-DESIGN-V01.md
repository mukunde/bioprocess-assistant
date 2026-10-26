# Free-text machine design v01: schemas and input/output expectations

Date: 26 October 2026. **MC01-MC06 and clarifications approved; refined fixtures
have all four groups GR01-GR04 validated with reservations. No interpreter or bridge implementation,
freeze or comparison execution.** The [machine-design decision](../decisions/2026-10-26-free-text-machine-design-review.json)
preserves the actual collective approval. FI01-FI06, IF01-IF14
and the six preceding clarifications were approved in one
[actual human message](../decisions/2026-10-26-free-text-interface-review.json).
The earlier FI approval is distinct from the later MC approval. Neither is a
completed review of the newly refined individual origins and test conditions.

## Artifacts

| File | Purpose |
|---|---|
| [Input schema](free-text-input-v01.schema.json) | Caller supplies language and original text only; rejects policy/identity overrides and extra properties |
| [Interpretation schema](free-text-interpretation-v01.schema.json) | Ledger, typed origins, literal assertions, tasks, known units, unresolved fragments, issues and projection/mapping definitions |
| [Outcome schema](free-text-outcome-v01.schema.json) | Actual application-side bridge outcome, immutable core result or explicit absence/error, unit accounting, failure and timings |
| [Examples](../experiments/free-text-interface-examples-v01.json) | Sixteen hand-specified I/O expectations and three invalid caller inputs; none is an observed F result |
| [Current static checks](free-text-machine-design-checks-v07.json) | Revised fixture shapes, origin/pointer/hash and external-condition checks after GR01-GR04; no parser, planning or model inference |
| [Grouped review](../experiments/free-text-interface-group-review-v01.md) | Four groups covering every refined example and invalid caller input; GR01-GR04 validated with reservations |

The schemas use JSON Schema Draft 2020-12 with closed application objects and
versioned URNs. Existing structured definitions are referenced, not copied or
edited. Register the three new schemas and the original
[structured schema](task-request-v01.schema.json) by their exact `$id` in an
offline resource registry; no remote reference resolution or schema download.
The original opaque core audit is retained as an object and bound by a whole
result hash; this draft does not invent a stricter replacement for that audit.

## Caller, application and design records are different

The caller input is exactly `language` and `text`. The application supplies its
own request ID and pinned identities; neither can be overridden by user text.
Original UTF-8 bytes determine the text digest. Invalid Unicode encoding and
cross-record semantics require checks beyond JSON Schema.

The outcome schema's root is an actual `free_text_bridge_outcome` with
`record_status=runtime_record`. If it contains a ledger, its component identities
must be pinned rather than `unimplemented`. Hashes establish content consistency,
not authenticity or scientific correctness. The approved source policy remains
the authority; user text cannot change it.

Example entries instead validate against the outcome schema's separate
`#/$defs/design_example` definition. Their expected output is labelled
`schema_stage=specified_not_executed`, keeps `core_result=null` and `timings=null`,
and states expected invocation counts and later core checks. They deliberately
cannot be accepted as actual root outcomes. Interpreter/bridge/policy identities
remain `unimplemented` with null hashes, rather than fabricated component hashes.

For positive examples, only the ledger and intended projection are supplied.
Expected evaluated-unit lists mean which units should reach the unchanged core;
they do not mean those units were successfully answered. Expected summary values
are provisional fixture expectations, not measured performance. For example E02
expects the representable conflict to reach the core and remain unserved.

## New draft bounds and states

MC04 approves resource bounds of 16,000 Unicode code points of caller text, 16 known
tasks, 64 recognizable information units/mappings, 256 entries for each ordinary
ledger list, and 4,096 origins or field-origin links. These are reviewable intake
bounds, not latency measurements. They neither replace nor multiply the unchanged
six-root/2,048-token context budget. An over-limit input must be rejected/countable,
not truncated into a different question. Their approval does not establish measured capacity.

`requested_units` contains recognizable positive selectors from the original
structured vocabulary; unknown selectors remain unresolved fragments with issues,
not fabricated enum values. An unresolved owner has no selected task and can
retain zero known candidates or explicit A/B candidates. Every candidate must be
an actual ledger scope; possible candidates do not become positive requests.

An active ban and a negated ban have distinct polarity/active fields. A restriction
kept only for an omitted item stays auditable and never widens to a task-level ban.
An origin is a real text span, explicit not-stated record or application metadata.
Provided false/zero and unknown/null remain distinct. Decimal punctuation can
normalize within a declared unit; cross-unit conversion remains out of scope.

The wrapper distinguishes `planner_evaluated`, `preblocked` and
`not_evaluated_due_to_error`. Preblocked units have no core binding, no assigned
sources and documentary state `not_assessed_by_planner`. That state is not a claim
of missing manual evidence. Runtime-attempt count is zero or one, including an
attempt that raised an exception; no retry is hidden inside that count.

## Semantic obligations beyond JSON Schema

Shape validity alone does not establish interpretation correctness. Before a
future runtime result is accepted, require all of the following:

1. All IDs are unique in their namespaces. Every issue, assertion, origin,
   fragment, task candidate, item and mapping reference resolves. The single ID
   bijection used for S/F scoring preserves all relationships and order.
2. Text hash, code-point offsets and exact substrings verify against the original
   input, including decomposed accents and supplementary characters. An absent
   field has no fabricated text span. Normalization keeps raw lexemes and roles.
3. Every substantive projection field has justified origins. A pointer resolving
   to a field is not evidence that its value follows from its text. Default or
   not-applicable claims must match reviewed policy. Refined fixtures now use
   focused request/scope/value spans and field-specific absence/default reasons;
   their semantic entailment and exact spans are human-validated with reservations in GR01-GR04; this does not measure interpreter behavior.
4. Every known unit is represented exactly once in the final unit outcomes.
   Counters and inventory flags agree; unknown possible requests prevent a
   complete-inventory claim. Report known-unit accounting separately from full
   request coverage and the diagnostic evaluation score.
5. Projected units have resolved owners and preserve applicable active exclusions,
   task context and relative order. Preblocked units have blocking scoped issues
   and no mapping or source assignment. Empty projections do not call the core.
6. Projection hashes bind the canonical submitted object. Mapping pointers reach
   the correct task/item/information. Shared facts are retained; removed-item
   restrictions cannot weaken or broaden surviving restrictions.
7. When an invalid candidate projection is rejected, preserve it and pointer
   errors in a separate diagnostic audit with its original hash. Do not present
   it as a valid projection or retry a repaired payload. `projection.status=invalid`
   therefore has no valid submitted object. The refined draft schema represents
   this separately as `rejection_audit`, including candidate value/hash and
   pointer errors; E16 specifies the test expectation. No rejected value is run.
8. A non-null core result is the exact single returned result and matches its
   full-content hash, core input snapshot, mapping and pinned identities. Never
   edit the core's own flags or pretend its projection-only coverage covers
   preblocked items. Quarantines and mandatory dependencies remain enforced.
9. Full service requires complete inventory, at least one known unit, no error
   or preblocked unit and actual supported outcomes for all units. It cannot be
   inferred merely from the design's expected dispatch list or a valid schema.
10. Runtime failure preserves prior preblocking and every known remaining unit
    as an explicit error outcome. Timings are actual measurements for completed
    stages; null means not measured/not reached, never zero-duration success.

The current static preparation checks the concrete draft examples for identity,
shape, origin geometry, mapping and accounting consistency. It cannot demonstrate
that a future interpreter infers those records, that a default is substantively
justified, or that the planner will produce the expected documentary outcome.
No IF control is reported as an executed implementation test.

## Examples to review

| Example | Intended boundary | Conformance coverage |
|---|---|---|
| E01 | Washing flow plus binding formulation, both projected | IF01, IF12 |
| E02 | Product label 5 mL versus explicit column 1 mL, preserved for core diagnosis | IF02 |
| E03 | Revised G05: unresolved A/B washing owner, independent C projected | IF03 |
| E04 | G06: policy override rejected, A preblocked, C projected | IF04 |
| E05 | Synthetic partial-item boundary: flow preblocked, endpoint selector retained | IF05 |
| E06 | All recognizable units preblocked, no planner invocation | IF06 |
| E07 | Negated washing exclusion plus active elution ban | IF07 |
| E08 | False scenario fact remains false; general SEC request | IF08 |
| E09 | Sample/loaded-volume roles, unknown loaded volume, decomposed accent and emoji | IF08, IF09 |
| E10 | Ambiguous ban affects both A and B | IF10 |
| E11 | Expected core exception: preserve A preblocking and C error | IF11 |
| E12 | Unknown possible extra request prevents full-inventory service claim | IF13 |
| E13 | Removed-item restriction stays local; shared observed-flow fact remains | IF14 |
| E14 | G02 addition retains endpoints and binding formulation | IF07 |
| E15 | French `1,0 mL/min` retains its lexeme and normalizes to `1.0` in the same unit | IF09 |
| E16 | Expected projection-validation failure before any core call | IF11 |

E05/E13 now have ordinary caller text; their forced unresolved classification
lives in `test_conditions`, with a test-only application origin, not a phrase
the interpreter should recognize. E12 similarly declares its preclassified
fragment boundary. E11/E16 declare external fault injection outside caller text;
the same input as E04 does not secretly trigger a different route by example ID.
Test conditions exist only in the design-example definition, not caller input.
E01 is not a
measured S/F comparison. GR01 fixtures (E01/E07/E08/E09/E14/E15), including the corrected E08 origin, are human-validated with reservations. GR02 fixtures (E02/E03/E06/E10), including the added E03 washing-stage origin, are also human-validated with reservations. GR03 fixtures (E04/E05/E12/E13) are human-validated with reservations, distinguishing caller-input E04 from the three preclassified-ledger bridge cases. GR04 fixtures E11/E16 and invalid inputs N01-N03 are also human-validated with reservations; fault injection remains external to caller input. N01-N03 reject blank input, extra source-approval
keys and undeclared language. Shape/semantic corruption checks are separate from
these interpretation examples and are not extra benchmark cases.

## Review completed and next steps

MC01-MC06 and GR01-GR04 are approved with their recorded clarifications and reservations. All 16 design examples and three invalid-input cases have actual human decisions. The historical per-example preparation markers remain unchanged; live approvals and content bindings are recorded separately.

E05/E12/E13 test a preclassified-ledger boundary, E11/E16 test external fault injection, and E04 starts from caller input. These distinctions must be preserved in implementation and reporting. No design expectation is an observed interpreter or core result.

Next: consolidate the reviewed design package before separately requested implementation. Prior P/G text/form equivalence reviews and the future prospective dataset remain pending. No runtime code, existing schema, source policy or frozen S artifact is changed; E118-I/E121-EQ remain excluded.
