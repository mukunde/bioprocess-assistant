# Cytiva contaminants: ten candidate retrieval questions

**Prepared before the first retrieval measurement; human reference review pending.**

Scope: contaminant management after antibody purification, PDF/printed pages 118–121, including the Blue Sepharose / HiTrap Blue HP albumin protocol. This is a troubleshooting use case within the contaminant-removal chapter.

The four complete pages were inspected on Poppler renders. Exact pypdf-native excerpts retain page offsets and hashes. Cross-page product scope and page-121 buffer/protocol heading associations are candidate source annotations, awaiting human review.

Files: [questions and expected answers](../../experiments/cytiva/contaminants-pilot-v01/questions.json), [exact source passages](../../experiments/cytiva/contaminants-pilot-v01/evidence.json), [candidate source topology](../../experiments/cytiva/contaminants-pilot-v01/source_context.json), [preparation manifest](../../experiments/cytiva/contaminants-pilot-v01/manifest.json).

The set contains ten intents in English and French: seven supported-answer references, one clarification, and two scoped refusals. Refusal means declining the unsupported numeric or guarantee component while still returning supported guidance. No human approval is inferred.

## Candidate questions and review cards

### C01 — answer

My murine monoclonal antibody preparation contains co-purified bovine immunoglobulins. What source context and separation options does the manual identify?

**Required source excerpts:** E119-BH (p. 119), E119-B (p. 119), E119-BI (p. 119).

**Expected response:** The manual associates co-purification with native sources or sources supplemented with calf serum or bovine serum albumin. Similar physical characteristics require careful selection and optimization; HIC and IEX are options. Serum-free systems are described as largely circumventing this problem in large-scale therapeutic MAb manufacture.

**Conditions to preserve:**

- Preserve native/supplemented-source alternatives and the manufacturing scope of the serum-free statement.
- Treat HIC and IEX as options requiring selection/optimization.

**Do not infer:**

- No unique cause established for the user sample.
- No guaranteed removal or automatic culture change.
- No pH, salt, flow or column recipe invented.

**Human review checks:**

- Are both technique alternatives retained?
- Is the source association distinguished from a confirmed diagnosis?

### C02 — answer

Bovine immunoglobulins remain with my mouse monoclonal antibody. Does the manual justify choosing HiTrap Phenyl HP directly, or should I screen HIC media?

**Required source excerpts:** E119-BH (p. 119), E119-BI (p. 119), E119-S (p. 119), E119-X (p. 119).

**Expected response:** Protein hydrophobicity is difficult to predict, so the manual advises screening media with different hydrophobicities. The kit is described as including seven media. HiTrap Phenyl HP was optimal in the specific mouse-antibody screening example, not established as the universal best medium.

**Conditions to preserve:**

- Keep the recommendation to screen and optimize binding/elution conditions.
- Distinguish the seven-media kit statement from the subset of columns shown in the example.

**Do not infer:**

- Do not prescribe Phenyl HP for every murine antibody.
- Do not infer chromatogram purity or clearance from the plot.
- Do not reuse example buffer settings as a universal protocol.

**Human review checks:**

- Is the specific-example qualification preserved?
- Are screening and final medium selection distinct?

### C03 — refuse

Albumin and transferrin remain after IEX purification of my antibody. What exact pH does this section prescribe to fix the separation?

**Required source excerpts:** E119-AH (p. 119), E119-A (p. 119), E119-I (p. 119).

**Expected response:** The selected subsection gives no exact pH for this problem. Similar charge properties can leave these contaminants after IEX; in some cases, optimizing pH and elution conditions may improve separation. Decline to supply a numeric setting while providing that conditional guidance.

**Conditions to preserve:**

- Absence is scoped to the selected albumin/transferrin IEX subsection.
- Preserve "in some cases" and "might".

**Do not infer:**

- Do not transfer pH 7.0 from the separate Blue-column protocol.
- Do not invent a numeric pH, pI or gradient.
- Do not present similar charge as a confirmed cause.

**Human review checks:**

- Is the scoped refusal compatible with giving available guidance?
- Are the IEX advice and Blue-column buffers kept separate?

### C04 — answer

How does HIC remove albumin and transferrin from an antibody preparation, and is the Blue Sepharose alternative described for both contaminants?

**Required source excerpts:** E119-AH (p. 119), E119-A (p. 119), E119-H (p. 119), E119-BL (p. 119).

**Expected response:** The manual says most monoclonal antibodies are more hydrophobic than albumin and transferrin: HIC can bind the antibody while these contaminants wash through. The Blue Sepharose 6 Fast Flow alternative is stated for albumin removal; this passage does not extend that alternative to transferrin.

**Conditions to preserve:**

- Preserve "most" and conditional applicability to the target.
- Blue Sepharose alternative is albumin-specific in this passage.

**Do not infer:**

- Do not state that every antibody binds HIC.
- Do not extend Blue Sepharose removal to transferrin.
- Do not infer quantitative clearance.

**Human review checks:**

- Are target binding and contaminant wash-through correctly attributed?
- Is the albumin-only scope preserved?

### C05 — clarify

My antibody is still impure after affinity capture, but the contaminant is unidentified. Should I add IEX, HIC, SEC or a Blue column?

**Required source excerpts:** E118-USE (p. 118), E118-C (p. 118), E118-M (p. 118), E120-H (p. 120), E120-U (p. 120), E120-W (p. 120).

**Expected response:** Ask about the sample/source, intended application and purity need, the suspected or measured contaminant, and available target/contaminant characteristics. The manual selects IEX by charge differences, HIC by hydrophobicity and SEC by size. Minor contamination can be acceptable if it does not interfere with the application; Blue-column advice is conditional on albumin and target hydrophobicity. Do not select a recipe from the symptom alone.

**Conditions to preserve:**

- Identification need not be a confirmed diagnosis before clarification can begin.
- Preserve the intended-application criterion and Blue warning.

**Do not infer:**

- Do not assume albumin, aggregates or a unique contaminant.
- Do not automatically choose a column or require unnecessary polishing.
- No regulatory purity threshold or numerical acceptance criterion invented.

**Human review checks:**

- Does the answer request decision-relevant context without choosing a recipe?
- Are the technique principles and product restriction retained?

### C06 — answer

My sample has high albumin, but the target immunoglobulin has hydrophobicity similar to albumin. Does this section recommend Blue Sepharose?

**Required source excerpts:** E120-H (p. 120), E120-A (p. 120), E120-U (p. 120), E120-W (p. 120).

**Expected response:** Although HiTrap Blue HP is advised for known high albumin levels or host albumin in mammalian systems, the section explicitly says not to use Blue Sepharose media when the target has hydrophobicity similar to albumin. Preserve this exception rather than recommending it solely because albumin is abundant.

**Conditions to preserve:**

- Apply the warning to an immunoglobulin or other target with similar hydrophobicity.
- Keep the known-albumin use case separate from this exclusion.

**Do not infer:**

- No predicted target recovery or binding percentage.
- No claim that HIC or IEX will necessarily solve this case.
- No guaranteed outcome inferred.

**Human review checks:**

- Does the warning override the general use case for this stated condition?
- Is no unsupported alternative prescribed?

### C07 — answer

For HiTrap Blue HP, what flow ranges does the albumin-removal protocol give for loading and washing a 1 mL column versus a 5 mL column?

**Required source excerpts:** E120-H (p. 120), E120-P (p. 120), E121-PH (p. 121), E121-L (p. 121), E121-W (p. 121), E121-F (p. 121).

**Expected response:** During sample application: 0.2–1 mL/min for the 1 mL column and 0.5–5 mL/min for the 5 mL column. During washing: 1–2 and 5–10 mL/min respectively. Wash with binding buffer, generally at least 5–10 CV, until a steady absorbance baseline or no material remains in the effluent. Preserve column size and phase; the syringe footnote gives only approximate drop-rate correspondences.

**Conditions to preserve:**

- Keep sample application distinct from washing.
- Retain "generally at least", both alternative wash endpoints, and approximate syringe footnote scope.

**Do not infer:**

- Do not transfer 5 mL/min sample-loading advice to the 1 mL column.
- Do not confuse mL/min, mL column size and CV.
- No duration calculated without volume.

**Human review checks:**

- Are all four ranges assigned to the correct size and phase?
- Does the cross-page protocol attribution remain explicit?

### C08 — answer

For albumin elution on HiTrap Blue HP 1 mL, what volumes and flow range are stated for step versus linear-gradient elution?

**Required source excerpts:** E120-H (p. 120), E120-P (p. 120), E121-PH (p. 121), E121-E (p. 121).

**Expected response:** Use elution buffer with one-step or linear-gradient elution as alternatives. Step elution: 5 CV is usually sufficient. Linear gradient: 10–20 CV is usually sufficient. For the 1 mL column, the stated elution flow is 1–2 mL/min. The same passage lists 5–10 mL/min for the separate 5 mL column.

**Conditions to preserve:**

- Retain "usually sufficient", not mandatory universal volumes.
- Keep step and gradient alternatives and column-size attribution.

**Do not infer:**

- No gradient start/end composition, slope or duration invented.
- Do not combine the two alternatives into one sequence.
- Do not transfer the 5 mL-column flow to 1 mL.

**Human review checks:**

- Are both elution choices and their separate volume ranges retained?
- Is the 1 mL flow correctly assigned?

### C09 — answer

Which binding-buffer and elution-buffer alternatives does the HiTrap Blue HP albumin protocol list? Keep every concentration, salt and pH with its own formulation.

**Required source excerpts:** E120-H (p. 120), E120-P (p. 120), E121-BH (p. 121), E121-B (p. 121).

**Expected response:** Binding: 20 mM sodium phosphate, pH 7.0; OR 50 mM potassium hydrogen phosphate (KH2PO4), pH 7.0. Elution: 0.02 M sodium phosphate with 2 M sodium chloride, pH 7.0; OR 0.05 M potassium hydrogen phosphate with 1.5 M potassium chloride, pH 7.0. Preserve all four formulations separately.

**Conditions to preserve:**

- Keep binding and elution distinct and each OR as an alternative.
- KH2PO4 is a plain-text rendering of the printed subscript formula.

**Do not infer:**

- Do not mix salts or buffer strengths across alternatives.
- Do not infer that all cross-pairings are interchangeable or validated.
- Do not derive a pH adjustment recipe.

**Human review checks:**

- Are all concentrations, salts and pH values attached to the right formulation?
- Is the page-120 product scope linked to the page-121 buffer box?

### C10 — refuse

I load a sample onto HiTrap Blue HP 5 mL at 5 mL/min. How many minutes are required, and does that guarantee complete albumin removal?

**Required source excerpts:** E120-H (p. 120), E120-P (p. 120), E120-W (p. 120), E121-PH (p. 121), E121-L (p. 121), E121-W (p. 121).

**Expected response:** The stated loading rate lies within the 0.5–5 mL/min range for the 5 mL column, but sample volume is unspecified, so a loading duration cannot be calculated. Washing has its own flow range and conditional endpoint, not a universal duration. These selected passages provide no guarantee of complete albumin removal; retain the target-hydrophobicity warning.

**Conditions to preserve:**

- Scope missing duration/guarantee to the selected protocol.
- Distinguish loading time, washing endpoint and actual removal performance.

**Do not infer:**

- Do not treat 5 mL column size as sample volume or calculate one minute.
- No guaranteed clearance or purity percentage.
- Do not transfer the unrelated 12 h cleaning hold from page 166.

**Human review checks:**

- Are both the missing sample volume and lack of guarantee stated?
- Is refusal limited to unsupported claims while giving the available range?

## Exact source catalogue

Quotes below preserve extracted text; source headings are separate records. Page-121 headings appear late in native reading order but are assigned by visual layout, with explicit page-120 product scope. Figures, chromatogram interpretation and table capacities are outside the expected-answer scope.

### E118-USE — page 118

Scope: Contaminants after initial antibody purification; laboratory-scale guidance. Role: `applicability`. Required parents: none.

```text
For many applications at laboratory scale, contaminant molecules are not always a significant problem. Affinity 
chromatography (AC) will provide sufficient purity and, as long as the presence of any minor contaminants does not 
interfere with the intended application, the purified sample can be used directly.
```

### E118-C — page 118

Scope: Contaminants after initial antibody purification; laboratory-scale guidance. Role: `contaminant_context`. Required parents: none.

```text
Common contaminants after initial purification are albumin, transferrin, antibody aggregates, leached protein A, DNA, 
and host or bovine immunoglobulins that originate from ascites or cell culture serum. The problem of contaminants of 
animal origin in, for example, bovine cell culture systems for monoclonal antibody (MAb) production, has been largely 
circumvented by use of serum-free systems. The three main contaminants albumin, transferrin, and host or bovine 
immunoglobulins pose three different purification problems: albumin because of its abundance; transferrin because of its 
similarity to the charge characteristics of many antibodies; and host or bovine immunoglobulins because of the similarity 
to that of the target immunoglobulin.
```

### E118-M — page 118

Scope: Contaminants after initial antibody purification; laboratory-scale guidance. Role: `method_selection`. Required parents: none.

```text
 Select chromatography techniques that utilize differences in the characteristics of the contaminant and target 
molecule: ion exchange chromatography (IEX) for separation by differences in charge; hydrophobic interaction 
chromatography (HIC) for separation by differences in hydrophobicity; and size exclusion chromatography (SEC) for 
separation by size. See Appendix 9 for an overview of the principles of the chromatography techniques used  
at laboratory scale.
```

### E118-I — page 118

Scope: Contaminants after initial antibody purification; laboratory-scale guidance. Role: `conditional_iex`. Required parents: none.

```text
 If the pI value of the antibody is sufficiently different from the contaminants, a cation exchange medium (negatively 
charged) can be used for removal of the contaminants at a pH above the pI of the impurities and below that of the 
antibody. This will ensure that the antibody (positively charged) binds to the column while the impurities, including 
negatively charged nucleic acids, pass through.
```

### E119-BH — page 119

Scope: Host or bovine immunoglobulin co-purification. Role: `section_heading`. Required parents: none.

```text
Bovine immunoglobulins
```

### E119-B — page 119

Scope: Host or bovine immunoglobulin co-purification. Role: `source_context`. Required parents: E119-BH.

```text
Co-purification of host or bovine immunoglobulins is a problem associated with any affinity purification of antibodies 
from a native source or a source to which supplements such as calf serum or bovine serum albumin are added. This 
contamination problem has been largely circumvented in the large-scale manufacture of MAbs for therapeutic use 
through the widespread use of serum-free cell culture systems.
```

### E119-BI — page 119

Scope: Host or bovine immunoglobulin co-purification. Role: `method_alternatives`. Required parents: E119-BH.

```text
Difficulties have also been encountered when murine monoclonal antibodies are the target molecule. The similarities 
between the physical characteristics of the target antibody and the contaminants require careful selection and 
optimization to find the most suitable chromatography technique for purification. Both HIC and IEX can be used.
```

### E119-S — page 119

Scope: Host or bovine immunoglobulin co-purification. Role: `screening_advice`. Required parents: E119-BH.

```text
 The hydrophobicity of proteins is difficult to predict. Screen several chromatography media with different 
hydrophobicities (e.g., using HiTrap HIC Selection Kit) to find the medium that gives optimal results.
```

### E119-X — page 119

Scope: Host or bovine immunoglobulin co-purification. Role: `scoped_example`. Required parents: E119-BH.

```text
HiTrap HIC Selection Kit includes seven HIC media with different hydrophobic properties for small-scale screening and 
selection of optimal binding and elution conditions. Figure 4.1 shows an example of chromatography media screening 
of a mouse monoclonal antibody on different HIC media prepacked in HiTrap 1 mL columns. In this case, the optimal 
medium for purification was HiTrap Phenyl HP.
```

### E119-AH — page 119

Scope: Albumin and transferrin after antibody purification. Role: `section_heading`. Required parents: none.

```text
Albumin and transferrin
```

### E119-A — page 119

Scope: Albumin and transferrin after antibody purification. Role: `method_alternatives`. Required parents: E119-AH.

```text
Ion exchange and hydrophobic interaction chromatography are two methods used for removing albumin and transferrin, 
separating the molecules on the basis of differences in their isoelectric points or hydrophobicities (see Appendix 9 for the 
principles of these techniques).
```

### E119-I — page 119

Scope: Albumin and transferrin after antibody purification. Role: `residual_contaminants`. Required parents: E119-AH.

```text
 After an IEX purification, albumin and transferrin can be present if their charge properties are similar to those of 
the target antibody. In some cases, it might be possible to optimize pH and elution conditions in the IEX step to 
improve the separation between the antibody and the contaminants (Appendix 9).
```

### E119-H — page 119

Scope: Albumin and transferrin after antibody purification. Role: `conditional_hic`. Required parents: E119-AH.

```text
 Since most monoclonal antibodies are more hydrophobic than albumin and transferrin, HIC can be used to bind the 
antibody and allow these contaminants to wash through the column.
```

### E119-BL — page 119

Scope: Albumin and transferrin after antibody purification. Role: `albumin_specific_alternative`. Required parents: E119-AH.

```text
However, AC using Blue Sepharose 6 Fast Flow is a useful alternative to IEX and HIC for removing albumin.
```

### E120-H — page 120

Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL. Role: `section_heading`. Required parents: none.

```text
Removal of albumin using Blue Sepharose chromatography media
```

### E120-A — page 120

Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL. Role: `product_scope_and_mechanism`. Required parents: E120-H.

```text
Blue Sepharose 6 Fast Flow or prepacked HiTrap Blue HP 1 mL and 5 mL columns (Fig 4.2) can be used to remove albumin 
either before or after other purification steps (see Table 4.1). The albumin binds in a nonspecific manner by electrostatic 
and/or hydrophobic interactions with the aromatic anionic ligand, Cibacron Blue F3G-A, coupled to Sepharose.
```

### E120-U — page 120

Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL. Role: `conditional_use`. Required parents: E120-H.

```text
 Use HiTrap Blue HP 1 mL or 5 mL columns to remove host albumin from mammalian expression systems or when 
the sample is known to contain high levels of albumin that might mask the UV absorption of other protein peaks.
```

### E120-W — page 120

Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL. Role: `warning`. Required parents: E120-H.

```text
 Do not use Blue Sepharose chromatography media if the immunoglobulin or other target molecule has a 
hydrophobicity similar to that of albumin.
```

### E120-P — page 120

Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL. Role: `cross_page_protocol_scope`. Required parents: E120-H, E120-W.

```text
The protocol for removal of albumin using HiTrap Blue HP 1 mL and 5 mL columns is described below.
```

### E121-BH — page 121

Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL. Role: `buffer_heading`. Required parents: E120-P.

```text
Buffer preparation
```

### E121-B — page 121

Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL. Role: `buffer_alternatives`. Required parents: E121-BH.

```text
Binding buffer: 20 mM sodium phosphate, pH 7.0, or 50 mM potassium hydrogen phosphate (KH 2PO4), pH 7.0
Elution buffer: 0.02 M sodium phosphate, 2 M sodium chloride, pH 7.0, or 0.05 M potassium hydrogen phosphate, 
1.5 M potassium chloride, pH 7.0
```

### E121-PH — page 121

Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL. Role: `protocol_heading`. Required parents: E120-P.

```text
Albumin removal
```

### E121-EQ — page 121

Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL. Role: `equilibration`. Required parents: E121-PH.

```text
4. Equilibrate the column with at least 5 column volumes of binding buffer. Recommended flow rates are 1 mL/min 
(1 mL column) and 5 mL/min (5  mL column).
```

### E121-L — page 121

Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL. Role: `sample_application`. Required parents: E121-PH, E121-F.

```text
 5. Apply the sample using a syringe fitted to the Luer connector or by pumping it onto the column. For optimal 
results, use a flow rate of 0.2 to 1 mL/min (1 mL column) and 0.5 to 5 mL/min (5 mL column) during sample 
application*.
```

### E121-W — page 121

Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL. Role: `wash_conditions`. Required parents: E121-PH.

```text
 6. Wash with binding buffer (generally at least 5 to 10 column volumes) until the absorbance reaches a steady 
baseline or no material remains in the effluent. Maintain a flow rate of 1 to 2 mL/min (1 mL column) and  
5 to 10 mL/min (5 mL column) for washing.
```

### E121-E — page 121

Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL. Role: `elution_alternatives`. Required parents: E121-PH.

```text
 7. Elute with elution buffer using a one-step or linear gradient. For step elution, 5 column volumes is usually 
sufficient. For linear gradient elution, 10 to 20  column volumes are usually sufficient. Maintain a flow rate of  
1 to 2 mL/min (1 mL column) and 5 to 10 mL/min (5 mL column) for elution.
```

### E121-F — page 121

Scope: Albumin removal using Blue Sepharose / HiTrap Blue HP 1 mL and 5 mL. Role: `sample_application_footnote`. Required parents: E121-PH.

```text
*       1 mL/min corresponds to approximately 30 drops/min when using a syringe with a 1 mL HiTrap column; 5 mL/min corresponds to approximately 
120 drops/min when using a 5 mL HiTrap column
```

## Frozen evaluation plan after human review

1. Review C01–C10 and their exact passages one by one. Record human decisions separately without promoting this frozen preparation in place.
2. Use the same source-only corpus and the declared transitive source dependencies for both top-five and top-six arms. Do not index questions, expected answers, required IDs or decision metadata.
3. Keep the existing BM25 parameters, existing FR/EN alias bridge, token counter and 2048-token serialized-context limit. Do not add vocabulary after reading failures. Report English/French differences.
4. Use the generic atomic assembler on this new source topology. The existing cleaning-specific launcher is hard-wired to pages 166–167 and cannot evaluate this package unchanged. A separate dataset adapter is needed; reusing those pressure/flow overview IDs here would be invalid.
5. Freeze the adapter and candidate corpus before measuring. Save code/config/input hashes, top-six and full diagnostic rankings, exact contexts, excluded bundles, required-source coverage, token overhead and timings in a fresh output directory. Preserve all earlier runs.
6. Score against the reviewed source sets only after retrieval/context construction. Separate retrieval coverage from generation correctness, refusal/clarification behaviour and scientific applicability. No answer generation is part of this preparation.

This probes transfer to a section outside the previous 17-excerpt cleaning corpus. The author already knows the method and has inspected this section; these are prospective new-section development probes, not an independently authored or blind held-out benchmark. The limited selected pages do not establish facts absent from the entire manual.

## Verification and local artifacts

Deterministic checks cover source identity, all excerpt hashes and exact offsets, unique inventories, source dependency closure, bilingual questions, response-status counts, reference existence, frozen-method consistency and preservation of earlier tracked files/runs. No retrieval metrics or answer scores have been computed.

Local ignored source texts, Poppler renders and the verification report are under `data/experiments/cytiva/contaminants-pilot-v01/`. The source PDF and generated page images remain outside Git. No LLM, API call, OCR, model download or database mutation is used.
