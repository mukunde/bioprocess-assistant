# Corrected Protein A/G Sepharose candidate delivery

Prepared on 5 November 2026 against main
`28775130a9500bf202f67c60151bac53f2c8027c`.

## Explicit eleven-file inventory

| File | Purpose |
| --- | --- |
| `app.py` | Explicit candidate mode and isolated actions; no model fallback. |
| `serving/sepharose_candidate.py` | Separate staged material, source integrity, scoped summaries, clarification and simulated withdrawals. |
| `demo/chainlit_sepharose.py` | Guided candidate controls, citations, refusals and separate held-scope notices. |
| `tests/test_sepharose_candidate.py` | 20 service tests, including four new correction regressions. |
| `tests/test_chainlit_sepharose.py` | 14 adapter tests, including two combined withdrawal/clarification regressions. |
| `tests/test_registry_tracing.py` | Existing tracing fixture synchronization and deterministic parent-span completion regression. |
| `docs/CHAINLIT-SEPHAROSE-CANDIDATE.md` | Explicit local preparation/inspection commands and non-activation limits. |
| `docs/validation/SEPHAROSE-CANDIDATE-IMPLEMENTATION.md` | Initial implementation history, retained failures and tracing fixture repair. |
| `docs/validation/SEPHAROSE-CANDIDATE-CORRECTIONS.md` | Two review findings, fixes, regressions and corrected review. |
| `docs/validation/SEPHAROSE-CANDIDATE-PACKAGE.md` | This scoped inventory and proposed Git metadata. |
| `docs/validation/SEPHAROSE-CANDIDATE-PACKAGE.json` | Explicit list, LF hashes and verification evidence; excludes its own digest. |

The tracing fixture repair is test-only: collection waits, with a bounded
condition, for the request handler and parent span to finish before flushing the
exporter. Its controlled regression first reproduced the race. Production tracing
and application request deadlines are unchanged. See the implementation history.

## Delivery assessment

- Corrected full suite: **1,050 executed, 1,049 passed, one optional PDFium skip**,
  zero failures/errors, in 631.375 seconds.
- Focused suite: 64 passed, including six new regression methods. Three selected
  regressions were first observed failing against the uncorrected implementation.
- Separate check: 36 corrected local control combinations and their delivered
  source views passed; this overlaps conformance coverage.
- Both freezes verify (36/52 pins); raw inventories preserve nine private files,
  636 original workspace files, 109 pilot/previous-trial files and the three
  previous candidate artifacts. No private material is included in the package.
- Current source/test files match the final run; local documentation links and
  the explicit LF-normalized inventory are checked during packaging.

The [corrected review](SEPHAROSE-CANDIDATE-CORRECTIONS.md) addresses both findings.
An eligible clarification survives an independent indication withdrawal; a held
scope cannot reappear inside another summary. Source quotations and original
decisions remain unchanged. The candidate remains staged and is never inserted
into the active private registry. The JSON inventory records current results,
protection checks and local evidence digests without publishing raw logs.

Local candidate v02 was prepared separately. Original v01 material is retained
and refused by its obsolete code pins. Both are excluded from the commit. A
fresh clone can prepare its own staged candidate with the documented command;
this does not create an approval or an activated release.

Exclude the private registry, both freezes, 16 old notes, both pilots, prior raw
trials, original v01 and corrected v02 local preparations, logs/probe runners,
dependencies, caches, PDFs, README and roadmap. Only the eleven paths above belong
to this lot. Preparing the inventory does not stage files or alter Git history.

## Proposed Git metadata

Branch: `codex/chainlit-sepharose-candidate`

```text
feat(documentary): add reviewed Protein A/G Sepharose candidate
```

Suggested body:

```text
Add an isolated, non-activated Protein A/G Sepharose service and guided Chainlit mode.
Preserve scoped source citations, conditions, alternatives and warning dependencies.
Keep clarification independent from held support and isolate each review summary.
Cover withdrawals, stale citations, refusals and the existing tracing fixture race.
Record corrected verification and preservation without private registry artifacts.
```

See the [machine inventory](SEPHAROSE-CANDIDATE-PACKAGE.json) and
[repository instructions](../../AGENTS.md). A future freeze or activation remains
a separate decision; this package grants neither.
