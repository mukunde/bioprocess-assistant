# Cytiva demo: second Windows PC validation

Status: **prepared, not executed on a second PC**. Protocol v01 targets merged
commit `3c19e24aa8dbd04bcb827c1314fafeebed3529bf` (after PR #56). The earlier
[installation review](../experiments/cytiva-demo-installation-review.md) describes
same-PC evidence only. Fill the [blank result sheet](windows-second-pc-results-template.md)
with observations from the second physical machine; do not copy previous results.

## Scope and prerequisites

- A different physical Windows x64 PC, Git and **CPython 3.13.0 x64** installed
  separately. Another Python patch version or ARM64 is outside this protocol.
- PowerShell 5.1 or 7 and a browser. Allow time for installation before starting
  the five-minute walkthrough; installation duration is recorded separately.
- Internet access for GitHub, PyPI/package files and the public tokenizer asset.
  These are source/package/data downloads, not LLM calls or paid APIs.
- No Docker, Neo4j, API key, Cytiva PDF or model weights are needed. Do not copy
  `.venv-demo`, `.local-tools`, an old tokenizer cache or `.env` from the first PC.
  Record whether a pre-existing pip cache was reused or is unknown; do not delete it.

The protocol and blank sheet are local documentation additions until published.
They are not present in the pinned commit above. Transfer these two text files
separately or keep them open alongside the pinned clone. A completed sheet and
logs belong in the clone's ignored `.local-tools/second-pc-validation/` directory.

## 1. Fresh clone and machine record

Open PowerShell in a directory where `bioprocess-cytiva-second-pc` does not exist.
If that name is already used, choose a new name rather than reusing an old clone.

```powershell
git --version
py -3.13 --version
$PSVersionTable | Select-Object PSVersion, PSEdition
Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, OSArchitecture

git clone --branch main --single-branch https://github.com/mukunde/bioprocess-assistant.git bioprocess-cytiva-second-pc
if ($LASTEXITCODE -ne 0) { throw 'Clone failed; stop and record the error.' }
Set-Location -LiteralPath .\bioprocess-cytiva-second-pc
git switch --detach 3c19e24aa8dbd04bcb827c1314fafeebed3529bf
if ($LASTEXITCODE -ne 0) { throw 'Pinned revision unavailable; stop rather than substituting another revision.' }
git rev-parse HEAD
git status --short
New-Item -ItemType Directory -Force -Path .local-tools\second-pc-validation | Out-Null
```

Record the actual revision, Windows edition/build, PowerShell version, Python
version/architecture and a machine alias in the sheet. Initial `git status` must
be empty. If `py` is absent, use the explicit installed Python executable with
`-PythonPath` below; verify it is exactly 3.13.0 x64. No global Python change or
execution-policy bypass is part of this protocol. If scripts are blocked, record
`BLOCKED` and the diagnostic rather than changing security settings.

## 2. Explicit online installation

```powershell
powershell.exe -NoProfile -NonInteractive -File .\Install-CytivaDemo.ps1 *> .local-tools\second-pc-validation\install.log
$cytivaInstallExit = $LASTEXITCODE
Get-Content .local-tools\second-pc-validation\install.log
if ($cytivaInstallExit -ne 0) { throw 'Installation failed; retain install.log and stop.' }
```

If automatic Python discovery fails, record that first failure. Retry the same
command with `-PythonPath "C:\path to Python313\python.exe"` before `*>`, preserving
the first log under another name. Mark the retry and selected executable in the
sheet. Do not silently switch Python versions or regenerate the v03 lock.

Expected: a new clone-local `.venv-demo`, twelve exact dependency versions,
`No broken requirements found`, a tokenizer downloaded and hash-verified, and
`Setup complete`. No installed packages or cache from the first PC are required.
An explicit offline installation is a separate variant described in the
[setup guide](../DEMO-FIRST.md#install-from-a-fresh-windows-clone); do not count it
as execution of the primary online path.

## 3. Readiness, dependency and cache checks

```powershell
powershell.exe -NoProfile -NonInteractive -File .\Start-CytivaDemo.ps1 -CheckOnly *> .local-tools\second-pc-validation\launcher-check.log
$cytivaCheckExit = $LASTEXITCODE
Get-Content .local-tools\second-pc-validation\launcher-check.log
if ($cytivaCheckExit -ne 0) { throw 'Launcher readiness failed; stop.' }

.\.venv-demo\Scripts\python.exe -m pip check
if ($LASTEXITCODE -ne 0) { throw 'Dependency consistency failed; stop.' }
.\.venv-demo\Scripts\python.exe -m demo.launch --check --json > .local-tools\second-pc-validation\readiness.json
if ($LASTEXITCODE -ne 0) { throw 'Environment or freeze verification failed; stop.' }

$cytivaLock = Get-Content experiments\cytiva\free-text-v03-freeze-v01\method-lock.json -Raw | ConvertFrom-Json
$cytivaAssetHash = Get-FileHash -LiteralPath $cytivaLock.environment.tokenizer_asset_file -Algorithm SHA256
$cytivaAssetHash | Format-List | Out-File .local-tools\second-pc-validation\tokenizer-hash.txt
if ($cytivaAssetHash.Hash -ne $cytivaLock.environment.tokenizer_asset_sha256) { throw 'Tokenizer hash differs from the freeze; stop.' }
```

Expected readiness: `ready: true`, Python 3.13.0, `dependency_count: 12`,
`pinned_files: 36`, `environment_verified: true`, empty `errors`, and freeze ID
`free-text-v03-corrected-runtime-freeze-v01`. The launcher must select this clone's
`.venv-demo`, not another project environment. Expected tokenizer SHA-256:
`223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7`.

Optional: run the installer a second time and save a separate log. A ready
installation should report `Already ready` without reinstalling packages.

## 4. Start and five-minute browser walkthrough

```powershell
.\Start-CytivaDemo.ps1
```

Keep this terminal open. Open `http://127.0.0.1:8766/` in the second PC's browser.
If the port is occupied, record the conflict and use `-Port 8767`; use the printed
URL consistently. Do not terminate the existing process. `-CheckOnly` did not
test port availability. Time the following walkthrough from the loaded page.

| Time / ID | Exact action | Expected observation |
|---|---|---|
| 0:00–1:00 / W01 | Keep Guided request, English, 1 mL and only Washing · flow rate. Submit. Follow the E121-W citation and return to results. | Support 1/1, eligible context 1/1; five source passages (E120-H, E120-W, E120-P, E121-PH, E121-W), page numbers, format binding and Blue Sepharose warning visible. Quotes retain both documented formats; highlighting does not remove text. |
| 1:00–2:00 / W02 | Add Washing · column volumes and Washing · stopping criteria. Inspect the stale-result notice, then submit. | Old results are identified until resubmission; afterwards support 3/3 and eligible context 3/3. The full shared source bundle and warning remain. |
| 2:00–3:00 / W03 | Uncheck volumes and stopping criteria. Keep washing flow; add General maximum pressure and Equilibration · flow rate. Submit. | Exactly three items: supported washing, missing-source pressure and quarantined equilibration. Support 1/3 differs from eligible context 1/1. Pressure absence is limited to the 25 excerpts; excluded E118-I/E121-EQ contents are not admitted. |
| 3:00–3:40 / W04 | Uncheck pressure and equilibration, leaving only washing flow. Choose Not specified for the column; submit. Click Choose column format. | Support 0/1, No eligible context, explicit clarification and no assumed format/source bundle. The correction button focuses Column format. |
| 3:40–4:10 / W05 | Select 5 mL and submit. | Support 1/1 and a 5 mL washing binding. The source quotation still retains both formats and their distinct documented flow rates. |
| 4:10–5:00 / W06 | Select EN / FR text · bounded grammar. Click Use French example and submit. | The input language becomes Français. `B : HiTrap Blue HP 1 mL. Donne le débit de lavage pour B.` yields support 1/1, with a 1 mL binding and original English source quotations. |

Optional W07, after the timed core: replace the French text with
`B : HiTrap Blue HP 1 mL. Donne les formulations du tampon de fixation et du tampon d’élution pour B.`
and submit. Expect incomplete intent inventory, clarification and no admissible
source bundle; no buffer purpose is silently chosen. Record it separately from
the six mandatory walkthrough checks. UI labels remain in English; the language
selector describes the input language, not a full interface translation.

For every submitted request, the UI should show zero model calls and EUR 0 API
cost. This is a model-free code path and an observed UI check, not a network-capture
audit or generated-answer quality measurement. Do not change the engine to make
an observation pass; retain the failure and its exact inputs for later triage.

## 5. Stop, preserve integrity and return results

Press Ctrl+C in the server terminal. Confirm the command prompt returns and the
chosen server URL is no longer available after a browser reload. Then run:

```powershell
.\.venv-demo\Scripts\python.exe -m experiments.cytiva.free_text_v03_freeze --environment > .local-tools\second-pc-validation\freeze-after.json
if ($LASTEXITCODE -ne 0) { throw 'Final freeze verification failed.' }
git diff --exit-code
if ($LASTEXITCODE -ne 0) { throw 'Tracked files changed; record the diff.' }
git status --short
```

Expected: unchanged freeze with 36 pinned files and verified environment, no
tracked diff and empty Git status. Store the completed sheet, logs and optional
screenshots only in the ignored results directory. Review logs/screenshots for
personal paths before returning them; use a machine alias, not a serial number.

## Acceptance and interpretation

- Mark each row `PASS`, `FAIL`, `BLOCKED` or `NOT_RUN`; blank or expected outcomes
  are not results. Do not leave the overall result as PASS when a mandatory row
  is failed, blocked or unexecuted. A documented successful retry can pass that
  row while preserving the original failure; it is not a first-attempt success.
- A complete portability pass requires P01–P04, W01–W06 and C01–C02 on a different
  physical PC. W07 and repeat-install checks are optional and do not replace these.
- A local/same-PC dry run remains preparation evidence. Do not promote it to a
  second-PC result, a clean-OS certification, full-suite test run or scientific
  validation. No full test-suite installation is required for this product check.
- Record install/download failures separately from source/clarification/quarantine
  failures. After the second-PC result is reviewed, prioritize a short demonstration
  and concrete usability feedback, then a bounded troubleshooting workflow.

## Preparation verification and delivery inventory

Preparation checkpoint: 28 October 2026. Local checks resolve 32 documentation
links and the referenced heading anchor, confirm the pinned application commit
exists, and parse all ten PowerShell command blocks in this protocol and the
linked setup guide under PowerShell 5.1 and 7. Parsing does not execute the
commands. The result sheet has twelve mandatory rows and two optional rows, all
`NOT_RUN`, and its overall status remains `NOT_RUN`.

The v03 runtime/environment check verifies all 36 pinned files and the unchanged
method-lock digest. The sixteen excluded older local notes retain their original
hashes. No new runtime behavior, full-suite run or second-PC result is claimed.

The compact documentation delivery contains exactly four files:

| File | Purpose |
|---|---|
| `docs/validation/WINDOWS-SECOND-PC.md` | Pinned commands, walkthrough, acceptance criteria and preparation checks |
| `docs/validation/windows-second-pc-results-template.md` | Blank observations, evidence and retry sheet |
| `docs/DEMO-FIRST.md` | Protocol links and aligned next-delivery priorities |
| `docs/README.md` | Documentation-index entry |

Proposed branch: `codex/cytiva-second-pc-protocol`.

Proposed commit message:

```text
docs: prepare second-PC Windows validation protocol and result sheet
```

Completed results, raw logs, command extracts and local verification receipts
remain outside this four-file inventory. The existing installer, launcher,
frozen engine and historical decisions are unchanged.
