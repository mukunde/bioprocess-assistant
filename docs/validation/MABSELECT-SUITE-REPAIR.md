# MabSelect integration-suite repair

Prepared on 1 November 2026 after the [first package check](MABSELECT-CLEANING-PACKAGE.md). This is a test/documentation integration repair, not a new extraction, scientific review, score or runtime freeze.

## Retained first result

The initial complete-suite run remains retained: 826 tests, three failures, eleven errors and one optional PDFium skip, 417.641 seconds. Its private log has not been overwritten. Five failure/error entries concerned stale root README bindings; eight concerned long Windows temporary paths (including subtest entries); one was a Node subprocess timeout. The timed-out product-payload mutant passed when rerun alone in 7.138 seconds; the earlier targeted 40-test rerun also passed.

## Documentation bindings

Only documentation support hashes were updated in three historical manifests: compositional navigation v04, reviewed v05, and the containing free-text v02 manifest. They bind the current root README, current test guide and the two updated nested manifests. Source data, method locks, frozen code, human decisions and recorded results are unchanged. These are current support-document digests, not a rewrite of old experimental outcomes.

## Windows temporary fixtures

The failed run forced tempfile into a long directory inside an already deep worktree. Nested input snapshots exceeded the Windows path budget, producing WinError 3/206. The new [maintained runner](../../scripts/run_tests.py) accepts `--temp-root`, rejects Windows roots longer than 60 characters before starting the suite, and allocates a unique child. It restores Python's previous tempfile setting on both success and failure and removes only its owned child, preserving existing root files. It does not change system TEMP, long-path registry policy or Windows security protections.

Use the environment's Python and a short writable root:

```powershell
python scripts/run_tests.py --temp-root "$env:LOCALAPPDATA\Temp"
```

Three regressions exercise nested fixture creation, preservation/cleanup and state restoration, including failure and an oversized Windows root. Existing frozen test files and synthetic runner behavior are unchanged.

## DOM timeout analysis and mitigation

The original Python traceback reports a subprocess wait timeout with a negative remaining duration (`-161.9022788000002` seconds). This is consistent with a substantial scheduling interruption, but the retained diagnostics do not prove a unique cause. The same mutant subsequently passed; no incorrect-product success was observed.

The original harness polled the event loop via setImmediate while awaiting HTTP/DOM completion, and fetch itself had no abort deadline. It now yields 10 ms between checks, bounds page/API fetches at 8 seconds below the existing 10-second submission deadline, and records request dispatch/completion. The Python timeout failure reports mutation and partial stdout/stderr. The 40-second process ceiling is unchanged; timeouts still fail, and tests are not retried automatically. A regression verifies that a simulated timeout cannot be counted as a successful mutation witness.

These changes improve resource usage and diagnosis. They do not claim that scheduling pauses can never recur or that timing alone establishes UI correctness.

## Validation

The targeted repair run exercised 74 tests: all path and DOM cases passed, with one remaining nested-manifest binding failure. After updating that enclosing documentation digest, its isolated regression passed. The subsequent complete-suite result is recorded below. Previous failed logs and historical scores remain distinct.

## Complete-suite result after repair

The maintained runner executed **830 tests: 829 passed, one optional PDFium preview skip, zero failures and zero errors**. Unittest reported 118.291 seconds for execution; the complete invocation including suite loading took 447.824 seconds. The longer outer duration is recorded separately and is not evidence of a unique cause for the earlier DOM timeout.

All original MC01–MC12 checks, the six real DOM/mutation checks, the timeout-diagnostic regression, the temporary-workspace regressions and the historical manifest checks were included. The original failed 826-test run remains retained separately. No source reference was rescored, no skipped test was added and the existing optional skip was not changed.

Frozen v03 and its environment still verify all 36 pins. The sixteen excluded notes, both Flowshot pilots, existing videos and all unrelated local files retain their pre-task hashes. This repair does not modify the MabSelect application implementation, approved human decisions, source dossier or original runtime freeze.
