# Onboarding v05 packaging review

Status: human-approved film, prepared as an independent editable package.
The final approval is [decision 005](decisions/human-decision-005.json); the five
original decision records retain their exact bytes and original human quotations.
The approved MP4 and poster retain their approval hashes. Older pending status
and obsolete arrow descriptions remain visible only inside the historical
production receipt in [provenance.json](provenance.json), with an explicit current
status and correction. The canonical geometry and integration map govern v05.

## Verification and limits

- Six scenes, 34 s, 1,020 frames, 1920 × 1080, 30 fps, H.264/AAC.
- Relocated Hyperframes checks passed with no errors or warnings; four
  informational `connector_orphan` findings remain documented in [verification.json](verification.json).
  Product and operation paths are heuristically associated with a
  hidden title/route. The approved SVG geometry is unchanged. Contrast: 61/61 pass.
- Four displayed arrow instances match the three approved SVGs; the operation
  instance differs only by the approved 99.5 px translation.
- E121-W matches the reviewed repository passage, page 121. The film quotes a
  continuous excerpt with ellipses, restricted to washing the 1 mL column.
- Local documentation and HTML asset references, pinned package-lock versions,
  decision/export hashes and source inventory are checked by [verify-package.py](verify-package.py).
- Frozen v03 and its dependency environment verify successfully. All 16 old notes
  and the previous production/first-teaser files match their pre-packaging hashes.
- The media-only change does not rerun or certify the application regression suite.
  It does not validate a laboratory protocol, a whole manual, or retrieval accuracy.
- No dependency implementation, private capture, PDF, raw render, font, cache or
  temporary output belongs to this inventory. The source music track is intentionally
  retained as an editable asset under its separate attribution terms.

## Intended Git lot

Branch: `codex/cytiva-onboarding-v05`

Commit message:

```text
docs(media): add approved Cytiva onboarding v05 and editable sources
```

Only the following files, all under `media/cytiva-onboarding-v05/`, belong to this
lot. The earlier first-teaser package is separate. Repository rules: [AGENTS.md](../../AGENTS.md).

- `media/cytiva-onboarding-v05/.gitattributes`
- `media/cytiva-onboarding-v05/.gitignore`
- `media/cytiva-onboarding-v05/ATTRIBUTION.md`
- `media/cytiva-onboarding-v05/Invoke-Onboarding.ps1`
- `media/cytiva-onboarding-v05/README.md`
- `media/cytiva-onboarding-v05/REVIEW.md`
- `media/cytiva-onboarding-v05/approved-arrows/case-long.svg`
- `media/cytiva-onboarding-v05/approved-arrows/case-short.svg`
- `media/cytiva-onboarding-v05/approved-arrows/case-source.svg`
- `media/cytiva-onboarding-v05/approved-arrows/geometry.json`
- `media/cytiva-onboarding-v05/approved-arrows/perfect-arrows-LICENSE.txt`
- `media/cytiva-onboarding-v05/brag-plan.md`
- `media/cytiva-onboarding-v05/composition-brief.md`
- `media/cytiva-onboarding-v05/composition/assets/music/bed.mp3`
- `media/cytiva-onboarding-v05/composition/assets/sfx/click.ogg`
- `media/cytiva-onboarding-v05/composition/assets/sfx/reveal.ogg`
- `media/cytiva-onboarding-v05/composition/assets/theme.css`
- `media/cytiva-onboarding-v05/composition/compositions/evidence.html`
- `media/cytiva-onboarding-v05/composition/compositions/limits.html`
- `media/cytiva-onboarding-v05/composition/compositions/outro.html`
- `media/cytiva-onboarding-v05/composition/compositions/problem.html`
- `media/cytiva-onboarding-v05/composition/compositions/purpose.html`
- `media/cytiva-onboarding-v05/composition/compositions/request.html`
- `media/cytiva-onboarding-v05/composition/index.html`
- `media/cytiva-onboarding-v05/decisions/human-decision-001.json`
- `media/cytiva-onboarding-v05/decisions/human-decision-002.json`
- `media/cytiva-onboarding-v05/decisions/human-decision-003.json`
- `media/cytiva-onboarding-v05/decisions/human-decision-004.json`
- `media/cytiva-onboarding-v05/decisions/human-decision-005.json`
- `media/cytiva-onboarding-v05/exports/onboarding.jpg`
- `media/cytiva-onboarding-v05/exports/onboarding.mp4`
- `media/cytiva-onboarding-v05/finalize-video.py`
- `media/cytiva-onboarding-v05/integration-map.json`
- `media/cytiva-onboarding-v05/licenses/Hyperframes-Apache-2.0.txt`
- `media/cytiva-onboarding-v05/licenses/brag-MIT.txt`
- `media/cytiva-onboarding-v05/manifest.json`
- `media/cytiva-onboarding-v05/package-lock.json`
- `media/cytiva-onboarding-v05/package.json`
- `media/cytiva-onboarding-v05/provenance.json`
- `media/cytiva-onboarding-v05/share-copy.txt`
- `media/cytiva-onboarding-v05/verification.json`
- `media/cytiva-onboarding-v05/verify-package.py`
