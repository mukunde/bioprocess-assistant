// === Seed minimal — Walking skeleton étape 1 ===
// Périmètre : capture Protein A.
// 1 symptôme, 2 causes, 2 actions. Chaque nœud porte un champ `source` obligatoire.
// MERGE rend ce script ré-exécutable sans créer de doublons (cf. schema.cypher).
//
// Usage (Neo4j Browser AuraDB) : ouvrir l'instance, coller tout le contenu de ce
// fichier dans la barre de requête, exécuter. Puis valider avec la requête de
// vérification en bas du fichier.

// --- Nettoyage défensif : supprime tout nœud sans label, séquelle possible
// d'un seed antérieur où un MERGE de relation sans rebind créait des orphelins. ---
MATCH (n) WHERE labels(n) = [] DETACH DELETE n;

// --- Symptôme ---
MERGE (s:Symptom {name: "Chute du rendement de capture"})
SET s.description = "Le rendement de l'étape de capture sur Protein A est inférieur à l'historique attendu sur le pool de production : une part significative du produit est perdue dans le flow-through ou dans les fractions de lavage.",
    s.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) — Protein A capture, troubleshooting";

// --- Causes ---
MERGE (c1:Cause {name: "Résine Protein A dégradée"})
SET c1.description = "Perte progressive de la capacité de liaison dynamique (DBC) de la résine après cycles répétés et exposition aux conditions de nettoyage (CIP). La résine ne fixe plus assez d'anticorps par mL, d'où la fuite dans le flow-through.",
    c1.source = "Cytiva, MabSelect SuRe Data File — section lifetime / DBC characterization";

MERGE (c2:Cause {name: "Débit de chargement trop élevé"})
SET c2.description = "Vitesse linéaire de chargement supérieure à celle pour laquelle la résine a un temps de résidence suffisant : les anticorps traversent la colonne avant d'avoir saturé les sites de liaison Protein A, d'où une fuite dans le flow-through indépendamment de l'état de la résine.",
    c2.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) — loading conditions";

// --- Actions ---
MERGE (a1:Action {name: "Mesurer la DBC actuelle et remplacer la résine si dégradée"})
SET a1.description = "Effectuer un test de capacité dynamique de liaison (typiquement DBC à 10% de percée) et comparer à la spec d'origine du lot de résine. En cas de dégradation significative, planifier le remplacement. En parallèle, revoir le protocole de CIP (concentration NaOH, durée de contact) pour prolonger la durée de vie du prochain lot.",
    a1.source = "Cytiva, MabSelect SuRe Data File — section lifetime / DBC characterization";

MERGE (a2:Action {name: "Réduire le débit de chargement"})
SET a2.description = "Diminuer la vitesse linéaire de chargement pour augmenter le temps de résidence sur la colonne et restaurer la capacité utile. Vérifier que le temps de résidence respecte la valeur recommandée par le fournisseur de la résine.",
    a2.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) — loading conditions";

// --- Relations causales ---
// MATCH rebind chaque nœud à sa variable (les variables d'un MERGE précédent
// ne survivent pas à un `;`). Ensuite les MERGE créent les arêtes entre nœuds
// nommés, pas entre nœuds anonymes.
MATCH (s:Symptom {name: "Chute du rendement de capture"}),
      (c1:Cause {name: "Résine Protein A dégradée"}),
      (c2:Cause {name: "Débit de chargement trop élevé"}),
      (a1:Action {name: "Mesurer la DBC actuelle et remplacer la résine si dégradée"}),
      (a2:Action {name: "Réduire le débit de chargement"})
MERGE (s)-[:INDIQUE]->(c1)
MERGE (s)-[:INDIQUE]->(c2)
MERGE (c1)-[:RESOLU_PAR]->(a1)
MERGE (c2)-[:RESOLU_PAR]->(a2);

// --- Vérification (à exécuter séparément après le seed) ---
// MATCH (s:Symptom)-[:INDIQUE]->(c:Cause)-[:RESOLU_PAR]->(a:Action)
// RETURN s.name AS symptome, c.name AS cause, a.name AS action;
