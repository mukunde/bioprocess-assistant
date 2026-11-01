# Flowshot on GitHub Pages

Status: integration prepared locally on 1 November 2026. The public `/flowshot/` route has not been published or verified. The previously published video remains available at the site root.

## Delivery

The existing manual Pages workflow builds one site: video at `/`, recorded wide Flowshot walkthrough at `/flowshot/`. Both share the same Pages deployment; neither requires a Python application server for visitors. Python is used only to assemble static files during the build.

The builder verifies all nine allowlisted Flowshot assets against the reviewed package manifest before writing output. It retains the original player, four JPEG captures, tour configuration, MIT license and credits. Only the served HTML is adapted to add navigation and remove the local-only publication label. The reviewed source package is unchanged. The output contains twelve files in total, including the three existing video files. No prior pilot, local implementation, source PDF, notes, model, dependency directory or private audit is copied.

## Local validation

From the repository root:

```powershell
python scripts/prepare_cytiva_video_site.py --output .local-tools/cytiva-pages-flowshot-preview
python -m http.server 8782 --bind 127.0.0.1 --directory .local-tools/cytiva-pages-flowshot-preview
```

The output must be new or empty. Check `/` → walkthrough → problem → result → E167-W citation → clarification → Restart. Verify Back and the return-to-video link. The README link targets the future public `/flowshot/` URL; using the local site does not prove that public link works.

## Publication gate and limits

The manual workflow executes repository files from GitHub. It cannot publish these local builder and README edits until they are integrated into the remote repository. Dispatching the current unchanged workflow would only republish the video. After integration, run the manual Pages workflow from `main`, wait for successful deployment, then verify the README link and all four screens as a signed-out visitor. Public verification remains pending until that happens.

This is a captured tour of the separately developed MabSelect journey, not a live backend, a new scientific validation or an operational cleaning authorization. The captured local implementation has not been included in this site integration. Rasterized screenshots are less accessible than live text and require sufficient display width. Flowshot credits and original Cytiva source attribution remain attached. See the [wide package credits](../media/cytiva-flowshot-pilot-v02/CREDITS.md).

## Preparation checks — 1 November 2026

- Three targeted tests passed: exact twelve-file allowlist and original assets, altered-capture rejection, and preservation of nonempty output. Tests used a workspace-local temporary directory because the managed environment's default temporary location denied access.
- The assembled local site was exercised at the video root and `/flowshot/`: all four screens, three hotspots, Back, Restart and return-to-video navigation worked. No console warning or error was observed during the walkthrough.
- This is local output verification, not public deployment verification. The README's future HTTPS link remains unverified until publication.
- Frozen v03 and its environment were verified; prior pilots, sixteen excluded notes and unrelated local work were checked by hashes. No application suite or new retrieval experiment was run for this static hosting change.
