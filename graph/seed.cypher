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

// --- Check (run separately after the seed) ---
// MATCH (s:Symptom)-[:INDICATES]->(c:Cause)-[:RESOLVED_BY]->(a:Action)
// RETURN s.name AS symptom, c.name AS cause, a.name AS action;
