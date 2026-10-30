# First bounded troubleshooting journey

Implemented locally on 30 October 2026. This is a deterministic documentary
journey for increasing backpressure on **Protein A or Protein G Sepharose**.
It is separate from the frozen v03 procedural interpreter and the legacy chat.
It uses no model, database, paid API, new extraction or new scientific approval.

## Try it

Start the current checkout's demo using the existing installation and launcher,
then select **Troubleshooting · rising backpressure** in Input. A direct link is
`http://127.0.0.1:8766/#troubleshooting-controls` for the default port. The local
development verification uses port 8776 to avoid interrupting an existing server.
An already running Python server must be restarted to load changed Python code;
an older Sandbox clone does not automatically receive these local changes.

1. Leave the product unspecified and submit: clarification, no recipe.
2. Select Protein A Sepharose and leave context unknown: the manual's cleaning
   indication is shown, with a request for context and no assumed deposit.
3. Explore precipitated/denatured proteins: the original two-step quotation is
   shown with its product/category scope and page citation.
4. Explore strongly bound hydrophobic proteins, lipoproteins or lipids: the
   detergent example and ethanol alternative remain separate. The ethanol
   pressure precaution is included, not separated from its route.
5. Select MabSelect: explicitly outside this first journey; no Sepharose recipe
   is transferred. Other reviewed MabSelect excerpts are not a supported recipe
   selector in this prototype.
6. Change a field without resubmitting: previous results are marked stale.
   Return to Guided request to exercise the existing v03 route independently.

Choosing a context means exploring a documentary category, not asserting a
confirmed diagnosis. No pressure threshold, solvent flow, missing volume,
performance guarantee or operational authorization is invented. English UI and
original English quotations are retained; this is not a new free-text parser.

## Source and approval boundaries

The source corpus is the 17 original excerpts on PDF pages 166–167 in
`experiments/cytiva/retrieval-pilot-v01/evidence.json`. Their frozen preparation
flags remain untouched. The completed ten-question documentary review in
`experiments/cytiva/reviewed-cleaning-retrieval/` supplies the scoped approvals and
unchanged reservations. Question/reference answers are never indexed or displayed
as source quotations. The prototype is not an independent retrieval benchmark.

| Branch | Reused review scope | Required displayed source bundle |
|---|---|---|
| Unknown product | Q09 | E166-H/T/PH/LH and E167-H/PH/SH/LH; headings/context only, no recipes |
| Known supported product, unknown context | Q01 + Q09 | Same clarification bundle; no deposit-specific recipe |
| Precipitated/denatured proteins | Q01 + Q02 | E166-H/T/PH/P |
| Hydrophobic deposit context | Q01 + Q03 + Q04 | E166-H/T/LH/D/E/W; alternative routes, warning retained |
| MabSelect | Q09 | Clarification scope only; outside supported product route |

The package verifier checks original review events, source identity, quotations,
offsets and reservations on every request. Loaded evidence and review snapshots
are checked against their file bindings before use. Responses retain source PDF
identity, quote hashes, PDF pages/indexes and exact extracted-text offsets.
The review's `publication_allowed: false`, production-retrieval and scientific
validation limitations are not promoted. Nothing is written to Neo4j or published.

The original manual text is displayed intact. For example, the detergent's
temperature/time remain an example; the ethanol hold is not copied to MabSelect;
the following wash and the pressure precaution are retained. No CV-to-mL or
duration calculation is performed.

## Verification

Ten new regressions cover unknown/missing scope, no recipe from pressure alone,
both supported products, preservation of alternatives and quantities, unsupported
products, invalid/source-override payloads, unavailable review, exact provenance
and reservations, evidence changes after validation and separation from v03.
Together with the sixteen existing demo/HTTP tests, all **26 targeted checks pass**.

Browser checks exercised product clarification, context clarification, stale
results, the protein sequence, hydrophobic alternatives, MabSelect refusal and
return to the old guided route. Quotes retain Unicode and link to source cards.
The normal narrow in-app viewport was used; no second-PC or broad browser/device
certification is claimed. Private screenshots and test logs remain under
`.local-tools/troubleshooting-demo-v01/`.

The new journey is development work awaiting user usability review. Frozen v03,
historical trials, source records and the sixteen excluded old notes are preserved.

The maintained complete suite ran **812 tests in 302.879 seconds: 811 passed,
one skipped, no failures or errors**. The skip is the existing optional PDFium
preview dependency. This verifies the maintained tests, not new operational or
scientific suitability. The new route remains outside the frozen v03 contract.

## Four-scenario usability review — 30 October 2026

The agent replayed all four scenarios in the real local browser, before and
again after the two presentation changes below. This is an agent usability
check, not a new human scientific approval or independent retrieval benchmark.

| Scenario | Observed result | Status |
|---|---|---|
| Unknown product and context | Asks for the exact product; no deposit-specific recipe; product-selection button returns to the form | Pass |
| Protein A Sepharose, hydrophobic context | Two separate alternatives; detergent remains an example; ethanol retains 12 h, following wash and pressure precaution | Pass |
| MabSelect | Explicitly outside this first journey; zero recipe cards; no Sepharose treatment transferred | Pass |
| Open E166-W citation | Navigates to the original quotation, PDF page 166, product scope and lower-flow warning; return link available | Pass |

Two minor usability issues were corrected in the HTML only:

- The long hydrophobic context label was clipped by the native select control.
  A wrapping selected-context summary now displays the full label, also associated
  with the select for assistive technology.
- Clarification and outside-scope source bundles now explicitly describe their
  role as context and section headings, with no recipe selected. Original
  quotations and their product scopes remain unchanged.

Changing a selection still marks previous results stale. The final browser
console contained no warnings or errors. These checks used the normal desktop
in-app viewport; the earlier narrow-viewport checks are historical. Reloading
resets the unsaved form; use the direct troubleshooting link to restart this
journey. No persistent request history is implemented.

After the presentation corrections, all 26 targeted tests passed again in
9.368 seconds:

```powershell
.\.local-tools\verification-venv\Scripts\python.exe -m unittest tests.test_cytiva_troubleshooting tests.test_cytiva_demo tests.test_cytiva_http_rejection -v
```

The 812-test complete-suite result above predates these two HTML presentation
changes. It is retained as the implementation baseline, not described as a new
complete-suite run. The unchanged v03 freeze and environment were reverified;
all sixteen excluded notes, 100 protected media files and 88 prior Sandbox
trial/diagnostic files matched their recorded raw SHA-256 baselines.

## Prepared versioning lot

Exactly these six files belong to the new journey:

| File | Purpose |
|---|---|
| `demo/cytiva.py` | Dispatch the separate documentary journey after the unchanged freeze check |
| `demo/troubleshooting.py` | Bounded rules, verified review scope, exact quotations and provenance |
| `demo/static/cytiva.html` | Product/context form, alternatives, clarification, source links and usability fixes |
| `tests/test_cytiva_troubleshooting.py` | Ten regressions for source scope, quantities, input rejection and v03 separation |
| `docs/DEMO-FIRST.md` | Link the local journey from the demonstration guide |
| `docs/validation/CYTIVA-TROUBLESHOOTING-DEMO.md` | Scope, review mapping, verification, limitations and this lot |

Proposed branch: `codex/cytiva-backpressure-demo`.

Proposed commit message:

```text
feat: add reviewed Cytiva backpressure troubleshooting journey
```

No raw screenshots, private test logs, dependencies, source PDFs, old notes,
previous media, frozen artifacts or unrelated changes belong to this lot.
The three preceding local Sandbox/reliability commits are separate work and
are not part of this six-file diff. The lot is prepared for user approval;
no staging, commit, push or publication was performed during this review.
