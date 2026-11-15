param(
    [Parameter(Mandatory)][string]$Clone,
    [Parameter(Mandatory)][string]$TestLogin,
    [Parameter(Mandatory)][securestring]$TestPassword
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $Clone
$python = (Resolve-Path .venv-pilot/Scripts/python.exe).Path
if (Test-Path .env) { throw 'Use a fresh clone without a .env file.' }
$fixtureRoot = Join-Path ([IO.Path]::GetTempPath()) ('cytiva-pilot-' + [guid]::NewGuid().ToString('N').Substring(0,8))
$env:CYTIVA_PILOT_FIXTURES = $fixtureRoot
@"
import os
from pathlib import Path
from serving import local_registry, sepharose_candidate
from tests.test_local_registry import approve_fixture

root = Path(os.environ["CYTIVA_PILOT_FIXTURES"])
root.mkdir(exist_ok=False)
mabselect = local_registry.prepare(root / "mabselect", "pilot-mabselect")
approve_fixture(mabselect)
local_registry.Registry(root / "mabselect").activate("pilot-mabselect")
sepharose_candidate.prepare(root / "sepharose", "pilot-sepharose")
sepharose_candidate.prepare(
    root / "withdrawal", "pilot-sepharose-held", withheld_sources=["E166-W"],
)
"@ | & $python -
if ($LASTEXITCODE -ne 0) { throw 'Fixture preparation failed.' }

$env:DEMO_USERNAME = $TestLogin
$env:DEMO_PASSWORD = [System.Net.NetworkCredential]::new('', $TestPassword).Password
$env:CHAINLIT_AUTH_SECRET = & $python -c 'import secrets; print(secrets.token_hex(32))'
Remove-Item Env:ANTHROPIC_API_KEY, Env:ANTHROPIC_AUTH_TOKEN, Env:MABSELECT_TRACE_FILE -ErrorAction SilentlyContinue

$instances = @(
    @{ mode = 'mabselect'; port = 18881; folder = 'mabselect' },
    @{ mode = 'sepharose_candidate'; port = 18882; folder = 'sepharose' },
    @{ mode = 'sepharose_candidate'; port = 18883; folder = 'withdrawal' }
)
$processes = foreach ($instance in $instances) {
    $env:BIOPROCESS_MODE = $instance.mode
    $env:MABSELECT_REGISTRY_ROOT = Join-Path $fixtureRoot 'mabselect'
    $env:SEPHAROSE_CANDIDATE_ROOT = Join-Path $fixtureRoot $instance.folder
    $port = $instance.port
    $process = Start-Process $python -WindowStyle Hidden -PassThru `
        -ArgumentList @('-m','chainlit','run','app.py','--host','127.0.0.1','--port',$port,'--headless') `
        -RedirectStandardOutput (Join-Path $fixtureRoot "$port.out") `
        -RedirectStandardError (Join-Path $fixtureRoot "$port.err")
    [pscustomobject]@{ Port = $port; ProcessId = $process.Id; Fixture = $instance.folder }
}
$processes | ConvertTo-Json | Set-Content (Join-Path $fixtureRoot 'processes.json')
Write-Output "Fixture and log directory: $fixtureRoot"
$processes
