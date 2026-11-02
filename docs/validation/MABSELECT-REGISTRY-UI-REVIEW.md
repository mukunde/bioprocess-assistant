# Pre-freeze review — opt-in MabSelect registry UI

Reviewed on 2 November 2026 against the six local implementation files on top of
merged `1af1b60`. No implementation correction, activation, real withdrawal,
commit or push is performed by this review.

## Findings requiring correction

### P2 — malformed authority disconnects citation requests

Location: `demo/registry_ui.py`, lines 60–67.
The source HTTP handler catches OSError, ValueError and RuntimeError but not all
exceptions that registry validation can raise on malformed authority. A disposable
approved/active store was changed to contain well-formed JSON `null` in its
release manifest. The normal POST correctly returned `invalid_authority` with
zero passages. GET of its existing E167-P citation instead raised an uncaught
TypeError in the server; the client observed RemoteDisconnected rather than a
controlled 503 source-unavailable response.

This remains fail-closed for quotations; no withdrawn/unverified quote was
observed. It is an error-containment and usability defect at the new HTTP boundary.
Existing tests remove the pointer but do not exercise this malformed-shape case.
Correct the outer source-error boundary without modifying frozen registry/core
files. Distinguish an actually unregistered source from validation/backend failure;
return a generic controlled failure, with no exception details or private paths.
Add regression coverage for malformed authority types and unexpected source
backend exceptions, retaining the unknown-source behavior.

### P2 — a nonsettling request leaves the UI permanently pending

Location: `demo/static/registry.html`, lines 16–25.
The shipped fetch has neither an AbortSignal nor a recovery deadline. Its finally
block restores the button only once the promise settles. A jsdom probe of the
actual shipped script used a fetch that never resolves: submit remained disabled,
the checking message remained visible, no abort signal was provided and no
recovery timer was scheduled. This can happen if a local request/registry lock or
connection stalls; the server's body-read socket timeout does not bound the whole
request or client wait.

Add a bounded, clearly messaged request deadline/cancellation path, restoring
controls and clearing old procedures/citations without preview fallback. Ensure
late responses cannot overwrite a newer request and clear timers after success,
input change or failure as appropriate. Test a never-settling/late request and
successful retry. The existing stale-input test releases its response eventually;
it does not cover this case.

## Conformance already observed

The unchanged twelve HTTP/DOM regressions pass again (46.459 seconds), covering:
explicit server-side root configuration; correct source text and reservations;
clarification without selecting a recipe; scoped pressure abstention; held current
and bookmarked sources after explicit old/new-version events; independent support
and solvent warning; missing authority with no preview fallback; Host/Origin and
client authority-field rejection; read-only request behavior; and input changes
while a response is pending.

Both reproductions above are outside those tests and explain why a passing suite
is insufficient to approve this candidate unchanged. The earlier complete run
of the exact unchanged implementation passed 908 tests: 907 passed and one
optional PDFium skip. That historical run was not repeated for a documentation-only
review. Its file identities were checked against the implementation verification.

## Preservation and boundary

All test approvals, corruption and withdrawals occurred in owned disposable
stores. The private active store remains byte-identical, generation 1, withdrawal
version 1, zero events. Both original freeze/environment verifiers pass unchanged;
the sixteen old notes, pilots and every pre-existing file remain unchanged.
Private review probes/logs are diagnostic artifacts and are not runtime inputs.
No new source approval, scientific validation or answer-quality score is implied.

Review conclusion: two P2 error-handling/recovery gaps should be fixed before
freezing or versioning the UI candidate as reviewed. No defect was reproduced in
normal citation fidelity, clarification, scoped abstention or withdrawal filtering.
The original [implementation report](MABSELECT-REGISTRY-UI.md) remains a historical
implementation/test checkpoint; this subsequent review records the additional gaps.
