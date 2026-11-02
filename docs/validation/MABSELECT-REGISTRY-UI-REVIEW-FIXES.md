# Corrected pre-freeze review — MabSelect registry UI

Prepared on 2 November 2026 after the [two-gap review](MABSELECT-REGISTRY-UI-REVIEW.md).
The original implementation/review and their 908-test result remain historical.
No new runtime freeze, activation, withdrawal, commit or push is performed.

## Citation failure containment

The new UI boundary catches ordinary source-validation and rendering exceptions,
builds the whole HTML body before sending headers, and returns a generic 503
without quote, exception contents or private paths. Only the boundary and exception
class are logged; raw exception text/tracebacks are not added to these diagnostics.
Process-control BaseExceptions are not treated as ordinary service errors.

A KeyError is not automatically called an unknown source: a fresh validated
snapshot and target inventory must confirm that the requested source is absent.
If that check fails, the outcome stays unavailable. This extra classification
validation occurs only on the error path; successful requests retain the existing
Registry lookup and per-operation/final authority checks.

Regressions use well-formed wrong-shape manifests (`null`, `[{}]`), unexpected
TypeError/KeyError from source lookup or HTML rendering, and an unregistered source
under valid versus invalid authority. They assert controlled 503 or 404, no leaked
quotation/details, private class-only logging and the unchanged fail-closed POST.
Every authority edit is in an owned disposable root.

## Bounded UI waiting and safe retry

The production deadline is 15,000 ms, covering fetch and JSON-body parsing.
An AbortController is combined with an explicit cancellation promise; a transport
that ignores abort cannot leave the UI waiting forever. Timeout clears procedures
and citations, reports the deadline and restores controls for manual retry.
There is no automatic retry, alternate authority, preview fallback or generated
answer. This bounds UI waiting, not server-side computation already underway.

Input changes or a superseding submit immediately cancel the pending display
attempt. Request-object identity guards all rendering and control updates so a
late result/finally block cannot overwrite a newer request. Timers are cleared on
success, failure, timeout and cancellation. Existing scoped abstention and the
separate held-evidence label are preserved.

The real shipped DOM/JS tests advance a controlled clock at the unchanged
15-second threshold. Three new scenarios cover a fetch that never settles, a
late fetch response and a stalled/late JSON body. They seed a supported result,
verify immediate clearing, expire the request, complete a successful retry with
scoped pressure abstention, then release any late old response. The newer result
and enabled controls must remain; no deadline may remain queued.

## Verification and renewed review

The corrected targeted suite passed **18 tests** in **68.988 seconds**, including
six new regressions. The original HTTP/DOM cases still check citations,
clarification, scoped abstention, current/bookmarked withdrawals, independent
support/warnings, strict client fields, Host/Origin and read-only operations.
The complete maintained suite passed **914 tests executed: 913 passed, one
optional PDFium preview skip**, in **378.905 seconds**, with no failures or errors.

The source boundary and request lifecycle were reread against the accepted
single-writer/explicit-root contract. Both reproduced review findings are covered
by passing executable regressions. No further blocking discrepancy was
identified within this local scope after the complete suite and preservation
checks below. This is not an independent scientific
or answer-quality benchmark.

The localhost:8784 UI server alone was restarted to load the corrected Python
boundary, with its existing private root unchanged. Browser verification of a
normal documented result and E167-P source passed after restart. Timeout and
corruption scenarios were exercised in controlled DOM/temporary HTTP fixtures,
not by modifying or stalling the private project registry. Screenshots and full
logs remain private review artifacts.

## Preservation boundary

Only the new, unfrozen UI module/page, their tests and local usage/review documents
are corrected. `serving/local_registry.py`, the original frozen handoff/preview,
v03 and all source/human-review records remain unchanged. The private registry
must remain byte-identical, generation 1, withdrawal version 1, zero events.
Both original environment/inventory verifiers passed with their unchanged lock
digests. Raw before/after checks confirmed the private store, sixteen notes,
pilots and every pre-existing file outside the explicit correction scope are
unchanged. The old review records the previous candidate;
this correction report is its successor, not a rewrite of past evidence.

[Usage](../CYTIVA-REGISTRY-UI.md) ·
[Original review](MABSELECT-REGISTRY-UI-REVIEW.md) ·
[Local activation](MABSELECT-REGISTRY-V02-LOCAL-ACTIVATION.md)
