[CmdletBinding()]
param(
    [ValidateSet('CPU', 'Hybrid', 'IrisXe')][string]$Profile = 'CPU',
    [ValidateRange(1024, 65535)][int]$Port = 8000,
    [ValidateRange(1024, 65535)][int]$OllamaPort = 11435,
    [switch]$CheckOnly
)

$ErrorActionPreference = 'Stop'
$python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw 'Create .venv and install requirements.txt as described in docs/LOCAL-GRAPH-CHAT.md.'
}
$arguments = @('--profile', $Profile, '--port', $Port, '--ollama-port', $OllamaPort)
if ($CheckOnly) { $arguments += '--check-only' }
& $python -B (Join-Path $PSScriptRoot 'start_local_graph_chat.py') @arguments
exit $LASTEXITCODE
