# Documentary fidelity and model choice — 19 October 2026

Historical v0.1 trial report. Raw artifacts remain local under `data/experiments/cytiva/pages-097-099-v01/`; tools are in [experiments/cytiva](../../experiments/cytiva/README.md). The current contract is v0.2.

**Recommendation: provisionally retain GPT‑6.1 Sol for extraction with this prompt and effort setting.** It better preserves conditions, distinguishes purposes from applicability restrictions and identifies two ambiguities actually present in the PDF. Its output still needs three representation corrections and quarantine of a contradictory instruction before graph integration can be prepared.

This choice rests on the assistant's review of 49 proposals, not raw relation counts. Responses were read alongside cited text, full renderings of the three PDF pages and ontology v0.1 definitions. The review is not blind; rationales are explicit so Gaël can challenge them. At this historical checkpoint, the eight earlier cards remained a development catalogue without human approval. No claim was approved in the database or modified in original outputs.

## Proposal assessment

| Assistant's proposed verdict | Sonnet 5.5 | GPT‑6.1 Sol |
|---|---:|---:|
| Faithful, no correction identified in this claim | 10 | 22 |
| Faithful content with representation/normative-force reservation | 2 | 3 |
| Requires correction before use in our ontology | 8 | 3 |
| Faithful to an ambiguous passage; quarantine required | 0 | 1 |
| Total examined | 20 | 29 |

These are not comparable precision rates: extracted units differ, particularly Sonnet's 6 PROCEDURE entries versus Sol's 19. Corrections include logical or ontological reformulations, not just invented assertions. Model uncertainty notes are considered, but do not neutralize an edge that remains usable with incorrect meaning.

Some v0.1 requirements, notably restricting RECOMMENDED_FOR to an observed symptom and explicitly distinguishing cleaning from CIP, were less precise in the benchmark prompt. Related corrections therefore also identify extraction-contract defects; they cannot all be attributed to intrinsic model weaknesses. Rules were applied equally to both candidates.

Both outputs conform to the JSON schema and have no nonexistent item references. The only automatically detected domain/range error is Sonnet c20. Type checks detect neither its incorrect c15 predicate nor Sol cl8's cleaning-to-CIP substitution.

## Differences motivating the choice

| Checked point | Sonnet | Sol | Conclusion |
|---|---|---|---|
| Acid-labile IgG, p.98, items 59–60 | c13 imposes acid-labile IgG under applicability, restricting general tube preparation | cl14 preserves general preparation and its rationale in stated_purpose_context | Sol advantage. Quantities are correct in both. |
| Denaturation prevention, p.99, item 70 | c15 invents prevention of accumulated low-pH exposure; c14 also uses RECOMMENDED_FOR | cl11 retains a possible cause; cl12 also uses RECOMMENDED_FOR for prevention | Sol advantage, but cl12 must also become a procedure with a stated purpose. In v0.1, RECOMMENDED_FOR means a recommendation when the symptom is observed. |
| Increased pressure, p.99, item 78 | c9 preserves cleaning the column | cl8 replaces cleaning with CIP | Sonnet advantage. CIP context makes Sol's choice plausible, but the ontology prohibits automatic equivalence. |
| Cross-contamination, p.97, item 1 | c20 forces RECOMMENDED_FOR toward a Cause; the model acknowledges this | cl10 retains a procedure purpose | Sol advantage. |
| Decreased flow, p.99, item 71 | c16 loses the possible necessity within the proposal itself; the caveat appears only in uncertainties | cl13 retains that possibility in the parameter and action name | Sol advantage. |
| Reuse, p.99, item 75 | c18 encodes conditional Reuse without retaining that reuse is only to be considered and depends on sample nature | cl15 explicitly preserves a necessary, not sufficient, condition | Sol advantage. |
| Sample preparation, p.98, item 53 | c19 applies not_equals to a whole sentence, which is not an evaluable condition | cl17 retains if required; cl16 has an overly broad and apparently unconditional subject | Both need correction; Sol's is localized to cl16's name/subject. |
| Blank run, p.99, item 78 | c10 changes a recommendation's purpose into CAN_REMOVE despite cautious modality and note | cl9 represents a procedure and purpose, but lacks explicit recommended force | Sol advantage. Preserve normative force in the next schema. |

## Quantities, units, comparators and sequences

**No incorrect numeric value was identified among present parameters.** An omitted parameter is not counted as a false value. Product/phase, conditions, alternatives and denominators are checked too: the same number does not ensure a faithful instruction.

| PDF parameter | Sonnet | Sol | Verification |
|---|---|---|---|
| Tubes: 60–200 µL of 1 M Tris-HCl, pH 9.0 **per mL of fraction**, p.98 | c13 | cl14 | Correct in both; Sonnet applicability needs correction. Approximately neutral final pH preserved. |
| CIP if required immediately after elution: **at least 2 CV**, **0.1–0.5 M** NaOH, **10–15 min** contact, then **5 CV** binding buffer, p.99 | c11 | cl20 | Numbers, minimum, context and order preserved. The manual does not define the if-required criterion. |
| No CIP planned: **5 CV** elution buffer **and/or 3 CV** binding buffer, p.99 | c12 | cl19 | Correct; Sonnet stores and/or in the parameter/action name, a fragile representation for logical execution. |
| Sample pH **6–9** before loading, p.98 | c19 | cl16 | Correct number; Sonnet's condition logic and Sol's action subject need correction. |
| Centrifugation **10,000 × g**, **10 min**, then **0.45 µm** filter, p.98 | Not extracted | cl22 | Correct; no conversion to RPM. |
| Binding buffer: **0.02 M** phosphate, **0.15 M** NaCl, **pH 7.2**; elution: **0.1 M** citrate, **pH 3.0–3.6**, p.98 | No complete composition card | cl17, cl19–21, cl25–27 | Correct and associated with the protocol. |
| Buffer filtration **0.45 µm** before use, p.98 | Not extracted | cl23 | Correct. |
| Loading: **0.2–1 mL/min** for a **1 mL** column, **0.5–5 mL/min** for **5 mL**, p.98 | Not extracted | cl24 | Correct, without mixing figure-example conditions. |
| Washing: usually at least **5–10 CV**, until a stable baseline or no material in effluent; **1–2 / 5–10 mL/min** for **1 / 5 mL**, p.98 | Not extracted | cl25 | Numbers, column sizes and stopping criterion preserved. |
| Step elution: **5 CV** usually sufficient; gradient: **10–20 CV** usually sufficient; **1–2 / 5–10 mL/min**, p.98 | No numeric parameter | cl26–27 | Correct; usually preserved, without guaranteed sufficiency. |
| Syringe: **2–5 CV of binding buffer**, p.98 | Not extracted | cl28 | Faithfully copies a PDF ambiguity; quarantine mandatory before use. |
| Re-equilibration: **5–10 CV OR until the same pH as the buffer**, p.99 | Not extracted | cl21 | Alternative and sequence preserved. |
| Storage: **20%** ethanol, **2–8 °C**, p.99 | Not extracted | cl29 | Correct; percentage basis unspecified, no invented v/v. |

CV means column volume: no automatic conversion to mL without a specified column volume. µ and μ are typographic alternatives for micro, not different quantities.

## Source ambiguities and omissions

Two difficulties flagged by Sol are visible in the PDF:

1. P.98, step 5, item 64: the sentence actually contains « with at 10 column volumes ». Sol abstains on this volume. Do not automatically resolve it as exactly 10 or at least 10. The step's recommended flow rates remain separately extractable.
2. P.98, step 8, item 67: the general instruction requests elution buffer, then the syringe sentence mentions binding buffer. Sol reproduces the latter and flags the issue. This is documentary ambiguity, not model hallucination. A global note alone does not block the claim: add a source_conflict status to cl28, preventing its availability as an instruction until clarification.

Both models correctly separate the p.98 protocol from the p.97 figure example: figure pH 7.4/glycine-HCl pH 3.5 is not merged with protocol pH 7.2/citrate pH 3.0–3.6. Neither transfers HiTrap MabSelect SuRe instructions to SuRe LX, whose heading opens another scope on p.99. No numeric pressure threshold or CIP interval is invented.

Sol notably omits global changes in chromatographic properties (Sonnet c1) and descriptive step-elution benefits (Sonnet c17). Both omit the initial 3–5 CV ethanol rinse, approximate drops/minute equivalents and final transfer/desalting. These are not necessarily priority omissions for the troubleshooting assistant. Neither extraction is a complete operating protocol.

## Coverage of eight development cards

Presence means the expected fact was found, not recall over the entire passage. The catalogue was known during development and was not validated as an independent reference.

| Card | Sonnet | Sol |
|---|---|---|
| C01 severe fouling → pressure | c5, faithful | cl4, faithful |
| C02 severe fouling → flow | c6, faithful | cl5, faithful |
| C03 severe fouling → blockage | c4, faithful | cl3, faithful |
| C04 cleaning recommended if pressure increases | c9, faithful | cl8, cleaning must be distinguished from CIP |
| C05 CIP can remove described contaminants | c7, faithful | cl6, faithful content, target needs normalization |
| C06 regular CIP prevents accumulation | c8, faithful content, target needs normalization | cl7, faithful content, target needs normalization |
| C07 quantified post-elution CIP if required | c11, faithful | cl20, faithful |
| C08 collection tubes, amount per mL and rationale | c13, faithful numbers but undue applicability filter | cl14, faithful |

Both recover all eight topics; each has one of these eight items requiring correction. Sol's selection mainly reflects preservation of nuance across proposals and treatment of ambiguity, not a supposed 8/8 versus 7/8 score.

## Proposed corrections before the next extraction

1. Keep Sol's three corrections in a proposed-review layer: cl8 = clean the column; cl12 = preventive procedure; cl16 = target pH before loading, distinct from conditional adjustment in cl17. Do not overwrite originals.
2. Explicitly quarantine cl28. Retain the quotation and contradiction without intuitively correcting the manual.
3. Clarify the schema contract: normative force (recommended, necessary, possible) separate from rationale; instruction separate from descriptive benefit; cleaning distinct from CIP; a purpose is neither a capability edge nor treatment of an observed symptom.
4. Represent alternatives and conditions with suitable operators and an unresolved state. `equals`/`not_equals` on sentences cannot support reliable numeric comparisons.
5. Associate every claim with explicit product and phase as well as scope_refs. Severe-fouling subjects currently encode severity in their name; do not lose it during entity normalization.
6. After validating corrections and a small human reference, test the revised contract on previously unused pages under a controlled budget. This trial cannot establish manual-wide quality, API costs or actual speed.

## Project decision

Use **GPT‑6.1 Sol as the provisional reference extractor for subsequent work**, with deterministic type/reference/quantity checks followed by targeted human documentary review. Retain Sonnet as a comparator without paying for two extractions per edition. This trial does not justify changing the daily assistant's lightweight model.

Counts above come from `audit-fidelite.json`. `AUDIT-DETAILLE.md` contains a card for each of the 49 claims, original values/conditions, reasoned verdict and pages/items to check. At this historical checkpoint human status remained pending. Capture timestamps are not inference latency; no API invoice was measured. No new model call was made during this review.
