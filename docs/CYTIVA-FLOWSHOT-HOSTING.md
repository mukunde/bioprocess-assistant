# Flowshot on GitHub Pages

Published on **1 November 2026** at [the wide walkthrough](https://mukunde.github.io/bioprocess-assistant/flowshot/).
[PR #65](https://github.com/mukunde/bioprocess-assistant/pull/65) (package) and
[PR #66](https://github.com/mukunde/bioprocess-assistant/pull/66) (integration) are merged.
The [manual deployment](https://github.com/mukunde/bioprocess-assistant/actions/runs/41350245456)
succeeded from `5decd53487709044f6f110f8eb010d2df3debc50`. The README-to-walkthrough
route was verified as a signed-out visitor. The existing video remains at the site root.

## Delivery

The existing manual Pages workflow builds one site: video at `/`, recorded wide Flowshot walkthrough at `/flowshot/`. Both share the same Pages deployment; neither requires a Python application server for visitors. Python is used only to assemble static files during the build.

The builder verifies all nine allowlisted Flowshot assets against the reviewed package manifest before writing output. It retains the original player, four JPEG captures, tour configuration, MIT license and credits. Only the served HTML is adapted to add navigation and remove the local-only publication label. The reviewed source package is unchanged. The output contains twelve files in total, including the three existing video files. No prior pilot, local implementation, source PDF, notes, model, dependency directory or private audit is copied.

## Local validation

From the repository root:

```powershell
python scripts/prepare_cytiva_video_site.py --output .local-tools/cytiva-pages-flowshot-preview
python -m http.server 8782 --bind 127.0.0.1 --directory .local-tools/cytiva-pages-flowshot-preview
```

The output must be new or empty. Check `/` → walkthrough → problem → result → E167-W citation → clarification → Restart. Verify Back and the return-to-video link. Local checks remain useful before later deployments; they do not replace public verification.

## Repeat publication and limits

The manual workflow executes committed repository files from GitHub. For a later
reviewed revision, run **Publish Cytiva video and walkthrough** from `main`, wait
for successful deployment, then repeat the public README-link and four-screen
checks. The workflow has no automatic push trigger. The first public verification
is recorded below.

This is a captured tour of the separately developed MabSelect journey, not a live backend, a new scientific validation or an operational cleaning authorization. The captured local implementation has not been included in this site integration. Rasterized screenshots are less accessible than live text and require sufficient display width. Flowshot credits and original Cytiva source attribution remain attached. See the [wide package credits](../media/cytiva-flowshot-pilot-v02/CREDITS.md).

## Historical preparation checks — 1 November 2026, before publication

- Three targeted tests passed: exact twelve-file allowlist and original assets, altered-capture rejection, and preservation of nonempty output. Tests used a workspace-local temporary directory because the managed environment's default temporary location denied access.
- The assembled local site was exercised at the video root and `/flowshot/`: all four screens, three hotspots, Back, Restart and return-to-video navigation worked. No console warning or error was observed during the walkthrough.
- At preparation time, only local output had been verified. The public verification below supersedes that pending status.

## Public verification — 1 November 2026

- Opened the public repository while signed out and clicked the README's **Explore the interactive walkthrough — no installation** link. It opened the published HTTPS `/flowshot/` route.
- Exercised problem → result → E167-W citation → clarification, using all three hotspots. The original product scope, PDF page 167 and pressure warning remained visible. Back and Restart worked.
- Followed **Watch the video** to the existing root player, then its walkthrough link back to `/flowshot/`. This checks navigation; video playback was not re-evaluated in this session.
- No console warnings or errors were observed during the walkthrough. This does not certify every browser or mobile display, accessibility, backend execution, retrieval accuracy or scientific suitability.
- Build and deploy jobs succeeded. Three targeted publication tests passed on the deployed revision.
- The package manifest's preparation status, captured source hashes and original local HTML labels remain historical provenance. The deployment builder adapts the served HTML without editing those source assets. Subsequent documentation edits refresh only the affected documentation digests.
