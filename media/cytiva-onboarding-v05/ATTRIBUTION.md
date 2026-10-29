# Credits and third-party material

## Music and sound

- `composition/assets/music/bed.mp3`: **Happy Beats / Business Moves Vol. 12**,
  Sascha Ende, [ende.app](https://ende.app/en),
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
  The original bundled track is retained as the source asset. The edit uses its
  first 34 seconds, gain 0.21 and edge fades. Credit is visible in the outro and
  preserved in `share-copy.txt`.
- `composition/assets/sfx/click.ogg`: Kenney `interface/click_003.ogg`.
- `composition/assets/sfx/reveal.ogg`: Kenney `impact/impactSoft_medium_001.ogg`.
  The two sound effects are [Kenney](https://kenney.nl/) CC0 assets bundled with brag.
  Their clip lengths and gains are set in the composition.

Source of the music/SFX licence declarations: the brag repository at commit
`669ab9286aa28b6c3ee30e75f181ee74319d012a`, `assets/music/README.md` and
`references/audio.md`. Music and sound assets retain their own terms; they are
not relicensed under the project's licence.

## Authoring tools and adapted primitives

- [brag](https://github.com/latent-spaces/brag): MIT. Original notice:
  [licenses/brag-MIT.txt](licenses/brag-MIT.txt).
- [Hyperframes](https://github.com/heygen-com/hyperframes): Apache-2.0.
  Original licence: [licenses/Hyperframes-Apache-2.0.txt](licenses/Hyperframes-Apache-2.0.txt).
  Browser-device-stage styling and the agent-cursor SVG were adapted into
  the original first-cut composition; this new film uses an editorial rectangular focus and the same cursor SVG; they are not unmodified registry files.
  Upstream revision: `67c7ec27d9978076137459d471be936a993e22df`.
- GSAP 3.15.0: [GSAP standard licence](https://gsap.com/standard-license),
  not MIT. It is installed as an npm dependency and copied to an ignored vendor
  directory at runtime; no GSAP implementation is versioned here.
- FFmpeg/FFprobe executables are installed locally by their pinned npm packages;
  they are not redistributed in this package. Their notices remain with the
  downloaded distributions. No font files are redistributed; Windows Segoe UI and Georgia (regular/bold) are resolved locally.

Correction to the original private production note: Hyperframes is Apache-2.0,
not MIT. The independent brag skill is MIT.

## Demo UI and documentary excerpts

The UI elements were captured from the actual local demo at the application
revision recorded in `provenance.json`. Layout, cursor and timing are edited;
this is not a continuous screen recording or live model inference.

E121-W is an explicitly labelled continuous quotation excerpt with ellipses,
limited to washing with the 1 mL column. E120-W is linked as contextual material in the real demo, but is not shown in this film.
Cytiva manual reference: **CY13981-25Jan21-HB**, PDF pages 120–121. The public
manual and the product names remain the material of their respective owners;
no PDF, page image, endorsement or new redistribution licence is included.
The existing project evidence provides the documentary provenance; raw PDF pages and private captures are excluded from this package. No scientific or operational approval is asserted by the teaser.

## Approved arrow integration

Perfect Arrows 0.3.7 (Steve Ruiz), MIT: see approved-arrows/perfect-arrows-LICENSE.txt.
Cases 1/2 use its geometry; the approved case 3 S is a documented cubic extension,
not native Perfect Arrows output. Approved SVGs are reused as static source assets;
no arrow runtime dependency or new installation is required.
