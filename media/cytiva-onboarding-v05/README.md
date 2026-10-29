# Cytiva onboarding v05 — approved film

A 34-second, silent-readable introduction for a recruiter without laboratory expertise:
why a manual is difficult to use, how to make a guided request, where to verify a
quotation, and why incomplete or quarantined information is not presented as an answer.
French guidance overlays distinguish themselves from the actual English demo UI.

The delivered MP4 and poster are approved by [decision 005](decisions/human-decision-005.json).
Their bytes are preserved in [exports](exports/onboarding.mp4); subsequent renders
are separate working outputs and require their own review. Older production receipts
are historical; their pending-review status is superseded by this approval.

## View and reproduce

Open `exports/onboarding.mp4` in a video player. See [credits](ATTRIBUTION.md),
[storyboard](brag-plan.md), [design brief](composition-brief.md) and [review](REVIEW.md).
The approved arrow source SVGs are editable and need no Perfect Arrows installation.

Windows prerequisites: Node.js 22+, npm, Python 3.10+, Chrome, and the standard
Segoe UI and Georgia regular/bold fonts. No font or executable is redistributed.
Dependency installation needs network access; the composition uses local assets.
From this folder, in PowerShell:

```powershell
npm ci
python .\verify-package.py
powershell -NoProfile -ExecutionPolicy Bypass -File .\Invoke-Onboarding.ps1 -Action Check
powershell -NoProfile -ExecutionPolicy Bypass -File .\Invoke-Onboarding.ps1 -Action Preview
powershell -NoProfile -ExecutionPolicy Bypass -File .\Invoke-Onboarding.ps1 -Action Render
```

`Check` performs lint, runtime, layout and contrast checks at eight targeted times.
`Render` checks first, renders to `renders/onboarding.raw.mp4`, then creates a
final MP4 and poster under ignored `renders/`. It never replaces approved exports.
The finalizer preserves 1,020 frames and places the citation poster at frame zero.
Use `-ToolsDirectory` to reuse an installation matching the four pinned packages,
`-ChromePath` for another Chrome location, and `-Python` for a Python executable.
Rendering can vary across browser/font/platform versions; the approved export
hashes, not a claim of cross-platform byte reproducibility, identify the reviewed film.

The package is independent of the earlier teaser folder. Its verifier additionally
uses the repository's reviewed evidence to check the displayed quotation. No app
runtime, frozen method, retrieval result or source-review decision is modified.
Repository collaboration rules are in [AGENTS.md](../../AGENTS.md).
