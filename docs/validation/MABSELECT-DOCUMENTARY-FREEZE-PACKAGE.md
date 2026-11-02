# MabSelect documentary freeze — versioning package

Prepared on 2 November 2026 from merged `main` at `776dc12`. This package adds a
separate local freeze of the corrected documentary handoff, its reproducible
inventory, accepted-case replay, regression tests and verification records.
It does not activate serving or change the old v03 freeze.

## Result and scope

Freeze: `mabselect-documentary-handoff-corrected-freeze-v01`, **52 pinned files**.
The inventory covers runtime/preview, schemas, accepted design decisions and the
transitive source/review/preparation files read by the Q/N verifiers. The new
verifier, method, decision and test source are included. The lock and generated
outputs are excluded from their own input hashes to avoid circular references.

The lock SHA-256 (LF) remains:
`055df054e7aa72036703e0899f85e02cef5332ab5a063fcba99a61ffe9bbfab4`.
No frozen input or prior result was edited while preparing this package.

All six accepted examples, SX01–SX06, passed. Complete native requests/responses,
response digests, lookup counts and resolved citation identities are retained in
the shipped replay. Replaying them again produced canonically identical output.
An inventory-only copy, run using CPython 3.13.0 with `-S`, also produced identical
complete output without site packages, PDF, tokenizer cache or private files.
Socket operations were blocked; no attempt, LLM call or paid API call was recorded.

See the [frozen method](../../experiments/cytiva/mabselect-handoff-freeze-v01/METHOD.md),
[commands and limits](../../experiments/cytiva/mabselect-handoff-freeze-v01/README.md)
and [initial verification](../../experiments/cytiva/mabselect-handoff-freeze-v01/VERIFICATION.md).
These are known-case reproducibility/conformance checks, not a prospective,
generated-answer or scientific benchmark. Original suitability and scope
reservations remain in the saved responses.

## Tests and review

- Ten new freeze tests cover input/inventory/policy drift, CRLF portability,
  environment mismatch, pre-runtime refusal, accepted-case assertions and output
  preservation. The 24 existing handoff tests and five old-v03 freeze tests also
  passed: **39 targeted tests**, no failures/errors/skips.
- The subsequent complete maintained suite passed **864 tests executed:
  863 passed and one optional PDFium preview skip**, in 127.544 seconds. The
  original logs remain local; no old test result is overwritten.
- The saved six native responses passed the existing machine schemas. Frozen
  v03 retains its original 36 pins and method-lock digest. The sixteen historical
  notes, both pilots and all other pre-existing files are preserved.
- Review found no blocking discrepancy for this local freeze/replay scope.
  Production release/withdrawal authority, default chat integration, numerical
  parsing and scientific validation remain separate gates.

Reproduce verification with the commands in the package README; the standalone
verifier/replay requires only the declared Python standard library. The combined
project regressions and full suite use the already prepared verification
environment, with local HTTP tests and a short Windows temporary root.

## Exact inventory — nine new files

```text
docs/validation/MABSELECT-DOCUMENTARY-FREEZE-PACKAGE.md
experiments/cytiva/mabselect-handoff-freeze-v01/METHOD.md
experiments/cytiva/mabselect-handoff-freeze-v01/README.md
experiments/cytiva/mabselect-handoff-freeze-v01/VERIFICATION.md
experiments/cytiva/mabselect-handoff-freeze-v01/freeze-decision.json
experiments/cytiva/mabselect-handoff-freeze-v01/method-lock.json
experiments/cytiva/mabselect-handoff-freeze-v01/replay-results.json
experiments/cytiva/mabselect_handoff_freeze.py
tests/test_mabselect_handoff_freeze.py
```

The 52 pinned inputs are reproducibility dependencies, not 52 files to recommit:
the existing merged runtime, source/review records and schemas are unchanged.
No pilot, raw PDF, private log/copy, environment, cache, dependency tree or
deployment file belongs to this nine-file delivery.

## Branch and commit message

Branch: `codex/mabselect-documentary-freeze`.

```text
feat: freeze MabSelect documentary handoff and replay accepted cases

Pin the corrected handoff and its complete source/review dependency closure.
Add a standard-library verifier, accepted-case replay and integrity regressions.
Preserve native results and record inventory-only reproducibility and full-suite
verification without activating serving or modifying v03 and the pilots.
```

The next integration step is a separately reviewed PR/merge of this isolated lot.
After integration, explicit local release/withdrawal authority is still needed
before serving activation; a runtime freeze is not an activation decision.
