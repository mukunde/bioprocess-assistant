# Lot A — reviewed UA01-UA08 acceptance trial

Prepared against main at `04e3bd3`. Eight approved human reference decisions,
complete bounded request/response observations, thirteen opened source identities,
checks and historical findings are ready as one isolated lot.

## Results and checks

- Preserved trial: 8/8 functional outcomes; 216 case checks and 91 source checks.
  Three noncritical usability findings remain in the historical result.
- Offline compact verifier passes; four new integrity/portability tests pass with
  the existing short-temporary-directory runner (1.109 seconds). No trial rerun.
- The first checker report (5/8 due to an incorrect clarification-binding assertion)
  and its corrected assessment are both retained, without replacing observations.
- Exact original human messages/reservations and source/review identities remain
  bound to the unchanged preparation method. The initial README/cards are historical
  proposals; completed decisions and REVIEW-STATUS.md state the current review.
- No serving code, private store or frozen input is included. Raw HTTP files,
  preflight path inventories and local preservation snapshots remain local.

[Compact trial](../../experiments/cytiva/reviewed-registry-ui-acceptance-v01/README.md)
· [Offline verification](../../experiments/cytiva/reviewed-registry-ui-acceptance-v01/verification.json)

This measures known-source guided UI combinations, not novel retrieval, generation,
scientific suitability or latency. Withdrawals were not injected in the live store.

## Exact inventory — 20 files

```text
experiments/cytiva/registry-ui-acceptance-v01/evidence.json
experiments/cytiva/registry-ui-acceptance-v01/manifest.json
experiments/cytiva/registry-ui-acceptance-v01/method-lock.json
experiments/cytiva/registry-ui-acceptance-v01/questions.json
experiments/cytiva/registry-ui-acceptance-v01/README.md
experiments/cytiva/registry-ui-acceptance-v01/references.json
experiments/cytiva/registry-ui-acceptance-v01/REVIEW-STATUS.md
experiments/cytiva/registry-ui-acceptance-v01/review.json
experiments/cytiva/registry-ui-acceptance-v01/REVIEW.md
experiments/cytiva/reviewed-registry-ui-acceptance-v01/assessment-history.json
experiments/cytiva/reviewed-registry-ui-acceptance-v01/manifest.json
experiments/cytiva/reviewed-registry-ui-acceptance-v01/observations.json
experiments/cytiva/reviewed-registry-ui-acceptance-v01/provenance.json
experiments/cytiva/reviewed-registry-ui-acceptance-v01/README.md
experiments/cytiva/reviewed-registry-ui-acceptance-v01/results.json
experiments/cytiva/reviewed-registry-ui-acceptance-v01/verification.json
experiments/cytiva/reviewed-registry-ui-acceptance-v01/verify.py
tests/test_registry_ui_acceptance_package.py
docs/validation/REGISTRY-UI-ACCEPTANCE-PACKAGE.md
docs/validation/REGISTRY-UI-ACCEPTANCE-PACKAGE.json
```

Excluded: private registry and activation/journal files, raw HTTP captures and local
path inventories, environments/caches/dependencies, PDFs, both freeze closures,
sixteen old notes, pilots/media and every unrelated local change. No Git operation
has been performed; branch names and messages below are proposals only.

Proposed branch: `codex/cytiva-ua-ui-acceptance-reviewed`.

Proposed commit message:

```text
test: preserve reviewed MabSelect UI acceptance trial
```
