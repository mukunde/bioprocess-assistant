# Browser playback for the approved Cytiva video

Published on **29 October 2026** at
[mukunde.github.io/bioprocess-assistant](https://mukunde.github.io/bioprocess-assistant/).
[PR #60](https://github.com/mukunde/bioprocess-assistant/pull/60) is merged;
GitHub Pages is configured to use GitHub Actions with HTTPS enforced. The
[manual deployment](https://github.com/mukunde/bioprocess-assistant/actions/runs/40862970741)
completed successfully from commit `497f0f152aa8aebc5ead72b62b8cc3612661f7c7`.
The README poster and browser-playback link open this player; the optional MP4
download remains available. Only the video is hosted, not the interactive demo.

## Choice

Use [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages),
free for public repositories on GitHub Free. A native HTML video player provides
play/pause, seeking, volume and fullscreen without a plugin, account or forced
file download. Playback still transfers video bytes to the browser. There is no
analytics script, external player library, embedded advertising or autoplay.

The static deployment contains exactly three files: `index.html`,
`assets/onboarding.mp4` and `assets/onboarding.jpg`. The original approved exports
are copied byte-for-byte after their decision-005 hashes are checked. No re-render,
application environment, PDF, prior video, local note or frozen runtime is deployed.

## Local check

From the repository root, use a Python 3.10+ interpreter:

```powershell
python scripts/prepare_cytiva_video_site.py
python -m http.server 8774 --bind 127.0.0.1 --directory .local-tools/cytiva-video-site
```

Open <http://127.0.0.1:8774/>. Check the poster, Play, 34-second duration, seek,
pause, fullscreen and the project/credit links. Stop the server with Ctrl+C.
To build again, pass `--output` with a different empty directory; existing output
is preserved. `.local-tools` is ignored by Git.

## Configuration and repeat publication

**Settings → Pages → Source: GitHub Actions** is configured. To publish a later
reviewed revision, manually run **Publish Cytiva video player** from `main`.
The workflow has no push trigger. Its deploy job requests only Pages publication
and its short-lived identity token; repository content access stays read-only.
The actions are official GitHub actions pinned to verified commit references.

Published address:
<https://mukunde.github.io/bioprocess-assistant/>. Verify the deployed address
reported by the workflow, then click the README poster and Play as a signed-out
visitor. If a custom domain or different Pages site already exists, resolve that
before a future reconfiguration: a repository can have only one Pages site.
The API returned 404 before activation; this is historical preparation evidence,
superseded by the successful activation and deployment above.

The workflow has run successfully. The local and public-browser checks below do
not certify every browser. The original video credits and the
existing source/dependency manifests remain authoritative and unchanged.

## Historical preparation checks — 29 October 2026, before publication

- Built exactly the three allowlisted site files; original export hashes match.
- In the in-app Chromium browser: metadata reports 34 seconds, 1920 × 1080 and
  ready state 4, with no media error. Play advances time, seeking changes position,
  Space pauses, and fullscreen opens and returns to the page. The paused position
  was 22.58 s after the controls check. Narrow-window layout was visually inspected.
- Python syntax and YAML parsing pass; the only deployment trigger is manual.
  The builder rejects a nonempty output directory rather than replacing its files.
- The reviewed video-package verifier passes. Frozen v03 verifies all 36 pins and
  its environment; the 16 old notes and previous production files match their hashes.
- Hosted playback had not yet been tested at this preparation stage; the public
  verification below supersedes that pending status. The application suite was
  not rerun for this page.

## Public verification — 29 October 2026

- Opened the public repository as a signed-out visitor and clicked the README
  poster. It opened the published HTTPS player at the address above.
- Pressed Play: the video advanced from 0 to 23.19 s, with duration 34 s, ready
  state 4, 1920 × 1080 dimensions and no reported media error. Pause also worked.
  Seeking and fullscreen were exercised locally during preparation, not repeated
  as public-site checks.
- HTTP checks returned 200 for the page (`text/html`), MP4 (`video/mp4`, 2,555,914
  bytes) and poster (`image/jpeg`, 151,073 bytes). Playback no longer requires
  manually downloading the MP4; the browser still transfers its data normally.
- The deployed workflow verified the reviewed package and prepared only the
  three allowlisted files. The original exports and approval records were unchanged.
- After the merge, local `main` matched `origin/main` at `497f0f1`. Frozen v03 and its
  environment verified; the 16 old notes and previous production files retained
  their hashes. No new model inference, application trial or application suite
  run was part of this media-publication check.
- GitHub emitted non-blocking runner notices about deprecated Node 20 action
  targets being forced onto Node 24, and the `ubuntu-latest` migration. Build and
  deployment both succeeded; action/runtime maintenance is separate follow-up work.
