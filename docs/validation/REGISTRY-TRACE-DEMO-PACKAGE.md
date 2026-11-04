# Corrected reusable trace demo delivery

Prepared on 4 November 2026 against main `f7ce8066c58a7ba4d17e86c64c8e2728409f16b8`. This is an additive local implementation candidate, outside both frozen closures. It reuses registry UI v02, with explicit approved authority and no automatic activation.

## Explicit nine-file inventory

| File | Purpose |
| --- | --- |
| `demo/registry_demo.py` | Separate loopback launcher on port 8786, new session filenames and summary navigation; failure-safe optional SDK metadata check. |
| `demo/trace_summary.py` | Bounded read-only HTML/terminal metadata summary; controlled HTTP-error vocabulary and neutral root-only rejection handling. |
| `tests/test_trace_demo.py` | 18 tests covering confidentiality, read-only behavior, real HTTP/baseline equality, errors, startup and cleanup. |
| `docs/REGISTRY-TRACE-DEMO.md` | Short Windows setup/operator guide and limitations. |
| `docs/validation/REGISTRY-TRACE-DEMO-IMPLEMENTATION.md` | Historical initial implementation verification and focused browser smoke. |
| `docs/validation/REGISTRY-TRACE-DEMO-REVIEW.md` | Historical review with two reproduced P2 findings before correction. |
| `docs/validation/REGISTRY-TRACE-DEMO-CORRECTIONS.md` | Both fixes, regression details and final complete-suite evidence. |
| `docs/validation/REGISTRY-TRACE-DEMO-PACKAGE.md` | This inventory and delivery assessment. |
| `docs/validation/REGISTRY-TRACE-DEMO-PACKAGE.json` | Explicit file list, compact checks and LF-normalized delivery hashes, excluding its own digest. |

## Behavior and review outcome

The new entry leaves baseline UI/static files, request JSON, citation HTML and authority rules unchanged. It adds a link to the configured local session summary. The reader accepts no browser-selected path, makes no export/activation call, displays allowlisted metadata only and does not trace its own refreshes. A standard-library-only CLI provides the same summary.

Both review findings are addressed: valid controlled GET/POST error spans remain visible, and a rejected evaluation/source root without a recorded child is labeled root-only without inventing dispatch or lost telemetry. Unexpected optional SDK-metadata failures produce a fixed diagnostic and do not prevent serving; invalid authority still refuses startup.

The original review's “not ready” assessment describes the pre-correction candidate. The [correction report](REGISTRY-TRACE-DEMO-CORRECTIONS.md) records the final behavior. The [initial implementation report](REGISTRY-TRACE-DEMO-IMPLEMENTATION.md) and [review](REGISTRY-TRACE-DEMO-REVIEW.md) remain unchanged, preserving their original counts and findings.

## Tests and verification

- Final complete suite: **991 executed, 990 passed, one optional PDFium skip, zero failures/errors**, in 551.299 seconds; all 18 demo tests and 28 existing tracing tests passed.
- The corrected targeted module passed 18 tests. The final seven-case HTTP test was additionally run after adding inside-registry validation; this is overlapping coverage, not 19 distinct tests.
- The earlier focused browser smoke verified request → E167-P → summary on disposable synthetic authority, 5 HTTP requests / 7 spans and no new spans on refresh. It preceded the two error-path corrections; no post-correction browser rerun is claimed. Real HTTP and launcher regressions cover the corrected behavior.
- Packaging verifies current runtime/test bytes against the final test record, result-log digests, local documentation links, metadata-only scope and preservation. No new complete-suite run or browser trial is needed for this inventory-only step.
- Both frozen inventories verify with their environment (36/52 pins). Private registry bytes/inventory, 16 old notes, both pilots, earlier raw walkthrough evidence and all pre-existing tracked files remain unchanged. HEAD and index are unchanged.

Ready for an explicitly scoped commit of these nine files. There is no new freeze, independent acceptance score, source approval, private-registry mutation or legacy-chat integration in this delivery.

## Exclusions and limits

Exclude raw HTTP response recordings, raw JSONL spans, test-only smoke/probe runners, temporary controls, all private authority, both frozen closures, 16 old notes, both pilots, prior raw acceptance trials, dependencies, caches and PDFs. README and roadmap are not part of this lot. Raw evidence stays ignored; the compact JSON retains its digests without copying it.

Metadata still reveals usage times and source/release identities; retain sessions locally. The reader is bounded, best effort and may show pending/partial records. It is not a durable audit, production benchmark or model-cost monitor. Optional OTel packages remain top-level pins rather than a complete wheel-hash closure. A fresh clone requires its own verified runtime/cache and approved authority; the normal launcher never manufactures synthetic approvals.

## Proposed Git metadata

Branch: `codex/registry-trace-demo`

Commit subject:

```text
feat(demo): add reusable local request-source-trace walkthrough
```

Suggested body:

```text
Add a separate registry demo and read-only metadata summary for browser and terminal.
Preserve source responses and authority checks with no automatic activation.
Handle controlled HTTP rejections and optional SDK metadata failures safely.
Add 18 tests and record the successful 991-test run with one optional skip.
```

See the [operator guide](../REGISTRY-TRACE-DEMO.md) and [Git instructions](../../AGENTS.md). Preparing this package does not stage or publish files.
