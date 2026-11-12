# Cytiva passage scope and alias review

**Status** Draft for human review before implementation.

This map covers all 42 passages in the frozen comparison corpus.
Assignments describe where the source applies. Each passage keeps its
canonical ID and direct source dependencies. The candidate will expand
those dependencies transitively using the existing assembler.
[Approved comparison protocol](cytiva-neo4j-product-procedure-protocol-v01.md)

## Product scopes and aliases

| Canonical scope | Accepted English forms | Binding limit |
| --- | --- | --- |
| Protein A Sepharose | Protein A Sepharose | Shares the documented A/G cleaning routes. Generic Protein A is insufficient. |
| Protein G Sepharose | Protein G Sepharose | Shares the documented A/G cleaning routes. Generic Protein G is insufficient. |
| Sepharose A/G | Protein A/G Sepharose, Protein A or Protein G Sepharose, Protein G and Protein A Sepharose | Shared cleaning scope on page 166. Bare Sepharose leaves the product unresolved. |
| MabSelect family | MabSelect, MabSelect media | Selects the common routes. An unspecified variant leaves eligibility for the stronger route unresolved. |
| MabSelect SuRe | MabSelect SuRe, SuRe within an explicit MabSelect context | May use the common routes and the documented stronger alkali route. |
| MabSelect SuRe LX | MabSelect SuRe LX, SuRe LX within an explicit MabSelect context | Same documented applicability as SuRe. Keep the named variant distinct. |
| Blue Sepharose 6 Fast Flow | Blue Sepharose 6 Fast Flow, Blue Sepharose 6 FF | Albumin guidance and shared warning. HiTrap operating parameters remain scoped to HiTrap Blue HP. |
| Blue Sepharose family | Blue Sepharose | Shared albumin guidance and warning. A specific column procedure requires the named product. |
| HiTrap Blue HP | HiTrap Blue HP | Operational passages cover 1 mL and 5 mL. Keep column size as a qualifier, with units and stage intact. |
| HiTrap HIC Selection Kit | HiTrap HIC Selection Kit | Screening guidance. |
| HiTrap Phenyl HP | HiTrap Phenyl HP, Phenyl HP in an explicit HiTrap HIC example | The source records an example outcome. |
| Antibody purification | affinity purification, affinity capture, antibody purification | General documentary scope for contaminant and method guidance. |

“Sepharose A/G” in the map denotes the documented shared scope. Each
named A or G medium can match it. Common MabSelect material can match
both named SuRe variants. Restricted passages retain their source
restriction. The Blue Sepharose family warning applies to both named
formats within its stated scope.

## Procedure aliases

| Canonical procedure | Accepted English signals | Binding limit |
| --- | --- | --- |
| Backpressure and cleaning | backpressure increase, increase in backpressure, increased backpressure | Pressure alone has no directional or confirmed-measurement meaning. |
| Precipitated or denatured material | precipitated protein, denatured protein, precipitated substance, denatured material, denatured-material wash, guanidine wash | Use the named product to select the applicable route. A reagent alone may leave the procedure unresolved. |
| Hydrophobic deposits | strongly bound lipids, lipoproteins, hydrophobic proteins, hydrophobic deposits | A shared context. A detergent or solvent mention selects the corresponding route. |
| Detergent cleaning | detergent cleaning, detergent wash, nonionic detergent, Triton X-100 | Within a product cleaning clause. The Triton example is specific to the A/G passage. |
| Solvent cleaning | solvent cleaning, solvent wash, solvent choice, solvent choices, ethanol, 2-propanol, isopropanol | In a cleaning clause. Ethanol occurs in two product routes. The alias for 2-propanol does not create a Sepharose route. |
| Stronger alkali cleaning | stronger alkali, stronger sodium hydroxide, concentrated sodium hydroxide option, SuRe alkali procedure | Identifies the restricted documentary route. “Sodium hydroxide” alone also occurs in the common route. |
| Direct use | use directly, direct use, intended application | Laboratory-scale context and interference condition apply. |
| Contaminant identification | contaminant, impurity, co-purified material | A mention alone leaves contaminant identity unresolved. |
| Method selection | method selection, ion exchange, IEX, hydrophobic interaction chromatography, HIC, size exclusion chromatography, SEC | Select by documented property difference. An explicit screening or contaminant clause supplies its narrower scope. |
| Bovine immunoglobulins | bovine immunoglobulins, host immunoglobulins, bovine IgG | Use the host or bovine section without assuming contaminant identity. |
| HIC screening | HIC screening, screen HIC media, HIC selection kit | A screening activity, with a distinct Phenyl HP example. |
| Albumin and transferrin | albumin and transferrin, transferrin | General removal guidance. A named Blue Sepharose route is scoped to albumin. |
| Albumin removal | albumin removal, remove albumin, albumin binding, UV masking | A named Blue medium selects the relevant albumin guidance and warning. |
| Buffer formulation | buffer formulation, buffer preparation, binding buffer composition, elution buffer formulation, pH option | Keep formulation separate from use during an operational stage. A bare binding-buffer mention may describe the wash instead. |
| Sample loading | sample loading, sample application, load the sample, syringe loading, loading with a named Blue HP context | Approximate drop rates belong to the documented loading conditions. |
| Column washing | column washing, wash the column, wash endpoint, steady baseline, washing with a named Blue HP context | A washing clause. Product context separates Blue HP washing from cleaning rinses. |
| Operational elution | step elution, one-step elution, linear-gradient elution, elution step | Operational volumes and flows. Buffer formulation stays separate. |

“Hydrophobic deposits”, the product cleaning headings, and the albumin
removal protocol heading supply context. Use the more specific procedure
when it is explicit. A question asking about both routes may request
both. The general identity or product term alone leaves the procedure
unresolved when several routes apply.

## Binding and normalization rules

- Normalize case, repeated whitespace, and equivalent Unicode hyphens.
  Match whole words or phrases and prefer the longest product name.
  Listed inflections may be normalized only by a reviewed exact rule.
  Keep quantities, negation, and units in the original question.
- Bind a procedure to the product named in its clause. Reuse a product
  across coordinated stages only when the question clearly shares it.
  Reuse a procedure across named products only when an explicit
  comparison shares the same procedure, as in AD01.
  Keep an explicit contrast or prohibited transfer as two documentary
  scopes without treating the transfer as authorized.
- A request about a restricted procedure may retrieve its restriction
  for explanation even when the exact product variant is unknown.
  Mark applicability unresolved. For XC06, the common wash and stronger
  alkali option are two named documentary scopes. The latter retains
  the SuRe/SuRe LX restriction.
- SP08 explicitly compares loading and washing on the same 1 mL
  column. Keep both documentary scopes and leave the observed stage
  unresolved. If the question fails to identify a supported documentary
  scope, use fixed 32 and record the unresolved binding.
- Reserve scope coverage for a retained substantive procedure or guidance
  passage with its required dependencies. A heading, warning, restriction,
  footnote, or example alone does not establish procedure coverage.
  Retrieve warnings and footnotes through their existing dependency links
  and honor their documented product, stage, and format.

## Review examples

| Case | Intended binding | Boundary to validate |
| --- | --- | --- |
| AD01 | MabSelect solvent and Protein A Sepharose solvent | Keep the two warnings and solvent options with the respective product. |
| XC06 | Common MabSelect wash and restricted SuRe/SuRe LX alkali | The question can compare the two procedures without establishing eligibility to apply the stronger one. |
| SP03 | MabSelect solvent and restricted stronger alkali | Retain the contact time only within the stronger alkali route. |
| SP07 | HiTrap Blue HP buffer formulation and column washing | A buffer pH option belongs to formulation. The wash endpoint belongs to washing. |
| SP08 | HiTrap Blue HP 1 mL loading and washing | Both ranges can be retrieved. The flow alone leaves the actual stage unknown. |

## Passage map

The table lists direct dependencies. A dash means the frozen corpus
specifies no direct dependency.

| Passage | Printed page | Product or source scope | Procedure | Role | Direct dependencies | Source boundary |
| --- | ---: | --- | --- | --- | --- | --- |
| `E166-H` | 166 | Sepharose A/G | Cleaning scope | Heading | — | Scope for both Protein A and Protein G Sepharose. |
| `E166-T` | 166 | Sepharose A/G | Backpressure and cleaning | Guidance | `E166-H` | Cleaning after observed increase. Possible residues do not establish the cause. |
| `E166-PH` | 166 | Sepharose A/G | Precipitated or denatured proteins | Heading | `E166-H` | Scope for the guanidine route. |
| `E166-P` | 166 | Sepharose A/G | Precipitated or denatured proteins | Procedure | `E166-PH` | Guanidine wash and immediate binding-buffer rinse. |
| `E166-LH` | 166 | Sepharose A/G | Hydrophobic deposits | Heading | `E166-H` | Shared by detergent and solvent routes. |
| `E166-D` | 166 | Sepharose A/G | Detergent cleaning | Procedure | `E166-LH` | Triton example and immediate rinse. |
| `E166-E` | 166 | Sepharose A/G | Solvent cleaning | Procedure | `E166-LH`, `E166-W` | Ethanol alternative with hold. |
| `E166-W` | 166 | Sepharose A/G | Solvent cleaning | Warning | `E166-LH` | Lower flow with 70% ethanol. |
| `E167-H` | 167 | MabSelect family | Cleaning scope | Heading | — | Common cleaning scope. |
| `E167-PH` | 167 | MabSelect family | Precipitated or denatured substances | Heading | `E167-H` | Common route and parent for the restricted alkali block. |
| `E167-P` | 167 | MabSelect family | Precipitated or denatured substances | Procedure | `E167-PH` | Common wash alternatives and rinse. |
| `E167-SH` | 167 | MabSelect SuRe and SuRe LX | Stronger alkali cleaning | Restriction | `E167-PH` | Restricts the stronger route to the two named variants. |
| `E167-S` | 167 | MabSelect SuRe and SuRe LX | Stronger alkali cleaning | Procedure | `E167-SH` | Three-step stronger sodium hydroxide route. |
| `E167-LH` | 167 | MabSelect family | Hydrophobic deposits | Heading | `E167-H` | Shared by detergent and solvent routes. |
| `E167-D` | 167 | MabSelect family | Detergent cleaning | Procedure | `E167-LH` | Nonionic detergent and immediate rinse. |
| `E167-E` | 167 | MabSelect family | Solvent cleaning | Procedure | `E167-LH`, `E167-W` | Ethanol or 2-propanol alternatives, rinse and gradient. |
| `E167-W` | 167 | MabSelect family | Solvent cleaning | Warning | `E167-LH` | Lower flow for the documented solvent alternatives. |
| `E118-USE` | 118 | Antibody purification | Direct use | Guidance | — | Laboratory scale and lack of interference with intended use. |
| `E118-C` | 118 | Antibody purification | Contaminant identification | Guidance | — | Contaminants and the challenges they pose. |
| `E118-M` | 118 | Antibody purification | Method selection | Guidance | — | IEX, HIC, and SEC principles by property difference. |
| `E119-BH` | 119 | Antibody purification | Bovine immunoglobulins | Heading | — | Host or bovine immunoglobulin section. |
| `E119-B` | 119 | Antibody purification | Bovine immunoglobulins | Guidance | `E119-BH` | Co-purification and scope of serum-free systems. |
| `E119-BI` | 119 | Antibody purification | Bovine immunoglobulins | Guidance | `E119-BH` | Murine target and HIC or IEX selection. |
| `E119-S` | 119 | Antibody purification | HIC screening | Guidance | `E119-BH` | Screen different hydrophobicities. |
| `E119-X` | 119 | HiTrap HIC Selection Kit and Phenyl HP | HIC screening | Example | `E119-BH` | Seven-media kit and illustrated Phenyl HP result. |
| `E119-AH` | 119 | Antibody purification | Albumin and transferrin | Heading | — | Shared contaminant section. |
| `E119-A` | 119 | Antibody purification | Albumin and transferrin | Guidance | `E119-AH` | IEX and HIC for the two contaminants. |
| `E119-I` | 119 | Antibody purification | Albumin and transferrin | Guidance | `E119-AH` | IEX caveat. No numeric pH. |
| `E119-H` | 119 | Antibody purification | Albumin and transferrin | Guidance | `E119-AH` | HIC retention of most monoclonal antibodies. |
| `E119-BL` | 119 | Blue Sepharose 6 Fast Flow | Albumin removal | Guidance | `E119-AH` | Alternative limited to albumin in this passage. |
| `E120-H` | 120 | Blue Sepharose family | Albumin removal | Heading | — | Common albumin removal section. |
| `E120-A` | 120 | Blue Sepharose family | Albumin removal | Guidance | `E120-H` | Named media, timing, and albumin binding mechanism. |
| `E120-U` | 120 | HiTrap Blue HP | Albumin removal | Guidance | `E120-H` | Host albumin and UV masking use cases. |
| `E120-W` | 120 | Blue Sepharose family | Albumin removal | Warning | `E120-H` | Avoid use with similarly hydrophobic targets. |
| `E120-P` | 120 | HiTrap Blue HP | Albumin removal protocol | Heading | `E120-H`, `E120-W` | Scope for 1 mL and 5 mL columns and warning link. |
| `E121-BH` | 121 | HiTrap Blue HP | Buffer formulation | Heading | `E120-P` | Buffer preparation. |
| `E121-B` | 121 | HiTrap Blue HP | Buffer formulation | Procedure | `E121-BH` | Binding and elution formulations by role. |
| `E121-PH` | 121 | HiTrap Blue HP | Albumin removal protocol | Heading | `E120-P` | Scope for operational stages. |
| `E121-L` | 121 | HiTrap Blue HP | Sample loading | Procedure | `E121-PH`, `E121-F` | Application modes and flow by column size. |
| `E121-W` | 121 | HiTrap Blue HP | Column washing | Procedure | `E121-PH` | Wash endpoint, volumes, and flow by size. |
| `E121-E` | 121 | HiTrap Blue HP | Operational elution | Procedure | `E121-PH` | Step or gradient volumes and flow by size. |
| `E121-F` | 121 | HiTrap Blue HP | Sample loading | Footnote | `E121-PH` | Approximate syringe drop rates at documented flows. |
