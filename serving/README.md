# Local reviewed-serving registry candidate

This standard-library adapter wraps the unchanged frozen MabSelect handoff.
It is separate from the original preview, frozen v03, Neo4j and the legacy chat.
The supplied release is **staged, not activated**. No HTTP route, active pointer,
activation decision, source publication or background server is created.

## Inspect and replay

From the repository root in the prepared CPython 3.13.0 environment:

```powershell
python -S -m experiments.cytiva.mabselect_registry_candidate
python -S -m experiments.cytiva.mabselect_registry_candidate --replay
```

These commands explicitly inspect the candidate, not the active service.
`--output new-result.json` retains a separate replay and refuses an existing file.
`--prepare --release-id another-version` creates another staged directory and
never replaces a version. The CLI deliberately provides no activation command.
Use the [candidate review](../docs/validation/MABSELECT-LOCAL-REGISTRY-CANDIDATE.md)
for the actual inventory, results, tests and pending approval.

## Files and authority

`serving-data/releases/mabselect-local-v01/` contains:

- `release.json`: versions, limits and complete artifact bindings;
- `catalog.json`: fixed registered IDs to repository/release paths;
- `mapping.json`: the five allowed bundle purposes and required Q/N sources;
- `source-index.json`: exact registered passages and original scoped reviews;
- `withdrawals.json`: explicit, versioned empty inventory;
- `withdrawal-decision.json`: **proposed**, with a null human message. Its
  validator field names the role designated by the accepted design; it is not
  an assertion that the user has approved the empty inventory.

The release binds the old 52-file freeze, its method lock, the two registry Python
files and the catalog (56 dependencies). Mapping/index/retraction artifacts and
their decisions have additional explicit references. The catalog contains safe
paths only; exact scope and source/review objects are checked against the frozen
handoff, even if somebody refreshes a changed artifact's declared digest.

`Registry(data_root).evaluate(request)` requires current active authority. With
the delivered candidate it returns `unavailable: release_not_activated`.
`evaluate(request, candidate=release_id)` is an explicit server/developer preview
argument, not a client request field. Strict request validation rejects client
authority overrides. No caller path is accepted inside a documentary request.

Each operation reloads and validates its complete authority (including the first
request) and checks it again before returning. A missing register is not empty;
invalid global authority yields an empty `unavailable` response. A mid-request
change discards the response as `authority_changed`, without hidden retry or
fallback. Version-bound source views check current withdrawal authority, including
when displaying an older release; they never silently redirect to a new source.

## Withdrawals and history

Events target an exact release plus bundle/review/source identity. Target hashes
are SHA-256 of canonical JSON for that mapping entry, original review object or
full source object respectively (not an interchangeable quote hash). A withdrawn
source/review holds every bundle that requires it. Required alternative sets stay
atomic; independent valid tasks may still be served. A held source view exposes
no quotation when it has no eligible scope.

The ordered event log preserves earlier entries and their bound decisions.
Reinstatement requires a preceding withdrawal and a new reviewed inventory/version.
An explicitly reviewed new release is a distinct identity: an event targeting an
older version is not silently promoted to a withdrawal of every later edition.
Unknown/stale targets, dropped history and missing approvals are rejected.

For later reviewed activation, the internal `Registry.activate(release_id)` method
requires an already activated manifest and matching, approved local decision
records with a nonempty original human message. The activation decision binds the
release content (excluding stage and its own decision reference to avoid circular
hashes). It validates history, rechecks inputs and atomically replaces the pointer.
It has been exercised **only with synthetic approvals in disposable test roots**;
it has not been called on the supplied candidate. No approval writer is supplied.

Trust is the configured user-controlled local directory, not arbitrary model
metadata or client input. Hashes detect drift; they are not cryptographic proof
of who authored an approval file. Cooperating threads in one process serialize
lookup/activation with the same lock; external edits are checked through hashes.
Multiple independent writer processes are not supported by this first candidate.
Later releases using changed code/source bindings need a separately reviewed
version/migration; the current runtime does not bless refreshed frozen inputs.
