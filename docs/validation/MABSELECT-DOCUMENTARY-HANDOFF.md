# Minimal MabSelect documentary handoff

Implementation and local verification: 2026-11-02. This is a working development
preview, not an activated serving release or a scientific validation.

## Run

From the repository root, using the prepared Python environment:

```powershell
.\.venv-demo\Scripts\python.exe -m demo.documentary_preview --port 8783
```

Open <http://127.0.0.1:8783/>. The implementation uses the Python standard library
and the existing reviewed MabSelect selector. It makes no model/API calls, graph
writes, downloads or release activation. The verification checkout used its
existing `.local-tools/verification-venv` environment instead of `.venv-demo`.

## Delivered slice

- `demo/documentary.py`: typed documentary handoff using the actual selector,
  accepted serving decisions and the original scoped reviews.
- `demo/documentary_preview.py`: loopback-only HTTP entry point and version-bound
  source views; strict request shape, body limit, Host and Origin checks.
- `demo/static/documentary.html`: existing product/category choices, original
  quotations, visible conditions and reservations, clarification and scoped
  abstention. No automatic choice between treatment alternatives.
- `tests/test_documentary_handoff.py`: 18 regression tests including real local
  HTTP requests, the six accepted interface examples, per-item isolation, missing
  warnings, withdrawals, authority drift, atomic budgets and HTML escaping.

The default Python service is disabled (`Handoff()` returns
`release_not_activated`). The dedicated preview explicitly opts in on the server;
a client cannot activate it. A staging identifier binds source links to the
loaded authority, implementation and preview configuration. Changed dependencies
invalidate that staging context instead of silently falling back.

Original PDF identifiers, page indices/labels, extraction version, offsets,
quote hashes, original human decisions and reservations travel with the context.
The source page displays the original excerpt and scoped review, not the PDF.
Application notes are visibly labelled separately from original reservations.

## Browser verification

1. MabSelect + precipitated/denatured context: four separate formulations remain
   in their original numbered block, with the minimum contact time and immediate
   follow-up wash. No formulation is selected as suitable.
2. Family with unknown variant: requests the exact product, shows documentary
   clarification context and no recipe. The edit action focuses the product field.
3. SuRe LX + hydrophobic context + numerical pressure: preserves the alternative
   detergent/solvent routes and warnings, while abstaining only on the unsupported
   numerical pressure. The absence statement is limited to selected excerpts.
4. E167-W citation: opens the original warning, PDF page 167, provenance controls
   and the original review reservations. No browser console warnings/errors were
   captured during this traversal.

Browser back navigation resets the displayed answer; the selected fields remain
and resubmitting reconstructs it. Persistent browser history is outside this slice.

## Initial implementation verification and limits (before corrections)

The 18 targeted tests passed. Actual outputs for SX01–SX06 and an E167-W source
view also passed the prepared Draft 2020-12 JSON Schemas using local resolution.
The complete maintained suite passed: 848 tests, no failures or errors, one skip
for the optional PDFium preview dependency (1,843.359 seconds in this run).
Command used:

```powershell
.\.local-tools\verification-venv\Scripts\python.exe scripts/run_tests.py --temp-root C:/Users/gaelm/AppData/Local/Temp
```

Raw SHA-256 checks preserved all 650 pre-existing Git-visible files, including
the design documents, selector and pilot assets. The 16 excluded historical notes
were unchanged. Frozen v03 verification passed with its original 36 pins and
method-lock digest `9c1cddca92b885ab03d7f68f012847f876ace62e6a5f32d8eaa042684aaf46f7`.

This intentionally does not implement a production active-release registry,
automatically refreshed withdrawal authority, general free-text synthesis or
independent scientific validation. Withdrawals are trusted staging configuration
exercised by regression tests. Quantities remain verbatim in original passages
and steps; the machine `quantities` arrays remain empty, so consumers must not
interpret them as a numerical extraction or calculate dosages from them.
E118-I and E121-EQ are not admitted. No existing freeze or pilot is modified.

## Corrected implementation — review before freeze

The subsequent code review identified three gaps. All three are corrected without
changing the selector, original evidence/reviews, frozen v03 or the pilots:

1. **Exact task/context association.** Each item now emits response-local
   `bundle_refs` resolving to its exact context objects. Identical keys across
   MabSelect and SuRe no longer require guessing which object belongs to a task.
   Q09 clarification context is explicitly referenced without counting it as a
   supported procedure. Identical objects remain shared, preserving deduplication
   and atomic budget allocation. Product/category and exclusion origins are
   retained. The preview displays the task owners derived from these references.
2. **Unexpected errors contained.** A selector exception such as `RuntimeError`
   becomes `unavailable` for that task's requested items, with no repeated lookup
   and no loss of independent valid tasks. Item assembly is similarly contained;
   tentative incomplete alternative sets are not delivered. Known shared-authority
   failures still invalidate the whole request. Server-side diagnostics record
   the failure boundary and exception class without the exception message or
   request contents. Cancellation/process-exit exceptions are not swallowed.
3. **Immediate force preserved.** N07 now retains `Wash immediately` in
   `force_text`, along with the unchanged original wording and predecessor link.
   The other following washes retain their original `Immediately wash` wording.

Six regression tests were added (24 documentary-handoff tests in total). The
combined targeted verification passed **48 tests**, no skips/failures/errors:

```powershell
.\.local-tools\verification-venv\Scripts\python.exe scripts/run_tests.py --temp-root C:/Users/gaelm/AppData/Local/Temp tests.test_documentary_handoff tests.test_mabselect_journey tests.test_mabselect_ui tests.test_free_text_v03_freeze
```

The nine machine schemas remain valid; the original 32 synthetic structural
fixtures retain their expected results. Eight actual response cases passed local
schema validation, including SX01–SX06, cross-product tasks and clarification.
The schema extension is additive; the old design decisions/fixtures are retained.
The earlier complete-suite result above is historical, not a new complete-suite
run after these corrections.

Browser checks on the corrected preview confirmed explicit Task A attribution
for Q09 clarification, hydrophobic alternatives with scoped pressure abstention,
and resolution of the original E167-W citation with its reservations.

Review conclusion: no remaining blocking discrepancy found for this minimal
staging slice. It is ready to prepare a local freeze, not automatically frozen
or activated. Production release/withdrawal authority and parsed numerical
annotations remain deferred as described above. No old result is overwritten.
