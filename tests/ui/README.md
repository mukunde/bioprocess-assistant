# Cytiva UI regressions (MC12)

Development-only dependencies, separate from the twelve Python runtime packages
and frozen v03. The demo installer/launcher and end users do not need Node or npm.
The maintained full test suite now requires these test tools explicitly; missing
Node/jsdom fails with a preparation error rather than silently skipping MC12.

Prerequisites: Node.js >=22.12.0 (verified with 24.16.0), npm, and the prepared
Python verification environment. From the repository root:

```powershell
npm ci --prefix tests/ui --ignore-scripts --no-audit --no-fund
python -m unittest tests.test_mabselect_ui -v
python -m unittest tests -v
```

Use the prepared Python executable if `python` resolves to another environment.
The first command installs test dependencies from `package-lock.json`; test runs
use only loopback HTTP. `node_modules` is ignored and is not a versioning artifact.
No model/API/database calls, browser download or runtime dependency change.

The harness fetches the real page from a temporary `HTTPServer` using the actual
`Demo` and handler, executes its shipped inline JavaScript with jsdom, dispatches
form/change/click events and inspects the resulting DOM. Its fetch bridge forwards
real JSON requests to that server, checks exact product/context payloads and rejects
other destinations. It does not mock response objects from the selector. No remote
scripts or resources are loaded. Only the local trusted application HTML is evaluated.

It checks family clarification/focus; plain-product alternatives; separate SuRe
blocks; stale-result handling; SuRe LX hydrophobic context and both precautions;
source/return anchors; mixed-context clarification; and return to guided/v03 and
Protein A/G routes. Five in-memory mutants remove the entry, miswire product,
disable stale detection, omit the rendered pressure quotation or break source
links. Each must make the UI regression fail at the relevant assertion. The
unmodified control must pass, so unrelated startup failures cannot count as a
successful overall run.

jsdom executes DOM behavior, not visual layout or a full browser. The sole layout
shim is `scrollIntoView`; focus, selection, events, hash changes and rendering are
executed. Anchor checks wait for the expected hash rather than assuming immediate
navigation. Actual browser checks remain separate; the unchanged page was already
checked through the in-app browser. See the upstream
[jsdom documentation](https://github.com/jsdom/jsdom) for its DOM and script model.

Portable approval verification is independent of Node/jsdom:

```powershell
python -S -m experiments.cytiva.verify_mabselect_design
python -m unittest tests.test_mabselect_design_integrity -v
```

The verifier checks three immutable artifacts: the exact approved contract, source
dossier and original human-decision record. It accepts LF/CRLF and never requires
an ignored audit file or PDF. New changes require a new explicit approval/version;
existing approved digests are not regenerated automatically.

## Timeout diagnostics

The Node subprocess retains its 40-second ceiling. Initial page and API fetches
have 8-second abort deadlines, below the 10-second submission deadline. Each API
request logs dispatch and completion to captured stderr; the Python failure
includes those diagnostics on timeout. DOM polling yields for 10 ms rather than
spinning on setImmediate. A timeout remains a failing test, never an accepted
mutation witness, and no automatic retry is performed.
