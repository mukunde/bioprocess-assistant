<#
.SYNOPSIS
Install the frozen demo dependencies and verified tokenizer in an isolated environment.
.EXAMPLE
.\Install-CytivaDemo.ps1
.EXAMPLE
.\Install-CytivaDemo.ps1 -PythonPath "C:\Python313\python.exe"
.EXAMPLE
.\Install-CytivaDemo.ps1 -Offline -Wheelhouse "D:\demo wheels" -TokenizerFile "D:\cl100k_base.tiktoken"
#>
[CmdletBinding()]
param(
    [string]$PythonPath,
    [switch]$Offline,
    [string]$Wheelhouse,
    [string]$TokenizerFile
)
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$candidates = @()
if ($PythonPath) {
    $candidates += @{ Executable = (Resolve-Path -LiteralPath $PythonPath).Path; Prefix = @() }
} else {
    $pyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($pyLauncher) { $candidates += @{ Executable = $pyLauncher.Source; Prefix = @('-3.13') } }
    $pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pythonCommand -and $pythonCommand.Source -notlike '*\Microsoft\WindowsApps\*') {
        $candidates += @{ Executable = $pythonCommand.Source; Prefix = @() }
    }
}
$selected = $null
foreach ($candidate in $candidates) {
    $exe = $candidate.Executable
    $prefixArgs = @($candidate.Prefix)
    try {
        $version = & $exe @prefixArgs -c "import platform,struct; print(platform.python_version()); print(struct.calcsize('P')*8)" 2>&1
        if ($LASTEXITCODE -eq 0 -and ($version -join '/').Trim() -eq '3.13.0/64') {
            $selected = $candidate; break
        }
    } catch { continue }
}
if (-not $selected) {
    Write-Error 'CPython 3.13.0 x64 is required by frozen v03. Install it separately or use -PythonPath. No global Python installation was changed.'
    exit 1
}
$setupArgs = @()
if ($Offline) { $setupArgs += '--offline' }
# Resolve caller-relative paths before changing the working directory.
if ($Wheelhouse) { $setupArgs += @('--wheelhouse', (Resolve-Path -LiteralPath $Wheelhouse).Path) }
if ($TokenizerFile) { $setupArgs += @('--tokenizer-file', (Resolve-Path -LiteralPath $TokenizerFile).Path) }
Push-Location -LiteralPath $PSScriptRoot
try {
    $exe = $selected.Executable
    $prefixArgs = @($selected.Prefix)
    & $exe @prefixArgs -m demo.setup @setupArgs
    $resultCode = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $resultCode
