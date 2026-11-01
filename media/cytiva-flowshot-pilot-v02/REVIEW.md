# Wide Flowshot pilot — package review

Prepared on 2026-11-01 as a local pilot. The package was merged in PR #65;
Pages integration was merged in PR #66 and published on 1 November 2026.
See the [publication and public-browser verification](../../docs/CYTIVA-FLOWSHOT-HOSTING.md).
Publication does not imply human scientific approval of the captured implementation.

## Included behavior

1. **Problem:** exact unsuffixed MabSelect product and hydrophobic context, with the real submission button highlighted.
2. **Result:** documented organic-solvent alternative and backpressure warning; E167-W leads to the next recorded screen.
3. **Citation:** product scope, PDF page 167 and original warning remain visible. The source is boxed; Edit request advances to a different recorded case.
4. **Clarification:** exact product retained, context unknown, clarification requested and no recipe selected.

## Checks and evidence

During the capture session, the four steps, three hotspots, Back, chapter navigation and Restart were exercised in the in-app browser. No warning or error console entries were observed. Wide screenshots and the source warning were inspected visually. Capture viewport overrides were reset afterwards. This is a report of browser checks, not an automated product test or a new retrieval evaluation.

Package preparation checks validate the four local JPEG references, dimensions, coordinate bounds, local HTML/Markdown assets, JSON syntax, unchanged upstream player and license, and manifest hashes. Text-file digests normalize CRLF to LF for checkout portability; JPEG digests use exact bytes. The manifest does not hash itself.

The frozen v03 verifier remains the authority for its 36 pinned files and environment. Preservation checks compare existing files outside this package and the 16 excluded notes against their pre-preparation hashes. No application implementation or historic experiment is part of this package.

## Limits and follow-up

- The player shows screenshots, so controls advance the tour rather than execute application requests.
- Text is rasterized; narrow screens and reduced display scale reduce readability. Vertical scrolling may be needed.
- The clarification case is intentionally a second request, not a consequence inferred from the preceding result.
- The captures include a pending local MabSelect implementation; publishing this tour does not merge that implementation.
- This package contains static HTML, JSON, JavaScript, four images, documentation and the license. Exclude dependencies, vendor Git metadata, source PDFs, temporary previews and private audit logs.
- The root README and Pages integration were outside the original 14-file package and were merged separately in PR #66. The previous pilot remains separate.

## Historical package commit

`docs(demo): add wide Flowshot walkthrough with source citations`

The explicit file inventory is `files_sha256_lf_or_raw` in `package-manifest.json`, plus the manifest itself: 14 files total.

## Publication follow-up — 1 November 2026

The README link, all four published screens, three hotspots, Back, Restart and
round-trip video navigation were exercised as a signed-out visitor without
observed console errors. This updates delivery status only; the capture-session
checks above and their limitations remain historical evidence. No new extraction,
scientific review, backend execution or answer-quality score was added.
