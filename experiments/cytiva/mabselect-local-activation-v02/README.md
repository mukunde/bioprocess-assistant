# MabSelect v02 — compact local activation record

Eight-file audit package prepared on 2 November 2026, against `ef58f0f`.
[Human decisions](../../../docs/decisions/MABSELECT-REGISTRY-V02-ACTIVATION-DECISIONS.json)
validate LA01–LA08, the stated limits and the initial empty withdrawal inventory.
The [review proposal](../../../docs/decisions/MABSELECT-REGISTRY-V02-ACTIVATION-REVIEW.md)
is preserved as a historical pre-approval snapshot. Its pending fields are not
current activation state; the subsequent decision and verification records are.

## What is preserved

- Exact staged candidate identity, artifact/dependency inventory, five bundle
  purposes, thirteen sources and original scope/recovery limits.
- The literal human approval message, eight decisions and empty inventory scope.
- Actual local activation identity: generation 1, withdrawal version 1, zero
  events; distinct staged and active manifest/authority digests.
- Six active-path case projections, canonical request/response identities, 25
  citation occurrences and thirteen independently checked source views.
- Historical execution attestations: 32 disposable lifecycle tests passed;
  v03 (36 pins) and MabSelect (52 pins) remained valid, with notes/pilots unchanged.

The manifest hashes seven package files and existing support files. It excludes
itself to avoid a circular digest. LF-normalized file hashes and canonical JSON
object hashes are explicitly separate. Actual human/source approval records are
preserved; no test creates replacement human approval.

## Inspect without the private store

Check each `files_sha256_lf` and `supporting_files_sha256_lf` entry in
[manifest.json](manifest.json) against its repository-relative file, normalizing
CRLF to LF before SHA-256. Check the proposal/decision hash bindings, the original
freeze verifiers and each source-object hash against the retained v02 index.

[results.json](results.json) references the already versioned candidate replay.
For each case, its request is identical; reconstruct the recorded active response
by replacing only the top-level `authority_digest` on documentary bundles.
Validation errors are unchanged. Canonicalize using the unchanged registry
`value_sha` convention, then compare the compact response hash/projection and
citation source IDs/quote hashes. This inspection requires neither the private
store nor a PDF, model, API or new activation. It verifies retained evidence;
it is not proof of a fresh active-service run or of who wrote approval files.

A fresh clone still has only staged releases. The private local store, active
pointer, journal, executable approval artifacts, raw audit logs and activation
helper are excluded. Recorded pointer/authority metadata inside the audit summary
is evidence, not an installation or automatic activation mechanism. No UI/HTTP
route or legacy-chat dispatch is added by this package.

## Files to version

```text
docs/decisions/MABSELECT-REGISTRY-V02-ACTIVATION-REVIEW.md
docs/decisions/MABSELECT-REGISTRY-V02-ACTIVATION-REVIEW.json
docs/decisions/MABSELECT-REGISTRY-V02-ACTIVATION-DECISIONS.json
docs/validation/MABSELECT-REGISTRY-V02-LOCAL-ACTIVATION.json
docs/validation/MABSELECT-REGISTRY-V02-LOCAL-ACTIVATION.md
experiments/cytiva/mabselect-local-activation-v02/results.json
experiments/cytiva/mabselect-local-activation-v02/README.md
experiments/cytiva/mabselect-local-activation-v02/manifest.json
```

Proposed commit:

```text
docs: record reviewed local activation of MabSelect v02

Preserve LA01-LA08 approvals, the staged inventory and recovery limits.
Export compact active replay and citation evidence with provenance hashes.
Exclude the private authority store; retain both freezes and prior results.
```

[Activation report](../../../docs/validation/MABSELECT-REGISTRY-V02-LOCAL-ACTIVATION.md)
contains the actual operator boundary and next integration step. Historical test
counts are attestations of completed runs, not results rerun by this export.

## Package preparation checks

A 25-file inventory-only copy (the eight delivery files plus existing support)
passed static verification with `python -S`, without site packages or the private
store. It checked 24 file digests, all eight approval bindings, six reconstructed
responses, 25 citation occurrences and thirteen source-object views. Relative
link targets also resolved. This validates the compact export; it does not run
activation or repeat the historical 32-test lifecycle execution.
