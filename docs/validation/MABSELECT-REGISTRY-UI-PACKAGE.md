# Corrected MabSelect registry UI — versioning package

Prepared on 2 November 2026 against merged `main` at `1af1b60`.
One delivery contains the new explicit-root UI, its tests, usage guide and retained
implementation/review/correction reports. No original frozen file is modified.
The historical two-gap review is preserved; the correction report records their
resolution. This package does not introduce a new runtime freeze or activation.

## Final behavior

The separate loopback server requires `--registry-root`, reads existing active
authority and uses the typed evaluation/source methods without a candidate override.
Citations are checked against current withdrawals, including old bookmarked
source URLs. Independent support and warnings remain available when another
scope is held. Missing/invalid authority refuses support with no preview/model
fallback. Unknown product/context asks for clarification; unsupported pressure
questions abstain within the selected excerpts.

Unexpected source/renderer failures return a generic 503 with private class-only
logging; an unknown source is 404 only under verified authority. A 15-second
fetch/body deadline restores controls and allows manual retry. Cancellation and
request identity prevent late responses from replacing newer results. No write,
activation, withdrawal or public-hosting endpoint is added.

## Validation and limits

- Corrected targeted run: 18 HTTP/DOM tests passed, including six new regressions.
- Complete maintained run on the exact runtime/test files: 914 executed,
  913 passed and one optional PDFium preview skip; no failures or errors,
  378.905 seconds. This package adds only this delivery document afterward.
- Real browser verification after UI-server restart: normal response and E167-P
  citation; earlier browser observations cover clarification and scoped abstention.
  Corruption, withdrawals and request stalls are tested in disposable/controlled
  fixtures, never against the private project store.
- Both original freezes/environment verifiers pass unchanged: v03 (36 pins),
  MabSelect (52 pins). Private active registry remains generation 1, withdrawal
  version 1, zero events; raw file identities are checked before delivery.
- No LLM or paid API calls, source/human-review changes, numerical inference,
  scientific validation or independent answer-quality score. Local single-writer
  storage/recovery limits remain as approved. The deadline bounds client waiting,
  not termination of server computation already underway.

The 18-test suite is reproducible with the existing verification environment and
locked development Node/jsdom setup; no private authority is needed:

```powershell
python scripts/run_tests.py --temp-root "$env:LOCALAPPDATA\Temp" tests.test_registry_ui
```

Use a Windows temporary root of at most 60 characters. Existing full-suite entry
points remain unchanged. [Usage](../CYTIVA-REGISTRY-UI.md) documents startup and
missing-authority behavior on a fresh clone.

## Exact delivery — nine files

```text
demo/registry_ui.py
demo/static/registry.html
tests/test_registry_ui.py
tests/ui/registry.cjs
docs/CYTIVA-REGISTRY-UI.md
docs/validation/MABSELECT-REGISTRY-UI.md
docs/validation/MABSELECT-REGISTRY-UI-REVIEW.md
docs/validation/MABSELECT-REGISTRY-UI-REVIEW-FIXES.md
docs/validation/MABSELECT-REGISTRY-UI-PACKAGE.md
```

Exclusions: `.local-tools` (private registry, approval/journal files, environments,
raw logs, screenshots and helper scripts), the sixteen old notes, both freeze
closures, all source/review data, pilots/videos and every unrelated local file.
The existing private store is read only; no pointer, withdrawal or authority hash
is refreshed to fit this UI. Root README/roadmap updates are outside this delivery.

Proposed branch: `codex/mabselect-registry-ui`.

Commit message:

```text
feat: add opt-in MabSelect UI backed by the active registry

Serve typed requests and current-authority citations through an explicit local root.
Contain source failures and bound UI requests with safe cancellation and retry.
Add HTTP/DOM withdrawal and recovery regressions; preserve both freezes.
```

[Initial implementation](MABSELECT-REGISTRY-UI.md) ·
[Two-gap review](MABSELECT-REGISTRY-UI-REVIEW.md) ·
[Corrected pre-freeze review](MABSELECT-REGISTRY-UI-REVIEW-FIXES.md)
