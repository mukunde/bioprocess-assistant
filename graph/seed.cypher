// === Minimal seed - Walking skeleton step 1 ===
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
    s.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p1-2, Key performance characteristics (recovery >95% démontré en Table 2)",
    s.keywords = "rendement faible chute baisse perte flow-through percée DBC capacité de liaison dynamique recovery yield";

// --- Causes ---
MERGE (c1:Cause {name: "Résine Protein A dégradée"})
SET c1.description = "Perte progressive de la capacité de liaison dynamique (DBC) de la résine après cycles répétés et exposition aux conditions de nettoyage (CIP). La résine ne fixe plus assez d'anticorps par mL, d'où la fuite dans le flow-through.",
    c1.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p1-2, Fig 2 et Table 2 (DBC après jusqu'à 200 cycles CIP avec NaOH 0.1-0.5 M)";

MERGE (c2:Cause {name: "Débit de chargement trop élevé"})
SET c2.description = "Vitesse linéaire de chargement supérieure à celle pour laquelle la résine a un temps de résidence suffisant : les anticorps traversent la colonne avant d'avoir saturé les sites de liaison Protein A, d'où une fuite dans le flow-through indépendamment de l'état de la résine.",
    c2.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Fig 3 (DBC vs residence time, ex. 2.4 min → ~30 mg/mL polyclonal hIgG); Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p58, Optimization of parameters";

// --- Actions ---
MERGE (a1:Action {name: "Mesurer la DBC actuelle et remplacer la résine si dégradée"})
SET a1.description = "Effectuer un test de capacité dynamique de liaison (typiquement DBC à 10% de percée) et comparer à la spec d'origine du lot de résine. En cas de dégradation significative, planifier le remplacement. En parallèle, revoir le protocole de CIP (concentration NaOH, durée de contact) pour prolonger la durée de vie du prochain lot.",
    a1.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p1-2, Fig 2 et Table 2 (DBC après jusqu'à 200 cycles CIP avec NaOH 0.1-0.5 M)";

MERGE (a2:Action {name: "Réduire le débit de chargement"})
SET a2.description = "Diminuer la vitesse linéaire de chargement pour augmenter le temps de résidence sur la colonne et restaurer la capacité utile. Vérifier que le temps de résidence respecte la valeur recommandée par le fournisseur de la résine.",
    a2.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Fig 3 (DBC vs residence time, ex. 2.4 min → ~30 mg/mL polyclonal hIgG); Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p58, Optimization of parameters";

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
    s2.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p166, Cleaning of Protein G and Protein A Sepharose media (Cleaning in place)",
    s2.keywords = "pression surpression contre-pression backpressure packing compaction encrassement fouling";

MERGE (c3:Cause {name: "Encrassement de la résine par protéines dénaturées ou lipides"})
SET c3.description = "Substances qui ne s'éluent pas pendant la régénération standard restent fixées sur la résine et obstruent progressivement le lit. Signe typique sur procédés avec feedstock riche en lipides ou en protéines partiellement dénaturées.",
    c3.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p166, Cleaning in place";

MERGE (c4:Cause {name: "Packing du lit dégradé ou débit excédant la spec"})
SET c4.description = "Lit qui s'est compacté avec les cycles (mauvaise flow distribution, asymétrie de l'écoulement) ou débit appliqué supérieur à 70% du packing flow rate de référence. Vérifiable via un test d'efficacité par injection d'acétone : facteur d'asymétrie hors plage 0.80-1.80.",
    c4.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p162-164, Column packing and efficiency (Appendix 5)";

MERGE (a3:Action {name: "Effectuer un CIP renforcé adapté à la résine"})
SET a3.description = "Pour MabSelect SuRe / SuRe LX : laver avec 2 CV de NaOH 100-500 mM, contact 10-15 min, puis ≥5 CV de buffer de binding stérile filtré. Pour Protein A Sepharose non-alkali-tolerant : 6 M guanidine HCl ou 70% éthanol à débit réduit. Si encrassement lipidique sévère : ajouter une étape détergent non-ionique 0.1% (ex. Triton X-100).",
    a3.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p166-167, Cleaning sections; Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - Cleaning and sanitization (p4)";

MERGE (a4:Action {name: "Tester l'efficacité colonne et re-packer si nécessaire"})
SET a4.description = "Injecter de l'acétone (qui n'interagit pas avec la résine) et mesurer le facteur d'asymétrie A_s = b/a sur le pic à 10% de la hauteur. Cible : 0.80 ≤ A_s ≤ 1.80. Si hors plage, dépacker et repacker selon la procédure standard. Vérifier que le débit de chargement ne dépasse pas 70% du packing flow rate de référence.",
    a4.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p164, Column packing and efficiency; Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - Fig 11 et p5 bed heights 10-30 cm";

MATCH (s2:Symptom {name: "Pression élevée sur la colonne"}),
      (c3:Cause {name: "Encrassement de la résine par protéines dénaturées ou lipides"}),
      (c4:Cause {name: "Packing du lit dégradé ou débit excédant la spec"}),
      (a3:Action {name: "Effectuer un CIP renforcé adapté à la résine"}),
      (a4:Action {name: "Tester l'efficacité colonne et re-packer si nécessaire"})
MERGE (s2)-[:INDICATES]->(c3)
MERGE (s2)-[:INDICATES]->(c4)
MERGE (c3)-[:RESOLVED_BY]->(a3)
MERGE (c4)-[:RESOLVED_BY]->(a4);

// =================================================================
// === Symptom #3: Présence d'agrégats / HMW dans le pool d'élution ===
// =================================================================

MERGE (s3:Symptom {name: "Présence d'agrégats / HMW dans le pool d'élution"})
SET s3.description = "Le pool d'élution de l'étape de capture Protein A contient une fraction significative d'agrégats (HMW, dimers, polymères) au-dessus de la spec produit, détectable par SEC analytique. Risque structurel de la capture Protein A à cause du pH acide nécessaire pour décrocher le mAb du ligand.",
    s3.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p4, Method development (mAb élué pH 3-4); Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p122, Dimers and aggregates",
    s3.keywords = "agrégats agglomérats HMW high molecular weight haut poids moléculaire dimères polymères SEC aggregates";

MERGE (c5:Cause {name: "Élution à pH trop bas ou temps de contact acide prolongé"})
SET c5.description = "L'élution Protein A se fait en milieu acide (typiquement pH 3.0-3.5 sur MabSelect SuRe). Plus le pH est bas et plus le mAb reste exposé à ce pH, plus la fraction d'agrégats augmente. La sensibilité varie avec la séquence du mAb.",
    c5.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Generic elution conditions et Fig 10 (distribution des pH d'élution MabSelect vs MabSelect SuRe)";

MERGE (c6:Cause {name: "Absence de neutralisation rapide du pool d'élution"})
SET c6.description = "Une fois collecté, le pool reste à pH acide jusqu'à neutralisation. Plus le hold à pH bas est long, a fortiori à concentration élevée (typiquement >10 g/L sur capture), plus la formation d'agrégats progresse en post-colonne.",
    c6.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p122, Dimers and aggregates (aggregates often formed at higher concentrations)";

MERGE (a5:Action {name: "Optimiser le pH d'élution au plus haut tolérable et privilégier une step elution"})
SET a5.description = "Tester l'élution à pH 3.5 puis monter par paliers de 0.1 unité pour identifier le pH le plus haut qui élue toujours quantitativement (>95% recovery). Privilégier une élution en step (volume défini au pH cible) plutôt qu'un gradient continu, qui prolonge le temps d'exposition au pH acide.",
    a5.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Generic elution conditions et Fig 10; p4, Method development";

MERGE (a6:Action {name: "Collecter dans un buffer neutralisant et prévoir un polissage IEX/SEC"})
SET a6.description = "Collecter les fractions d'élution directement dans un buffer neutralisant pré-déposé dans le pool tank (ex. 1 M Tris-HCl pH 8.0 ou 1 M acétate de sodium pH 5.5, environ 10% v/v du volume d'élution) pour ramener le pH à 5-6 en quelques minutes. Si la spec agrégats reste non tenue, ajouter en aval une chromatographie échangeuse d'ions multimodale (ex. Capto adhere) ou une SEC (Superdex 200) en polishing step.",
    a6.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p122, Dimers and aggregates (SEC + IEX recommandés en aval) + Chapter 7 polishing";

MATCH (s3:Symptom {name: "Présence d'agrégats / HMW dans le pool d'élution"}),
      (c5:Cause {name: "Élution à pH trop bas ou temps de contact acide prolongé"}),
      (c6:Cause {name: "Absence de neutralisation rapide du pool d'élution"}),
      (a5:Action {name: "Optimiser le pH d'élution au plus haut tolérable et privilégier une step elution"}),
      (a6:Action {name: "Collecter dans un buffer neutralisant et prévoir un polissage IEX/SEC"})
MERGE (s3)-[:INDICATES]->(c5)
MERGE (s3)-[:INDICATES]->(c6)
MERGE (c5)-[:RESOLVED_BY]->(a5)
MERGE (c6)-[:RESOLVED_BY]->(a6);

// =================================================================
// === Symptom #4: Fuite de Protein A (leaching) élevée dans l'éluat ===
// =================================================================

MERGE (s4:Symptom {name: "Fuite de Protein A (leaching) élevée dans l'éluat"})
SET s4.description = "Concentration de ligand Protein A leaching dans le pool d'élution > spec produit. Mesurable par ELISA non-compétitif. Plage normale typique sur MabSelect SuRe : 5-20 ppm (ng ligand/mg IgG). Au-delà, un déterminant procédé ou résine est en cause.",
    s4.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Protease stability and low ligand leakage + Fig 5 (low leakage over 100 cycles)",
    s4.keywords = "leaching fuite relargage ligand ppm leakage";

MERGE (c7:Cause {name: "Forte activité protéolytique dans le feedstock"})
SET c7.description = "Les protéases présentes dans le feedstock clarifié dégradent progressivement le ligand Protein A pendant la phase de chargement. L'intensité dépend de la lignée cellulaire, de l'âge de culture, et du hold time entre clarification et capture. Le Data File MabSelect SuRe cite ce mécanisme comme l'une des contributions principales au ligand leakage des résines Protein A.",
    c7.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Protease stability and low ligand leakage + Fig 4 (impact des protéases démontré par electrophorèse rProtein A vs SuRe)";

MERGE (c8:Cause {name: "Conditions CIP trop agressives (NaOH concentré ou contact prolongé)"})
SET c8.description = "MabSelect SuRe tolère NaOH 0.1-0.5 M jusqu'à 200 cycles, mais une concentration NaOH élevée combinée à un contact time long accélère la dégradation du ligand et corrèle avec un leaching accru. Fig 2 montre la perte de DBC selon la sévérité (0.1 M / 15 min vs 0.5 M / 60 min) - le leaching suit la même tendance.",
    c8.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p1-2, High stability in alkaline conditions + Fig 2 (DBC vs cycles CIP à différents NaOH et contact times)";

MERGE (a7:Action {name: "Réduire l'activité protéolytique pré-colonne"})
SET a7.description = "Minimiser le hold time entre clarification et capture (idéal <24h à 2-8°C). Conserver le feedstock clarifié à basse température pendant tout le hold. Évaluer l'ajout d'inhibiteurs de protéases si le feedstock est particulièrement chargé (à valider sur la compatibilité downstream). Si possible, sélectionner une lignée cellulaire à faible activité protéolytique.",
    a7.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Protease stability and low ligand leakage + Fig 4";

MERGE (a8:Action {name: "Resserrer le CIP et planifier un polishing CEX downstream"})
SET a8.description = "Utiliser la concentration NaOH la plus faible compatible avec l'efficacité du nettoyage testée - typiquement viser 0.1 M plutôt que 0.5 M, contact time 10-15 min plutôt que 60 min. Indépendamment, planifier une étape downstream de chromatographie échangeuse de cations (ex. HiTrap SP HP en step ou gradient à pH 5.2) qui élimine le Protein A leaching résiduel, démontré dans Fig 4.5 du Handbook.",
    a8.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p1-2, High stability in alkaline conditions + Fig 2; Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p124, Affinity ligands + Fig 4.5 (removal of leached Protein A by HiTrap SP HP CEX)";

MATCH (s4:Symptom {name: "Fuite de Protein A (leaching) élevée dans l'éluat"}),
      (c7:Cause {name: "Forte activité protéolytique dans le feedstock"}),
      (c8:Cause {name: "Conditions CIP trop agressives (NaOH concentré ou contact prolongé)"}),
      (a7:Action {name: "Réduire l'activité protéolytique pré-colonne"}),
      (a8:Action {name: "Resserrer le CIP et planifier un polishing CEX downstream"})
MERGE (s4)-[:INDICATES]->(c7)
MERGE (s4)-[:INDICATES]->(c8)
MERGE (c7)-[:RESOLVED_BY]->(a7)
MERGE (c8)-[:RESOLVED_BY]->(a8);

// =================================================================
// === Symptom #5: HCP résiduels élevés dans le pool d'élution    ===
// =================================================================

MERGE (s5:Symptom {name: "HCP résiduels élevés dans le pool d'élution"})
SET s5.description = "Taux de host cell proteins (CHO HCP typiquement, dosé par ELISA HCP) dans le pool d'élution > spec produit. Risque immunogénicité connu en biopharma, à éliminer impérativement avant release. La capture Protein A est moyennement sélective pour ce contaminant.",
    s5.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p124, Host cell proteins (HCP)",
    s5.keywords = "HCP protéines de cellule hôte host cell proteins CHO";

MERGE (c9:Cause {name: "Wash intermédiaire post-chargement insuffisant ou inadapté"})
SET c9.description = "Les HCPs peuvent se lier non-spécifiquement à la résine Protein A ou directement au mAb pendant le chargement. Si le wash entre chargement et élution est trop court, à conductivité trop basse, ou sans agent disruptif, ces HCPs co-éluent avec le mAb dans le pool d'élution.",
    c9.source = "Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p58, Optimization of parameters; Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p3, Low risk of host cell protein contamination";

MERGE (c10:Cause {name: "CIP insuffisant entre cycles avec carryover HCP"})
SET c10.description = "Lorsque le CIP est sous-dimensionné (NaOH dilué, contact trop court), les HCPs accumulées sur la résine ne sont pas désorbées et reviennent dans le pool d'élution du cycle suivant. Le Data File MabSelect SuRe cite explicitement que le CIP rigoureux réduit ce risque de contamination HCP et de carryover dans les product pools.",
    c10.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Low risk of host cell protein contamination or carryover + Fig 6 (Western blot confirmant absence de HCP après 100 cycles avec CIP rigoureux)";

MERGE (a9:Action {name: "Cribler en haut-débit les conditions de wash optimales"})
SET a9.description = "Utiliser des PreDictor 96-well filter plates ou HiTrap/HiScreen prepacked en HTS pour cribler différentes conditions de wash post-chargement : variations de conductivité (NaCl 150-500 mM), additifs disruptifs des interactions non-spécifiques (arginine 250 mM, caprylate de sodium 100 mM). Sélectionner les conditions qui réduisent les HCPs résiduelles sans dégrader le recovery mAb.",
    a9.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p4, Method development (PreDictor 96-well plates et HiTrap/HiScreen recommandés pour HTS optimization)";

MERGE (a10:Action {name: "Resserrer le CIP et ajouter une polishing AEX multimodale en aval"})
SET a10.description = "Sur MabSelect SuRe : laver entre cycles avec 2 CV de NaOH 0.1-0.5 M, contact 10-15 min, puis ≥5 CV de buffer de binding stérile filtré. Indépendamment, planifier une étape downstream de chromatographie échangeuse d'anions multimodale (Capto adhere ou Capto adhere ImpRes) qui élimine HCP + DNA + leached Protein A + agrégats en une seule étape - recommandation explicite Cytiva pour le polishing post-capture.",
    a10.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p2-3, Low risk of host cell protein contamination or carryover; Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p124, Host cell proteins (Capto adhere comme polishing recommandé) + p166-167, Cleaning sections (paramètres CIP)";

MATCH (s5:Symptom {name: "HCP résiduels élevés dans le pool d'élution"}),
      (c9:Cause {name: "Wash intermédiaire post-chargement insuffisant ou inadapté"}),
      (c10:Cause {name: "CIP insuffisant entre cycles avec carryover HCP"}),
      (a9:Action {name: "Cribler en haut-débit les conditions de wash optimales"}),
      (a10:Action {name: "Resserrer le CIP et ajouter une polishing AEX multimodale en aval"})
MERGE (s5)-[:INDICATES]->(c9)
MERGE (s5)-[:INDICATES]->(c10)
MERGE (c9)-[:RESOLVED_BY]->(a9)
MERGE (c10)-[:RESOLVED_BY]->(a10);

// =================================================================
// === Symptom #6: Bioburden / contamination microbienne          ===
// =================================================================

MERGE (s6:Symptom {name: "Bioburden ou contamination microbienne détectée dans la colonne ou le pool d'élution"})
SET s6.description = "Détection de croissance microbienne (bactéries, levures, moisissures) dans la colonne entre cycles ou dans le pool d'élution. Dépassement de la spec bioburden process (typiquement <1 CFU/10 mL en biopharma). Risque procédé et qualité, à traiter avant tout redémarrage.",
    s6.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p3, Low risk of host cell protein contamination or carryover (mention de microbial growth in the packed column); p4, Cleaning and sanitization",
    s6.keywords = "bioburden biocharge contamination microbienne croissance microbienne bactéries levures moisissures microbes";

MERGE (c11:Cause {name: "Sanitization en routine insuffisante pour le feedstock"})
SET c11.description = "Pour des feedstocks particulièrement riches en charge microbienne ou en contaminants difficiles (lipides, débris cellulaires non éliminés par clarification), le NaOH 0.1-0.5 M seul peut ne pas suffire. Le Data File MabSelect SuRe le reconnaît explicitement et propose des protocoles alternatifs.",
    c11.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p4, Cleaning and sanitization (mention explicite des challenging feedstocks avec recommandation d'agent réducteur ou combinaison NaOH + IPA)";

MERGE (c12:Cause {name: "Stockage de la colonne inadapté entre runs"})
SET c12.description = "Colonne stockée hors conditions recommandées (sans bactériostat type éthanol ou benzyl alcohol, hors plage de température 2-8°C, ou pour une durée non documentée) → croissance microbienne pendant le hold. Risque accru sur les longues campagnes avec arrêts intermédiaires.",
    c12.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p4, Storage (20% ethanol ou 2% benzyl alcohol à 2-8°C); Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p168, Storage of biological samples (Appendix 6)";

MERGE (a11:Action {name: "Renforcer le protocole de sanitization (NaOH + IPA ou ajout d'agent réducteur)"})
SET a11.description = "Passer à une sanitization combinée 0.1 M NaOH + 40% isopropanol (efficacité démontrée par Cytiva sur MabSelect SuRe). Pour les feedstocks très challengers, ajouter un cycle préalable avec agent réducteur (thioglycerol ou DTT) suivi du NaOH 0.1-0.5 M. Documenter contact time, concentration et fréquence des cycles dans la procédure CIP.",
    a11.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p4, Cleaning and sanitization (recommandations textuelles 0.1 M NaOH + 40% IPA; option DTT/thioglycerol pour challenging feedstocks)";

MERGE (a12:Action {name: "Standardiser le stockage en 20% éthanol ou 2% benzyl alcohol à 2-8°C"})
SET a12.description = "Avant tout arrêt prolongé, rincer la colonne avec ≥5 CV de la solution de stockage (20% éthanol ou 2% benzyl alcohol). Maintenir à 2-8°C, documenter la durée. Au redémarrage : rincer avec 3-5 CV d'eau distillée puis re-équilibrer avant chargement. Ne pas stocker à température ambiante ni à sec.",
    a12.source = "Cytiva, MabSelect SuRe Data File, CY12754-10Jul20-DF (2020) - p4, Storage; Cytiva, Affinity Chromatography Vol. 1: Antibodies Handbook, CY13981-25Jan21-HB (2021) - p168, Storage of biological samples";

MATCH (s6:Symptom {name: "Bioburden ou contamination microbienne détectée dans la colonne ou le pool d'élution"}),
      (c11:Cause {name: "Sanitization en routine insuffisante pour le feedstock"}),
      (c12:Cause {name: "Stockage de la colonne inadapté entre runs"}),
      (a11:Action {name: "Renforcer le protocole de sanitization (NaOH + IPA ou ajout d'agent réducteur)"}),
      (a12:Action {name: "Standardiser le stockage en 20% éthanol ou 2% benzyl alcohol à 2-8°C"})
MERGE (s6)-[:INDICATES]->(c11)
MERGE (s6)-[:INDICATES]->(c12)
MERGE (c11)-[:RESOLVED_BY]->(a11)
MERGE (c12)-[:RESOLVED_BY]->(a12);

// --- Check (run separately after the seed) ---
// MATCH (s:Symptom)-[:INDICATES]->(c:Cause)-[:RESOLVED_BY]->(a:Action)
// RETURN s.name AS symptom, c.name AS cause, a.name AS action;
