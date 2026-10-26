# Structured-control review corrections

Date: 26 October 2026. Status: local pre-freeze corrections and implementation
clarification; no prospective evaluation, new source approval or method freeze.

This supplements the [approved technical specification](TASK-REQUEST-TECHNICAL-SPEC-V01.md)
and [implementation guide](STRUCTURED-CONTROL-V01.md). It preserves their design
approval record and historical check results. The correction request authorizes
the three review fixes, regression tests and clarification of format-qualified
exclusions. The detailed behavior below is an implementation clarification, not
an additional human source-review decision or an inferred scientific rule.

## Corrections and regression coverage

| Review finding | Corrected behavior | Added regression cases |
|---|---|---|
| CF12: a blocked first item changed task precedence | Build each task's admissible item list first, then interleave those lists in task order. Keep the resulting order for subsequent candidate rounds. | Blocked A1 with admissible A2/B1; one-binding-only synthetic budget; partially blocked item retaining its supported unit |
| CF08/CF11: an unmapped interpretation could report complete coverage | An `unsupported_selector` summary, documentary-support status or retained diagnostic prevents `all_supported_ready_units_covered=true`. | Unmapped joint product/technique context with a supported sibling; quarantine summary retaining an unsupported-selector diagnostic |
| CF04: incoherent exclusions were silently ignored | Validate a stage/information/facet restriction against registered roles and unavailable selectors before checking positive-item overlap. An invalid restriction blocks its declared task/item scope with an explicit diagnostic. | Nonintersecting preparation/flow restriction; mixed valid/invalid selector; item-local ownership; valid nonintersecting and quarantined-source restrictions |

The coverage flag still concerns eligible, ready units. It is not equivalent to
all requested information having an answer. Normal input clarification and bounded
source absence remain distinct from missing adapter mappings; `has_unserved_units`
and `all_requested_units_accounted_for` retain their separate meanings.

## Product exclusions with explicit column size

Resolve the negative label through the same exact catalog as positive labels.
Preserve its stated size and form-field origin in `canonical_request.resolved_fields`
under the exclusion's own input pointer. A negative resolution never becomes
positive product or column context.

| Exclusion | Requested product/column | Outcome |
|---|---|---|
| HiTrap Blue HP | Same product, any or unresolved size | Product-wide overlap for product-dependent items; clarify the inclusion/exclusion conflict |
| HiTrap Blue HP 5 mL | Same product, explicitly resolved 5 mL | Format-specific overlap; clarify the conflict |
| HiTrap Blue HP 5 mL | Same product, explicitly resolved 1 mL | No overlap; do not expand the exclusion to the whole product |
| HiTrap Blue HP 5 mL | Same product, unknown/not-supplied/not-applicable column | Restriction cannot be scoped; report `unresolved_binding`, without choosing 1 mL by elimination |
| HiTrap Blue HP 5 mL | Positive qualified 1 mL label, separate column unknown | The positive label explicitly supplies 1 mL; no overlap, original column state preserved |
| HiTrap Blue HP 5 mL | Positive label/column size conflict or invalid volume unit/domain | Do not select one conflicting value to decide overlap; retain the original problems and unresolved exclusion scope |
| HiTrap Blue HP 5 mL | Explicit positive 2 mL bed volume | The format is known but outside the supported lookup perimeter. Keep `out_of_scope`; do not misreport its size as unknown |
| Any product exclusion | Product-free general principle | Do not activate a product-specific procedure or block an unrelated general-topic lookup |

The alias must be an explicitly cataloged spelling. Do not parse an unlisted
product name or repair a typo to invent a qualifier. Compare declared mL values
numerically as decimals (for example 5 and 5.0 denote the same explicit volume),
without unit conversion or inference from sample/loaded volume.

The exclusion retains its declared task/item ownership. A size qualifier adds a
scope condition, not a new global ban. A missing size may therefore need
clarification to determine the permission scope even when the requested source
statement itself is shared across the two documented formats. Never infer the
remaining format from an exclusion.

## Checks and freeze boundary

The [targeted tests](../../tests/test_structured_request.py) cover these cases
without a model or network connection. Scarce-budget ordering regressions use an
explicitly synthetic internal counter; other integration checks retain the real
pinned local tokenizer. These are conformance fixtures, not new prospective
questions or measured scientific performance.

The original [v01 check record](structured-control-v01-checks.json) remains an
unchanged historical snapshot. The [revision-2 check record](structured-control-v02-checks.json)
is written separately with the revised code/test/document hashes. The corrected
implementation passed 50 targeted tests and 533 maintained-suite tests, with no
failures, errors, skips or external connection attempts in the guarded full-suite
run. Old trials, source records, approval
quotes, schema/catalog/adapter hashes and quarantines remain unchanged.

The three original reproductions now behave as specified: admissible A2 is
visited before B1 when A1 is blocked; an unsupported joint context cannot set
the coverage aggregate to true; and an incoherent preparation/flow exclusion
produces a diagnostic instead of being silently discarded. Format-qualified
exclusions preserve exact size and ownership without choosing an unspecified
column. No additional blocking finding was identified in this bounded re-review.

After the review, a method freeze must capture both the approved specification
and this clarification along with the implementation/dependency hashes. Passing
conformance does not itself freeze v06 or approve a prospective reference set.
