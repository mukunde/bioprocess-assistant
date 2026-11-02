# Freeze and replay verification — 2 November 2026

The corrected MabSelect documentary handoff is frozen locally as
`mabselect-documentary-handoff-corrected-freeze-v01` from merged `main` at `776dc12`.
No serving release is activated. No original runtime, source/review artifact,
v03 file, excluded historical note or pilot was changed.

## Frozen inventory

- 52 files: runtime and preview, machine schemas, accepted design/decisions,
  complete Q/N verification/preparation dependencies, verifier, freeze method,
  decision and test source.
- Method-lock SHA-256 (LF): `055df054e7aa72036703e0899f85e02cef5332ab5a063fcba99a61ffe9bbfab4`.
- Environment: CPython 3.13.0, standard library only; no third-party runtime
  dependencies, PDF, tokenizer asset or private audit required.
- The method lock and generated outputs are excluded from their own input hashes.
  This report is a verification output, not another runtime input.

## Accepted-case replay

| Case | Observed outcome | Check |
|---|---|---|
| SX01 | supported | Plain MabSelect general block; no restricted sequence |
| SX02 | needs_clarification | Exact product requested; no procedure delivered |
| SX03 | partial | Hydrophobic alternatives supported; numerical pressure abstained |
| SX04 | partial | A asks for product/context; independent B remains supported |
| SX05 | abstained / no_requested_item | Explicit exclusion wins; no technical context |
| SX06 | validation error | Client authority override rejected; zero selector lookups |

All six passed. Complete native requests/responses, response digests, selector
call counts and resolved citation identities are retained in
[replay-results.json](replay-results.json). File SHA-256 (raw UTF-8):
`8949247abd065082080e87c7bd3ffa89cc8041c33933c53a08cf437a8657993e`. All socket operations were blocked; no attempts, LLM calls or paid API
calls were recorded. Original source/review reservations remain in the responses.
These are known accepted examples, not a new independent question set or
scientific/operational approval.

## Reproducibility and regression checks

A separate inventory-only directory contained exactly the 52 pinned files plus
`method-lock.json`; no `.git`, site packages, source PDF, environment, cache,
video/pilot or private artifact was copied. Executing the CLI with `python -S`
produced an output canonically identical to the saved replay, including complete
responses and citation checks. The temporary copy and logs stay outside this
versionable package.

The targeted suite passed **39 tests**, no failures, errors or skips: ten new
freeze tests, the existing 24 handoff regressions and five old-v03 freeze tests.
The regressions include task isolation, missing warnings, quarantine, scope,
atomic budgets, unexpected errors and original immediate-wash wording. New checks
exercise missing/changed dependencies, inventory/policy drift, CRLF portability,
Python mismatch, pre-runtime failure, accepted-case assertions and no-overwrite
output handling. This is not a new full-suite result.

```powershell
python scripts/run_tests.py --temp-root "$env:LOCALAPPDATA\Temp" tests.test_mabselect_handoff_freeze tests.test_documentary_handoff tests.test_free_text_v03_freeze
```

These combined regressions use the prepared project verification environment;
the standalone static verifier and accepted-case CLI need only the declared
Python standard library. No new dependencies were installed.

## Remaining gates

This freeze is not the production active-release/withdrawal registry. Any
serving activation or legacy-chat route needs its separate reviewed authority
and typed dispatch. Quantities remain original wording, with no new numerical
parsing, dosage calculation, suitability selection or graph publication.
No prior trial score is replaced, and no new question review is required to
reproduce these accepted-case checks. No commit or push was performed.
