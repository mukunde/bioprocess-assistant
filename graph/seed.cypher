// === Seed - Protein A capture troubleshooting knowledge graph ===
// Canonical language: ENGLISH (the source handbooks are English). User questions
// can be French or English; cross-lingual matching is handled at retrieval time.
// 6 symptoms, 12 causes, 12 actions. Every node carries a mandatory `source` field
// and symptoms carry a `keywords` field (discriminative EN synonyms for full-text).
//
// Usage (Neo4j Browser / AuraDB or scripts/load_graph.py): run schema.cypher first
// (constraints + full-text index), then this file.

// --- Language migration cleanup ---
// Node names changed FR -> EN, so MERGE on the new English names would leave the
// old French nodes orphaned. Wipe all domain nodes first, then recreate; the seed
// is the authoritative source for graph content. (Also drop any unlabeled orphans.)
MATCH (n) WHERE n:Symptom OR n:Cause OR n:Action DETACH DELETE n;
MATCH (n) WHERE labels(n) = [] DETACH DELETE n;

// =================================================================
// === Symptom #1: Capture step yield drop                       ===
// =================================================================

MERGE (s:Symptom {name: "Capture step yield drop"})
SET s.description = "The Protein A capture step yield is below the expected historical baseline for the production pool: a significant fraction of product is lost in the flow-through or in the wash fractions.",
    s.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p1-2, Key performance characteristics (recovery >95% demonstrated in Table 2)",
    s.keywords = "yield recovery low drop decrease loss flow-through breakthrough DBC dynamic binding capacity";

MERGE (c1:Cause {name: "Degraded Protein A resin"})
SET c1.description = "Progressive loss of the resin's dynamic binding capacity (DBC) after repeated cycles and exposure to cleaning-in-place (CIP) conditions. The resin no longer binds enough antibody per mL, causing product to leak into the flow-through.",
    c1.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p1-2, Fig 2 and Table 2 (DBC after up to 200 CIP cycles with 0.1-0.5 M NaOH)";

MERGE (c2:Cause {name: "Loading flow rate too high"})
SET c2.description = "Linear loading velocity higher than the one giving the resin a sufficient residence time: antibodies pass through the column before saturating the Protein A binding sites, causing flow-through leakage regardless of resin condition.",
    c2.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Fig 3 (DBC vs residence time, e.g. 2.4 min gives ~30 mg/mL polyclonal hIgG); Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p58, Optimization of parameters";

MERGE (a1:Action {name: "Measure current DBC and replace the resin if degraded"})
SET a1.description = "Run a dynamic binding capacity test (typically DBC at 10% breakthrough) and compare to the resin lot's original spec. If significantly degraded, plan replacement. In parallel, review the CIP protocol (NaOH concentration, contact time) to extend the next lot's lifetime.",
    a1.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p1-2, Fig 2 and Table 2 (DBC after up to 200 CIP cycles with 0.1-0.5 M NaOH)";

MERGE (a2:Action {name: "Reduce the loading flow rate"})
SET a2.description = "Lower the linear loading velocity to increase residence time on the column and restore usable capacity. Verify that the residence time meets the resin supplier's recommended value.",
    a2.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Fig 3 (DBC vs residence time, e.g. 2.4 min gives ~30 mg/mL polyclonal hIgG); Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p58, Optimization of parameters";

MATCH (s:Symptom {name: "Capture step yield drop"}),
      (c1:Cause {name: "Degraded Protein A resin"}),
      (c2:Cause {name: "Loading flow rate too high"}),
      (a1:Action {name: "Measure current DBC and replace the resin if degraded"}),
      (a2:Action {name: "Reduce the loading flow rate"})
MERGE (s)-[:INDICATES]->(c1)
MERGE (s)-[:INDICATES]->(c2)
MERGE (c1)-[:RESOLVED_BY]->(a1)
MERGE (c2)-[:RESOLVED_BY]->(a2);

// =================================================================
// === Symptom #2: High column pressure                          ===
// =================================================================

MERGE (s2:Symptom {name: "High column pressure"})
SET s2.description = "The inlet column pressure rises significantly relative to the historical pressure/flow profile of the same capture block, either over several consecutive cycles or during a single load.",
    s2.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p166, Cleaning of Protein G and Protein A Sepharose media (Cleaning in place)",
    s2.keywords = "pressure overpressure backpressure back-pressure packing compaction fouling clogging";

MERGE (c3:Cause {name: "Resin fouling by denatured proteins or lipids"})
SET c3.description = "Substances that do not elute during standard regeneration stay bound to the resin and progressively clog the bed. Typical on processes with feedstock rich in lipids or partially denatured proteins.",
    c3.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p166, Cleaning in place";

MERGE (c4:Cause {name: "Degraded bed packing or flow rate exceeding spec"})
SET c4.description = "Bed that has compacted over cycles (poor flow distribution, flow asymmetry) or applied flow rate above 70% of the reference packing flow rate. Checkable via an efficiency test by acetone injection: asymmetry factor outside the 0.80-1.80 range.",
    c4.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p162-164, Column packing and efficiency (Appendix 5)";

MERGE (a3:Action {name: "Run a reinforced CIP suited to the resin"})
SET a3.description = "For MabSelect SuRe / SuRe LX: wash with 2 CV of 100-500 mM NaOH, 10-15 min contact, then >=5 CV of sterile-filtered binding buffer. For non-alkali-tolerant Protein A Sepharose: 6 M guanidine HCl or 70% ethanol at reduced flow rate. For severe lipid fouling: add a 0.1% non-ionic detergent step (e.g. Triton X-100).",
    a3.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p166-167, Cleaning sections; Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - Cleaning and sanitization (p4)";

MERGE (a4:Action {name: "Test column efficiency and re-pack if needed"})
SET a4.description = "Inject acetone (which does not interact with the resin) and measure the asymmetry factor A_s = b/a on the peak at 10% of its height. Target: 0.80 <= A_s <= 1.80. If outside the range, unpack and repack per the standard procedure. Verify that the loading flow rate does not exceed 70% of the reference packing flow rate.",
    a4.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p164, Column packing and efficiency; Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - Fig 11 and p5 bed heights 10-30 cm";

MATCH (s2:Symptom {name: "High column pressure"}),
      (c3:Cause {name: "Resin fouling by denatured proteins or lipids"}),
      (c4:Cause {name: "Degraded bed packing or flow rate exceeding spec"}),
      (a3:Action {name: "Run a reinforced CIP suited to the resin"}),
      (a4:Action {name: "Test column efficiency and re-pack if needed"})
MERGE (s2)-[:INDICATES]->(c3)
MERGE (s2)-[:INDICATES]->(c4)
MERGE (c3)-[:RESOLVED_BY]->(a3)
MERGE (c4)-[:RESOLVED_BY]->(a4);

// =================================================================
// === Symptom #3: Aggregates / HMW in the elution pool          ===
// =================================================================

MERGE (s3:Symptom {name: "Aggregates / HMW in the elution pool"})
SET s3.description = "The Protein A capture elution pool contains a significant fraction of aggregates (HMW, dimers, polymers) above product spec, detectable by analytical SEC. A structural risk of Protein A capture, due to the acidic pH required to release the mAb from the ligand.",
    s3.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p4, Method development (mAb eluted at pH 3-4); Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p122, Dimers and aggregates",
    s3.keywords = "aggregates aggregation HMW high molecular weight dimers polymers SEC";

MERGE (c5:Cause {name: "Elution pH too low or prolonged acidic contact time"})
SET c5.description = "Protein A elution is performed in acidic conditions (typically pH 3.0-3.5 on MabSelect SuRe). The lower the pH and the longer the mAb stays exposed to it, the larger the aggregate fraction. Sensitivity varies with the mAb sequence.",
    c5.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Generic elution conditions and Fig 10 (distribution of elution pH, MabSelect vs MabSelect SuRe)";

MERGE (c6:Cause {name: "No rapid neutralization of the elution pool"})
SET c6.description = "Once collected, the pool stays at acidic pH until neutralization. The longer the low-pH hold, especially at high concentration (typically >10 g/L on capture), the more aggregate formation progresses post-column.",
    c6.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p122, Dimers and aggregates (aggregates often formed at higher concentrations)";

MERGE (a5:Action {name: "Optimize elution pH to the highest tolerable and prefer a step elution"})
SET a5.description = "Test elution at pH 3.5 then increase in 0.1-unit steps to find the highest pH that still elutes quantitatively (>95% recovery). Prefer a step elution (defined volume at the target pH) over a continuous gradient, which prolongs exposure to acidic pH.",
    a5.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Generic elution conditions and Fig 10; p4, Method development";

MERGE (a6:Action {name: "Collect into a neutralizing buffer and plan an IEX/SEC polishing step"})
SET a6.description = "Collect the elution fractions directly into a neutralizing buffer pre-charged in the pool tank (e.g. 1 M Tris-HCl pH 8.0 or 1 M sodium acetate pH 5.5, about 10% v/v of the elution volume) to bring the pH to 5-6 within minutes. If the aggregate spec is still not met, add a downstream multimodal ion-exchange chromatography (e.g. Capto adhere) or SEC (Superdex 200) as a polishing step.",
    a6.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p122, Dimers and aggregates (SEC + IEX recommended downstream) + Chapter 7 polishing";

MATCH (s3:Symptom {name: "Aggregates / HMW in the elution pool"}),
      (c5:Cause {name: "Elution pH too low or prolonged acidic contact time"}),
      (c6:Cause {name: "No rapid neutralization of the elution pool"}),
      (a5:Action {name: "Optimize elution pH to the highest tolerable and prefer a step elution"}),
      (a6:Action {name: "Collect into a neutralizing buffer and plan an IEX/SEC polishing step"})
MERGE (s3)-[:INDICATES]->(c5)
MERGE (s3)-[:INDICATES]->(c6)
MERGE (c5)-[:RESOLVED_BY]->(a5)
MERGE (c6)-[:RESOLVED_BY]->(a6);

// =================================================================
// === Symptom #4: High Protein A leaching in the eluate         ===
// =================================================================

MERGE (s4:Symptom {name: "High Protein A leaching in the eluate"})
SET s4.description = "Protein A ligand leaching concentration in the elution pool above product spec. Measurable by non-competitive ELISA. Typical normal range on MabSelect SuRe: 5-20 ppm (ng ligand/mg IgG). Beyond that, a process or resin determinant is at play.",
    s4.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Protease stability and low ligand leakage + Fig 5 (low leakage over 100 cycles)",
    s4.keywords = "leaching leakage ligand bleed ppm";

MERGE (c7:Cause {name: "High proteolytic activity in the feedstock"})
SET c7.description = "Proteases present in the clarified feedstock progressively degrade the Protein A ligand during the load phase. Intensity depends on the cell line, the culture age, and the hold time between clarification and capture. The MabSelect SuRe Data File cites this mechanism as one of the main contributors to ligand leakage from Protein A resins.",
    c7.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Protease stability and low ligand leakage + Fig 4 (protease impact shown by electrophoresis, rProtein A vs SuRe)";

MERGE (c8:Cause {name: "CIP conditions too aggressive (concentrated NaOH or prolonged contact)"})
SET c8.description = "MabSelect SuRe tolerates 0.1-0.5 M NaOH for up to 200 cycles, but a high NaOH concentration combined with a long contact time accelerates ligand degradation and correlates with increased leaching. Fig 2 shows DBC loss by severity (0.1 M / 15 min vs 0.5 M / 60 min); leaching follows the same trend.",
    c8.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p1-2, High stability in alkaline conditions + Fig 2 (DBC vs CIP cycles at different NaOH and contact times)";

MERGE (a7:Action {name: "Reduce pre-column proteolytic activity"})
SET a7.description = "Minimize the hold time between clarification and capture (ideally <24h at 2-8C). Keep the clarified feedstock at low temperature throughout the hold. Evaluate adding protease inhibitors if the feedstock is particularly loaded (validate downstream compatibility). If possible, select a cell line with low proteolytic activity.",
    a7.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Protease stability and low ligand leakage + Fig 4";

MERGE (a8:Action {name: "Tighten the CIP and plan a downstream CEX polishing step"})
SET a8.description = "Use the lowest NaOH concentration compatible with tested cleaning efficacy: typically target 0.1 M rather than 0.5 M, 10-15 min contact rather than 60 min. Independently, plan a downstream cation-exchange chromatography step (e.g. HiTrap SP HP in step or gradient at pH 5.2) that removes residual Protein A leaching, as shown in Fig 4.5 of the Handbook.",
    a8.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p1-2, High stability in alkaline conditions + Fig 2; Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p124, Affinity ligands + Fig 4.5 (removal of leached Protein A by HiTrap SP HP CEX)";

MATCH (s4:Symptom {name: "High Protein A leaching in the eluate"}),
      (c7:Cause {name: "High proteolytic activity in the feedstock"}),
      (c8:Cause {name: "CIP conditions too aggressive (concentrated NaOH or prolonged contact)"}),
      (a7:Action {name: "Reduce pre-column proteolytic activity"}),
      (a8:Action {name: "Tighten the CIP and plan a downstream CEX polishing step"})
MERGE (s4)-[:INDICATES]->(c7)
MERGE (s4)-[:INDICATES]->(c8)
MERGE (c7)-[:RESOLVED_BY]->(a7)
MERGE (c8)-[:RESOLVED_BY]->(a8);

// =================================================================
// === Symptom #5: High residual HCP in the elution pool         ===
// =================================================================

MERGE (s5:Symptom {name: "High residual HCP in the elution pool"})
SET s5.description = "Host cell protein level (typically CHO HCP, measured by HCP ELISA) in the elution pool above product spec. A known immunogenicity risk in biopharma, to be eliminated before release. Protein A capture is only moderately selective against this contaminant.",
    s5.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p124, Host cell proteins (HCP)",
    s5.keywords = "HCP host cell proteins CHO contaminants";

MERGE (c9:Cause {name: "Insufficient or unsuitable post-load intermediate wash"})
SET c9.description = "HCPs can bind non-specifically to the Protein A resin or directly to the mAb during loading. If the wash between load and elution is too short, at too low conductivity, or without a disruptive agent, these HCPs co-elute with the mAb into the elution pool.",
    c9.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p58, Optimization of parameters; Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p3, Low risk of host cell protein contamination";

MERGE (c10:Cause {name: "Insufficient CIP between cycles with HCP carryover"})
SET c10.description = "When the CIP is undersized (dilute NaOH, too-short contact), HCPs accumulated on the resin are not desorbed and return to the next cycle's elution pool. The MabSelect SuRe Data File explicitly states that a rigorous CIP reduces this risk of HCP contamination and carryover into the product pools.",
    c10.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Low risk of host cell protein contamination or carryover + Fig 6 (Western blot confirming no HCP after 100 cycles with rigorous CIP)";

MERGE (a9:Action {name: "High-throughput screen the optimal wash conditions"})
SET a9.description = "Use PreDictor 96-well filter plates or HiTrap/HiScreen prepacked columns in HTS to screen different post-load wash conditions: conductivity variations (150-500 mM NaCl), additives disrupting non-specific interactions (250 mM arginine, 100 mM sodium caprylate). Select the conditions that reduce residual HCPs without degrading mAb recovery.",
    a9.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p4, Method development (PreDictor 96-well plates and HiTrap/HiScreen recommended for HTS optimization)";

MERGE (a10:Action {name: "Tighten the CIP and add a downstream multimodal AEX polishing step"})
SET a10.description = "On MabSelect SuRe: wash between cycles with 2 CV of 0.1-0.5 M NaOH, 10-15 min contact, then >=5 CV of sterile-filtered binding buffer. Independently, plan a downstream multimodal anion-exchange chromatography step (Capto adhere or Capto adhere ImpRes) that removes HCP + DNA + leached Protein A + aggregates in a single step, an explicit Cytiva recommendation for post-capture polishing.",
    a10.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Low risk of host cell protein contamination or carryover; Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p124, Host cell proteins (Capto adhere as recommended polishing) + p166-167, Cleaning sections (CIP parameters)";

MATCH (s5:Symptom {name: "High residual HCP in the elution pool"}),
      (c9:Cause {name: "Insufficient or unsuitable post-load intermediate wash"}),
      (c10:Cause {name: "Insufficient CIP between cycles with HCP carryover"}),
      (a9:Action {name: "High-throughput screen the optimal wash conditions"}),
      (a10:Action {name: "Tighten the CIP and add a downstream multimodal AEX polishing step"})
MERGE (s5)-[:INDICATES]->(c9)
MERGE (s5)-[:INDICATES]->(c10)
MERGE (c9)-[:RESOLVED_BY]->(a9)
MERGE (c10)-[:RESOLVED_BY]->(a10);

// =================================================================
// === Symptom #6: Bioburden / microbial contamination           ===
// =================================================================

MERGE (s6:Symptom {name: "Bioburden or microbial contamination in the column or elution pool"})
SET s6.description = "Detection of microbial growth (bacteria, yeast, mold) in the column between cycles or in the elution pool. Exceeds the process bioburden spec (typically <1 CFU/10 mL in biopharma). A process and quality risk, to be addressed before any restart.",
    s6.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p3, Low risk of host cell protein contamination or carryover (mentions microbial growth in the packed column); p4, Cleaning and sanitization",
    s6.keywords = "bioburden microbial contamination microbial growth bacteria yeast mold microbes";

MERGE (c11:Cause {name: "Insufficient routine sanitization for the feedstock"})
SET c11.description = "For feedstocks particularly rich in microbial load or in difficult contaminants (lipids, cell debris not removed by clarification), 0.1-0.5 M NaOH alone may not be enough. The MabSelect SuRe Data File explicitly acknowledges this and proposes alternative protocols.",
    c11.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p4, Cleaning and sanitization (explicit mention of challenging feedstocks with recommendation of a reducing agent or NaOH + IPA combination)";

MERGE (c12:Cause {name: "Unsuitable column storage between runs"})
SET c12.description = "Column stored outside recommended conditions (without a bacteriostat such as ethanol or benzyl alcohol, outside the 2-8C range, or for an undocumented duration), leading to microbial growth during the hold. Higher risk on long campaigns with intermediate stops.",
    c12.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p4, Storage (20% ethanol or 2% benzyl alcohol at 2-8C); Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p168, Storage of biological samples (Appendix 6)";

MERGE (a11:Action {name: "Reinforce the sanitization protocol (NaOH + IPA or add a reducing agent)"})
SET a11.description = "Switch to a combined 0.1 M NaOH + 40% isopropanol sanitization (efficacy demonstrated by Cytiva on MabSelect SuRe). For very challenging feedstocks, add a prior cycle with a reducing agent (thioglycerol or DTT) followed by 0.1-0.5 M NaOH. Document contact time, concentration, and cycle frequency in the CIP procedure.",
    a11.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p4, Cleaning and sanitization (textual recommendations 0.1 M NaOH + 40% IPA; DTT/thioglycerol option for challenging feedstocks)";

MERGE (a12:Action {name: "Standardize storage in 20% ethanol or 2% benzyl alcohol at 2-8C"})
SET a12.description = "Before any prolonged stop, flush the column with >=5 CV of the storage solution (20% ethanol or 2% benzyl alcohol). Keep at 2-8C, document the duration. At restart: flush with 3-5 CV of distilled water then re-equilibrate before loading. Do not store at room temperature or dry.",
    a12.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p4, Storage; Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p168, Storage of biological samples";

MATCH (s6:Symptom {name: "Bioburden or microbial contamination in the column or elution pool"}),
      (c11:Cause {name: "Insufficient routine sanitization for the feedstock"}),
      (c12:Cause {name: "Unsuitable column storage between runs"}),
      (a11:Action {name: "Reinforce the sanitization protocol (NaOH + IPA or add a reducing agent)"}),
      (a12:Action {name: "Standardize storage in 20% ethanol or 2% benzyl alcohol at 2-8C"})
MERGE (s6)-[:INDICATES]->(c11)
MERGE (s6)-[:INDICATES]->(c12)
MERGE (c11)-[:RESOLVED_BY]->(a11)
MERGE (c12)-[:RESOLVED_BY]->(a12);

// --- Check (run separately after the seed) ---
// MATCH (s:Symptom)-[:INDICATES]->(c:Cause)-[:RESOLVED_BY]->(a:Action)
// RETURN s.name AS symptom, c.name AS cause, a.name AS action;
