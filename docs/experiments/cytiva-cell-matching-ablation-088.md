# Cytiva page 88: cell-matching ablation

Date: 2026-10-21. Historical experiment status: **technical ablation executed; neither Docling variant accepted**.
The subsequent [human review of the deterministic reconstruction](cytiva-page-088-human-review.md)
is complete with nine validations with reservations. It does not approve either
Docling variant, validate this ablation as a general benchmark or authorize publication.
This follows the [first table trial](cytiva-conversion-chunking-results-077-088.md)
and its [validation protocol](cytiva-conversion-chunking-protocol.md).
No claims are approved or published by this experiment.

## Decision

**Retain cell matching enabled as the experimental default. Disabling it does not
repair “Available formats” and introduces a column-association regression in the
MabSelect velocity. Both Docling conversions of table 3.6 remain quarantined.**

The defect is not caused solely by cell matching: an oversized TableFormer cell
box is already present without matching. The matching path groups source words
into that cell; the nonmatching path reads source text within the same oversized
box. Neither produces four correct product associations.

## Controlled setup and artifacts

- Original PDF page 88, printed page 88, excerpt page 1; source SHA-256:
  `a6fd949e904ec0bafbcc7d85a3be1660f2bea8949098e86c57ae43d06492946a`.
- Reused the original frozen page-88 excerpt after checking its hash and source
  map against the full manual. The source was rendered with Poppler and visually
  inspected before comparing outputs. A new targeted reference records four
  distinct format cells, product headers, quantities, units, markers and reagents.
  At this experiment stage it was an assistant annotation, not a human decision.
  Later approval of the exact reconstructed table is recorded separately.
- Same Docling 2.140.0, docling-core 2.101.1, Docling Graph 1.9.1 pinned revision,
  weights, CPU/four threads, TableFormer V1 `accurate`, OCR disabled, images scale 2,
  and no chart/picture description or classification.
- The only effective processing difference is
  `table_structure_options.do_cell_matching`: true versus false. A serialized
  capability set for disabled chart extraction has different list ordering;
  sorting that set makes all other saved settings identical. No chart engine runs.
- Standard workers run sequentially in fresh directories. Python network audit
  guards remain enabled: both workers record zero attempts, zero LLM calls and
  zero API calls. The guard is not a native-code firewall. No weights were downloaded.

Authoritative local artifacts are under
`data/experiments/cytiva/visual-validation-v01/cell-matching-088-20261021-d/`:
`manifest.json`, `targeted-reference.json`, `comparison.json`,
`backend-cell-diagnostic.json`, `cell-matching-comparison.png`, and the
`matching-on/` / `matching-off/` outputs. Each variant retains its effective
profile, complete document JSON, HTML/CSV table, images, metrics and worker log.
The visual comparison overlays cell boxes on the original PDF: underlying text
is source text, not a rendering of the extracted table. Full sources stay local.

## Results by product and check

| Check | Matching enabled | Matching disabled |
|---|---|---|
| Logical grid | 8 rows × 5 columns | 8 rows × 5 columns |
| MabSelect formats | Four source cells concatenated into one | Same concatenation persists |
| MabSelect Xtra formats | Empty | Correct complete text |
| MabSelect SuRe formats | Empty | Only the second text line; first line missing |
| MabSelect SuRe LX formats | Empty | Only the second text line; first line missing |
| Correct format/product associations | 0/4 | 1/4 |
| Capacity, unit and note-marker checks | 4/4 | 4/4 |
| Velocity value/unit in correct product cell | 4/4 | 3/4 |
| Particle size/unit checks | 4/4 | 4/4 |
| CIP reagent checks | 4/4 | 4/4 |
| Product headers | 4/4 | 4/4 |
| Table footnotes | All five present | All five present, identical text |

Both variants pass 20 of the 24 targeted checks, but fail different checks.
That aggregate hides the velocity regression and is not an adoption criterion.
There are 35 versus 37 nonempty grid cells; more filled cells do not mean better
fidelity. Missing fields were never forward-filled, nor were repeated phrases
split and reassigned by assumption.

The enabled table data is exactly identical to the earlier T1 output. Apart from
the formats row, the disabled variant changes two logical cells: the velocity
label receives `500 cm/h`, and the MabSelect value becomes empty. Other grid text
matches the earlier T1 after declared whitespace normalization. This is a
comparison against the previous conversion, not independent verification of
all possible omissions. The targeted numeric checks remove whitespace only;
values, units, approximation signs and note markers must still match.

## Why it fails

### 1. Geometry is already incorrect before text matching

The nonmatching path preserves a predicted first-product format box spanning
approximately x=404–1825 on a 1920-wide PDF page, while declaring `col_span=1` and
logical product column 1. It physically covers all four product columns. With
matching enabled, its final box remains approximately x=403–1828 and collects
all four source texts. This contradiction is visible in the overlays and JSON.

For the third and fourth product cells without matching, box tops are about
y=555 and y=556, whereas the first source text line starts around y=541. Those
boxes retain only the second line. The source has two lines for each product;
it does not contain three genuinely empty format cells.

The installed TableFormer/Docling code confirms that disabling matching uses
predicted boxes and then `get_text_in_rect`, while enabling it assigns PDF words
through matching and postprocessing. This isolates a geometric error upstream
of text assignment; it does not identify the exact neural layer or prove why
TableFormer predicted that box. Repeated text and absent vertical rules are
possible influences, not established causes.

### 2. Disabling matching exposes a line-grouping regression

The PDF backend has one textline containing the velocity label, its note marker
and the first `500 cm/h`. Its rectangle reader selects a textline when more than
50% of that line overlaps the requested box. A deterministic replay finds:

- label box: overlap fraction **0.7496**, so the entire line, including the value,
  is selected;
- MabSelect value box: overlap fraction **0.1802**, so the line is excluded.

This explains why the value moves into the label rather than disappearing from
the source. The enabled path uses word-level PDF tokens and retains the four
velocity values in their product cells. The replay used the installed backend
on the same frozen excerpt, without layout inference, a language model or network.

## Timing and failed attempts

| Authoritative run | Full worker | Imports/setup | Conversion including lazy model loading | Sampled peak RSS |
|---|---:|---:|---:|---:|
| Matching enabled | 71.7 s | 37.0 s | 30.1 s | 1.11 decimal GB |
| Matching disabled | 58.6 s | 35.5 s | 20.0 s | 1.14 decimal GB |

The pair took approximately 130.3 seconds of worker elapsed time. This is one
sequential pair with changing caches, not a controlled speed comparison or
proof that disabling matching is faster. It excludes earlier failed attempts
and diagnostic preparation; it is not total task duration. Local CPU, electricity
and human time are not measured as financial costs. Additional API cost is zero.

All attempts are retained separately:

- `...-a`: timeout before a profile or conversion output; empty worker log,
  approximately 3803 seconds reported elapsed. The cause of this excessive elapsed
  interval is unresolved; it is not an inference-time measurement.
- `...-b`: instrumented diagnostic worker failed with Windows native access
  violation (`3221225477`) before producing a usable conversion. It is excluded
  from quality and timing comparisons; this does not establish a TableFormer defect.
- `...-c`: both standard conversions succeeded and showed the same table outputs,
  but polymorphic options serialized as an empty object. Those outputs remain
  intact and are corroborating results, not the authoritative profile record.
- `...-d`: complete standard pair after fixing profile serialization. The effective
  table settings are explicit; no diagnostic prediction hooks were used.

## Runner changes and verification

The launcher now accepts `--cell-matching` / `--no-cell-matching`; the default
remains enabled. The public conversion command forwards the setting to each
worker. For a future reproduction, use different new output directories for
both variants; the public command also runs its usual T0 control:

```powershell
& '.\.venv-ingestion\Scripts\python.exe' -m experiments.cytiva.visual_validation convert --source 'references/manual.pdf' --output 'data/experiments/cytiva/visual-validation-v01/matching-on-NEW' --blocks p088 --cell-matching
& '.\.venv-ingestion\Scripts\python.exe' -m experiments.cytiva.visual_validation convert --source 'references/manual.pdf' --output 'data/experiments/cytiva/visual-validation-v01/matching-off-NEW' --blocks p088 --no-cell-matching
```

This experiment used only the T1 workers after the same source/cache preflight;
it did not repeat the unnecessary T0 control. Exact executed commands are local
in its manifest.

Profile serialization now uses `serialize_as_any=True`: Pydantic previously
omitted subclass fields such as `do_cell_matching` and `mode`. Existing profiles
were not rewritten. At that time, seven model-free launcher tests passed, including a check
that public/private CLI entrypoints preserve the enabled default and accept both
explicit settings. Runtime checks verify saved settings, source hashes, all 24
probes, five note references and unchanged earlier conversion/reference artifacts.

## Subsequent reconstruction and remaining limits

Keep both Docling outputs quarantined. The later deterministic reconstruction
from PDF word coordinates preserves each source segment separately and has since
received documentary human review with reservations. That review does not turn
this ablation into a successful conversion or validate other tables generally.
Alternatively compare another table-structure model in a separate frozen trial;
this ablation did not evaluate TableFormer V2 or OCR.

A geometry validator could flag a single-column cell whose box overlaps multiple
product columns despite `col_span=1`. Real merged cells must remain supported;
this would be a review trigger, not an automatic repair. Any reconstruction must
read all four source regions, not copy the first value into apparent blanks.
No global chunk-budget change or LLM extraction is justified by this result.

On 2026-10-22, the launcher suite was extended to nine tests. The two added
regressions exercise real public-runner command construction for both T0/T1 and
both matching settings, and effective worker-profile serialization. A lightweight
Pydantic base/subclass fixture reproduces erased subclass fields if
`serialize_as_any=True` is removed. The Docling converter is stubbed and stops
before inference; no model or PDF conversion is run by these tests.
