# MabSelect local registry — candidate before activation

Prepared on 2 November 2026 on merged `main` at `4f35ea9`.
Candidate: `mabselect-local-v01`. **Staged only; no activation authorized or
performed by this candidate.** Both earlier freezes, original decisions and
source facts remain unchanged.

## Delivered candidate

- Five registered bundle purposes: Q05, Q06, N06, N07 and Q09.
- Thirteen exact registered excerpts and five original scoped reviews. These
  are the MabSelect/clarification dependency subset, not the entire manual or
  a newly approved corpus.
- Fifty-six bound dependencies: the original 52-file documentary freeze, its
  method lock, two registry Python files and the fixed artifact catalog.
- Versioned mapping/source index and explicit empty withdrawal register. The
  withdrawal decision is **proposed**, with no original approval message.
- Default serving remains unavailable because `serving-data/active.json` and the
  release's activation decision do not exist. The original local demo/preview and
  recorded pilots are untouched; they are not wired to this registry yet.

See [commands and authority rules](../../serving/README.md). The frozen code is
wrapped, not edited. No LLM, paid API, database write, HTTP listener, deployment
or automatic activation is introduced.

## Replayed accepted cases

SX01–SX06 all pass against the explicit staged-candidate argument:

| Case | Observed result |
|---|---|
| SX01 | Plain MabSelect supported, without the restricted sequence |
| SX02 | Product clarification, no procedure |
| SX03 | Hydrophobic alternatives plus scoped numerical-pressure abstention |
| SX04 | Missing fields on A; independent B served |
| SX05 | Explicit exclusion wins; no technical context |
| SX06 | Client authority override rejected before lookup |

Complete requests, native responses and citation-check identities are retained in
[the candidate replay](../../experiments/cytiva/mabselect-registry-candidate-v01/replay-results.json).
All returned citations resolve through the candidate index to the exact delivered
source object. Socket operations were blocked and no attempts were recorded.
There is no new independent question set or answer/scientific quality claim.

An inventory-only copy of 62 files (frozen closure/lock, registry/CLI and candidate
artifacts), run using `python -S`, produced canonically identical full output.
It contained no environment, cache, PDF, private run directory or site packages.
The copied files and raw logs stay local outside the versionable candidate.

## Regression and integration verification

Twenty-four new registry tests exercise:

- staged vs active authority, proposed vs approved decisions, explicit empty vs
  missing withdrawal inventory and malformed/duplicate JSON;
- immutable version preparation, safe paths/catalog, complete runtime bindings,
  altered mappings/source data even after refreshed declared digests;
- default inactive behavior, exact citations, task-local clarification/abstention
  and rejection of client authority overrides;
- withdrawal of bundle, review or indispensable source, complete alternative
  withholding and survival of independent tasks;
- older-release source holds, explicit reinstatement, preserved event decisions,
  append-only history and refusal of rollback/stale identities;
- authority changes during response/source assembly, atomic-pointer input drift,
  incomplete approvals and absence of stale fallback.

Approvals used in lifecycle tests are explicitly synthetic and confined to
temporary directories. No real candidate approval or active pointer is written.

The complete maintained suite passed **888 tests executed: 887 passed and one
optional PDFium preview skip**, in 149.661 seconds. This includes the existing
documentary and two-freeze tests. The four registry artifacts (`release`,
`mapping`, `source-index`, `withdrawals`) also passed their unchanged Draft
2020-12 schemas using local reference resolution. No old result is rescored.

## Review before activation

No blocking discrepancy was found for this bounded registry candidate. It is
ready for code/candidate review, **not automatically active**. The next decision
must explicitly cover the release, its source/mapping scope and initially empty
withdrawal inventory. The activation operation would require matching approved
decision records and a new activated manifest, then create the active pointer;
none is prefilled here. Any UI/chat integration is a separate step.

Limitations are explicit: trusted local authority files rather than digital
signatures; cooperating single-process writers; no remote control endpoint;
no independent answer evaluation, operational authorization or new numerical
parsing. E118-I and E121-EQ remain excluded. The frozen v03 and MabSelect locks,
sixteen old notes, pilots and all previously existing files remain unchanged.

## Isolated delivery — 13 files

```text
docs/validation/MABSELECT-LOCAL-REGISTRY-CANDIDATE.md
experiments/cytiva/mabselect-registry-candidate-v01/replay-results.json
experiments/cytiva/mabselect_registry_candidate.py
serving-data/releases/mabselect-local-v01/catalog.json
serving-data/releases/mabselect-local-v01/mapping.json
serving-data/releases/mabselect-local-v01/release.json
serving-data/releases/mabselect-local-v01/source-index.json
serving-data/releases/mabselect-local-v01/withdrawal-decision.json
serving-data/releases/mabselect-local-v01/withdrawals.json
serving/README.md
serving/__init__.py
serving/local_registry.py
tests/test_local_registry.py
```

Branch: `codex/mabselect-local-registry`.

```text
feat: add staged MabSelect release and withdrawal registry

Wrap the frozen documentary handoff with versioned local authority, bound
source/mapping inventories and reviewed withdrawal/reinstatement history.
Recheck authority before delivery, fail closed on drift and preserve independent
tasks and old-version source holds. Add lifecycle regressions and candidate
replay evidence without activating serving or changing either freeze.
```

No `active.json`, approved decision, source PDF, environment, cache, raw private
log or pilot belongs to this delivery. Code review/integration and later explicit
activation are distinct decisions.
