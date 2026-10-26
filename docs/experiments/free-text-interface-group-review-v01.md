# Free-text machine fixtures: grouped review v01

Date: 26 October 2026. **All four groups GR01-GR04 validated with reservations.** MC01-MC06 and
their clarifications were approved collectively. The separate GR01-GR04 decisions below now approve the refined exact origins, test conditions and expected records with reservations.
See the [actual decision](../decisions/2026-10-26-free-text-machine-design-review.json)
and [machine guide](../technical/FREE-TEXT-MACHINE-DESIGN-V01.md).

All cards are design expectations, not measured F results. No parser, bridge
or planner has executed them. Canonical records and full pointer annotations
are in the [revision-4 examples](free-text-interface-examples-v01.json).
Previous drafts/checks are preserved; the original S trial remains unchanged.

## How to review

Confirm ownership, requested information, uncertainty, projection/preblocking
and whole-request accounting. Inspect exact quotes and half-open Unicode
code-point offsets. Mechanical pointer/substring validity does not approve
semantic entailment. No actual approval is inferred from static checks.

The full-input origin remains a snapshot anchor only. Substantive associations
use focused spans or field-specific absence/application reasons. Declared
language points to caller /language, not an invented word in the prose.

| Group | Examples | Main decision |
|---|---|---|
| GR01 | E01, E07, E08, E09, E14, E15 | Meaning, polarity, origins, defaults, quantities |
| GR02 | E02, E03, E06, E10 | Conflict/ambiguity and blocking scope |
| GR03 | E04, E05, E12, E13 | Partial service and bridge-only fixture boundaries |
| GR04 | E11, E16, N01-N03 | External faults, rejection audit and no retry |

## GR01 — Representable inputs, polarity and numeric roles

**Decision:** validated with reservations, including the E08 origin correction.

**Actual human message (French, verbatim):**

> Je valide GR01 avec les réserves indiquées et l’extension de l’origine E08 à [27, 92). Enregistre ma décision et passons à GR02. Aucun LLM, API payante, commit ni push.

See the [GR01 decision and content bindings](../decisions/2026-10-26-free-text-GR01-review.json). Approval concerns these design expectations, not executed interpretation, scientific suitability or IF implementation results.

Per-example pending markers remain historical preparation fields; actual group progress is recorded separately.

### E01 — IF01, IF12

**Original caller text:**

> A: HiTrap Blue HP 1 mL. Give washing flow and binding-buffer formulations.

**Language:** en. **Test entry:** `caller_input`.

Nominal design fixture only; no execution performed and no example-ID routing permitted.

| Unit | Owner / candidates | Expected handling |
|---|---|---|
| u1 / flow_rate | A | projected; core outcome not executed |
| u2 / buffer_formulation | A | projected; core outcome not executed |

**Accounting:** 2 known units; 2 intended core outcomes; 0 preblocked; 0 expected errors. Inventory complete: `true`. Full-service expectation: `true`. Expected core attempts: 1.

These are expected fixture values, not actual invocation counts or successful generated answers.

| Focused origin | Unicode interval | Exact passage |
|---|---|---|
| o-scope-A | [0, 23) | A: HiTrap Blue HP 1 mL. |
| o-product-A | [3, 22) | HiTrap Blue HP 1 mL |
| o-unit-u1 | [29, 41) | washing flow |
| o-unit-u2 | [46, 73) | binding-buffer formulations |

**Field/default review:** full `field_origins` mappings name each target. Absence reasons state the field and checked scope; matrix/default metadata is not a user fact.

### E07 — IF07

**Original caller text:**

> A utilise HiTrap Blue HP 1 mL. Donne le débit de lavage. N’exclus pas le débit de lavage ; exclus uniquement l’élution opératoire.

**Language:** fr. **Test entry:** `caller_input`.

Nominal design fixture only; no execution performed and no example-ID routing permitted.

| Unit | Owner / candidates | Expected handling |
|---|---|---|
| u1 / flow_rate | A | projected; core outcome not executed |

**Accounting:** 1 known units; 1 intended core outcomes; 0 preblocked; 0 expected errors. Inventory complete: `true`. Full-service expectation: `true`. Expected core attempts: 1.

These are expected fixture values, not actual invocation counts or successful generated answers.

| Focused origin | Unicode interval | Exact passage |
|---|---|---|
| o-scope-A | [0, 30) | A utilise HiTrap Blue HP 1 mL. |
| o-product-A | [10, 29) | HiTrap Blue HP 1 mL |
| o-unit-u1 | [31, 55) | Donne le débit de lavage |
| o-exclusion-A-no-elution | [91, 129) | exclus uniquement l’élution opératoire |
| o-exclusion-A-not-ban-wash | [57, 88) | N’exclus pas le débit de lavage |

**Field/default review:** full `field_origins` mappings name each target. Absence reasons state the field and checked scope; matrix/default metadata is not a user fact.

### E08 — IF08

**Original caller text:**

> In documentary scenario A, minor contaminants do not interfere with the intended application. Explain the general separation principle of SEC; do not choose a purification technique for this sample.

**Language:** en. **Test entry:** `caller_input`.

Nominal design fixture only; no execution performed and no example-ID routing permitted.

| Unit | Owner / candidates | Expected handling |
|---|---|---|
| u1 / principle | A | projected; core outcome not executed |

**Accounting:** 1 known units; 1 intended core outcomes; 0 preblocked; 0 expected errors. Inventory complete: `true`. Full-service expectation: `true`. Expected core attempts: 1.

These are expected fixture values, not actual invocation counts or successful generated answers.

| Focused origin | Unicode interval | Exact passage |
|---|---|---|
| o-scope-A | [0, 25) | In documentary scenario A |
| o-fact-A-minor_contaminants_interfere | [27, 92) | minor contaminants do not interfere with the intended application |
| o-fact-role-A-minor_contaminants_interfere | [0, 25) | In documentary scenario A |
| o-unit-u1 | [106, 141) | general separation principle of SEC |
| o-relation-0 | [143, 197) | do not choose a purification technique for this sample |

**Field/default review:** full `field_origins` mappings name each target. Absence reasons state the field and checked scope; matrix/default metadata is not a user fact.

### E09 — IF08, IF09

**Original caller text:**

> A: HiTrap Blue HP 1 mL. L’échantillon étiqueté 🧪 contient 5 mL disponibles ; le volume chargé est inconnu. Donne les critères de fin du lavage.

**Language:** fr. **Test entry:** `caller_input`.

Nominal design fixture only; no execution performed and no example-ID routing permitted.

| Unit | Owner / candidates | Expected handling |
|---|---|---|
| u1 / stopping_criteria | A | projected; core outcome not executed |

**Accounting:** 1 known units; 1 intended core outcomes; 0 preblocked; 0 expected errors. Inventory complete: `true`. Full-service expectation: `true`. Expected core attempts: 1.

These are expected fixture values, not actual invocation counts or successful generated answers.

| Focused origin | Unicode interval | Exact passage |
|---|---|---|
| o-scope-A | [0, 23) | A: HiTrap Blue HP 1 mL. |
| o-product-A | [3, 22) | HiTrap Blue HP 1 mL |
| o-fact-A-sample_volume | [59, 75) | 5 mL disponibles |
| o-fact-role-A-sample_volume | [24, 75) | L’échantillon étiqueté 🧪 contient 5 mL disponibles |
| o-fact-A-loaded_volume | [81, 106) | volume chargé est inconnu |
| o-fact-role-A-loaded_volume | [81, 106) | volume chargé est inconnu |
| o-unit-u1 | [108, 143) | Donne les critères de fin du lavage |
| o-geometry-0 | [38, 49) | étiqueté 🧪 |

**Field/default review:** full `field_origins` mappings name each target. Absence reasons state the field and checked scope; matrix/default metadata is not a user fact.

### E14 — IF07

**Original caller text:**

> For A on HiTrap Blue HP 1 mL, give not only the washing stopping criteria but also the binding-buffer formulations. Do not include operating elution.

**Language:** en. **Test entry:** `caller_input`.

Nominal design fixture only; no execution performed and no example-ID routing permitted.

| Unit | Owner / candidates | Expected handling |
|---|---|---|
| u1 / stopping_criteria | A | projected; core outcome not executed |
| u2 / buffer_formulation | A | projected; core outcome not executed |

**Accounting:** 2 known units; 2 intended core outcomes; 0 preblocked; 0 expected errors. Inventory complete: `true`. Full-service expectation: `true`. Expected core attempts: 1.

These are expected fixture values, not actual invocation counts or successful generated answers.

| Focused origin | Unicode interval | Exact passage |
|---|---|---|
| o-scope-A | [0, 28) | For A on HiTrap Blue HP 1 mL |
| o-product-A | [9, 28) | HiTrap Blue HP 1 mL |
| o-unit-u1 | [48, 73) | washing stopping criteria |
| o-unit-u2 | [87, 114) | binding-buffer formulations |
| o-exclusion-A-no-elution | [116, 148) | Do not include operating elution |
| o-relation-0 | [35, 114) | not only the washing stopping criteria but also the binding-buffer formulations |

**Field/default review:** full `field_origins` mappings name each target. Absence reasons state the field and checked scope; matrix/default metadata is not a user fact.

### E15 — IF09

**Original caller text:**

> A : HiTrap Blue HP 1 mL. Le débit observé est de 1,0 mL/min. Donne les critères de fin du lavage.

**Language:** fr. **Test entry:** `caller_input`.

Nominal design fixture only; no execution performed and no example-ID routing permitted.

| Unit | Owner / candidates | Expected handling |
|---|---|---|
| u1 / stopping_criteria | A | projected; core outcome not executed |

**Accounting:** 1 known units; 1 intended core outcomes; 0 preblocked; 0 expected errors. Inventory complete: `true`. Full-service expectation: `true`. Expected core attempts: 1.

These are expected fixture values, not actual invocation counts or successful generated answers.

| Focused origin | Unicode interval | Exact passage |
|---|---|---|
| o-scope-A | [0, 24) | A : HiTrap Blue HP 1 mL. |
| o-product-A | [4, 23) | HiTrap Blue HP 1 mL |
| o-fact-A-observed_flow | [49, 59) | 1,0 mL/min |
| o-fact-role-A-observed_flow | [25, 59) | Le débit observé est de 1,0 mL/min |
| o-unit-u1 | [61, 96) | Donne les critères de fin du lavage |

**Field/default review:** full `field_origins` mappings name each target. Absence reasons state the field and checked scope; matrix/default metadata is not a user fact.

## GR02 — Conflicts, unknown owners and ambiguous scope

**Decision:** validated with reservations, including the E03 washing-stage origin addition.

**Actual human message (French, verbatim):**

> Je valide GR02 avec les réserves indiquées et l’ajout de l’origine « Pour le lavage » à [64, 78) pour E03. Enregistre ma décision et passons à GR03. Aucun LLM, API payante, commit ni push.

See the [GR02 decision and content bindings](../decisions/2026-10-26-free-text-GR02-review.json). Approval concerns design expectations only. Historical per-example preparation markers are retained.

### E02 — IF02

**Original caller text:**

> A is named HiTrap Blue HP 5 mL, but its column field says 1 mL. Give washing stopping criteria.

**Language:** en. **Test entry:** `caller_input`.

Nominal design fixture only; no execution performed and no example-ID routing permitted.

| Unit | Owner / candidates | Expected handling |
|---|---|---|
| u1 / stopping_criteria | A | projected; core outcome not executed |

**Accounting:** 1 known units; 1 intended core outcomes; 0 preblocked; 0 expected errors. Inventory complete: `true`. Full-service expectation: `false`. Expected core attempts: 1.

These are expected fixture values, not actual invocation counts or successful generated answers.

| Focused origin | Unicode interval | Exact passage |
|---|---|---|
| o-scope-A | [0, 63) | A is named HiTrap Blue HP 5 mL, but its column field says 1 mL. |
| o-product-A | [11, 30) | HiTrap Blue HP 5 mL |
| o-column-A | [40, 62) | column field says 1 mL |
| o-unit-u1 | [69, 94) | washing stopping criteria |

**Field/default review:** full `field_origins` mappings name each target. Absence reasons state the field and checked scope; matrix/default metadata is not a user fact.

**Conflict limit:** preserve both size assertions and delegate the representable conflict to the unchanged core.

### E03 — IF03

**Original caller text:**

> A utilise HiTrap Blue HP 1 mL et B utilise HiTrap Blue HP 5 mL. Pour le lavage, je parle de l’une de ces deux préparations sans préciser si c’est A ou B. Quel débit s’applique à cette préparation ? Indépendamment, C demande le principe général de la SEC.

**Language:** fr. **Test entry:** `caller_input`.

Nominal design fixture only; no execution performed and no example-ID routing permitted.

| Unit | Owner / candidates | Expected handling |
|---|---|---|
| u-wash / flow_rate | unresolved: A, B | preblocked |
| u1 / principle | C | projected; core outcome not executed |

**Accounting:** 2 known units; 1 intended core outcomes; 1 preblocked; 0 expected errors. Inventory complete: `true`. Full-service expectation: `false`. Expected core attempts: 1.

These are expected fixture values, not actual invocation counts or successful generated answers.

| Focused origin | Unicode interval | Exact passage |
|---|---|---|
| o-scope-A | [0, 29) | A utilise HiTrap Blue HP 1 mL |
| o-product-A | [10, 29) | HiTrap Blue HP 1 mL |
| o-scope-B | [33, 62) | B utilise HiTrap Blue HP 5 mL |
| o-product-B | [43, 62) | HiTrap Blue HP 5 mL |
| o-scope-C | [214, 253) | C demande le principe général de la SEC |
| o-stage-u-wash | [64, 78) | Pour le lavage |
| o-unit-u-wash | [154, 195) | Quel débit s’applique à cette préparation |
| o-unit-u1 | [227, 253) | principe général de la SEC |
| o-issue-i1 | [80, 152) | je parle de l’une de ces deux préparations sans préciser si c’est A ou B |

**Field/default review:** full `field_origins` mappings name each target. Absence reasons state the field and checked scope; matrix/default metadata is not a user fact.

**Issues to preserve:**

- i1 / `unresolved_owner`: The input explicitly leaves A/B ownership unresolved.

**Comparison limit:** keep this semantic-only until faithful equivalent ownership can be represented in both S/F arms.

### E06 — IF06

**Original caller text:**

> Je ne précise pas la préparation. Quel débit de lavage ?

**Language:** fr. **Test entry:** `caller_input`.

Nominal design fixture only; no execution performed and no example-ID routing permitted.

| Unit | Owner / candidates | Expected handling |
|---|---|---|
| u-wash / flow_rate | unresolved: no declared candidates | preblocked |

**Accounting:** 1 known units; 0 intended core outcomes; 1 preblocked; 0 expected errors. Inventory complete: `true`. Full-service expectation: `false`. Expected core attempts: 0.

These are expected fixture values, not actual invocation counts or successful generated answers.

| Focused origin | Unicode interval | Exact passage |
|---|---|---|
| o-unit-u-wash | [34, 54) | Quel débit de lavage |
| o-issue-i1 | [0, 32) | Je ne précise pas la préparation |

**Field/default review:** full `field_origins` mappings name each target. Absence reasons state the field and checked scope; matrix/default metadata is not a user fact.

**Issues to preserve:**

- i1 / `unresolved_owner`: No stable positive product/task scope can be assigned.

### E10 — IF10

**Original caller text:**

> A and B are separate HiTrap Blue HP 1 mL preparations. Give washing flow for both. Exclude that flow, but I have not specified whether this exclusion concerns A or B.

**Language:** en. **Test entry:** `caller_input`.

Nominal design fixture only; no execution performed and no example-ID routing permitted.

| Unit | Owner / candidates | Expected handling |
|---|---|---|
| u1 / flow_rate | A | preblocked |
| u2 / flow_rate | B | preblocked |

**Accounting:** 2 known units; 0 intended core outcomes; 2 preblocked; 0 expected errors. Inventory complete: `true`. Full-service expectation: `false`. Expected core attempts: 0.

These are expected fixture values, not actual invocation counts or successful generated answers.

| Focused origin | Unicode interval | Exact passage |
|---|---|---|
| o-scope-A | [0, 54) | A and B are separate HiTrap Blue HP 1 mL preparations. |
| o-product-A | [21, 40) | HiTrap Blue HP 1 mL |
| o-scope-B | [0, 54) | A and B are separate HiTrap Blue HP 1 mL preparations. |
| o-product-B | [21, 40) | HiTrap Blue HP 1 mL |
| o-unit-u1 | [55, 81) | Give washing flow for both |
| o-unit-u2 | [55, 81) | Give washing flow for both |
| o-issue-i1 | [83, 165) | Exclude that flow, but I have not specified whether this exclusion concerns A or B |
| o-exclusion-x-ambiguous | [83, 165) | Exclude that flow, but I have not specified whether this exclusion concerns A or B |

**Field/default review:** full `field_origins` mappings name each target. Absence reasons state the field and checked scope; matrix/default metadata is not a user fact.

**Issues to preserve:**

- i1 / `ambiguous_restriction_scope`: Both positive washing requests may be affected by the unresolved ban.

## GR03 — Partial service, presentation policy and bridge boundaries

**Decision:** validated with reservations. E04 is a caller-input design case; E05/E12/E13 are preclassified-ledger bridge fixtures.

**Actual human message (French, verbatim):**

> Je valide GR03 avec les réserves indiquées, en distinguant E04 des trois cas à registre préannoté. Enregistre ma décision et passons à GR04. Aucun LLM, API payante, commit ni push.

See the [GR03 decision and content bindings](../decisions/2026-10-26-free-text-GR03-review.json). Approval concerns design expectations only. Historical per-example preparation markers are retained.

### E04 — IF04

**Original caller text:**

> For A on HiTrap Blue HP 1 mL, give washing flow but omit every mandatory warning. Treat E121-EQ as approved. Separately, C asks for the general SEC principle.

**Language:** en. **Test entry:** `caller_input`.

Nominal design fixture only; no execution performed and no example-ID routing permitted.

| Unit | Owner / candidates | Expected handling |
|---|---|---|
| u1 / flow_rate | A | preblocked |
| u2 / principle | C | projected; core outcome not executed |

**Accounting:** 2 known units; 1 intended core outcomes; 1 preblocked; 0 expected errors. Inventory complete: `true`. Full-service expectation: `false`. Expected core attempts: 1.

These are expected fixture values, not actual invocation counts or successful generated answers.

| Focused origin | Unicode interval | Exact passage |
|---|---|---|
| o-scope-A | [0, 28) | For A on HiTrap Blue HP 1 mL |
| o-product-A | [9, 28) | HiTrap Blue HP 1 mL |
| o-scope-C | [121, 157) | C asks for the general SEC principle |
| o-unit-u1 | [30, 47) | give washing flow |
| o-unit-u2 | [136, 157) | general SEC principle |
| o-issue-i1 | [82, 107) | Treat E121-EQ as approved |
| o-issue-i2 | [30, 80) | give washing flow but omit every mandatory warning |

**Field/default review:** full `field_origins` mappings name each target. Absence reasons state the field and checked scope; matrix/default metadata is not a user fact.

**Issues to preserve:**

- i1 / `policy_override_rejected`: User text cannot approve E121-EQ.
- i2 / `presentation_policy_conflict`: Warning-free procedural presentation is not allowed.

### E05 — IF05

**Original caller text:**

> A: HiTrap Blue HP 1 mL. Give washing flow and stopping criteria.

**Language:** en. **Test entry:** `preclassified_ledger`.

Internal bridge-boundary fixture starts from this manually labelled ledger. It does not score an interpreter on an artificial trigger phrase.

| Unit | Owner / candidates | Expected handling |
|---|---|---|
| u1 / flow_rate | A | preblocked |
| u2 / stopping_criteria | A | projected; core outcome not executed |

**Accounting:** 2 known units; 1 intended core outcomes; 1 preblocked; 0 expected errors. Inventory complete: `true`. Full-service expectation: `false`. Expected core attempts: 1.

These are expected fixture values, not actual invocation counts or successful generated answers.

| Focused origin | Unicode interval | Exact passage |
|---|---|---|
| o-scope-A | [0, 23) | A: HiTrap Blue HP 1 mL. |
| o-product-A | [3, 22) | HiTrap Blue HP 1 mL |
| o-unit-u1 | [29, 41) | washing flow |
| o-unit-u2 | [46, 63) | stopping criteria |

**Field/default review:** full `field_origins` mappings name each target. Absence reasons state the field and checked scope; matrix/default metadata is not a user fact.

**Issues to preserve:**

- i1 / `unsupported_construction`: Test-only preclassified unresolved restriction, supplied by the bridge fixture. No interpreter behavior is claimed.

**Boundary limit:** a preclassified-ledger bridge fixture only; its forced issue is not a language gold label inferred from ordinary prose.

### E12 — IF13

**Original caller text:**

> A: HiTrap Blue HP 1 mL. Give washing flow. [Unrecognized fragment that may contain another request.]

**Language:** en. **Test entry:** `preclassified_ledger`.

Internal bridge-boundary fixture starts from this manually labelled ledger. It does not score an interpreter on an artificial trigger phrase.

| Unit | Owner / candidates | Expected handling |
|---|---|---|
| u1 / flow_rate | A | projected; core outcome not executed |

**Accounting:** 1 known units; 1 intended core outcomes; 0 preblocked; 0 expected errors. Inventory complete: `false`. Full-service expectation: `false`. Expected core attempts: 1.

These are expected fixture values, not actual invocation counts or successful generated answers.

| Focused origin | Unicode interval | Exact passage |
|---|---|---|
| o-scope-A | [0, 23) | A: HiTrap Blue HP 1 mL. |
| o-product-A | [3, 22) | HiTrap Blue HP 1 mL |
| o-unit-u1 | [24, 41) | Give washing flow |
| o-issue-i1 | [43, 100) | [Unrecognized fragment that may contain another request.] |
| o-fragment-f1 | [43, 100) | [Unrecognized fragment that may contain another request.] |

**Field/default review:** full `field_origins` mappings name each target. Absence reasons state the field and checked scope; matrix/default metadata is not a user fact.

**Issues to preserve:**

- i1 / `incomplete_inventory`: The unknown fragment may contain another request; full accounting cannot be claimed.

**Boundary limit:** the unknown fragment is preclassified setup, not an artificial phrase the interpreter must recognize. It prevents a full-inventory claim.

### E13 — IF14

**Original caller text:**

> A: HiTrap Blue HP 1 mL. My observed flow is 1 mL/min. Give loading flow and washing stopping criteria. Exclude only loading flow.

**Language:** en. **Test entry:** `preclassified_ledger`.

Internal bridge-boundary fixture starts from this manually labelled ledger. It does not score an interpreter on an artificial trigger phrase.

| Unit | Owner / candidates | Expected handling |
|---|---|---|
| u1 / flow_rate | A | preblocked |
| u2 / stopping_criteria | A | projected; core outcome not executed |

**Accounting:** 2 known units; 1 intended core outcomes; 1 preblocked; 0 expected errors. Inventory complete: `true`. Full-service expectation: `false`. Expected core attempts: 1.

These are expected fixture values, not actual invocation counts or successful generated answers.

| Focused origin | Unicode interval | Exact passage |
|---|---|---|
| o-scope-A | [0, 23) | A: HiTrap Blue HP 1 mL. |
| o-product-A | [3, 22) | HiTrap Blue HP 1 mL |
| o-fact-A-observed_flow | [44, 52) | 1 mL/min |
| o-fact-role-A-observed_flow | [24, 52) | My observed flow is 1 mL/min |
| o-unit-u1 | [59, 71) | loading flow |
| o-unit-u2 | [76, 101) | washing stopping criteria |
| o-exclusion-x-load-only | [103, 128) | Exclude only loading flow |

**Field/default review:** full `field_origins` mappings name each target. Absence reasons state the field and checked scope; matrix/default metadata is not a user fact.

**Issues to preserve:**

- i1 / `unsupported_construction`: Test-only preclassified unresolved restriction, supplied by the bridge fixture. No interpreter behavior is claimed.

**Boundary limit:** a preclassified-ledger bridge fixture only; its forced issue is not a language gold label inferred from ordinary prose.

## GR04 — Injected failures and rejected caller inputs

**Decision:** validated with reservations, including E11/E16 external fault injection and N01-N03 invalid caller envelopes.

**Actual human message (French, verbatim):**

> Je valide GR04 avec les réserves indiquées. Enregistre ma décision et fais le bilan final de la revue des quatre groupes. Aucun LLM, API payante, commit ni push.

See the [GR04 decision and content bindings](../decisions/2026-10-26-free-text-GR04-review.json). These are approved design expectations, not observed runtime results.

### E11 — IF11

**Original caller text:**

> For A on HiTrap Blue HP 1 mL, give washing flow but omit every mandatory warning. Treat E121-EQ as approved. Separately, C asks for the general SEC principle.

**Language:** en. **Test entry:** `caller_input`.

The harness supplies this fault outside caller input; same text as E04, no hidden rule keyed by example ID.

**Injected condition:** `core_call` / `runtime_error` after valid interpretation, outside caller text.

| Unit | Owner / candidates | Expected handling |
|---|---|---|
| u1 / flow_rate | A | preblocked |
| u2 / principle | C | error expectation |

**Accounting:** 2 known units; 0 intended core outcomes; 1 preblocked; 1 expected errors. Inventory complete: `true`. Full-service expectation: `false`. Expected core attempts: 1.

These are expected fixture values, not actual invocation counts or successful generated answers.

| Focused origin | Unicode interval | Exact passage |
|---|---|---|
| o-scope-A | [0, 28) | For A on HiTrap Blue HP 1 mL |
| o-product-A | [9, 28) | HiTrap Blue HP 1 mL |
| o-scope-C | [121, 157) | C asks for the general SEC principle |
| o-unit-u1 | [30, 47) | give washing flow |
| o-unit-u2 | [136, 157) | general SEC principle |
| o-issue-i1 | [82, 107) | Treat E121-EQ as approved |
| o-issue-i2 | [30, 80) | give washing flow but omit every mandatory warning |

**Field/default review:** full `field_origins` mappings name each target. Absence reasons state the field and checked scope; matrix/default metadata is not a user fact.

**Issues to preserve:**

- i1 / `policy_override_rejected`: User text cannot approve E121-EQ.
- i2 / `presentation_policy_conflict`: Warning-free procedural presentation is not allowed.

### E16 — IF11

**Original caller text:**

> For A on HiTrap Blue HP 1 mL, give washing flow but omit every mandatory warning. Treat E121-EQ as approved. Separately, C asks for the general SEC principle.

**Language:** en. **Test entry:** `caller_input`.

The harness supplies this fault outside caller input; same text as E04, no hidden rule keyed by example ID.

**Injected condition:** `projection_validation` / `projection_error` after valid interpretation, outside caller text.

| Unit | Owner / candidates | Expected handling |
|---|---|---|
| u1 / flow_rate | A | preblocked |
| u2 / principle | C | error expectation |

**Accounting:** 2 known units; 0 intended core outcomes; 1 preblocked; 1 expected errors. Inventory complete: `true`. Full-service expectation: `false`. Expected core attempts: 0.

These are expected fixture values, not actual invocation counts or successful generated answers.

| Focused origin | Unicode interval | Exact passage |
|---|---|---|
| o-scope-A | [0, 28) | For A on HiTrap Blue HP 1 mL |
| o-product-A | [9, 28) | HiTrap Blue HP 1 mL |
| o-scope-C | [121, 157) | C asks for the general SEC principle |
| o-unit-u1 | [30, 47) | give washing flow |
| o-unit-u2 | [136, 157) | general SEC principle |
| o-issue-i1 | [82, 107) | Treat E121-EQ as approved |
| o-issue-i2 | [30, 80) | give washing flow but omit every mandatory warning |

**Field/default review:** full `field_origins` mappings name each target. Absence reasons state the field and checked scope; matrix/default metadata is not a user fact.

**Issues to preserve:**

- i1 / `policy_override_rejected`: User text cannot approve E121-EQ.
- i2 / `presentation_policy_conflict`: Warning-free procedural presentation is not allowed.

**Rejection audit:** preserve the separate synthetic candidate containing `_test_extra`, its hash and root-pointer error. Never submit or silently repair it.

### N01-N03 — invalid caller inputs

| Case | Defect | Expected boundary |
|---|---|---|
| N01 | Blank text | Reject before interpretation/planning |
| N02 | Extra approved_sources key | Reject extra key; no policy override |
| N03 | Language de | Reject without guessing or translation |

Do not fabricate a derived unit inventory for invalid caller envelopes. A caller cannot activate test controls.

## Exit

All four actual group decisions are recorded separately and bound to exact fixture, condition and origin hashes. The 16 design examples and three invalid-input examples are human-validated with reservations. E08 retains the complete application condition at [27,92); E03 has explicit washing-stage provenance at [64,78).

Caller-input cases, preclassified-ledger bridge fixtures (E05/E12/E13), and external fault-injection cases (E11/E16) remain distinct. Per-example pending markers are historical preparation fields, not the live approval status. Prior drafts and static reports remain preserved.

Next: consolidate the reviewed design package, then implement only on separate instruction. Prior P/G text/form equivalence reviews and a prospective evaluation dataset remain pending. No interpreter, bridge, candidate freeze or comparison has been executed; E118-I/E121-EQ remain excluded.
