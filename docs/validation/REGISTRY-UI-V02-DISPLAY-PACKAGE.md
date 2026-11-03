# Lot B — opt-in MabSelect presentation v02

Depends on lot A for the compact acceptance report linked by the usage guide.
Apply/review lot A before this lot. All runtime and source dependencies already
exist on main; only the new display entry point and page are added.

## Changes and checks

- Reason-specific outside-release abstention distinguishes cleaning from pressure.
- One clarification action retains each item state, with all eight sources and
  original reservations available in a labelled disclosure.
- Complete duplicated solvent text is folded conservatively; its full quotation
  and citation remain available, while independent precautions stay expanded.
- Twenty-six targeted inherited/new HTTP/DOM regressions passed, followed by one
  additional comparison test: 27 distinct tests passed. Across eight combinations,
  structured JSON and thirteen source HTML pages match the baseline exactly.
- Three browser smoke checks confirmed the display changes. No new prospective
  acceptance score or full-project-suite result is claimed. No runtime code has
  changed since those tests; only a documentation link/export pointer was updated
  while packaging. Four runtime/test file hashes were rechecked against that run.
- Both freezes remain valid. The old entry point and accepted trial are preserved;
  this new page is explicit opt-in via `python -m demo.registry_ui_v02` (port 8785).

[Usage](../CYTIVA-REGISTRY-UI-V02.md)
· [Correction review](REGISTRY-UI-V02-DISPLAY-REVIEW.md)

Review the opt-in page before later promotion. Collapsing context changes default
visibility, not payload size, retrieval, source eligibility or authority policy.

## Exact inventory — 9 files

```text
demo/registry_ui_v02.py
demo/static/registry-v02.html
tests/test_registry_ui_v02.py
tests/ui/registry-v02.cjs
docs/CYTIVA-REGISTRY-UI-V02.md
docs/validation/REGISTRY-UI-V02-DISPLAY-REVIEW.json
docs/validation/REGISTRY-UI-V02-DISPLAY-REVIEW.md
docs/validation/REGISTRY-UI-V02-DISPLAY-PACKAGE.md
docs/validation/REGISTRY-UI-V02-DISPLAY-PACKAGE.json
```

Excluded: private registry and activation/journal files, raw HTTP captures and local
path inventories, environments/caches/dependencies, PDFs, both freeze closures,
sixteen old notes, pilots/media and every unrelated local change. No Git operation
has been performed; branch names and messages below are proposals only.

Proposed branch: `codex/mabselect-ui-v02-display`.

Proposed commit message:

```text
fix: clarify MabSelect registry UI presentation in opt-in v02
```
