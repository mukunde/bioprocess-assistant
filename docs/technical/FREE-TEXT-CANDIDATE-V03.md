# Candidate v03: coverage, buffer occurrences and French phase attachment

## Status and entry points

This is an opt-in implementation following the approved CC01–CC06 coverage
contract. It is not frozen or a new prospective result. The default interface,
v01/v02 modules, method locks, reviews, references and historical run artifacts
are unchanged. The 16 older local notes are outside this work.

```python
from ingestion.free_text_bridge_v03 import FreeTextControlV03
from ingestion.structured_request_v03 import StructuredControlV03

text_control = FreeTextControlV03()
outcome = text_control.evaluate({
    "language": "fr",
    "text": "B : HiTrap Blue HP 1 mL. Donne le débit de lavage pour B.",
})
coverage = outcome["coverage_summary"]
legacy_payload = outcome["compatibility_outcome"]

# Pass an existing validated structured_submission to this entry point:
structured_control = StructuredControlV03()
# structured_outcome = structured_control.evaluate(submission)
```

The new [envelope schema](control-v03-outcome.schema.json) keeps the versioned
`coverage_summary` separate from `compatibility_outcome` (text) or
`compatibility_result` (structured). Consumers must unwrap the compatibility
payload before using helpers that expect the old outcome shape. Component
identities bind the v03 implementation and schema hashes. No old schema is
silently extended and old ledgers cannot be relabelled as v03 input.

## Coverage authority and meaning

The [approved semantic decisions](../decisions/2026-10-27-coverage-contract-CC-review.json)
and [machine encoding](COVERAGE-CONTRACT-V03-ENCODING.md) remain the design record.
Their pre-implementation wording is historical. This candidate implements the
specified `coverage-0.3-proposed` encoding; the version string is preserved rather
than inventing a subsequent human approval or stable release.

The structured core captures the eligible-ready set **before** context assembly,
in each returned audit record. A unit rejected by the context budget stays in
that denominator. The bridge maps this set back to its original requested-unit
identities. Unsupported, missing, quarantined, ambiguous and excluded positive
requests remain in the whole-request denominator. Directives do not create
additional positive requests.

Counting support requires exact source provenance, an admissible unit binding,
the full dependency/guard bundle, consistent roots and real serialized-context
token accounting. Hashing a forged binding again does not make it admissible.
Unvalidated global context counts as no support and yields an explicit error.
Known structured units receive explicit error outcomes when execution fails.

For FV06, the new meaning is:

- Eligible context: **1 covered / 1 eligible**, state `complete`.
- Whole request: **1 supported / 3 requested**, `full_service=false`.
- The retained legacy `all_supported_ready_units_covered=false` keeps its old
  semantics. Its historical evaluation failure is not rewritten.

The summary distinguishes `complete`, `partial`, `not_applicable`, `not_assessed`
and `error`, and complete-request versus known-subset scope. Unknown counts are
null; zero positive requests never imply full service or a 100% ratio. Exact key
accounting detects duplicate, missing and orphan outcomes even when counts match.
The standalone summarizer supports retaining reliable sibling evidence during a
unit-local error. The current planner boundary treats a raised planner exception
or global integrity failure conservatively as a failed assessment; it does not
introduce independent per-unit recovery or retries.

## Bounded interpretation corrections

| Defect | v03 correction |
|---|---|
| Binding and elution buffer formulations collapse into one item | Generated buffer item IDs include use and occurrence, for example `B-buffer_preparation-binding-1` and `B-buffer_preparation-elution-2`. Repeating the same use still keeps separate occurrences. |
| Buffer-use facet borrows another formulation's purpose | Resolve the use from the current formulation phrase and preserve its exact text origin. An ambiguous combined purpose remains unresolved. |
| French washing stopping criteria inherit loading | Prefer a phase explicitly inside the selector, such as `critères de fin du lavage`. |
| `débit d’élution` inherits preceding equilibration | Recognize the local French apostrophe connector and attach its own explicit phase. |
| General pressure inherits a preceding French flow's phase | Do not inherit a phase already owned by another selector. Unqualified pressure stays in `operating_limits`; explicitly phased pressure keeps that phase and may remain unsupported. |

Adjacent, bounded coordinated requests can still share an explicit phase. Buffer
purposes do not become operating phases. Unknown substantive clauses still
prevent a full-service claim. Original Unicode text and code-point offsets remain
the provenance basis, including decomposed accents and typographic apostrophes.

E118-I and E121-EQ stay excluded. The unchanged source adapter/catalog, scoped
exclusions, independent tasks, mandatory warnings, one-core-call rule and
six-root/2,048-token context limits remain in force. Runtime modules do not read
question sets, reviewed answers or expected outcomes.

## Validation and limits

The [coverage tests](../../tests/test_coverage_v03.py) execute the 12 design
boundaries, budget rejection, FV06, duplicate/orphan accounting, per-call audit
isolation, execution errors and forged context/binding/input checks. Some design
boundaries are isolated summarizer fixtures rather than operational fault
injection through every planner state; that distinction matters before a freeze.

The [interpreter tests](../../tests/test_free_text_v03.py) replay the existing
interface and prior review checks through v03, check all 24 FV language inputs as
development regressions, and cover distinct/repeated/ambiguous buffer purposes,
French phase ownership, general versus explicit pressure, Unicode origins,
incomplete inventory, empty positive inventory and source-integrity failure.

FV inputs and references were consulted during repair. Their reuse cannot
establish generalization or replace the frozen v02 score. A subsequent review,
fresh freeze and human-reviewed unseen questions are required for a prospective
comparison. Neither context coverage nor successful request handling certifies
scientific suitability or answer quality.

See the [implementation verification record](../experiments/free-text-v03-implementation-checks.json)
for suite results, preservation checks and component fingerprints. No model,
paid API, extraction or new frozen trial is used by this implementation task.
