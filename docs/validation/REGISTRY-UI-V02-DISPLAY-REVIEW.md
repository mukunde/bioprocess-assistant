# MabSelect presentation v02 — correction review

**Three presentation findings corrected; 27 distinct targeted tests passed.**
The new opt-in [module](../../demo/registry_ui_v02.py) serves a separate
[page](../../demo/static/registry-v02.html). The baseline entry point, accepted
UA01-UA08 preparation, completed trial, registry service and sources are unchanged.
See [usage](../CYTIVA-REGISTRY-UI-V02.md) and [machine review](REGISTRY-UI-V02-DISPLAY-REVIEW.json).

## Corrections

1. Outside-release results explicitly name the documentary release boundary.
   Cleaning and pressure use different refusal text without invented procedures,
   values, incompatibility or whole-manual absence claims.
2. Each requested item retains its own outcome, but a single clarification action
   focuses the relevant field. Repeated headings are removed. The Q09 explanation,
   eight citations and five original reservations remain accessible in a labelled
   disclosure. Known fields and the ability to remain uncertain are preserved.
3. The repeated E167-E quotation is folded only when the complete warning text is
   already covered by the combined steps with matching source identity. Its full
   original wording and link remain available. The independent E167-W warning
   stays expanded. Partial text coverage or different provenance prevents folding.

## Validation

- The initial targeted suite passed 26 tests in 193.651 seconds, including inherited
  HTTP, source, withdrawal, invalid-authority, stale-response and timeout coverage.
- One additional comparison regression passed in 79.414 seconds: all eight control
  combinations return exactly the baseline JSON, and all thirteen distinct source
  HTML pages are identical. The final test module contains 27 tests; no production
  code changed between these successful test runs.
- Browser smoke checks confirmed the three display changes on the actual local
  v02 page. A short browser-tool locator wait expired while a request was pending;
  a fresh observation confirmed completion without another submission. No browser
  console warning/error was observed. This is not an application timeout result.
- Both runtime freezes validate with the prepared Python environment. The prior
  trial manifest, all preexisting Git-visible files, every private registry file,
  the sixteen old notes, original checkout and pilots retain their original hashes.

## Scope and remaining work

The full project suite was not rerun; the targeted suite includes the original UI
boundary checks on the new presentation. No new prospective acceptance score is
claimed. Folding text improves default readability but does not reduce the JSON
context payload (approximately 12 kB for clarification in the preserved trial).

This page deliberately coexists with the baseline to preserve the method tested
in trial v01. It is available through an explicit separate module/port; launchers
and documentation entry points are not switched. Review this presentation before
promoting it or consolidating the duplicated baseline/variant HTML in a later lot.
No LLM, paid API, commit or push was used.
