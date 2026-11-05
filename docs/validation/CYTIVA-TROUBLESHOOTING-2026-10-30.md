# Cytiva backpressure demo validation (30 October 2026)

This record covers the standalone local demo at its initial delivery.
For current instructions, see the [demo guide](CYTIVA-TROUBLESHOOTING-DEMO.md).

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
certification is claimed.

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

After the presentation corrections, the historical run passed all 26 targeted
tests in 9.368 seconds. This count describes the test layout at that date.

The 812-test complete-suite result above predates these two HTML presentation
changes. It is retained as the implementation baseline, not described as a new
complete-suite run. The v03 freeze and its environment were reverified.
