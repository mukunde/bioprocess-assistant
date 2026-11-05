# Chainlit MabSelect — corrections and re-review

Date: 5 November 2026. Base: `main` at `56a5552`, with the uncommitted
documentary candidate described in the [initial implementation report](CHAINLIT-MABSELECT-IMPLEMENTATION.md).
This report supplements that historical record; it does not replace its results.
No release, activation, scientific/source approval or Git operation is implied.

## Reproduced gaps and corrections

| Area | Reproduced gap | Corrected behavior and regression |
|---|---|---|
| Submitted scope | Rendered answers omitted the selected product/context and exposed machine item names. Changing Settings made earlier messages difficult to associate with a specific request. | Capture submitted controls before dispatch; display exact product label, explored context and human-readable question/outcome labels. `test_answer_identifies_submitted_product_context_and_questions` checks a SuRe LX request with cleaning and pressure. |
| Clarification | Cleaning plus pressure could repeat the same clarification and show internal target names. | Aggregate missing targets across items into one focused prompt, using exact-product/context labels; preserve all item outcomes, documentary context, citations and reservations. `test_combined_questions_have_one_focused_clarification` checks both questions with unknown product/context. |
| Initial outage | Failed startup returned before creating Settings and supplied no submit/retry action. The fixed error text said retry, but the ordinary control path was unavailable. | Publish controls before checking authority and retain an explicit manual retry action on failure. A later click rereads authority; it never repairs or activates it. `test_unavailable_start_has_controls_and_manual_recovery` verifies failure and recovery. |
| Invalid controls | Converting unvalidated settings could throw outside the error handler; malformed values could replace the last valid server-side controls. | Validate exact dictionary shape, string enums and actual booleans before storing controls. Invalid inputs revoke old actions and block dispatch until valid settings are confirmed. `test_malformed_settings_do_not_crash_or_replace_last_valid_controls` covers null, arrays, strings, unhashable fields, wrong switch types and authority-path injection. |
| Late source error | A source lookup failing after Settings changed could report a current registry outage against newer controls. | Check current state identity/revision and source token in the error path as well as the success path. Superseded results report stale state. `test_late_source_failure_does_not_report_outage_for_new_controls` covers a delayed failure. |
| Replaced state | Revision-only checks allowed an old in-flight answer to be published after replacement of session state with the same revision. | Require state identity and revision before publishing an answer or citation. `test_replaced_session_cannot_publish_an_old_inflight_response` verifies refusal and absence of revived old source tokens. |

All six new regression methods were executed against the previous candidate first:
the red run recorded ten failed assertions/subtests and two errors across the six
methods. Its ignored local log is retained. After correction, the focused adapter
and legacy app suite passed **30 tests** in **58.951 seconds**: 24 adapter tests
and six legacy app tests. No model or paid API was called; approved synthetic
authority exists only inside disposable test directories.

## Contract re-review

- **DS04/DS06:** rendering still retains complete conditions, alternatives, step
  ownership, original precautions and scoped reservations. Human-readable headings
  do not rewrite underlying quantities or reviewed source/review objects.
- **DS05 / RC2:** unknown remains unknown; product and explored context are now
  visible in the submitted response. Clarification retains supplied controls and
  does not demand a confirmed diagnosis or choose a substitute recipe.
- **DS07:** citation actions remain opaque and session-bound. Opening them calls
  the real registry source view afresh; original quotation, PDF page, offsets,
  digest and scoped review decisions remain inspectable.
- **DS08/DS09:** outside-release/pressure abstention remains scoped. Withdrawn
  support produces no new quote or incomplete recipe, while independent support
  remains available. Authority failure has no preview fallback or automatic
  activation, including during startup recovery.
- **TS06:** backend authority rechecks remain unchanged. The adapter additionally
  rejects superseded controls/session state before publishing returned content or
  contextual errors. Already delivered messages remain historical snapshots.

The six new regressions complement the existing tests for exact citations,
withdrawn old-release source actions, independent hydrophobic support, invalid
authority, empty selections, forged tokens, timeout, busy dispatch, ignored free
text and unchanged graph behavior. They are conformance checks over known evidence,
not an independent prospective answer-quality benchmark.

## Verification outcome

A new browser smoke used another synthetic temporary authority on loopback port
8787 and synthetic login credentials. It confirmed:

- Two questions with unknown product/context produce one focused missing-fields
  prompt and an explicit submitted-scope header, with documentary clarification
  context and review limits still available.
- A subsequent MabSelect SuRe LX / precipitated-or-denatured request retains that
  exact submitted scope and separate cleaning/pressure outcomes. General
  alternatives and the product-restricted sequence remain separate, with original
  conditions and reservations; pressure abstains without an invented limit.
- E167-S opens its original quotation, PDF page 167 and full provenance/scoped
  review element after a fresh authority check.

The console retained two `Unauthorized` entries at sign-in/startup; authenticated
operations completed. No error-free-console claim is made. Screenshots and raw
logs stay ignored and distinct from the first smoke. The browser tab and server
were closed and the temporary authority removed. Withdrawal, fault and manual-
recovery coverage comes from the callback/service tests, not a new browser
acceptance score.

Preservation checks verify byte-identical inventories for all nine private store
files, 636 files in the original workspace (including the 16 notes), and 109 active
pilot/previous-trial files. Both original freeze verifiers pass with their recorded
environment: v03 keeps 36 pins and MabSelect 52. Local documentation links and the
final preservation check are verified at completion. No original source, review,
result, freeze or release artifact is changed.

The complete maintained suite on the corrected candidate executed **1,015 tests:
1,014 passed, one optional PDFium preview skip**, no failures/errors, in
**664.905 seconds**. It includes all 24 adapter tests, six legacy app tests and
existing registry, tracing, UI, freeze and package regressions. Candidate code was
unchanged during that run. Timing is descriptive, not a performance comparison.

Re-review outcome: **no remaining blocking gap identified within this tested
local guided scope**. All six reproduced gaps have passing regressions. Original
implementation results, smoke logs and reviewed evidence are preserved. No commit,
push, private-store write or new activation was performed.

## Remaining scope limits

The shared Chainlit shell retains its generic LLM footer, README menu and upload
icon; this documentary route does not interpret free text or uploaded files.
The original MIME/sign-in diagnostics are retained in the initial report. These
are presentation/deployment follow-ups, not approval to change the default graph
UI or either frozen method. Only loopback development operation is documented;
public deployment, chat persistence/resume and a compatible trace-summary UI are
not claimed. Optional registry tracing remains metadata-only and best-effort.

See the [operator guide](../CHAINLIT-MABSELECT.md) for the corrected manual path.
