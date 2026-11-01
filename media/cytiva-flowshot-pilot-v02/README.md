# Cytiva Flowshot pilot v02 — wide walkthrough

A four-screen interactive screenshot tour of the real local MabSelect cleaning journey: problem, result, citation and clarification. Explanations sit above the wide application captures. Pink outlines and dimming distinguish onboarding guidance from the application's teal UI.

## Preview locally

From this directory, run:

```powershell
python -m http.server 8781 --bind 127.0.0.1
```

Open [the local walkthrough](http://127.0.0.1:8781/). Click the highlighted controls or Next; Back, chapter selection and Restart are available. Python serves static files only. No installation of Flowshot CLI, Node packages or application dependencies is required to play the tour.

## Scope

These are recorded app states, not an executable Python application. The last screen is a separate unknown-context example. No model or paid API is called. The [published tour](https://mukunde.github.io/bioprocess-assistant/flowshot/) has been
accessible from the root README since 1 November 2026. All four screens, citations,
clarification and navigation were verified while signed out. See the
[publication report](../../docs/CYTIVA-FLOWSHOT-HOSTING.md). The previous portrait pilot remains separate.

Captures use a 1200 × 800 browser viewport, producing 1185 × 790 JPEG files. Screenshot text is rasterized and cannot replace accessible source text. Small screens reduce readability and the page may need vertical scrolling.

See [credits and provenance](CREDITS.md), the [verification report](REVIEW.md), and the [package manifest](package-manifest.json). The manifest binds the distributable assets and records the application source versions used for capture. It does not package or certify those pending application changes.

The manifest's preparation status and local-only labels in the original HTML
remain historical capture/package metadata. The Pages builder adapts the served
HTML. Current publication status is recorded in the hosting report; source image,
player and captured-application hashes remain unchanged.
