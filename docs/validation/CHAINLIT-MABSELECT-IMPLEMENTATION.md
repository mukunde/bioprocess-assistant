# Chainlit MabSelect documentary integration — candidate

Date: 4 November 2026. Base: merged `main` at `56a5552` (PR88).
This is an uncommitted implementation, not an activated private service, runtime
freeze, independent prospective acceptance trial or scientific validation.

## Behavior and scope

`app.py` routes server-selected `BIOPROCESS_MODE=mabselect` sessions to
`demo/chainlit_mabselect.py`. Missing/`graph` retains the original graph route;
any other configured mode refuses documentary service instead of calling the
model. Model import is lazy and only occurs on the graph route. The existing
authentication callback is retained. A fresh-process import check confirms that
neither `agent` nor `anthropic` is imported at application startup.

The adapter uses the existing `Registry.evaluate`/`Registry.source` contracts,
without candidate overrides, preparation, activation or preview fallback.
Guided selections cover the same seven product and four context values as UI v02,
with separate cleaning/pressure questions. Initial product/context are unknown.
Text input gives instructions only. No browser value selects an authority path.

Rendering keeps conditions, alternatives, steps, attached original precautions,
source IDs and scoped reservations. Pressure absence remains bounded to the
selected excerpts; outside-release product refusal does not infer incompatibility.
Clarification names missing controls without demanding a confirmed diagnosis.
The existing approved selector determines support; no new retrieval/interpreter
or model-generated procedure is introduced.

Opaque session-bound source actions resolve current withdrawal authority even
for old-release citations. Complete original text, page/offset/digest provenance
and scoped review decisions are retained in an inline JSON element. Invalid or
held authority supplies no new quotation. A later withdrawal cannot erase
messages already seen: the UI labels responses as historical snapshots.

Settings changes invalidate older actions and discard in-flight stale results.
Empty/invalid selections do not dispatch. Busy requests reject duplicate dispatch;
15-second waits discard late results and offer manual retry. Read-only worker
threads can finish after cancellation. Errors use fixed text without internal
details. Optional tracing reuses metadata-only, fail-open registry instrumentation;
there is no HTTP trace-schema compatibility claim for this Chainlit entry point.

## Verification evidence

The new test module covers sourced support, all displayed warnings/reservations,
exact source/provenance preservation, focused clarification, pressure and
outside-product abstention, old/current-release withdrawal, independent support,
missing/invalid authority, unknown mode, malformed controls, stale/forged/cross-
session actions, ignored free text, contained errors, busy dispatch, late results,
timeouts and literal-text escaping. All registry fixtures are disposable synthetic
authorities. Network connections are blocked and the graph agent is replaced with
a failing guard. Tests capture transport while retaining real Chainlit callbacks,
elements and registry behavior.

The first test-harness attempt replaced the `socket.socket` class, which broke
Windows ProactorEventLoop's type check; the guard now patches `connect` instead.
The first completed focused run had one test failure because no Chainlit context
had been initialized for a citation element. Initializing the same HTTP context
used by existing app tests fixed the fixture. The unchanged application then
passed the 22-test focused run (16 new tests plus six legacy app tests). Two more
regressions for timeout and busy dispatch were added before the complete run.
No Windows protection or application timeout was weakened.

Complete maintained suite: **1,009 executed, 1,008 passed, one optional PDFium
preview skip**, no failures/errors, in 615.763 seconds. It includes the 18 new
adapter tests and all existing graph/registry/UI regressions. During that run,
the literal-text escape helper was adjusted to retain apostrophes/double quotes
without numeric HTML entities; its existing markup test gained a corresponding
assertion. The final **24-test focused run** (18 adapter + six legacy app tests)
passed on that final source in 45.162 seconds. The broad run predates that final
one-line escape adjustment; the focused rerun verifies it. Timings are descriptive,
not controlled performance measurements.

Both original freeze verifiers passed with their recorded environment: v03 retains
36 pins and MabSelect retains 52. Byte hashes match the previous inventories for
all nine private-registry files, 636 files in the original workspace (including
the 16 excluded notes), and 109 active pilot/previous-trial files. No original
claim, review decision, experiment result, manifest or README was rewritten.
The new guide's local links resolve, and the tracked diff has no whitespace errors.
The synthetic browser server stopped and its temporary authority was removed.
No commit, push, private activation or public publication was performed.

## Browser smoke on synthetic authority

A separate loopback Chainlit process on port 8787 used a temporary, explicitly
synthetic activated release and synthetic test login. It did not read the private
verification store. The browser verified:

- Startup notice and Settings with unknown product/context defaults.
- Exact unsuffixed MabSelect + precipitated context, cleaning and pressure selected:
  supported cleaning plus pressure abstention; four alternatives, conditions,
  Q05 reservations and E167-H/PH/P citation buttons visible.
- E167-P source click: original quotation, PDF page 167 and complete provenance/
  scoped-review JSON rendered in Chainlit.
- Product changed to family/variant unknown: product clarification retained the
  selected context and did not infer an exact variant or procedure.

This is a focused known-source smoke, not the UA acceptance trial repeated or an
independent score. Withdrawals and authority faults were exercised by automated
callback/service regressions, not by modifying private authority. The narrow
browser viewport was observed; full source/provenance output requires scrolling.
The inherited Chainlit shell still shows a generic LLM footer, README menu and
upload icon; this adapter does not interpret uploaded files or free text. Existing
`*/*` upload configuration emitted MIME warnings in the browser; it was not changed
as part of this integration. The console retained three `Unauthorized` entries
during sign-in/startup; the authenticated guided request, source rendering and
clarification subsequently completed. These shell diagnostics are retained rather
than reported as an error-free browser run. Public-deployment hardening is outside
this loopback candidate.

See the [local operator guide](../CHAINLIT-MABSELECT.md). Local raw logs, screenshots
and synthetic fixture launcher stay ignored; no credentials or authority are
included in the delivery sources.
