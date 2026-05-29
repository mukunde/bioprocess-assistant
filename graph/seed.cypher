// === Minimal seed — Walking skeleton step 1 ===
// Scope: Protein A capture.
// 1 symptom, 2 causes, 2 actions. Every node carries a mandatory `source` field.
// MERGE keeps this script re-runnable without creating duplicates (see schema.cypher).
//
// Usage (Neo4j Browser / AuraDB): open the instance, paste this file into the
// query bar, run it. Then validate with the check query at the bottom.

// --- Defensive cleanup: orphan unlabeled nodes (left over from earlier seeds
// where a MERGE on relations was missing a rebind) + legacy French-named
// relations from before the English rename (one-time migration; the lines can
// be removed once the graph has been re-seeded). ---
MATCH (n) WHERE labels(n) = [] DETACH DELETE n;
MATCH ()-[r:INDIQUE]->() DELETE r;
MATCH ()-[r:RESOLU_PAR]->() DELETE r;

// --- Symptom ---
MERGE (s:Symptom {name: "Chute du rendement de capture"})
SET s.description = "Le rendement de l'étape de capture sur Protein A est inférieur à l'historique attendu sur le pool de production : une part significative du produit est perdue dans le flow-through ou dans les fractions de lavage.",
    s.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) — Protein A capture, troubleshooting";

// --- Causes ---
MERGE (c1:Cause {name: "Résine Protein A dégradée"})
SET c1.description = "Perte progressive de la capacité de liaison dynamique (DBC) de la résine après cycles répétés et exposition aux conditions de nettoyage (CIP). La résine ne fixe plus assez d'anticorps par mL, d'où la fuite dans le flow-through.",
    c1.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) — section lifetime / DBC characterization";

MERGE (c2:Cause {name: "Débit de chargement trop élevé"})
SET c2.description = "Vitesse linéaire de chargement supérieure à celle pour laquelle la résine a un temps de résidence suffisant : les anticorps traversent la colonne avant d'avoir saturé les sites de liaison Protein A, d'où une fuite dans le flow-through indépendamment de l'état de la résine.",
    c2.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) — loading conditions";

// --- Actions ---
MERGE (a1:Action {name: "Mesurer la DBC actuelle et remplacer la résine si dégradée"})
SET a1.description = "Effectuer un test de capacité dynamique de liaison (typiquement DBC à 10% de percée) et comparer à la spec d'origine du lot de résine. En cas de dégradation significative, planifier le remplacement. En parallèle, revoir le protocole de CIP (concentration NaOH, durée de contact) pour prolonger la durée de vie du prochain lot.",
    a1.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) — section lifetime / DBC characterization";

MERGE (a2:Action {name: "Réduire le débit de chargement"})
SET a2.description = "Diminuer la vitesse linéaire de chargement pour augmenter le temps de résidence sur la colonne et restaurer la capacité utile. Vérifier que le temps de résidence respecte la valeur recommandée par le fournisseur de la résine.",
    a2.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) — loading conditions";

// --- Causal relations ---
// MATCH rebinds each node to its variable (variables from a previous MERGE
// don't survive a `;`). Then MERGE creates edges between named nodes, not
// between anonymous ones.
MATCH (s:Symptom {name: "Chute du rendement de capture"}),
      (c1:Cause {name: "Résine Protein A dégradée"}),
      (c2:Cause {name: "Débit de chargement trop élevé"}),
      (a1:Action {name: "Mesurer la DBC actuelle et remplacer la résine si dégradée"}),
      (a2:Action {name: "Réduire le débit de chargement"})
MERGE (s)-[:INDICATES]->(c1)
MERGE (s)-[:INDICATES]->(c2)
MERGE (c1)-[:RESOLVED_BY]->(a1)
MERGE (c2)-[:RESOLVED_BY]->(a2);

// =================================================================
// === Symptom #2: Pression élevée sur la colonne                ===
// =================================================================

MERGE (s2:Symptom {name: "Pression élevée sur la colonne"})
SET s2.description = "La pression mesurée en entrée de colonne augmente significativement par rapport au profil pression/débit historique du même bloc capture, soit sur plusieurs cycles consécutifs, soit pendant un même chargement.",
    s2.source = "Cytiva, Antibody Purification Handbook, CY13981-25Jan21-HB (2021) — p166, Cleaning of Protein G and Protein A Sepharose media (Cleaning in place)";

MERGE (c3:Cause {name: "Encrassement de la résine par protéines dénaturées ou lipides"})
SET c3.description = "Substances qui ne s'éluent pas pendant la régénération standard restent fixées sur la résine et obstruent progressivement le lit. Signe typique sur procédés avec feedstock riche en lipides ou en protéines partiellement dénaturées.",
    c3.source = "Cytiva, Antibody Purification Handbook, CY13981-25Jan21-HB (2021) — p166, Cleaning in place";

MERGE (c4:Cause {name: "Packing du lit dégradé ou débit excédant la spec"})
SET c4.description = "Lit qui s'est compacté avec les cycles (mauvaise flow distribution, asymétrie de l'écoulement) ou débit appliqué supérieur à 70% du packing flow rate de référence. Vérifiable via un test d'efficacité par injection d'acétone : facteur d'asymétrie hors plage 0.80-1.80.",
    c4.source = "Cytiva, Antibody Purification Handbook, CY13981-25Jan21-HB (2021) — p162-164, Column packing and efficiency (Appendix 5)";

MERGE (a3:Action {name: "Effectuer un CIP renforcé adapté à la résine"})
SET a3.description = "Pour MabSelect SuRe / SuRe LX : laver avec 2 CV de NaOH 100-500 mM, contact 10-15 min, puis ≥5 CV de buffer de binding stérile filtré. Pour Protein A Sepharose non-alkali-tolerant : 6 M guanidine HCl ou 70% éthanol à débit réduit. Si encrassement lipidique sévère : ajouter une étape détergent non-ionique 0.1% (ex. Triton X-100).",
    a3.source = "Cytiva, Antibody Purification Handbook, CY13981-25Jan21-HB (2021) — p166-167, Cleaning sections; Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) — Cleaning and sanitization (p4)";

MERGE (a4:Action {name: "Tester l'efficacité colonne et re-packer si nécessaire"})
SET a4.description = "Injecter de l'acétone (qui n'interagit pas avec la résine) et mesurer le facteur d'asymétrie A_s = b/a sur le pic à 10% de la hauteur. Cible : 0.80 ≤ A_s ≤ 1.80. Si hors plage, dépacker et repacker selon la procédure standard. Vérifier que le débit de chargement ne dépasse pas 70% du packing flow rate de référence.",
    a4.source = "Cytiva, Antibody Purification Handbook, CY13981-25Jan21-HB (2021) — p164, Column packing and efficiency; Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) — Fig 11 et p5 bed heights 10-30 cm";

MATCH (s2:Symptom {name: "Pression élevée sur la colonne"}),
      (c3:Cause {name: "Encrassement de la résine par protéines dénaturées ou lipides"}),
      (c4:Cause {name: "Packing du lit dégradé ou débit excédant la spec"}),
      (a3:Action {name: "Effectuer un CIP renforcé adapté à la résine"}),
      (a4:Action {name: "Tester l'efficacité colonne et re-packer si nécessaire"})
MERGE (s2)-[:INDICATES]->(c3)
MERGE (s2)-[:INDICATES]->(c4)
MERGE (c3)-[:RESOLVED_BY]->(a3)
MERGE (c4)-[:RESOLVED_BY]->(a4);

// --- Check (run separately after the seed) ---
// MATCH (s:Symptom)-[:INDICATES]->(c:Cause)-[:RESOLVED_BY]->(a:Action)
// RETURN s.name AS symptom, c.name AS cause, a.name AS action;
