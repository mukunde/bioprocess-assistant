# Selected v04 development history A-D

This is lot B and depends on lot A's reviewed v03b export. All four local
development runs are preserved, with 64 bilingual contexts each (V12/H10/C10),
256 contexts total. This is known-case development after inspecting failures,
not a new prospective evaluation. E118-I and E121-EQ remain excluded.

Final run D retains all required evidence in both languages: V12/12, H10/10,
C10/10. V has zero explicitly unrequested sources and zero outside-acceptable
contexts; H has zero outside-acceptable contexts. Missing H/C phase annotations
and C acceptable-context annotations are null in D, not measured zero errors.
A-C's original historical zeros for those missing annotations remain unchanged.

`results.json` keeps native saved contexts and metrics for A-D. `provenance.json`
binds input hashes and preserves the historical source text of code/tests that
differ from current files; no historical snapshot is overwritten. It also records
the original run safety checks. `manifest.json` binds the current runtime,
configuration, tests, suite correction, README and report plus lot A's manifest.

Standard-library verification needs no raw private runs, PDF, model or tokenizer:

```powershell
python -S -m experiments.cytiva.verify_compositional_navigation_package
python -S -m unittest tests.test_compositional_navigation_package -v
```

Verification checks exact quote serialization, source dependencies, native hashes,
recorded token bounds, measured summaries, grids, historical inputs and reference
scores. It does not rerun search, retokenize, authenticate a human or certify
scientific applicability. Original raw runs and local preservation inventories
remain ignored; no source PDF, full page images, cache, secret or absolute private
path inventory is included.

The [current complete suite](../../../tests/README.md) preserves the original
frozen v03b test file and runs its eleven named safeguards through an explicit
subclass, replacing only the obsolete real-directory-absence fixture. No test is
skipped. The current full-suite entry point is `python -m unittest tests -v`.

See [the development report](../../../docs/experiments/cytiva-compositional-context-results.md)
and [lot A](../reviewed-v03b-evaluation/README.md). The six-seed cap still drops one
optional V03 source; that structural incompleteness is reported. No default
retriever activation or generated-answer quality claim is made.
