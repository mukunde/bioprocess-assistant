# Demo-first delivery: local Cytiva evidence explorer

## Priority and current slice

The user explicitly selected the local, free guided Cytiva route on 27 October
2026. The first product checkpoint is a usable request-to-citation path. Do not
gate it on another twelve-question review campaign, a new graph framework or a
broader corpus.

Corrected v03 is [frozen separately](../experiments/cytiva/free-text-v03-freeze-v01/README.md).
The first local UI is implemented in [demo/cytiva.py](../demo/cytiva.py). It calls
the frozen engine and renders complete source bundles without generated advice.
It does not change the existing Chainlit/Neo4j chat or publish new graph records.

The guided slice covers HiTrap Blue HP 1 mL/5 mL, or an unspecified format, and
the supported loading/washing/elution/buffer questions from the existing 25
reviewed excerpts. Pressure and equilibration demonstrate missing evidence and
quarantine. The optional EN/FR text input retains the bounded parser and its
clarification behavior. Source quotations remain in their original English.

## Install from a fresh Windows clone

Prerequisites: Git and **CPython 3.13.0 x64** installed separately. The exact Python
version is part of the unchanged v03 freeze; another 3.13 patch version is rejected.
This procedure targets Windows x64, not ARM64, and needs no Docker, source PDF,
model weights, account, API key or existing project environment.

From PowerShell, clone the project, then run the explicit installation step:

```powershell
git clone https://github.com/mukunde/bioprocess-assistant.git
cd bioprocess-assistant
.\Install-CytivaDemo.ps1
.\Start-CytivaDemo.ps1 -CheckOnly
.\Start-CytivaDemo.ps1
```

The installer is merged in [PR #55](https://github.com/mukunde/bioprocess-assistant/pull/55)
and available in new clones of main. Setup and the walkthrough were verified in
a fresh clone on the same PC; a second-machine check remains pending.

For that next check, use the [second-PC protocol](validation/WINDOWS-SECOND-PC.md)
and its [blank result sheet](validation/windows-second-pc-results-template.md).
They pin a merged revision and separate real observations from expected outcomes.

Installation creates the ignored `.venv-demo` in this clone. It installs all 12
runtime dependencies from `demo/requirements-windows.lock`, with exact versions,
SHA-256 wheel hashes and no source builds or dependency expansion. It downloads
`cl100k_base.tiktoken` from the public OpenAI encoding-asset endpoint, verifies the
SHA-256 recorded in the freeze and writes the ignored cache at the frozen path.
These are package/static-file downloads, not model calls; no manual or question
is transmitted. The engine continues to read only the verified local cache.

The setup runs `pip check` and the launcher's readiness check. It never modifies
global Python, the previous verification environment, the frozen lock or the
serving engine. A ready installation is a no-op; a corrupt cache or a non-isolated
existing `.venv-demo` fails with a diagnostic. After an interrupted dependency
installation, rerun the command. If virtual-environment creation itself was
interrupted and left no working Python/pip, retry in a fresh clone instead of
reusing that incomplete environment. Never regenerate the v03 lock to hide a failure.

If Python is not discoverable, use a caller-relative or absolute executable path:

```powershell
.\Install-CytivaDemo.ps1 -PythonPath "C:\path with spaces\python.exe"
```

For a disconnected machine, prepare the wheelhouse on a matching Windows x64 /
Python 3.13.0 machine and separately obtain the tokenizer asset from
`https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken`:

```powershell
py -3.13 -m pip --isolated download --require-hashes --only-binary=:all: --no-deps --index-url https://pypi.org/simple -r demo/requirements-windows.lock -d "D:\demo wheels"
.\Install-CytivaDemo.ps1 -Offline -Wheelhouse "D:\demo wheels" -TokenizerFile "D:\cl100k_base.tiktoken"
```

The offline installation uses `--no-index` and the supplied files; it fails if a
required wheel/cache asset is absent or has the wrong hash. Keep wheels, caches
and virtual environments outside Git. No execution-policy changes are made.

The [installation review](experiments/cytiva-demo-installation-review.md) records
the fresh-clone test, Windows PowerShell 5.1/7 checks, browser walkthrough and
remaining second-machine limitation.

## Launch on the prepared Windows workstation

From the repository root in Windows PowerShell 5.1 or PowerShell 7:

```powershell
.\Start-CytivaDemo.ps1
```

The launcher first tries `.venv-demo`, the prepared `.local-tools/verification-venv`
and `.venv`, then available Python 3.13/system commands. It selects the first
environment that passes all checks. An explicit `-PythonPath` disables fallback.
Paths containing spaces and invocation from another working directory are
supported; relative Python paths are resolved from the caller's directory.

Before constructing the engine, it verifies the recorded Python version, all
12 dependency versions, all 36 frozen files, and the offline tokenizer cache and
its hash. Missing/mismatched versions and invalid cache/frozen files produce
diagnostics and a nonzero exit. No packages, model weights or tokenizer data are
installed or downloaded; no database or API key is used.

Open [the local demo](http://127.0.0.1:8766/). Stop the server with Ctrl+C. It binds
only to loopback, keeps no conversational state and writes no submitted text or
results to disk. This is a workstation demo, not a hosted deployment.

Optional commands:

```powershell
.\Start-CytivaDemo.ps1 -CheckOnly
.\Start-CytivaDemo.ps1 -Port 8767
.\Start-CytivaDemo.ps1 -PythonPath "C:\path with spaces\python.exe" -CheckOnly
```

`-CheckOnly` validates readiness without binding a port or starting an engine.
A port already in use is never reclaimed or its process killed: the launcher
reports it and suggests choosing another port or stopping the existing server.
Keep the terminal open while using the demo. Closing it stops the foreground
service; the launcher does not create a hidden persistent service.

For a different machine, use the separate installation step above. The private
verification environment/cache is not redistributed. The launcher itself remains
read-only with respect to installation: it checks an existing environment.

## Five-minute walkthrough

1. Keep the default 1 mL column and washing flow. Submit; inspect complete source
   context, the column-specific binding and the Blue Sepharose warning.
2. Add washing volume and stopping criteria. Show that the request uses several
   units while the complete shared source bundle is retained.
3. Add general maximum pressure and equilibration flow. Show partial service,
   missing selected-corpus evidence and quarantine without losing washing support.
4. Clear the column format. Show clarification rather than guessing a format.
5. Optionally use the French text example. Then try coordinated buffer purposes;
   the interpreter asks for clarification instead of silently dropping a purpose.

The corrected interface labels the request behind each result and flags it as
stale after input changes. Missing-format clarification has a direct correction
button; source/result navigation stays available. Highlighting marks a literal
format mention while preserving the complete original quotation. See the
[usability review and browser checks](experiments/cytiva-demo-ux-review.md).

The display reports whole-request support separately from eligible-context
coverage. A complete context ratio is not a fully answered request when other
units are missing. All admitted passages, required scope, conditions and warnings
remain visible. Each supported unit links to its bound source bundle. Absence is
limited to the selected excerpts, not the entire Cytiva manual.

## Next deliveries and stop rules

1. **Validate on a second Windows PC.** The installer, launcher and corrected
   walkthrough are merged and have same-PC evidence. Execute the pinned protocol
   above and review its completed sheet; keep failures and retries visible.
2. **Record a short demo and collect feedback.** Fix blockers to understanding,
   navigation or correct transmission. A scope or provenance defect remains a
   release blocker; cosmetic and broader language refinements can be iterative.
3. **Extend one useful workflow.** Add a confirmed troubleshooting use case or
   connect the reviewed records to the existing chat, keeping serving provenance
   and rollback. Do not claim a procedural lookup is a causal diagnosis.
4. **Instrument the real path.** Start with operation/timing/context counts and
   OpenTelemetry; add call/cost accounting if model calls are introduced. Ragas
   and Promptfoo follow the actual answering/attack surface rather than delaying
   this deterministic demonstration.
5. **Evaluate and broaden incrementally.** Add a small fresh holdout appropriate
   to the next behavior change. Keep original freezes/results and use new versions
   for engine changes. LightRAG/KAG, fine-tuning, full-manual extraction and a
   generalized language grammar remain separate later decisions.

Passing implementation tests establishes behavior on their fixtures, not new
prospective performance, scientific validity, GxP readiness or whole-manual
coverage. The current UI exposes documentary evidence, not generated answers.
