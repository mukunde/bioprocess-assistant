# MabSelect journey — re-review after MR01/MR02 corrections

31 October 2026. Local uncommitted work based on `main` at `9b4bd25`.
The [first review](MABSELECT-CLEANING-IMPLEMENTATION-REVIEW-V01.md) and its probes
remain unchanged. MS01–MS08/C1–C4 human decisions, source dossier and original
review messages are preserved. This re-review supplies no new scientific or
operational approval and creates no runtime freeze.

## MR01 — resolved: portable approval replay and tamper checks

The exact [approved contract](mabselect-cleaning-approved-contract-v01.md) hashes
to the already recorded value
`1506c3e1d3045d97b0fa0ee53e81b4a4bb3dbad92093f00e2d0ac6752de61f9c`.
No historical hash or message was rewritten to fit the current edited guide.
The [standard-library verifier](../../experiments/cytiva/verify_mabselect_design.py)
anchors contract, dossier and decision-record digests independently of mutable
review input. It checks historical cross-references, twelve decisions and MS
statements, accepts LF/CRLF and replays from only three portable artifacts.

The MabSelect runtime calls this verifier before reading original Q/N source
reviews. Tests reject changed human messages, C4/MS wording, decisions, dates,
both referenced hashes, missing/changed contract or dossier, and a simultaneous
contract-plus-reference rewrite. The original MC12 now invokes approval integrity.
The previously successful in-memory approval-record mutation is therefore refused.

## MR02 — resolved: actual page/handler integration with mutation witnesses

The [MC12 UI tests](../../tests/test_mabselect_ui.py) start the actual local API,
load the served HTML and execute its JavaScript with jsdom. They dispatch real
DOM change/click events, inspect rendered content and forward real HTTP requests
to `Demo`, rather than mocking selector outputs or duplicating the renderer.
The fetch bridge rejects other destinations; no models or external APIs run.

The passing control covers exact family/plain/SuRe/SuRe LX payloads and product
clarification/focus; four alternatives; distinct restricted block; stale notices;
hydrophobic alternatives and pressure quotation; source and return anchors;
mixed-context focus/product retention; old guided/v03 and Protein A/G paths.
Five in-memory mutants remove the MabSelect entry, miswire product, remove stale
updates, omit the rendered pressure quotation or break source links. All must
fail the relevant assertion while the unchanged control passes.

jsdom is a development-only dependency in a separate locked npm package. The
complete suite requires its setup, fails clearly if missing, and does not silently
skip these checks. Its DOM execution does not emulate layout: `scrollIntoView`
is the only layout shim; focus/hash/selection/handlers are executed. Anchor tests
wait for their actual hash. Prior real-browser checks remain valid for the
unchanged HTML, but no broad browser, physical-PC or visual certification is claimed.

## Verification

The targeted set passed **40/40 tests in 21.085 seconds**: MC01–MC12, five approval
integrity tests, six UI/in-memory-mutation tests and seventeen prior journey/demo
regressions. An initial DOM-test failure assumed immediate anchor navigation;
the test now waits for the actual hash, with no application code changed for it.

The complete suite ran **823 tests in 151.294 seconds: 822 passed, one optional
PDFium preview skip, no failures or errors**. The main test guide now includes
the isolated npm setup command; only its two dependent documentation hashes
were refreshed afterward, with the affected package tests rechecked. No source,
method, decision or historical score binding was altered.

## Before-freeze assessment

Both identified gaps are resolved in implementation and regression coverage.
No additional MS01–MS08/C1–C4 deviation was found in the reviewed changes. Exact
product scopes, general/restricted alternatives, quantities, pH ownership and
quarantine/source reservations remain those already approved. Keep the new local
runtime unfrozen until the user reviews the corrected lot; preparation and
verification do not constitute another human approval.

The known intermittent WinError 10053 in the older forbidden-Origin HTTP test is
separate transport work and was not fixed, hidden or weakened here. The targeted
run above passed. No Windows protections or Origin policy changed.

Frozen v03, sixteen excluded notes, prior records/media/trials and the original
checkout are checked separately by hash. No commit, push, source publication or
model/API request is part of this task.
