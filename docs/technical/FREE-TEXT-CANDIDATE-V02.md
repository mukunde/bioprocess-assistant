# Free-text candidate v02: grammar, owner boundaries and pressure routing

## Status and entry point

This is an opt-in development candidate prepared after the FT01-FT12 frozen run.
It is not frozen, deployed or independently validated. The original interpreter,
bridge, method lock, questions, reviews, scores and raw run remain unchanged.
The existing public `FreeTextControl` still selects v01.

```python
from ingestion.free_text_bridge_v02 import FreeTextControlV02

control = FreeTextControlV02()
result = control.evaluate({
    "language": "en",
    "text": "B: HiTrap Blue HP 5 mL. Give washing flow and maximum pressure for B.",
})
```

The two executable modules are deliberate versioned snapshots rather than edits
to files pinned by the historical lock. The bridge uses v02's instruction splitting
for projection provenance as well as interpretation, including new commands after
restrictions. Shared contracts, structured engine, catalog and source policy are
unchanged. Component identities bind v02 source hashes and the baseline/shared
component identities; a v01 ledger cannot be silently accepted as v02 input.
There is no global monkeypatch, text rewrite or experiment/reference read in the
runtime. Original Unicode text and code-point offsets remain the provenance basis.

## Changes

| Defect | Bounded correction |
|---|---|
| Recognized intent still blocked by ordinary EN/FR wording | Accept `I need`, `il me faut`, `List`/`Liste`/`Listez`; cover exact manual-question wrappers, available-sample clauses, washing-volume wording, and relevant French apostrophe prefixes. Accept `séparément` as a connective. |
| Elution-buffer formulation mistaken for an extra operating phase | Consume a phase word as a buffer-use facet only inside an explicit elution-buffer noun phrase with a formulation request. A bare extra operating phase still makes the inventory incomplete. |
| `son` creates a task `S` | Require a complete single-letter owner token before a scope marker, for both scope detection and label extraction. Recognize the bounded possessive column phrase separately without creating a new owner. |
| Maximum pressure inherits the preceding flow's washing stage | Route unqualified maximum pressure to general `operating_limits`. Preserve a directly attached explicit operating phase rather than silently generalizing it; unsupported combinations remain unsupported. |

Unrecognized substantive text still prevents a complete inventory and may block
the request conservatively. This candidate does not guess that an unknown clause
is independent or discard it as a stop word. The independent siblings in reviewed
cases become dispatchable because their surrounding grammar is understood, not
because quarantine or ambiguity checks were relaxed.

E118-I and E121-EQ remain excluded. The existing six-root/2,048-token limits,
single-core-call rule, scoped exclusions, unknown/conflicting context behavior,
mandatory warnings and source/projection validation still apply.

## Regression coverage and interpretation

The [candidate tests](../../tests/test_free_text_v02.py) include:

- All 24 FT language inputs, now explicitly development material, checked against
  the reviewed intent, documentary unit states, complete source bundles and actual
  original context token accounting. All 24 pass after correction.
- The 33 existing interface checks and 14 prior implementation-review regressions,
  applied to the opt-in candidate as compatibility tests.
- Ten targeted tests (including the FT batch): bounded owner tokens, general versus
  explicitly phased pressure, unknown substantive clauses, independent siblings,
  distinct component identities, extra bare phases, decomposed Unicode offsets,
  and a new command after an active restriction in both languages.

The targeted module contains 57 tests. The complete suite passes 667 tests with
zero failures, errors or skips; its guarded launcher records zero external
connection attempts and 33 loopback operations. Restricted Windows execution
initially stalled in Python's local socket-pair creation before the first test;
the completed run allowed loopback while keeping external connections blocked.
Its success is repair/regression evidence,
not a second prospective comparison: the historical result remains **12/24 F0
observations and 4/12 bilingual pairs**. The case texts and reviewed references
were already consulted during repair. No successful-case filtering or new score
is written to the old run directory.

See the [verification record](../experiments/free-text-candidate-v02-checks.json)
for full-suite status, preservation hashes and connection-attempt checks. The
16 older local notes remain separate and unchanged.

## Next checkpoint

Review this candidate before any new freeze. If retained, pin both v02 modules,
their shared dependencies and the comparator before authoring fresh questions.
Review the new pairs before a new prospective run. Broader grammar coverage or
localization of unknown-clause blocking remains separate work requiring explicit
scope and conservative tests.
