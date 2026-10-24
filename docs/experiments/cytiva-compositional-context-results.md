# Compositional source navigation v04: development results

## Status and scope

Prepared 24 October 2026 after inspecting the frozen v03b V01-V12 failures.
This is an opt-in development variant, not the application's default retriever,
a prospective benchmark or independently validated reasoning. No LLM, embedding,
paid API, model download or database mutation was used.

The original v03b runtime, configuration, queries, references, review, locked run
and report are unchanged. Before editing, local experiment artifacts and the
frozen package were hashed. Their content hashes were checked again after the
new runs. The old preparation verifier still passes.

## Changes

[The new runtime](../../ingestion/compositional_passage_context.py) inherits source
index construction from v03b but uses a separate planner and assembly selection.
[Its configuration](../../experiments/cytiva/section_navigation_v04.json) preserves
BM25 k1=1.2/b=0.75, six seeds, the 0.65 fallback cutoff, the 2,048-token context
cap, source metadata/dependencies and the E118-I/E121-EQ exclusions.

- Bounded FR/EN clause rules separate affirmative and negative phase mentions,
  including coordinated exclusions, rather-than contrasts and common contractions.
  A buffer name alone does not activate an operating phase. Conflicting phase
  mentions remain observable and prevent navigation_complete; they are not an
  automatically resolved user intent.
- Source-family requests compose instead of competing in one if/elif chain.
  Screening plus Blue warnings and buffer formulations plus elution can coexist.
  An explicit general-characteristics question does not automatically request a
  bovine-specific method merely because it names bovine contaminants.
- Round-robin family selection prevents one route from consuming all six seeds.
  Role order is an explicit development policy; dropped seeds remain reported.
- Uncertainty paraphrases can request general applicability, contaminants and
  method-selection context. The finite dictionary is not a general NLP model.
- A pressure request uses reviewed protocol scope and exposes a selected-corpus
  support limitation. A pH/pI request retains the reviewed IEX general passage and
  exposes the unapproved conditional source boundary. Neither generates a value.
- A generic HiTrap syringe-note request does not assume the product is Blue.
  Navigation needs an eligible footnote and positive lexical support from its
  parent passage in exactly one source family. Ambiguity or missing support
  yields no forced product selection. Unrelated washing/elution sources are not
  appended merely because they rank highly.
- Exact source bundles, warnings, quote hashes and provenance remain atomic.
  No synthetic facts or human approval decisions enter the index.

## Preserved development trials

All local results and input snapshots are retained separately under
`data/experiments/cytiva/scoped-navigation-v04/`:

- `development-a`: V coverage fixed; H02 gained bovine context outside its
  acceptable reference. The saved artifact remains unchanged.
- `development-b`: general-question routing narrowed; H coverage and acceptable
  context restored. Expanded standalone negation tests followed.
- `development-c`: expanded negation handling, same V/H/C coverage.
- `development-d`: final code/configuration and reporting. Missing phase/scope
  annotations are represented by null, not a zero-error claim. In A-C some such
  absent annotations produced zero counts; those historical fields are not
  evidence of scoped correctness. Source selection did not change in D.

Every output directory is created exclusively; an existing directory is refused.
The runner hashes earlier local files before each run, saves contexts before
reference scoring, records inputs and network attempts, and preserves failure
artifacts rather than overwriting them. Individual red/green unit-test iterations
were development work, not extra prospective trials.

## Final development measurements

| Known set | Complete evidence in both languages | Explicit unrequested sources | Outside acceptable context | Mean/max context tokens |
|---|---:|---:|---:|---:|
| V01-V12 | 12/12 | 0/24 formulations | 0/24 | 663.75 / 1,220 |
| H01-H10 | 10/10 | Not annotated for this metric | 0/20 | 593.4 / 993 |
| C01-C10 | 10/10 | Not annotated for this metric | Not annotated for this metric | 794 / 1,222 |

On V, the frozen v03b run had 6/12 evidence-complete intents and 3/12 satisfying
both completeness and phase scope. v04 has 12/12 on those same known references.
Mean V context falls from 705.33 to 663.75 tokens (about 5.9%); maximum context
rises from 1,187 to 1,220 because the combined request now keeps both families.
Do not portray this as reducing every context or proving generalization. Existing
C coverage is retained, but mean C context is 794 versus the earlier v03b report's
733.2; wider warning/context conservation has a token tradeoff.

E118-I/E121-EQ leakage is zero; no network attempts were recorded. All contexts
passed quote, dependency and token-budget checks. V03 still reports one dropped
optional screening seed E119-BI in each language because the composed request
exceeds six seeds. All human-required sources are retained, but navigation_complete
is false: that structural limitation is not hidden by the coverage score.

## Regression checks and limitations

[Twenty-one new tests](../../tests/test_compositional_passage_context.py) cover all
known V queries in both languages (required, acceptable and forbidden context),
existing H/C required coverage and H acceptable scope, alternate negation syntax,
positive multi-phase requests, buffer/phase composition, contradictory mentions,
ambiguous footnote support, fair capped selection, pressure/pending-source limits,
exact quotes/dependencies, a quarantined warning, atomic over-budget exclusion,
unrelated queries, frozen-method integrity, no-overwrite output guards, and the
distinction between missing annotations and observed zero errors.

The first complete suite run finished with 423/424 passing. The pre-existing,
frozen `test_unreviewed_input_blocks_runtime_and_real_output` rejects incomplete
review correctly, then asserts that the real locked-run directory does not exist.
That final preparation-stage assumption became false when the authorized v03b
trial was executed. The test is bound by the original freeze and was not edited;
no real output was removed or hidden to satisfy it. A new isolated fixture checks
the actual invariant: incomplete review is rejected before runtime construction,
and an already existing output remains byte-for-byte intact. This is a test
fixture limitation that must be addressed in a separately versioned test package,
not evidence of a v04 retrieval failure. The final complete suite finished with
424/425 passing: all twenty-one new tests pass, and that same historical assertion
is the sole failure. No test was skipped or patched to manufacture a green suite.
The new fixture was added after the D
measurement; runtime/configuration/runner input hashes remain identical.

Clause rules do not implement unrestricted negation, nested conditionals,
coreference or arbitrary mixed-product language. Conflicting mentions are flagged,
not resolved. The six-seed cap can still omit requested optional roles. The
source_support_complete flag is separate from navigation_complete and does not
establish scientific answerability. Source exclusions do not by themselves prove
that an actual generated answer would refuse safely; no answers were generated.

V/C/H are now known development/regression cases. The next defensible validation
is a new frozen question set reviewed before measurement, with new paraphrases,
negation scope, mixed requests and unsupported-parameter cases. No automatic
adoption or production claim follows from this development result.

## Local commands

```powershell
.\.venv-ingestion\Scripts\python.exe -m unittest tests.test_compositional_passage_context -v
.\.venv-ingestion\Scripts\python.exe -m experiments.cytiva.v03b_evaluation
```

The default v03b command verifies integrity only; it does not rerun its locked
trial. For another explicitly requested development run, choose a new output
under `data/experiments/cytiva/scoped-navigation-v04/` and invoke
`python -m experiments.cytiva.compositional_navigation_retrieval --output <new-directory>`.
The runner requires the completed original human review and local tokenizer cache;
no download fallback exists. Never point it at the frozen v03b run.

See [the original frozen outcome](cytiva-v03b-prospective-results.md) and
[the frozen protocol](../../experiments/cytiva/v03b-evaluation-v01/PROTOCOL.md).

## Subsequent test-fixture maintenance, 24 October 2026

The earlier 424/425 result above is retained as history. The maintained complete
suite now passes **427/427**, with zero failures, errors or skipped tests. All 425
previous case names remain represented, plus two loader-inventory checks. No
retrieval trial was rerun during this maintenance.

The [current test-suite notes](../../tests/README.md) explain how the obsolete
fixture was revised without changing the frozen historical file. The package
loader selects an explicit subclass for the eleven v03b cases; ten methods are
inherited unchanged. The corrected method checks the real incomplete-review gate
in temporary fixtures both with and without an existing output, asserting no
runtime construction, no new output and exact conservation of existing bytes.

The original manifest, method lock, runtime, historical test file, reviewed
references, human decisions and all earlier local trial artifacts remain
byte-for-byte unchanged. Raw SHA-256 checks passed for all 1,194 files recorded
before this maintenance; the original preparation verifier also passes. The
maintenance audit is local under
`data/experiments/cytiva/test-suite-maintenance-v01/`.

The [compact A-D export](../../experiments/cytiva/compositional-navigation-v04-results/README.md) preserves native contexts, metrics and historical input versions for portable verification.

During compact-package preparation, six additional portable-export checks were added. The complete current suite then passed **433/433**, with no skipped tests. Both selected verifiers also passed on clean HEAD snapshots with only lot A, then A+B, without private data, PDF or model assets.
