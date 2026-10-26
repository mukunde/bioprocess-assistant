# Deterministic EN/FR interpreter and structured bridge v01

Implementation candidate, not frozen or prospectively evaluated. The separate
[GR01-GR04 package](../experiments/free-text-group-review-package-v01.md) records
the approved design and remains unchanged. Its schemas and expected records are
historical preparation artifacts, not measured runtime results. This document
describes the new local implementation; no chat path is activated.

## Use and data flow

```python
from ingestion.free_text_bridge import FreeTextControl, record_sizes

control = FreeTextControl()
result = control.evaluate({
    "language": "fr",
    "text": "A utilise HiTrap Blue HP 1 mL. Donne le débit de lavage.",
})
print(result["request_summary"])
print(record_sizes(result))
```

The caller supplies exactly `language` (`en` or `fr`) and verbatim `text`. An
application UUID and component identities are assigned outside user input.
The interpreter returns a new ledger with exact original UTF-8 hash, code-point
origins, assertions, unresolved fragments and the complete recognizable-unit
inventory. The bridge validates it, constructs and validates a structured
submission, then calls the unchanged `StructuredControl.evaluate` at most once.
Empty or invalid projections do not call the engine. No model, database, browser,
embedding service or network client is used.

The returned object follows the existing runtime-outcome schema. The exact core
result is retained without editing its flags or context; its canonical hash and
per-unit mapping distinguish planner coverage from whole-request service.
`projection_bytes(result)` reconstructs the canonical submitted UTF-8 JSON bytes
whose hash is `projection.sha256_canonical`. `record_sizes` reports ledger,
projection and complete-record byte sizes separately; those are not token
estimates. Actual stage timings are milliseconds; null marks an unexecuted stage.
The engine retains its one shared six-root/2,048-token context budget.

## Declared language perimeter

This is an explicit bounded grammar, not a general natural-language model.

| Construction | Examples / behavior |
|---|---|
| Named preparations | `A: ...`, `For A on ...`, `Pour A sur ...`, `A utilise ...`, `A is named ...`, `A est nommé ...`; single-letter scope names |
| Product identity | Complete catalog-exact labels; unknown explicit labels pass literally to the common catalog for diagnosis, never repaired by substring or fuzzy matching |
| Positive selectors | `flow` / `débit`, `stopping criteria` / `critères de fin`, buffer `formulations` / `composition`, column volumes, maximum pressure, general `principle` / `principe` |
| Explicit phase | washing/lavage, loading/chargement, elution/élution, equilibration/équilibrage; binding/fixation formulation becomes buffer preparation, not operating elution |
| Scope | Single named current preparation; explicit `for both` / `pour les deux` expands to both known scopes; otherwise several candidates remain unresolved |
| Observations | `My observed flow is 1.0 mL/min`, `Le débit observé est de 1,0 mL/min`, `contient 5 mL disponibles`, `loaded volume is unknown` / `volume chargé est inconnu` |
| Scenario fact | Minor contaminants interfere/do not interfere **with the intended application**, including the declared French equivalent; supplied false remains false |
| Exclusions | `Exclude ...`, `Do not include ...`, `exclus ...`; `Do not exclude` / `N’exclus pas` retain a negated ban; `Do not give` is a ban, not a positive request |
| Policy conflicts | Source-approval directives are rejected; requests to omit mandatory warnings are preblocked; independent scopes may proceed |

Matching uses an accent-insensitive casefolded view with an index map to the
original Unicode code points, including decomposed accents and supplementary
characters. Decimal punctuation normalizes only within the supplied unit. Zero,
false, missing and explicitly unknown states remain distinct. A qualified product
name does not fill a separate column field. No volume, duration or unit conversion
is inferred. General method principles do not require invented product context.

Unrecognized substantive words, qualifiers, additional requests or unsupported
coordinations remain as unresolved fragments. They prevent full-inventory claims;
when their independence is not established, known dependent units are preblocked.
The runtime does not assume the independence supplied by the preclassified E12
test. No nearest-preparation choice, phase transfer between scopes or last-wins
context repair is permitted. Multiple incompatible values in a single slot are
preserved as assertions and blocked when the existing form cannot represent both.
The reviewed product-label-versus-column conflict is representable and reaches
the common engine unchanged.

Intake limits remain the MC04 values: 16,000 original code points, 16 tasks,
64 known units, 256 ordinary-array entries and 4,096 origins/field links. Over-limit
input is rejected without truncation. Root schemas, catalogs, source policy and
historical experiments are unchanged. E118-I/E121-EQ remain excluded.

## Validation and test boundaries

The registry resolves all four schemas offline. Cross-record checks verify IDs,
references, assertion literals, supplied-context assertions, input/origin hashes,
offsets, blocking scope, projection pointers, unit ownership and accounting.
Every generated projection leaf has provenance. Defaults and absence are labelled
as application metadata or field-specific not-stated origins, not user assertions.
These mechanical checks do not establish scientific suitability or universal
semantic entailment.

`evaluate_ledger` is an internal boundary for already-classified ledgers; it is
not a caller-envelope option. Tests E05/E12/E13 explicitly supply their reviewed
preclassification and current component identities. Their original records are
never edited. E11/E16 use test-side injected failures, not text triggers or example
IDs. Invalid projection candidates and their hashes/errors remain in a rejection
audit; there is no silent repair or retry. Errors preserve earlier preblocking.

Run in the application verification environment:

```powershell
python -m unittest tests.test_free_text_interface -v
python -m unittest tests.test_free_text_review_regressions -v
python -m unittest tests -v
```

The first command covers IF01-IF14 plus lexical, scope, Unicode, unknown-fragment,
immutability and input-validation regressions. IF12 compares real core context,
ordered units/bindings and source semantics after one ID bijection; generated
annotation reason prose is excluded from meaning comparison. It does not replace
the still-pending P/G text/form equivalence review or the prospective paired set.
All model/database calls in the maintained suite are mocked; only local socket
tests need loopback access. The offline verification launcher blocks external
connections and disables telemetry.

Next: implementation review, then a separately requested freeze and a new human-
reviewed prospective S/F dataset. Conformance checks are development tests, not
held-out accuracy, generated-answer quality or permission to activate the chatbot.

## Historical first-implementation verification

The [implementation checks](free-text-runtime-v01-checks.json) record 33 new
conformance/regression tests within a complete **589/589** passing suite, no skips
and no external connection attempts. Loopback operations are for existing socket
tests. The 16 old local notes remain byte-identical and untracked. All previously
tracked files, including the core, schemas, approved examples, decisions and frozen
results, are unchanged. This is verification in the existing local environment,
not fresh-install certification or prospective evaluation.

## Corrected candidate and review

The [v02 implementation review](FREE-TEXT-RUNTIME-REVIEW-V02.md) and
[v02 verification report](free-text-runtime-v02-checks.json) supersede the initial
candidate's current-status claims. The original v01 report is retained as a
historical run record; its component hashes describe that earlier source snapshot.

The corrected parser separates positive requests from restrictions in the same
sentence while retaining original offsets and the positive-unit denominator.
Restrictions preserve their information selectors and known owner. Phase-only
coordinations become separate typed exclusions on that same owner; ambiguous
phase/selector pairings block dependent units without blocking unrelated scopes.
Explicit `for A` / `pour A` associations bind individual selectors, including
`flow for A and stopping criteria for B`. A bare trailing `and B` is outside this
declared grammar and prevents a complete-inventory claim; it is never silently
ignored or interpreted as a second positive request.

An explicitly unknown column stays `unknown` with a real citation, never a
not-stated origin. The unchanged core remains responsible for interpretation of
qualified product labels and explicit column fields; this layer does not change
its format-resolution policy.

Cross-record validation now checks unit selector/phase against literal assertions,
facts against their scoped assertions, product identity and normalized quantities
against their literal lexemes, and projection context, ordered tasks/items,
stages/selectors and active exclusions against the ledger. Shared mutable values
are copied when assertions are created. Projection mismatch is rejected before
engine invocation, with the unsubmitted candidate retained for audit. These
deterministic checks do not claim general natural-language entailment.
