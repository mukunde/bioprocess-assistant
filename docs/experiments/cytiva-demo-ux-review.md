# Cytiva guided demo: usability fixes and browser walkthrough

Status: corrected local demo, ready for another user walkthrough. This document
closes the interface findings from the first browser walkthrough; it does not
change or revalidate the frozen v03 engine.

## Implemented changes

- Missing format: a guided `missing_context` diagnostic for `supported_column`
  now asks for 1 mL or 5 mL and provides a button focusing the format field.
  No value is selected on the user's behalf.
- Stale results: changing request fields shows a warning while retaining a
  summary of the request that produced the displayed results. A successful
  resubmission clears the warning only if current inputs still match that
  submission. Example buttons and text-mode changes use the same check.
- Navigation: persistent request/results/sources links, automatic result focus
  after a fresh response, and a return link beside each source reduce scrolling.
- Citations: the selected format is labelled and literal format mentions are
  highlighted. Complete quotations, warnings and source bindings remain intact;
  no flow value is inferred, removed or rewritten.
- Quarantine and absence: the interface explains that excluded excerpts cannot
  supply parameters and that absence is limited to the 25 selected excerpts.
  An assessed empty eligible set displays “No eligible context”, preserving the
  underlying `not_applicable` state rather than suggesting a success ratio.

Only the HTML/CSS/JavaScript presentation changed for these fixes. The server,
structured submission construction and all 36 frozen dependencies are unchanged.

## Browser checks performed

| Check | Observed result |
|---|---|
| UX01 — Guided 1 mL washing flow | 1/1 known requests supported; eligible context 1/1; request summary and column-specific binding visible |
| UX02 — Citation navigation | E121-W opens at its original page-121 quotation; return link restores the results location |
| UX03 — Quote preservation | All five displayed quotation `textContent` values equal the source registry exactly; only `1 mL column` is highlighted in E121-W |
| UX04 — Changed input | Selecting an unspecified format shows the stale-result warning while the previous 1 mL result summary remains explicit |
| UX05 — Clarification | New result is 0/1 supported, “No eligible context”, explicit 1 mL/5 mL instruction and a correction button |
| UX06 — Correction action | The button returns to the request and focuses the format selector without changing its value |
| UX07 — Mixed request | Washing supported, maximum pressure absent, equilibration quarantined; request support 1/3 and eligible context 1/1 |
| UX08 — Current result | After successful resubmission the stale warning is hidden; absence/quarantine explanations are visible |

These are interactive browser checks, not eight additional automated unit tests.
The complete automated suite and preservation fingerprints are recorded in
[the current checks](cytiva-demo-ux-checks.json). The earlier
[freeze/demo checks](v03-freeze-demo-checks.json) retain the initial interface's
fingerprints as a historical snapshot; their older HTML digest is not a claim
about this corrected interface.

## Remaining scope

No blocking problem was observed on this walkthrough. Input controls and
technical source quotations remain in English; the EN/FR selector describes the
input language. Cross-browser accessibility and a clean-machine installation
have not been certified. The local server must remain running during use.

Keep packaging/launch simplicity as the next product delivery. This walkthrough
is development evidence over known excerpts, not new prospective performance,
whole-manual coverage or scientific suitability. Frozen v03, historical methods,
source decisions, native results and the 16 older local notes remain unchanged.
