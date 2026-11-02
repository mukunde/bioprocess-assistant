# MabSelect registry v02 — local activation and verification

On 2 November 2026 the project user approved LA01–LA08, the stated limitations
and the initial empty inventory, and explicitly instructed local activation.
The [decision record](../decisions/MABSELECT-REGISTRY-V02-ACTIVATION-DECISIONS.json)
preserves the literal human message for all eight choices. It supersedes the
pending status of the unchanged [original proposal](../decisions/MABSELECT-REGISTRY-V02-ACTIVATION-REVIEW.md)
for this local execution only; original source reviews/quotations are untouched.

## Actual activation scope

`mabselect-local-v02` is active only in the private ignored directory
`.local-tools/mabselect-registry-v02-runtime`, relative to this checkout.
The configured `Registry` API can read it using that explicit data root; it is
not a background server. No existing UI, launcher, HTTP route, Neo4j or legacy
chat configuration was changed. The versioned `serving-data` remains staged and
inactive, preserving its original v02 artifacts and historical replay.

The private copy changes only the approved withdrawal/activation metadata and
its consequential bindings. Catalog, mapping, exact source/review objects,
runtime code, conditions, reservations, 56 dependencies and limits are unchanged.
The initial withdrawal version is 1, with zero events. E118-I and E121-EQ remain
excluded; this is neither their release nor new documentary/scientific approval.

Activation committed exactly one durable head (generation 1), then the active
pointer. The two match after constructing a new Registry instance. The active
manifest/authority hashes differ from the staged ones because the approval
references and stage have changed; this is recorded explicitly in the
[machine-readable verification](MABSELECT-REGISTRY-V02-LOCAL-ACTIVATION.json).

## Verification performed

- SX01–SX06 pass through active evaluation, with no `candidate=` override.
  The [compact results](../../experiments/cytiva/mabselect-local-activation-v02/results.json)
  preserve case projections, canonical response hashes and all citation checks.
  Full responses can be reconstructed from the retained candidate replay by
  changing only the recorded top-level authority digest. Private raw audit logs
  remain local and are not required to inspect the versioned compact results.
- All 25 citation occurrences resolve to the exact returned source object and
  quotation with the same active authority identity. All thirteen registered
  source views independently match the reviewed source-object and quote hashes.
  These are API-level source resolutions; no HTTP citation endpoint is added.
- Supported answers, clarification, partial support, scoped abstention/exclusions
  and invalid-request behavior match the six accepted cases. This is known-case
  conformance, not an independent answer-quality or operational benchmark.
- Network blocked during replay: zero attempts, LLM calls and paid API calls.
- The 32 lifecycle tests pass in disposable roots (46.868 seconds), including
  withdrawals, missing/corrupt authority, restored pointers, interrupted pointer
  replacement, restart and backend-error classification. The real initial
  withdrawal inventory was not modified to exercise these scenarios.
- Both original environment/inventory verifiers pass unchanged: v03 (36 pins)
  and MabSelect (52 pins). The sixteen old notes, pilots and every pre-existing
  Git-visible file were checked by raw SHA-256 and retained.

## Operator boundary

The approved local single-writer trust and recovery limitations remain in force.
A pointer-only rollback is rejected. A valid newer head with an old/missing
pointer remains unavailable pending reviewed manual recovery; no blind second
activation, journal deletion or automatic rollback is allowed. Whole-directory
rollback still needs an independent external anchor to detect. Hashes are not
signatures or proof of who wrote an approval record.

Next functional step: a separately authorized bounded UI dispatch through this
configured registry, preserving withdrawal/citation failure outcomes. The local
activation itself does not rewire the current demo or authorize public hosting.
No Git commit or push was performed as part of this activation.


## Compact versioning package

The [eight-file package](../../experiments/cytiva/mabselect-local-activation-v02/README.md)
contains the original proposal, actual human decisions, selected results and this
report. Its manifest binds those files and their existing repository evidence.
It is an audit record, not an activatable authority directory. A fresh clone
continues to contain the staged candidate, not this machine's active store.
