# Run the guided Chainlit pilot on Windows

Use a fresh clone to try MabSelect and both Protein A/G Sepharose
previews with disposable data. The pilot uses reviewed Cytiva
excerpts and runs on loopback without model or database requests.
Use Git and 64-bit CPython 3.13.0.

## Install and start

Open a dedicated PowerShell window. Keep ports 18881–18883 free.
The dependency installation downloads packages from PyPI.

```powershell
git clone https://github.com/mukunde/bioprocess-assistant.git
cd bioprocess-assistant
py -3.13 -m venv .venv-pilot
$python = '.\.venv-pilot\Scripts\python.exe'
& $python -m pip install -r requirements.txt
& $python -m pip check
.\scripts\Start-DisposableChainlitPilot.ps1 -Clone (Get-Location).Path `
  -TestLogin (Read-Host 'Temporary login') `
  -TestPassword (Read-Host 'Temporary password' -AsSecureString)
```

Use an email-shaped temporary login such as `operator@example.test`.
Start with no `.env` file. The launcher creates a temporary test
registry for MabSelect and two staged Sepharose previews. The second
preview simulates withdrawal of E166-W. It prints the process IDs and
the directory containing the startup logs. Wait for the startup
message in each log before opening its link.

| Open | Purpose |
| --- | --- |
| [MabSelect](http://127.0.0.1:18881/) | Explore cleaning options, clarification, and pressure abstention. |
| [Sepharose baseline](http://127.0.0.1:18882/) | Explore backpressure guidance and inspect a source. |
| [Sepharose withdrawal preview](http://127.0.0.1:18883/) | Compare which options and citations remain after the simulated withdrawal. |

## Check the pilot

Sign in using the temporary account. Use **Settings** to choose the
product and context, confirm, then submit the guided request. Open a
citation to verify the original passage, page, and provenance. Use a
fresh chat for each task and a separate session when comparing previews.

Use the process IDs printed by the launcher to stop the three servers
when finished. Close the dedicated PowerShell window to clear the
temporary credentials from its environment. Keep the pilot on loopback.

The reference Windows installation used CPython 3.13.0 and Chainlit
2.12.0. Independent operator evaluation is pending.

[MabSelect guide](CHAINLIT-MABSELECT.md) ·
[Sepharose guide](CHAINLIT-SEPHAROSE-CANDIDATE.md)
