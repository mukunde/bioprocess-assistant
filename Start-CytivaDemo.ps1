<#
.SYNOPSIS
Check the frozen local runtime and launch the Cytiva demo without installation.
.EXAMPLE
.\Start-CytivaDemo.ps1
.EXAMPLE
.\Start-CytivaDemo.ps1 -CheckOnly
.EXAMPLE
.\Start-CytivaDemo.ps1 -PythonPath "C:\path with spaces\python.exe" -Port 8767
#>
[CmdletBinding()]
param(
    [ValidateRange(1, 65535)][int]$Port = 8766,
    [string]$PythonPath,
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$projectRoot = $PSScriptRoot
$candidates = @()

if ($PythonPath) {
    if (-not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
        Write-Error "Python executable not found: $PythonPath"; exit 1
    }
    $candidates += @{ Executable = (Resolve-Path -LiteralPath $PythonPath).Path; Prefix = @() }
} else {
    foreach ($relative in @('.venv-demo\Scripts\python.exe', '.local-tools\verification-venv\Scripts\python.exe', '.venv\Scripts\python.exe')) {
        $candidatePath = Join-Path $projectRoot $relative
        if (Test-Path -LiteralPath $candidatePath -PathType Leaf) {
            $candidates += @{ Executable = $candidatePath; Prefix = @() }
        }
    }
    $pyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($pyLauncher) { $candidates += @{ Executable = $pyLauncher.Source; Prefix = @('-3.13') } }
    $pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pythonCommand -and $pythonCommand.Source -notlike '*\Microsoft\WindowsApps\*') {
        $candidates += @{ Executable = $pythonCommand.Source; Prefix = @() }
    }
}

$selected = $null
$failures = @()
$resultCode = 1
Push-Location -LiteralPath $projectRoot
try {
    foreach ($candidate in $candidates) {
        $exe = $candidate.Executable
        $prefixArgs = @($candidate.Prefix)
        try {
            $rawReport = & $exe @prefixArgs -m demo.launch --check --json 2>&1
            $probeCode = $LASTEXITCODE
            $report = ($rawReport -join "`n") | ConvertFrom-Json
            if ($probeCode -eq 0 -and $report.ready) {
                $selected = $candidate
                break
            }
            $failures += "${exe}: $($report.errors -join ' ') $($report.remedy)"
        } catch {
            $failures += "${exe}: Python could not run the local startup check. $($_.Exception.Message)"
        }
    }
    if (-not $selected) {
        Write-Host 'No compatible local Python environment found.'
        foreach ($failure in $failures) { Write-Host " - $failure" }
        Write-Host 'Use -PythonPath with the prepared environment, or restore the exact dependency versions and offline tokenizer cache recorded in experiments/cytiva/free-text-v03-freeze-v01/method-lock.json.'
        Write-Host 'No packages, weights or cache files have been installed or downloaded.'
    } else {
        Write-Host "Python: $($selected.Executable)"
        Write-Host "Dependencies verified. Frozen v03: $($report.freeze.pinned_files) files; offline tokenizer verified."
        if ($CheckOnly) {
            Write-Host 'Ready. CheckOnly does not start a server or test port availability.'
            $resultCode = 0
        } else {
            $exe = $selected.Executable
            $prefixArgs = @($selected.Prefix)
            & $exe @prefixArgs -m demo.launch --port $Port
            $resultCode = $LASTEXITCODE
        }
    }
} finally {
    Pop-Location
}
exit $resultCode
