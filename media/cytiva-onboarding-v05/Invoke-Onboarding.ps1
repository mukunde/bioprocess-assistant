[CmdletBinding()]
param(
    [ValidateSet('Check','Preview','Render')][string]$Action = 'Check',
    [string]$ToolsDirectory = $PSScriptRoot,
    [string]$ChromePath = '',
    [string]$Python = 'python',
    [int]$Port = 3005
)
$ErrorActionPreference = 'Stop'
$tools = (Resolve-Path -LiteralPath $ToolsDirectory).Path
$modules = Join-Path $tools 'node_modules'
$cli = Join-Path $modules '.bin/hyperframes.cmd'
$ffmpeg = Join-Path $modules 'ffmpeg-static/ffmpeg.exe'
$ffprobe = Join-Path $modules 'ffprobe-static/bin/win32/x64/ffprobe.exe'
$gsap = Join-Path $modules 'gsap/dist/gsap.min.js'
foreach ($file in @($cli,$ffmpeg,$ffprobe,$gsap)) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw "Missing dependency: $file. Run npm ci in the onboarding folder first."
    }
}
$nodeVersion = & node -p 'process.versions.node'
if ($LASTEXITCODE -ne 0 -or [int]($nodeVersion.Split('.')[0]) -lt 22) { throw 'Node.js 22+ is required.' }
foreach ($name in @('hyperframes','gsap','ffmpeg-static','ffprobe-static')) {
    $expected = (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'package.json') -Raw | ConvertFrom-Json).dependencies.$name
    $actual = (Get-Content -LiteralPath (Join-Path $modules "$name/package.json") -Raw | ConvertFrom-Json).version
    if ($actual -ne $expected) { throw "Dependency version mismatch: $name ($actual, expected $expected)." }
}
if (-not $ChromePath) {
    foreach ($candidate in @(
        (Join-Path $env:ProgramFiles 'Google/Chrome/Application/chrome.exe'),
        (Join-Path $env:LOCALAPPDATA 'Google/Chrome/Application/chrome.exe')
    )) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { $ChromePath=$candidate; break }
    }
}
if (-not $ChromePath -or -not (Test-Path -LiteralPath $ChromePath -PathType Leaf)) {
    throw 'Chrome was not found. Provide -ChromePath with an installed Chrome executable.'
}
foreach ($font in @('georgia.ttf','georgiab.ttf','segoeui.ttf','segoeuib.ttf')) {
    if (-not (Test-Path -LiteralPath (Join-Path $env:WINDIR "Fonts/$font"))) { throw "Required Windows font missing: $font" }
}
$vendor = Join-Path $PSScriptRoot 'composition/assets/vendor'
New-Item -ItemType Directory -Path $vendor -Force | Out-Null
Copy-Item -LiteralPath $gsap -Destination (Join-Path $vendor 'gsap.min.js') -Force
$env:HYPERFRAMES_NO_TELEMETRY = '1'
$env:CI = '1' # Run checks directly rather than leaving a warm-check worker alive.
$env:HYPERFRAMES_SKIP_SKILLS = '1'
$env:HYPERFRAMES_BROWSER_PATH = $ChromePath
$env:PRODUCER_HEADLESS_SHELL_PATH = $ChromePath
$env:HYPERFRAMES_FFMPEG_PATH = $ffmpeg
$env:HYPERFRAMES_FFPROBE_PATH = $ffprobe
$env:PATH = (Split-Path $ffmpeg) + ';' + (Split-Path $ffprobe) + ';' + $env:PATH
Push-Location -LiteralPath $PSScriptRoot
try {
    if ($Action -eq 'Check') {
        & $cli check composition --json --at '7,10.5,12.8,15.5,19,22,28,32' --timeout 30000
        if ($LASTEXITCODE -ne 0) { throw 'Hyperframes checks failed.' }
    } elseif ($Action -eq 'Preview') {
        & $cli preview composition --background --port $Port --json
        if ($LASTEXITCODE -ne 0) { throw 'Hyperframes preview failed.' }
    } else {
        & $cli check composition --json --at '7,10.5,12.8,15.5,19,22,28,32' --timeout 30000
        if ($LASTEXITCODE -ne 0) { throw 'Rendering refused: Hyperframes checks failed.' }
        New-Item -ItemType Directory -Path 'renders' -Force | Out-Null
        & $cli render composition --quality delivery --low-memory-mode --output renders/onboarding.raw.mp4
        if ($LASTEXITCODE -ne 0) { throw 'Hyperframes rendering failed.' }
        & $Python (Join-Path $PSScriptRoot 'finalize-video.py') --tools-directory $tools
        if ($LASTEXITCODE -ne 0) { throw 'Video finalization failed.' }
    }
} finally { Pop-Location }

