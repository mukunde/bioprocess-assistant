# v05: bounded polarity and compositional source navigation

## Scope and status

Prepared on 25 October 2026 after inspecting the frozen v04 W01-W12 results.
This is an opt-in development variant, not a fresh prospective evaluation or a
change to the application default. It uses no LLM, embedding or paid API.
E118-I and E121-EQ remain excluded, including through dependency eligibility.

The v04 implementation, configuration, preparation lock, reviewed questions,
references, decisions and completed run are unchanged. The historical outcome
remains documented in [the v04 report](cytiva-v04-prospective-results.md).

## Changes

- Attach positive/negative polarity to phase and Blue product mentions in
  bounded clauses. Recognize imperative exclusions, postposed scope exclusions
  and leave-out constructions in English and French. Preserve positive
  not-only constructions. Retain clause/alias/polarity traces in each context.
- Mask coordinated buffer names in both languages before interpreting operating
  phases. Buffer formulations and operating elution are separate source roles.
- Union independently requested source roles: a Blue request no longer suppresses
  general direct-use applicability; an unsupported pressure request no longer
  suppresses a supported washing request.
- Detect conflicting positive/negative phase mentions and expose
  `clarification_required`. For a named Blue request with contradictory scope,
  retain protocol scope anchors while withholding operating instructions.
- Route the residual-contaminant explanation to IEX/HIC sources when Blue is
  mentioned only negatively. Reduce screening context to its requested roles;
  retain immunoglobulin method context when that contaminant family is named.
- Extend the finite uncertainty and explanation signals. This remains explicit
  vocabulary matching, not general language understanding.

The separate executor deliberately preserves the frozen v04 executor verbatim
except for the new planner, excluded-product fallback filtering and contradiction
diagnostic. Refactoring the frozen module to insert a shared hook would alter its
method lock. Ranking, six-seed cap, 2,048-token limit, relative fallback threshold,
source quotations and atomic dependency assembly retain their previous settings.

Implementation and reproduction entry points:

- [Versioned planner and executor](../../ingestion/polarity_passage_context.py).
- [v05 configuration](../../experiments/cytiva/section_navigation_v05.json).
- [Development runner](../../experiments/cytiva/polarity_navigation_retrieval.py).
- [Regression tests](../../tests/test_polarity_passage_context.py).

From the repository root, with the already installed ingestion environment:

```powershell
.\.venv-ingestion\Scripts\python.exe -m unittest tests.test_polarity_passage_context -v
.\.venv-ingestion\Scripts\python.exe -m experiments.cytiva.polarity_navigation_retrieval --output data/experiments/cytiva/compositional-navigation-v05/new-development-run
```

The runner requires the existing local preservation baseline and completed W/V
human-review records. Use a new output path: existing directories are refused.
The normal full application suite is `python -m unittest tests -v`; use this
package entry point so the historical fixture compatibility loader is applied.

## Retained development attempts

Both attempts are retained under
`data/experiments/cytiva/compositional-navigation-v05/`, with input snapshots,
all 88 unscored contexts per attempt, timings, metrics and verification hashes.
No earlier result was overwritten.

| Attempt | W | V | H | C | Interpretation |
|---|---:|---:|---:|---:|---|
| A | 12/12 | 12/12 | 10/10 | 9/10 | Screening noise reduction omitted E119-BI for C02 in both languages. |
| B | 12/12 | 12/12 | 10/10 | 10/10 | Added the named-immunoglobulin method role and a full historical-coverage regression. |

Counts above mean all required evidence is present in both languages. They are
not answer-quality scores. All four suites are now known development cases.

For attempt B:

| Measure | Result |
|---|---:|
| W explicit scope failures | 0/24 |
| W diagnostic failures | 0/24 |
| W contexts outside acceptable references | 0/24 |
| V explicit scope failures / outside-reference contexts | 0/24 / 0/24 |
| H contexts outside acceptable references | 0/20 |
| W mean / maximum context tokens | 684.83 / 1,109 |
| V mean / maximum context tokens | 648.83 / 1,041 |
| H mean / maximum context tokens | 560.20 / 993 |
| C mean / maximum context tokens | 776.10 / 1,222 |
| Network attempts / pending-source leakage | 0 / 0 |

H has no explicit excluded-source annotation; C has neither explicit exclusions
nor an acceptable-context annotation. Their missing scope metrics remain `null`,
not zero-error claims. The W mean is 15.8% smaller than the frozen v04 W mean
(813 tokens), while restoring its missing passages. This is a same-question
development comparison, not a new generalization result. Single-sample timings
are retained for audit; no application-latency improvement is established.

## Regression coverage and preservation

Eleven test methods cover the known W criteria, known V/H/C coverage and annotated
scope, new synthetic negation forms, buffer-name coordination, conflict
withholding, excluded-product fallback, missing lexical support, quarantined
dependencies, exact serialization, atomic bundles, budget rejection, pending
source exclusion, output-path safeguards and the unchanged v04 lock.

The runner applies reference scoring only after all contexts have been saved.
Expected answers and required IDs never enter ranking or planning. A baseline of
raw file hashes protects earlier experiment, implementation, test and report
files; each attempt additionally protects the preceding local experiment files.
Completed attempt verification records confirm preservation. Raw outputs and
review records remain outside Git under the repository policy.

The complete current suite passed: **457 tests**, including all eleven new test
methods. The installed application runtime was used with the existing ingestion
site-packages appended to its search path; nothing was installed or downloaded.
The first full-suite environment lacked pypdf, and an earlier sandboxed focused
test could not create its temporary fixture. Both environment failures are
distinct from method regressions; the successful full run exercised that fixture.
Full-suite logs are retained as `full-suite-01.log` and `full-suite-02.log` beside
the development attempts.

## Limits and next step

The parser is a finite clause grammar. It does not resolve arbitrary coordination,
pronouns, product aliases, nested negation or the ownership of every clause by a
distinct sample. Independent roles are combined for context retrieval; this is
not a validated structured representation of separate scientific tasks. Conflicts
are handled conservatively across the request and may require clarification even
when a person could resolve the task boundaries. Diagnostic flags describe source
navigation, not correctness of a generated answer.

No automatic adoption is performed, despite passing the known W scorer. The next
step is to freeze this version, prepare a new human-reviewed challenge with unseen
negation/coordination and task-boundary formulations, and evaluate it once without
adjusting the method after results. Do not reuse W as a prospective benchmark.
