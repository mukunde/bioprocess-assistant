# MabSelect UI — opt-in active registry integration

Prepared on 2 November 2026 against merged `main` at `1af1b60`.
Implementation is local and uncommitted. This adds a separate UI around the
existing approved registry; it does not alter either runtime freeze, change the
private authority store, activate another release or dispatch through legacy chat.

## Implemented path and scope

- New entry: `python -m demo.registry_ui --registry-root <existing-root> --port 8784`.
  Root configuration is required, server-side and loopback-only. No root directory,
  approval, pointer or journal is created; no automatic preview fallback exists.
- Real typed evaluation through `Registry.evaluate(request)` without `candidate=`.
  Real release-bound citation lookup through `Registry.source(release, source)`.
  Both keep the existing per-operation authority/withdrawal checks.
- Separate `demo/static/registry.html` and source renderer; frozen preview/server,
  v03, the 52-file handoff and existing launchers are untouched. No new dependency.
- Product/context controls, cleaning/pressure questions, exact original excerpts,
  conditions, scoped reservations, clarification with focus on missing fields,
  scoped abstention and held/unavailable outcomes. No quantity conversion or
  treatment-selection logic is added.
- No-store response/source headers; original strict JSON/request limits and
  Host/Origin checks; extra framing/referrer policy and escaped source rendering.
  No activation, withdrawal or write endpoint. Unknown client authority fields
  are rejected instead of being interpreted as a root or candidate override.
- Previous procedures/citations clear when submitting. A response arriving after
  an input change is not displayed; existing results are marked stale on change.
  Empty question selection makes no request. User-facing labels explain fields;
  raw machine/audit data remains collapsed.

## Review findings and correction

The first restricted test execution could not connect to loopback (EACCES); its
failure is retained separately. Re-running with loopback access exercised the
actual HTTP/DOM path; no security setting, source approval or test gate was disabled.

The first executable DOM review found a display ambiguity: the frozen aggregate
status was `abstained` while its item was correctly `quarantined`. The page showed
only a generic absence-of-answer heading after a withdrawal. The new renderer
now explicitly says evidence is held when that item state is present. The frozen
schema/aggregate behavior is unchanged. Pressure-only absence still uses scoped
abstention and never becomes a withdrawal claim.

## Targeted regression evidence

Twelve tests passed (46.449 seconds in the corrected targeted run):

| Check | Evidence |
|---|---|
| Explicit opt-in and no writes | CLI requires a root; normal HTTP reads call neither preparation nor activation and preserve authority-file bytes. Missing root is not created. |
| Response and citations | Actual loopback POST and source GET use the shipped Registry/renderer and exact original source text; no staging banner or preview fallback. |
| Clarification and abstention | Unknown family/context requests clarification. Pressure-only hydrophobic request abstains within selected excerpts, without numerical inference. |
| Withdrawals | Two explicit synthetic source events target old and new release identities. Current precipitated support is held; old bookmarked source and current source return no quote. Independent hydrophobic support and its warning remain. |
| Missing/corrupt authority | Missing pointer/history returns unavailable and clears citations; source GET returns 503 without quotation/path leakage. Preview evaluation is not called. |
| HTTP boundary | Client `candidate`, `registry_root`, `data_root`, foreign Origin and foreign Host are refused. No activation endpoint exists. |
| Real UI/JS | Four jsdom scenarios execute the shipped form and renderer against the real local API: normal/clarification/abstention, withdrawals, unavailable authority, and input change while the response is pending. |

The test authority is exclusively synthetic and inside owned temporary roots.
No real withdrawal, corruption or activation is performed against the private
project store. The existing registry lifecycle tests remain unchanged.

The complete maintained suite passed **908 tests executed: 907 passed and one
optional PDFium preview skip**, in 326.581 seconds, including the twelve new UI
regressions. No failures or errors. No historical output is replaced; targeted
and complete results remain distinct.

## Browser observations

The in-app browser opened the separate service on 127.0.0.1:8784, reading the
already active private v02 store. Observed using real browser controls:

1. Exact plain MabSelect + precipitated substances: documented Q05 support,
   separate formulations, conditions and reservations visible.
2. Opened E167-P: correct source ID/PDF page, exact excerpt and original scoped
   review; current registry authority banner, no preview/activation claim.
3. Unknown family + unknown context: exact-product/context clarification;
   no recipe selected and no confirmed diagnosis demanded.
4. Hydrophobic context + pressure question only: explicit scoped abstention;
   no numerical pressure inferred.

Both narrow-screen form/results and the source page were visually inspected.
jsdom tests DOM semantics rather than pixel layout. Browser screenshots remain
private verification artifacts, not runtime inputs. Withdrawal/unavailable faults
were observed through HTTP/DOM tests only, never by editing the live register.
The current 8783 preview remains distinct; no published screenshot tour was edited.

## Preservation and limits

Before/after raw hashes cover the private store, both freeze closures, all sixteen
old notes, pilots and every pre-existing Git-visible file. The private active
release remains generation 1, withdrawal version 1, zero events. Both original
freeze/environment verifiers passed with their original lock digests; their
passing result validates those historical closures, not the new UI itself.

This is a bounded, local read-only UI path. It establishes known-case rendering
and lifecycle conformance, not independent answer-quality, scientific validity,
operational suitability, public hosting or multiwriter/whole-store-rollback safety.
No LLM or paid API is called. No commit/push is part of this implementation.

[Usage and walkthrough](../CYTIVA-REGISTRY-UI.md) ·
[Registry guide](../../serving/README.md) ·
[Approved local activation](MABSELECT-REGISTRY-V02-LOCAL-ACTIVATION.md)
