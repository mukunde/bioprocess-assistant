# MabSelect cleaning journey — validated design v01

Prepared 31 October 2026 against merged `main` at `9b4bd25`.
Status: MS01–MS08 and C1–C4 validated by the project user on 31 October 2026.
The application implementation and its verification are recorded separately.
The [exact approved contract](mabselect-cleaning-approved-contract-v01.md) and
[portable verifier](../../experiments/cytiva/verify_mabselect_design.py) preserve
the original review binding; this maintained guide is not that immutable snapshot.
The existing Protein A/G journey, frozen v03 and historical reviews stay unchanged.

## Purpose and boundary

Provide a local, model-free documentary lookup of **MabSelect cleaning guidance**
on PDF page 167 of CY13981-25Jan21-HB. Let the user explore a deposit category,
inspect documented alternatives, and open the exact original passages and
reservations. Do not choose a treatment for a real process or establish a cause.

The page-166 statement about cleaning when backpressure increases belongs to
Protein G/Protein A Sepharose (`E166-H/T`). It is not a documented MabSelect
cleaning trigger in this selected corpus. A pressure symptom may motivate opening
this journey, but cannot establish a MabSelect deposit, diagnosis or recipe.
The existing video illustrates the earlier guided route, not this proposed flow.

## Existing source and review basis

The [source dossier](mabselect-cleaning-sources-v01.json) contains exact snapshots,
source PDF identity, quote hashes, page indices/offsets, five original scoped
human decisions and their unchanged messages/reservations. It binds the original
[evidence](../../experiments/cytiva/retrieval-pilot-v01/evidence.json),
[Q review](../../experiments/cytiva/reviewed-cleaning-retrieval/review.json) and
[N review](../../experiments/cytiva/reviewed-section-questions/review.json).
Preparation flags in the original evidence remain pending; later Q/N decisions
supply documentary approvals only within their recorded scope. The separately recorded design approval adds no source publication or
scientific/operational validation. The source dossier remains the unchanged
pre-implementation snapshot; its pending-design status records that earlier stage.

| Documentary block | Existing decision | Entire required source bundle |
|---|---|---|
| Four general alternatives for precipitated/denatured substances | Q05 | E167-H, E167-PH, E167-P |
| Restricted stronger-alkali sequence | Q06 | E167-H, E167-PH, E167-SH, E167-S |
| Hydrophobic-context nonionic detergent and following-wash pH | N06 | E167-H, E167-LH, E167-D |
| Hydrophobic-context organic solvents and two precautions | N07 | E167-H, E167-LH, E167-E, E167-W |
| Missing product/context clarification | Q09 | E166-H/T/PH/LH plus E167-H/PH/SH/LH; context/headings only |

Q07, N02, N03 and N05 remain supporting comparison/refusal precedents in the
original reviews. They do not grant permission to drop required comparison
sources or promote them to independent recipe approvals. Primary single-product
bundles above avoid that problem. If a comparison feature is later added, it must
assemble that comparison's entire reviewed bundle separately.

## Proposed form and response

English UI labels and verbatim English source quotations. No free-text parser,
LLM, paid API, new extraction or Neo4j migration is needed for this first scope.

1. **Exact product**: Not specified; MabSelect family, variant unknown;
   MabSelect (exact unsuffixed product); MabSelect SuRe; MabSelect SuRe LX;
   Other product / variant not listed. The difference between the family label
   and the unsuffixed product must be explicit; no preselected SuRe variant.
2. **Context to explore**: Unknown; precipitated or denatured substances;
   strongly bound hydrophobic proteins, lipoproteins or lipids; mixed/other.
   This is a documentary category, not a required confirmed diagnosis.
3. **View documented guidance**: clarification or the complete relevant source
   blocks; no best-treatment selection, recommendation ranking or default chemical.

Unknown exact product blocks product-specific recipe cards, including generic
MabSelect-family selection. This is a conservative proposed application policy,
not a claim that the manual withholds all general guidance until a variant is known.
Show the section distinctions and ask for the exact label once. A known product
with unknown context asks for available sample/prior-treatment/deposit context,
without asking for the product again or demanding a confirmed diagnosis.

The first supported exact identities are MabSelect, MabSelect SuRe and MabSelect
SuRe LX. Other named or newer variants remain outside this edition-bound lookup;
absence from this list is not a chemical incompatibility or a claim about current
manufacturer availability. Do not infer other variant membership from a substring.

The response header names product and explored category and says that suitability
is not established. Show product/deposit scope before quantities. Every procedure
card retains ordered steps, immediate follow-up wash and attached warnings. Use
citation links to full passages and expose original reservations/provenance.
Changing input marks old results stale. Invalid, missing or altered source/review
bindings produce an unavailable result, never a partially reconstructed recipe.

## Documentary options — preserve exact scopes

CV means the manual's column volumes; do not calculate mL or minutes from CV.
The following summaries aid contract review; original quotations below remain
canonical and must not be replaced by an independently generated procedure.

### A. Precipitated or denatured substances: general block (Q05)

For a supported exact MabSelect identity, show four **separate alternatives**, each
using **2 CV**, with **at least 10 min** contact:

| Alternative | Keep this composition intact |
|---|---|
| A1 | 50 mM sodium hydroxide in 500 mM sodium sulfate |
| A2 | 50 mM sodium hydroxide in 1 M sodium chloride |
| A3 | 100 mM sodium phosphate; no added sodium hydroxide inferred |
| A4 | 6 M guanidine hydrochloride in 10 mM sodium hydroxide |

Every alternative keeps the immediate subsequent wash with **at least 5 CV of
sterile filtered binding buffer at pH 7.0–8.0**. The contact minimum is not exactly
10 min; the pH belongs to the following binding-buffer wash, not an inferred pH
for the cleaning solutions. Do not combine the four formulations, run them as
successive steps or select one as operationally suitable.

### B. Additional product-restricted block (Q06)

Only **MabSelect SuRe or MabSelect SuRe LX**, and only the precipitated/denatured
substances context supported by the review:

1. 3 CV binding buffer.
2. At least 2 CV of 100–500 mM sodium hydroxide; contact **10–15 min**.
3. Immediately at least 5 CV sterile and filtered binding buffer, pH 7.0–8.0.

Preserve the displaced scope paragraph `E167-SH` despite native extraction order.
Present this as an additional, explicitly restricted documentary sequence, beside
its general block. Do not call it a mandatory next step, a fifth formulation in
A1–A4, a superior treatment, or an equivalent substitute. The source does not
establish an operational choice between the two blocks or a concentration-selection
algorithm. Do not offer it for plain MabSelect, unknown variants or hydrophobic
context merely because a SuRe product is selected.

### C. Hydrophobic proteins, lipoproteins or lipids (N06/N07)

| Separate route | Preserved quantities and sequence | Limits and warnings |
|---|---|---|
| C1 — Nonionic detergent | 2 CV, with a 0.1% solution as an example; immediately at least 5 CV sterile filtered binding buffer, pH 7.0–8.0 | No named detergent, temperature, contact time or numerical flow in this block. The pH is for the subsequent wash, not the detergent |
| C2 — Organic-solvent alternative | 3–4 CV of **70% ethanol OR 30% 2-propanol**; immediately at least 5 CV sterile filtered binding buffer, pH 7.0–8.0 | Increasing gradients to avoid air bubbles at high organic-solvent concentrations; lower flow because these solvents increase backpressure. No numerical gradient, flow or pressure limit |

Display C1 versus C2 as alternatives; within C2 preserve ethanol OR 2-propanol,
not a mixture or consecutive treatments. The gradient precaution concerns air
bubbles; it must not be relabelled as a pressure-reduction instruction. Retain the
manual's two solvent formulations literally in the original quotation.

Do not import the Sepharose example's Triton X-100, 37°C, 1 min or 12-hour ethanol
stand. Missing contact time here means unspecified in this block, not prohibited,
zero, or absent from all product documentation. Do not infer restored capacity,
reuse permission, lifetime, contaminant removal or the cause of the observation.

## Clarification and bounded absence

| Situation | Proposed behaviour |
|---|---|
| No product or only MabSelect-family identity | Ask for exact product label; headings/context only, no recipe card |
| Exact supported product, context unknown | Ask which available context to explore; do not infer a protein/lipid deposit or require a confirmed diagnosis |
| Both deposit categories / uncertain choice | Preserve uncertainty; ask which category to inspect first. No combined chemical sequence or hidden prioritization |
| Other or contradictory product labels | Outside scope or clarification; do not choose a label by string similarity |
| Plain MabSelect asks for 100–500 mM NaOH block | State that the reviewed stronger-alkali block is restricted to SuRe/SuRe LX. Do not infer a universal ban on NaOH for plain MabSelect; Q05 itself contains NaOH alternatives |
| Pressure increase alone on MabSelect | No inferred deposit or recipe, and no attribution of E166-T to MabSelect. Ask product/context as needed |
| Solvent route asks for mL/min or maximum bar | Give documented lower-flow/gradient guidance; state numerical values are unspecified in the selected block. No percentages, mL/min, bar or cross-product transfer |
| MabSelect solvent route asks for contact duration | No transfer of the page-166 12 h. Keep the documented volumes, follow-up wash and precautions |
| Request to calculate mL, dose, exact pH or reuse count | Outside this first documentary selector; no calculation, optimization or lifetime claim |
| Missing exact source or review/reservation binding | Evidence unavailable; fail closed and retain the prior reviewed records |

These behaviours are proposed application rules, not additional manual quotations.
No new absence claim extends beyond the cited section. Numerical requests outside
the form need no new interpreter; the UI can state missing parameters and scope.

## Validated application decisions

| ID | Proposed decision |
|---|---|
| MS01 | Use a separate MabSelect cleaning entry point; do not extend the Sepharose pressure-trigger claim to MabSelect |
| MS02 | Distinguish family-unknown, plain MabSelect, SuRe and SuRe LX; allow recipe cards only for the three exact identities initially |
| MS03 | Keep A1–A4 separate, minimum contact and immediate wash intact, with no automatic treatment selection |
| MS04 | Show the additional restricted block only for SuRe/SuRe LX in the reviewed precipitated/denatured context; do not concatenate or rank it |
| MS05 | Keep detergent versus solvents, and ethanol versus 2-propanol, as separate alternatives, with both precautions attached |
| MS06 | Unknown/mixed context yields clarification, not a diagnosis or a combined recipe; bounded missing-parameter messages retain available guidance |
| MS07 | Reuse Q05/Q06/N06/N07/Q09 only within their entire scoped bundles and original reservations; source flags and original human messages remain unchanged |
| MS08 | Implement incrementally only after this contract review: no v03 modification, no source publication, no new parser/model/database or expanded scientific claim |

The [recorded approval](mabselect-cleaning-review-v01.json) covers MS01–MS08 and
C1–C4. It approves application design, not scientific or operational suitability.
C1 distinguishes exact product/family identity; C2 keeps general/restricted blocks
separate; C3 preserves unknown/mixed context; C4 attaches pH only to the following
wash and prohibits invented parameters.

## Acceptance checks — MC01–MC12 implemented

| ID | Case and required outcome |
|---|---|
| MC01 | Missing/family-only product: exact-label clarification; zero recipe cards |
| MC02 | Plain MabSelect + precipitated context: four alternatives, 2 CV and at least 10 min each, complete subsequent wash; no restricted block |
| MC03 | SuRe + precipitated context: general alternatives and separate complete three-step restricted block; no implied succession |
| MC04 | SuRe LX same context: same restriction and ordering; no arbitrary concentration selection |
| MC05 | Plain MabSelect asks for stronger-alkali route: scope explanation without a general NaOH prohibition |
| MC06 | Supported product + hydrophobic context: detergent and solvent alternatives; no restricted alkali block |
| MC07 | Detergent: 2 CV, example status, immediate wash; no transferred Triton/37°C/1 min; pH only on following buffer |
| MC08 | Solvents: 3–4 CV, OR preserved, full wash, separate air-bubble and pressure precautions; no 12 h, numerical flow, pressure or gradient |
| MC09 | Unknown/mixed context: no inferred deposit, chosen chemical or merged procedure; independently known fields retained |
| MC10 | Unlisted/contradictory product: outside scope/clarification; no family-name match that activates a recipe |
| MC11 | Exact quotation, PDF hash/page/index/offset, required headings and original scoped reservations remain available; tampering fails closed |
| MC12 | Existing Protein A/G and guided/text paths, stale results, source links, v03 integrity and excluded-source policy remain unchanged |

These are development conformance tests, implemented in
[test_mabselect_journey.py](../../tests/test_mabselect_journey.py). They are not
fresh held-out questions or an independent benchmark. All twelve passed together
with seventeen existing journey/demo regressions. MC12 is supplemented by
[DOM/HTTP regressions](../../tests/test_mabselect_ui.py) and
[approval-integrity regressions](../../tests/test_mabselect_design_integrity.py).
Their isolated [Node/jsdom setup](../../tests/ui/README.md) is a development-test
requirement only; it does not change the frozen Python runtime. The prior 800-test checkpoint
remains historical; see the [implementation verification](../validation/MABSELECT-CLEANING-DEMO.md)
for the current run, browser checks and limitations.

## Source quotations for the new product route

Exact wording and line breaks below come from the existing evidence ledger.
PDF page 167 has zero-based index 166. Offsets use Unicode code points in the
unchanged extracted page text, start inclusive and end exclusive. See the dossier
for exact UTF-8 quote hashes and the source PDF identity. No PDF is redistributed.

### E167-H — product_scope

PDF page 167, offsets [0, 94).

> Cleaning of MabSelect media
> All MabSelect media can be cleaned using the following procedures:

### E167-PH — deposit_scope

PDF page 167, offsets [96, 143).

> To remove precipitated or denatured substances:

### E167-P — procedure

PDF page 167, offsets [144, 515).

> 1.  Wash the medium with 2 column volumes of 50 mM sodium hydroxide in 500  mM sodium sulfate, or 50 mM   
> sodium hydroxide in 1 M sodium chloride, or 100 mM sodium phosphate, or 6 M guanidine hydrochloride in  
> 10 mM sodium hydroxide. Contact time: at least 10 min. 
> 2. Immediately wash with at least 5 column volumes of sterile filtered binding buffer at pH 7.0 to 8.0.

### E167-SH — restricted_product_scope

PDF page 167, offsets [1259, 1386).

> MabSelect SuRe and MabSelect SuRe LX are alkali-tolerant, allowing the use of more concentrated solutions of sodium 
> hydroxide:

### E167-S — procedure

PDF page 167, offsets [516, 780).

> 1. Wash with 3 column volumes of binding buffer. 
> 2. Wash with at least 2 column volumes of 100 mM to 500 mM sodium hydroxide. Contact time: 10 to 15 min. 
> 3. Immediately wash with at least 5 column volumes of sterile and filtered binding buffer at  pH 7.0 to 8.0.

### E167-LH — deposit_scope

PDF page 167, offsets [1387, 1459).

> To remove strongly bound hydrophobic proteins, lipoproteins, and lipids:

### E167-D — procedure

PDF page 167, offsets [781, 960).

> 1. Wash with 2 column volumes of a nonionic detergent (e.g., 0.1% solution).
> 2 Immediately wash with at least 5 column volumes of sterile filtered binding buffer at pH 7.0 to 8.0.

### E167-E — alternative_procedure

PDF page 167, offsets [962, 1258).

> 2a. Alternatively, wash with 3 to 4 column volumes of 70% ethanol or 30% 2-propanol. Wash immediately with at 
> least 5 column volumes of sterile filtered binding buffer at pH 7.0 to 8.0. Apply increasing gradients to avoid air 
> bubble formation when using high concentrations of organic solvents.

### E167-W — warning

PDF page 167, offsets [1461, 1605).

> Washing with 70% ethanol and 30% 2-propanol will increase backpressure. Use a lower flow rate when cleaning 
> with 70% ethanol or 30% 2-propanol.

