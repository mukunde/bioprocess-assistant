# Browser playback for the approved Cytiva video

Prepared locally, not deployed. The README's proposed browser-playback link will
work only after the Pages site has been configured and published. The existing
MP4 download remains available. No repository setting has been changed.

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

## Publication after review

After the files are merged, an administrator selects **Settings → Pages → Source:
GitHub Actions**, then manually runs **Publish Cytiva video player** from `main`.
The workflow has no push trigger. Its deploy job requests only Pages publication
and its short-lived identity token; repository content access stays read-only.
The actions are official GitHub actions pinned to verified commit references.

Expected address, subject to actual Pages settings:
<https://mukunde.github.io/bioprocess-assistant/>. Verify the deployed address
reported by the workflow, then click the README poster and Play as a signed-out
visitor. If a custom domain or different Pages site already exists, resolve that
before deployment: a repository can have only one Pages site. The read-only Pages
API lookup returned 404 during preparation, so no existing site was confirmed.

The workflow is prepared but has not run. Local playback validation does not
certify a live deployment or every browser. The original video credits and the
existing source/dependency manifests remain authoritative and unchanged.

## Preparation checks — 29 October 2026

- Built exactly the three allowlisted site files; original export hashes match.
- In the in-app Chromium browser: metadata reports 34 seconds, 1920 × 1080 and
  ready state 4, with no media error. Play advances time, seeking changes position,
  Space pauses, and fullscreen opens and returns to the page. The paused position
  was 22.58 s after the controls check. Narrow-window layout was visually inspected.
- Python syntax and YAML parsing pass; the only deployment trigger is manual.
  The builder rejects a nonempty output directory rather than replacing its files.
- The reviewed video-package verifier passes. Frozen v03 verifies all 36 pins and
  its environment; the 16 old notes and previous production files match their hashes.
- No hosted Pages playback or deployment has been tested. These checks do not
  replace application tests, and the application suite was not rerun for this page.
