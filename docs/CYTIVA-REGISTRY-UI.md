# Opt-in MabSelect UI through the local registry

This separate loopback entry uses an explicitly configured `Registry` for both
responses and citation views. It never prepares, approves or activates authority.
The original documentary preview, v03, both freezes, existing launchers and
legacy chat remain unchanged. The new UI itself is outside those historical
freezes and has its own HTTP/DOM regression coverage.

## Start explicitly

From the checkout containing the already reviewed private local store, in the
prepared CPython 3.13.0 environment:

```powershell
.\.venv-demo\Scripts\python.exe -m demo.registry_ui --registry-root .local-tools\mabselect-registry-v02-runtime --port 8784
```

Open [127.0.0.1:8784](http://127.0.0.1:8784/). Stop with Ctrl+C. The root argument
is required and is server-side only; the request contract rejects client fields
such as `candidate`, `registry_root` and `data_root`. The process binds only to
127.0.0.1. No new Python/runtime dependency, model, paid API or public host is
needed. Existing development UI tests use the already locked Node/jsdom setup.

A fresh clone does not contain the private store. Pointing at missing, staged or
invalid authority leaves responses unavailable and creates nothing; it does not
select the historical preview as a fallback. Obtain a separately reviewed local
activation before expecting supported responses. The existing preview on port
8783 remains a distinct path and is not upgraded implicitly by this launcher.

## Short walkthrough

1. Select exact plain MabSelect and precipitated/denatured substances, keeping
   cleaning options checked. Submit: documented alternatives retain their
   conditions and reservations; no treatment is chosen as suitable.
2. Open an E167-P citation: inspect the exact excerpt, PDF page, provenance and
   original scoped review. This is a current-registry source lookup, not a PDF
   viewer or a model-generated reference. Return to the form using the source link.
3. Select an unknown family variant/context: clarification asks for the missing
   labels without demanding a confirmed diagnosis or choosing a recipe.
4. Select exact MabSelect with hydrophobic context, uncheck cleaning options and
   check numerical maximum pressure: abstention is limited to the selected
   reviewed excerpts, with no invented pressure or conversion.

Retractions are exercised only in disposable test stores. The tests withdraw
E167-P explicitly for both an older release and its successor, verifying that the
current recipe is held and an old bookmarked citation exposes no quotation.
Independent hydrophobic support and its solvent warning remain available. Events
are version-scoped; withdrawing an old edition alone is not an implicit event
against every successor. The real private store retains zero withdrawal events.

## Failure and display behavior

The active evaluation path has no `candidate=` override. Missing/corrupt authority
returns unavailable; source lookups refuse quotations if authority cannot be
verified. Held support is distinguished from information absent in the selected
excerpts, even when the frozen aggregate response status is `abstained`.
No frozen response enum, source, condition, quantity or reservation is changed.

New submissions clear previous procedures/citations before awaiting the response.
A 15-second deadline covers both the response and JSON-body parsing. Expiration
aborts the browser request, restores controls and asks the user to try again,
without automatic retry or preview fallback. A race with an explicit cancellation
promise also recovers if a transport ignores AbortSignal. Late responses cannot
replace a successful newer request. Timers are cleared after completion or
cancellation. This bounds UI waiting; it does not guarantee termination of work
already running on the local server.

Changing inputs during a request immediately cancels that display attempt and
restores controls. Changing inputs after a result marks it stale. Empty question
selection makes no request. Machine field names and authority diagnostics are kept in the
collapsed audit view; ordinary labels explain the requested information.

Host/Origin checks, strict JSON/size validation and no-store responses reuse the
frozen HTTP boundary. The new source renderer escapes source/review content and
adds framing/referrer protections. Unexpected source-validation/rendering errors
return a generic 503 with no quotation/details; only the exception class is logged
privately. An actually unregistered source is 404 only after authority validation.
No activation or write HTTP endpoint exists.
All response/source operations check the configured current authority; they do
not silently redirect a bookmarked source to a newer release. The accepted local
single-writer and interrupted-activation recovery limits still apply; UI delivery
does not add signatures, whole-store rollback detection or multiwriter support.

## Run the UI regressions

With the project verification environment and existing test dependencies:

```powershell
python scripts/run_tests.py --temp-root "$env:LOCALAPPDATA\Temp" tests.test_registry_ui
```

Use a short Windows temporary root (at most 60 characters). The tests create and
approve only synthetic, owned temporary stores. They never depend on, activate,
withdraw from or corrupt the private project registry. Loopback access must be
available; EACCES from a restricted execution environment is a test-environment
failure, not a reason to bypass authority validation or skip the tests.

The eighteen tests cover explicit configuration, real HTTP and shipped DOM/JS,
citations, clarification, scoped abstention, withdrawals of current/bookmarked
sources, independent support, missing/corrupt authority, client authority-field
rejection, Host/Origin checks, input-change handling and read-only operations.
Six added regressions cover malformed authority, unexpected source/render errors,
404/503 classification, timeout of a nonsettling fetch, late fetch results and
stalled JSON-body parsing. Deadline tests advance a controlled clock at the actual
15-second production setting; no real 15-second sleep or private-store fault is
required. Successful retry and timer cleanup are checked.
jsdom checks DOM semantics, not pixel layout; browser observations are recorded
separately in the [implementation report](validation/MABSELECT-REGISTRY-UI.md)
and [corrected pre-freeze review](validation/MABSELECT-REGISTRY-UI-REVIEW-FIXES.md).

See the [registry guide](../serving/README.md) and
[local activation record](validation/MABSELECT-REGISTRY-V02-LOCAL-ACTIVATION.md).
