# Cytiva second-PC result sheet

**Blank template — not executed.** Copy this sheet to the tested clone's ignored
`.local-tools/second-pc-validation/results.md` (or fill the supplied copy outside
the clone). Follow the supplied `WINDOWS-SECOND-PC.md` protocol v01; keep this
master blank. The protocol is a separate supplied file because it is newer than
the pinned application revision.

## Run identity

| Field | Observed value |
|---|---|
| Date/time and timezone | TO_FILL |
| Tester / machine alias | TO_FILL |
| Different physical PC from the original workstation? | TO_FILL: yes / no / unknown |
| Windows edition, build and architecture | TO_FILL |
| PowerShell version / edition | TO_FILL |
| Browser / version | TO_FILL |
| Python actual version / architecture | TO_FILL |
| Python discovery: automatic or explicit path? | TO_FILL |
| Git version | TO_FILL |
| Expected commit | 3c19e24aa8dbd04bcb827c1314fafeebed3529bf |
| Actual `git rev-parse HEAD` | TO_FILL |
| New clone with no first-PC environment/cache copied? | TO_FILL |
| Primary online path or separate offline variant? | TO_FILL |
| Existing pip cache reused? | TO_FILL: yes / no / unknown |
| Installation duration, excluding prerequisite setup | TO_FILL |
| Timed walkthrough duration, excluding installation | TO_FILL |
| Port / local URL | TO_FILL |
| Retry count and reason | TO_FILL |

## Mandatory observations

Use `PASS`, `FAIL`, `BLOCKED` or `NOT_RUN`. Keep the observation column factual;
the Expected column does not establish success. Reference the relevant log or
screenshot filename and preserve initial failures when a retry succeeds.

| ID | Expected | Status | Actual observation / evidence / retry |
|---|---|---|---|
| P01 | Different Windows x64 PC, exact pinned commit, Python 3.13.0 x64, fresh clone and empty initial status | NOT_RUN | TO_FILL |
| P02 | Installer exits 0; twelve dependencies installed in clone-local `.venv-demo`; `pip check` passes | NOT_RUN | TO_FILL |
| P03 | Tokenizer prepared without copying first-PC cache; SHA-256 matches frozen value | NOT_RUN | TO_FILL |
| P04 | Launcher CheckOnly exits 0, selects `.venv-demo`; readiness true, 12 dependencies, 36 pins, environment verified | NOT_RUN | TO_FILL |
| W01 | Default 1 mL washing: support/context 1/1, five citations, source navigation and warning retained | NOT_RUN | TO_FILL |
| W02 | Combined washing: stale notice then support/context 3/3, complete shared sources | NOT_RUN | TO_FILL |
| W03 | Mixed request: supported / missing / quarantined; support 1/3 versus context 1/1; excluded contents absent | NOT_RUN | TO_FILL |
| W04 | Unspecified format: clarification, support 0/1, no eligible context/bundle, correction button focuses format | NOT_RUN | TO_FILL |
| W05 | Explicit 5 mL: support 1/1, 5 mL binding, both source formats retained | NOT_RUN | TO_FILL |
| W06 | French example: support 1/1, 1 mL binding, original English quotes; all walkthrough responses show 0 calls / EUR 0 | NOT_RUN | TO_FILL |
| C01 | Ctrl+C returns command prompt; browser reload cannot reach this test server | NOT_RUN | TO_FILL |
| C02 | Final freeze/environment check passes; tracked diff and Git status empty | NOT_RUN | TO_FILL |

## Optional observations

| ID | Expected | Status | Actual observation / evidence |
|---|---|---|---|
| W07 | Coordinated French buffer purposes: inventory incomplete, clarification, no admitted bundle | NOT_RUN | TO_FILL |
| O01 | Repeating installation reports Already ready without reinstalling packages | NOT_RUN | TO_FILL |

## Actual diagnostics

- Exact failing step, inputs and exit code: TO_FILL
- Error text and log filename: TO_FILL
- Changes/retries used, preserving the original failure: TO_FILL
- Source or quotation differences, if any: TO_FILL
- Model/API/Neo4j dependency unexpectedly requested, if any: TO_FILL
- Usability observations (distinguish blockers from preferences): TO_FILL

## Overall result

- **Overall status: NOT_RUN** (`PASS` only when all twelve mandatory rows pass).
- First-attempt or successful retry: TO_FILL
- Installation blockers: TO_FILL
- Source/scope/clarification/quarantine blockers: TO_FILL
- Remaining items: TO_FILL
- Evidence attached: TO_FILL (`install.log`, `launcher-check.log`, `readiness.json`,
  `tokenizer-hash.txt`, `freeze-after.json`, optional screenshots/retry logs).
- Reviewed by / date / disposition: TO_FILL

This sheet records one machine's observations. It does not establish whole-manual
coverage, generated-answer quality, prospective language performance or GxP
qualification. Leave the result NOT_RUN if only the first PC was used.
