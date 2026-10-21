# Cytiva verification cards - v0.1

**All cards are pending.** These are assistant proposals; quotations are located automatically in the existing conversion. Rendered PDF pages 97–99 were visually inspected during preparation. No human approval is inferred.

Source: *Affinity Chromatography Vol. 1: Antibodies*, CY13981-25Jan21-HB. Original/printed pages 97–99 correspond to excerpt pages 1–3.

[Open the local pages 97–99 excerpt](<../../references/cytiva-hitrap-sure-pages-097-099.pdf>)

Proposed shared scope: **HiTrap MabSelect SuRe**. Check the heading/introduction on p.97; the sections on pp.98–99 continue until the new heading “MabSelect SuRe LX”. Evidence for this scope is stored separately in the JSON.

Suggested review order: **C04 → C01 → C07 → C08**, then C02/C03/C05/C06. For each card, record approved / rejected / needs clarification with a note.

## C01 — Severe fouling → possible backpressure increase

**Status: pending.** Modality: `possible`.

Proposal: `cause:fouling` — `MAY_CAUSE` → `symptom:backpressure-increase`.

**Page 99** (excerpt 3), item `#/texts/77`, offsets `294:390` :

> If the fouling is severe, it can block the column, increase back pressure, and reduce flow rate.

Conditions / context: `fouling_severity` = `severe` (applicability)

**Review focus:** check “severe” and “can”. The symptom alone proves neither the presence nor the severity of fouling.

- [ ] Quotation and page checked in the PDF.
- [ ] Meaning, direction, modality and conditions are faithful.
- [ ] Product scope checked.
- Decision: …; note: …

## C02 — Severe fouling → possible flow reduction

**Status: pending.** Modality: `possible`.

Proposal: `cause:fouling` — `MAY_CAUSE` → `symptom:flow-reduction`.

**Page 99** (excerpt 3), item `#/texts/77`, offsets `294:390` :

> If the fouling is severe, it can block the column, increase back pressure, and reduce flow rate.

Conditions / context: `fouling_severity` = `severe` (applicability)

**Review focus:** check “severe” and “can”. The symptom alone proves neither the presence nor the severity of fouling.

- [ ] Quotation and page checked in the PDF.
- [ ] Meaning, direction, modality and conditions are faithful.
- [ ] Product scope checked.
- Decision: …; note: …

## C03 — Severe fouling → possible column blockage

**Status: pending.** Modality: `possible`.

Proposal: `cause:fouling` — `MAY_CAUSE` → `symptom:column-blockage`.

**Page 99** (excerpt 3), item `#/texts/77`, offsets `294:390` :

> If the fouling is severe, it can block the column, increase back pressure, and reduce flow rate.

Conditions / context: `fouling_severity` = `severe` (applicability)

**Review focus:** check “severe” and “can”. The symptom alone proves neither the presence nor the severity of fouling.

- [ ] Quotation and page checked in the PDF.
- [ ] Meaning, direction, modality and conditions are faithful.
- [ ] Product scope checked.
- Decision: …; note: …

## C04 — Clean the column when backpressure increases

**Status: pending.** Modality: `recommended`.

Proposal: `action:clean-column` — `RECOMMENDED_FOR` → `symptom:backpressure-increase`.

**Page 99** (excerpt 3), item `#/texts/78`, offsets `153:224` :

> When an increase in backpressure is seen, the column should be cleaned.

Conditions / context: `observed_symptom` = `symptom:backpressure-increase` (trigger)

**Review focus:** this sentence contains no intermediate cause. It does not by itself specify concentration, duration or a pressure threshold.

- [ ] Quotation and page checked in the PDF.
- [ ] Meaning, direction, modality and conditions are faithful.
- [ ] Product scope checked.
- Decision: …; note: …

## C05 — CIP can remove the targeted substances from the medium

**Status: pending.** Modality: `possible`.

Proposal: `action:cip` — `CAN_REMOVE` → `cause:retained-substances`.

**Page 99** (excerpt 3), item `#/texts/77`, offsets `0:105` :

> CIP can be performed to remove very tightly bound, precipitated, or denatured substances from the medium.

Conditions / context: shared product scope; no additional condition added.

**Review focus:** preserve “or” between categories. The target is a candidate state in the Cause class; this card adds no causal link to a symptom.

- [ ] Quotation and page checked in the PDF.
- [ ] Meaning, direction, modality and conditions are faithful.
- [ ] Product scope checked.
- Decision: …; note: …

## C06 — Regular CIP prevents contaminant buildup

**Status: pending.** Modality: `source_assertion`.

Proposal: `action:cip` — `PREVENTS_BUILDUP_OF` → `cause:contaminant-buildup`.

**Page 99** (excerpt 3), item `#/texts/78`, offsets `0:152` :

> Regular CIP prevents the build-up of contaminants and helps to maintain the capacity, flow properties, and general performance of HiTrap MabSelect SuRe.

Conditions / context: `frequency` = `regular` (applicability)

**Review focus:** prevention of buildup; frequency stays qualitative. No individual guarantee or per-cycle frequency is inferred.

- [ ] Quotation and page checked in the PDF.
- [ ] Meaning, direction, modality and conditions are faithful.
- [ ] Product scope checked.
- Decision: …; note: …

## C07 — Step 9 CIP parameters, if required after elution

**Status: pending.** Modality: `conditional_instruction`.

Proposal: `action:cip` — contextualized procedure.

**Page 99** (excerpt 3), item `#/texts/72`, offsets `165:377` :

> If required, perform cleaning in place directly after elution with at least 2 column volumes of 0.1 to 0.5 M sodium hydroxide ensuring a contact time of 10 to 15 min. Wash with 5 column volumes of binding buffer.

Conditions / context: `cip_required` = `True` (applicability) ; `timing` = `directly_after_elution` (applicability)

Parameters to check:

```json
[
  {
    "name": "cip_reagent",
    "value": "sodium hydroxide",
    "evidence_item_refs": [
      "#/texts/72"
    ]
  },
  {
    "name": "cip_concentration",
    "min": 0.1,
    "max": 0.5,
    "unit": "M",
    "evidence_item_refs": [
      "#/texts/72"
    ]
  },
  {
    "name": "cip_volume",
    "operator": ">=",
    "value": 2,
    "unit": "column_volume",
    "evidence_item_refs": [
      "#/texts/72"
    ]
  },
  {
    "name": "contact_time",
    "min": 10,
    "max": 15,
    "unit": "min",
    "evidence_item_refs": [
      "#/texts/72"
    ]
  },
  {
    "name": "following_wash",
    "value": 5,
    "unit": "column_volume",
    "material": "binding buffer",
    "sequence": "after_CIP",
    "evidence_item_refs": [
      "#/texts/72"
    ]
  }
]
```

**Review focus:** check all parameters together, including the subsequent wash. “If required” has no defined criterion here. C04 does not make this protocol automatically applicable.

- [ ] Quotation and page checked in the PDF.
- [ ] Meaning, direction, modality and conditions are faithful.
- [ ] Product scope checked.
- Decision: …; note: …

## C08 — Prepare collection tubes: amount per milliliter of fraction

**Status: pending.** Modality: `instruction_with_stated_purpose`.

Proposal: `action:prepare-collection-tubes` — contextualized procedure.

**Page 98** (excerpt 2), item `#/texts/59`, offsets `0:115` :

> Prepare collection tubes by adding 60 to 200 µL of 1 M Tris-HCl, pH 9.0 per milliliter of fraction to be collected.

**Page 98** (excerpt 2), item `#/texts/60`, offsets `0:198` :

> To preserve the activity of acid-labile IgG, we recommend adding 60 to 200 µL of 1 M Tris-HCl pH 9.0 to collection tubes, which ensures that the final pH of the sample will be approximately neutral.

Conditions / context: `antibody_property` = `acid_labile_IgG` (stated_purpose_context)

Parameters to check:

```json
[
  {
    "name": "added_Tris_volume_per_fraction_volume",
    "min": 60,
    "max": 200,
    "unit": "µL",
    "denominator": {
      "value": 1,
      "unit": "mL",
      "material": "fraction to be collected"
    },
    "evidence_item_refs": [
      "#/texts/59"
    ]
  },
  {
    "name": "Tris_HCl_concentration",
    "value": 1,
    "unit": "M",
    "evidence_item_refs": [
      "#/texts/59"
    ]
  },
  {
    "name": "Tris_HCl_pH",
    "value": 9.0,
    "unit": null,
    "evidence_item_refs": [
      "#/texts/59"
    ]
  },
  {
    "name": "stated_final_sample_pH",
    "value": "approximately neutral",
    "unit": null,
    "evidence_item_refs": [
      "#/texts/60"
    ]
  }
]
```

**Review focus:** step 1 supplies the denominator “per milliliter”. The following note explains the purpose for acid-labile IgG; it is not an exclusive restriction on step 1. pH 9.0 is the Tris pH, not the final fraction pH.

- [ ] Quotation and page checked in the PDF.
- [ ] Meaning, direction, modality and conditions are faithful.
- [ ] Product scope checked.
- Decision: …; note: …

## Counterexamples to reject

- “Increased backpressure proves severe fouling”: invalid reversal of C01.
- “Cleaning always resolves increased pressure”: C04 provides no guarantee.
- “Use exactly 2 mL NaOH”: C07 specifies at least two column volumes.
- “Apply C07 parameters to MabSelect SuRe LX”: different product, separate instructions on p.99.
- “Add 60–200 µL total regardless of collected volume”: C08 denominator lost.
- “The final fraction must have pH 9.0”: Tris pH confused with final pH.
- “Regular CIP means CIP every cycle”: invented frequency.
- “The p.97 figure buffer and p.98 protocol buffer have the same pH”: different contexts, 7.4 and 7.2.

This set supports ontology development and discussion. It is neither exhaustive annotation of the three pages nor an independent performance test.
