# Guided MabSelect documentary mode in Chainlit

Local opt-in integration with the existing approved registry service. It uses
guided product/context controls and deterministic reviewed bundles, without a
model, paid API, Neo4j request, new interpreter or automatic activation. The
default graph chat stays unchanged when `BIOPROCESS_MODE` is absent or `graph`.
This working-tree candidate is not a new freeze or a published live service.

## Start locally

Use the existing development/verification environment with Chainlit installed,
not either frozen runtime. No dependencies are installed automatically. An
already reviewed, approved active registry is required; a fresh clone does not
include private authority. See [registry prerequisites](CYTIVA-REGISTRY-UI.md).

In PowerShell at the repository root, using the prepared verification environment:

```powershell
$env:BIOPROCESS_MODE = 'mabselect'
$env:MABSELECT_REGISTRY_ROOT = 'C:\path\to\your\approved-registry'
$env:DEMO_USERNAME = Read-Host 'Choose a local login name'
$localPassword = Read-Host 'Choose a local login password' -AsSecureString
$env:DEMO_PASSWORD = [System.Net.NetworkCredential]::new('', $localPassword).Password
$env:CHAINLIT_AUTH_SECRET = & .\.local-tools\verification-venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
.\.local-tools\verification-venv\Scripts\python.exe -m chainlit run app.py --host 127.0.0.1 --port 8787
```

These prompts work in Windows PowerShell 5.1 and PowerShell 7. Keep credentials out of Git
and screenshots. No Anthropic key is needed. Use the same local credentials at
[localhost:8787](http://127.0.0.1:8787/). This reuses the application's existing
password authentication and configuration; it is a loopback development run,
not a hardened public deployment. Do not expose it with a tunnel or public bind.

Optional metadata-only registry-operation traces can be enabled **before startup**:

```powershell
$env:MABSELECT_TRACE_FILE = "$env:TEMP\mabselect-chainlit-$([guid]::NewGuid().ToString('N')).jsonl"
```

The existing optional OTel dependencies must already be present for export.
The sink creates a new file only and refuses paths inside authority. SDK/export
failures do not block registry support. No free text, source quotations, login
credentials or exception messages are trace attributes. These are registry-operation
spans, not the HTTP-span schema of the separate port-8786 summary; that reader is
not asserted compatible with this entry point. Tracing is disabled by default.
Chainlit's own session/display data is separate from this telemetry guarantee.

## Five-minute operator check

1. Open **Settings** beside the message composer. Choose the exact unsuffixed
   MabSelect product and precipitated/denatured context. Keep cleaning enabled;
   submit with **Find documented guidance**. The response identifies the submitted
   product, explored context and questions independently of later Settings changes.
   Check separate options, conditions,
   original precautions and review reservations. Product/context selections are
   a context to explore, not a diagnosis.
2. Click a source button. Check the complete original quotation and PDF page.
   The inline JSON element retains original text, offsets, source hashes and
   scoped review decisions. The PDF itself is not served. Every click rereads
   current authority, including old-release withdrawals.
3. Change the product to family/variant unknown. Submit again: clarification
   identifies missing fields once across both questions and asks you to edit Settings. Supplied fields stay
   selected; no confirmed diagnosis or substitute recipe is required.
4. Ask for numerical maximum pressure in a known hydrophobic context. Cleaning
   may remain supported while pressure abstains. The absence is bounded to the
   selected reviewed excerpts, never the whole manual. For another product, no
   procedure is supplied and incompatibility is not inferred.
5. Withdrawals are exercised by regression tests in disposable synthetic stores,
   not by changing approved private authority. Held sources reveal no new quote;
   unrelated supported tasks retain their sources and warnings.

Text messages only explain how to use controls; they never dispatch a lookup.
Settings changes invalidate prior source/submit actions. Submissions have a
15-second wait limit; late results are discarded and retry is manual. A timed-out
read-only worker may finish in the background. Errors have fixed wording without
internal paths/details. Missing/invalid authority has no preview fallback.
Controls and an explicit submit/retry button also remain available when the
initial authority check fails. Once the operator has restored legitimate authority,
retry manually; the application does not repair or activate it. Malformed settings
invalidate old actions, retain the last valid server-side controls and require a
valid confirmed selection before any new lookup. Late answers or source errors
from superseded controls/session state are reported as stale, never as a new
answer or current outage.

Chat messages and already opened source elements are **historical snapshots**.
Withdrawal cannot erase text already seen. Resubmit and reopen a source for a
fresh check. This is documentary fidelity, not operational authorization or
independent scientific validation. No data layer/resume behavior is added.

## Return to the existing graph chat

Stop the server, remove the documentary settings, then relaunch the existing chat:

```powershell
Remove-Item Env:BIOPROCESS_MODE, Env:MABSELECT_REGISTRY_ROOT, Env:MABSELECT_TRACE_FILE -ErrorAction SilentlyContinue
```

Only the explicitly selected graph route may call the existing model/database.
An unknown mode value fails closed rather than silently calling that route.

## Regression checks

```powershell
.\.local-tools\verification-venv\Scripts\python.exe scripts/run_tests.py --temp-root $env:TEMP tests.test_chainlit_mabselect tests.test_app
```

Tests invoke real Chainlit callback functions with captured message transport and
real registry evaluation/source lookup on temporary approved synthetic fixtures.
They block outbound socket connections and replace the graph agent with a failing
guard. This is integration evidence for callbacks/service behavior, not browser
acceptance or an independent answer-quality score. Frozen methods and previous
experiments remain unchanged.

The [correction and re-review report](validation/CHAINLIT-MABSELECT-CORRECTIONS.md)
records the reproduced gaps and their regression coverage. The original
[implementation report](validation/CHAINLIT-MABSELECT-IMPLEMENTATION.md) remains
a historical record of the initial candidate and browser observations.
