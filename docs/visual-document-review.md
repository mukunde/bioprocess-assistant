# Targeted visual review of converted documents

Use this method when checking a converted table, caption, diagram or review UI
against its source PDF. It complements exact provenance checks and human review.
It is not a general visual similarity score or an automatic approval mechanism.

## Procedure

1. **Freeze the scope and inputs.** Identify the original PDF page, printed page,
   reviewed card and cells. Verify input file hashes, canonical JSON hashes where
   used, source-word provenance and the current decision state. Keep originals
   and previous results unchanged; write derivatives into a new experiment folder.
2. **Check content deterministically.** Compare each selected cell against the
   frozen source words and coordinates. Check token coverage, duplicates, word
   order, column/row assignment, boundary crossings, blank cells, quantities,
   operators, units and note anchors as applicable. Report checks individually.
   Never fill a missing value or use a guessed expected value as source evidence.
3. **Prepare the source view.** Use a full-page PDF render for context, then crop
   the relevant region. Overlay selected cell boundaries and separately identify
   note markers. Record coordinate origin, source dimensions, raster dimensions
   and the x/y scaling. Distinguish inferred cell boundaries from printed lines.
4. **Capture the actual review UI.** Use local Playwright/Chromium with a fixed
   viewport, device scale and recorded browser version. Wait for fonts and images.
   Capture the existing table or element, not a newly generated idealized copy.
   Check DOM text, note links, element overflow and text bounds. Block external
   requests for local review. Do not install a cloud testing service for this step.
5. **Inspect source and reconstruction.** Produce labeled side-by-side images and
   inspect each panel at readable resolution, with enlarged crops when needed.
   Check that headers, descriptions, labels, notes and values remain associated.
   Inspect the full source page to avoid missing captions and footnotes. A model's
   visual observations are technical findings, not human approval.
6. **Report and preserve.** Separate content/association errors, harmless reflow,
   typography losses, and out-of-scope observations. Include scope, input and
   output hashes, scripts, environment and failed attempts or limitations. Recheck
   frozen input hashes and pending decision state after the run. Ask for the
   human decision through the normal review workflow; do not record it implicitly.

## Choosing the comparison

- Use exact source tokens plus geometry for content and provenance. The same
  parser can introduce correlated errors; source-image inspection is therefore
  necessary and remains complementary.
- Use Playwright screenshots to inspect the real HTML and to catch subsequent
  UI regressions against a separately approved HTML screenshot baseline.
- Use pixel differences only for aligned renderings with comparable typography
  and a stable environment. A reflowed HTML table and a PDF can be faithful while
  differing in most pixels. Do not grade extraction using that pixel difference.
- For a larger annotated table corpus, consider TEDS or GriTS against an
  independently reviewed reference. A high aggregate score does not excuse an
  incorrect quantity, operator or footnote condition.

## Token and runtime discipline

Local parsing, checks, cropping and browser capture do not require LLM inference.
Return compact check summaries to the assistant; inspect a full-page context image
once, then only the relevant readable crops. Avoid repeated full DOM dumps,
full-page screenshots and navigation loops. Images and tool outputs inspected by
the assistant still consume conversation context. Do not claim a token saving
percentage without measurement. An explicit no-LLM extraction constraint does not
authorize adding a separate vision API call.

## First application: Cytiva P88-layout, 2026-10-21

Local artifacts are under
`data/experiments/cytiva/visual-validation-v01/p88-layout-visual-review-20261021-a/`.
The folder contains `prepare.py`, `capture.cjs`, `compose.py`, exact check reports,
the source overlay, the actual HTML capture, side-by-side views and a manifest.
These ignored artifacts contain source material and are not a dependency of a
fresh clone. The scripts are experiment snapshots, not a general production tool.

The review used the frozen `table-088-notes-20261021-a/review-v3` packet and its
existing `review.html`, with a native word export from
`deterministic-table-088-20261021-a/words.json`. P88-layout covers 16 cells and
52 unique source words. All 28 preparation checks passed. The actual Chrome
capture at 1800 x 1050, device scale 1, showed no overflowing cell text. A separate
check compared all 16 selected DOM cell texts and the two note links with the
packet. No external request occurred. Original review files and decisions remained
unchanged and pending.

Visual findings: no missing text, swapped product column, filled blank cell or
lost note marker was observed within P88-layout. Product headers lose their bold
weight in HTML and the velocity label wraps onto two lines; these are presentation
differences, not observed content errors. Outside this card, particle-size `d`
subscript typography is flattened to `d 50v`; record this for P88-N5, without
approving or changing that card. The current findings do not validate other values
or footnote conditions and do not establish scientific correctness.

Reproduction from the repository root, when the ignored inputs and snapshots are
available (Pillow in the Python environment, Playwright and Chrome locally):

```powershell
$p88Run = 'data/experiments/cytiva/visual-validation-v01/p88-layout-visual-review-20261021-a'
& '.\.venv-ingestion\Scripts\python.exe' -c "import runpy; runpy.run_path('$p88Run/prepare.py', run_name='__main__')"
# Point to your installed Playwright module; the capture does not install it.
$env:P88_PLAYWRIGHT_MODULE = 'C:\path\to\node_modules\playwright'
node "$p88Run/capture.cjs"
& '.\.venv-ingestion\Scripts\python.exe' "$p88Run/compose.py"
```

Use a new output directory for a new review. These snapshot scripts preserve the
frozen packet but recreate derivative images and check reports in their own run
directory. The assistant's image inspection must be repeated after regeneration;
running the scripts alone does not reproduce an authored visual judgment.
