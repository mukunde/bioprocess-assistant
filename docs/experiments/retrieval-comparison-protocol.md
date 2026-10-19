# Protocole : recherche actuelle, passages simples et LightRAG

Date : 2026-10-19. Statut : protocole préparé, non exécuté. LightRAG est un candidat, pas une migration décidée. Aucune installation, indexation, génération, dépense API, modification de base ou publication n'est engagée par ce document.

## 1. Question et décisions possibles

Sur un petit corpus Cytiva vérifié, quelle approche retrouve les preuves nécessaires au dépannage avec le moins d'erreurs, de latence et de complexité ? Comparer les solutions utilisables sur le PC de référence (i5-1135G7, 16 Go RAM, Iris Xe), sans présumer qu'un graphe est supérieur aux passages.

Les décisions admissibles sont : conserver la recherche actuelle ; ajouter une recherche de passages ; utiliser LightRAG comme composant de recherche ; ou conclure que les données ne permettent pas de trancher. Une adoption éventuelle garde le contrat v0.2, la provenance et la revue humaine. La migration du stockage ou de la génération n'est pas l'objet de ce premier essai.

## 2. Prérequis et périmètre réellement comparable

- Terminer la génération puis la revue humaine des extractions du paquet `pages-100-102-v02-r2`. Ce paquet est préparé avec 59 éléments, mais aucune réponse n'a encore été produite. Les pages 97–99 et les fiches déjà rédigées sont des données de développement, pas des références humaines approuvées.
- Constituer un ensemble de claims approuvés et de preuves localisées, incluant de vrais symptômes/causes/actions. Les pages 100–102, principalement procédurales, ne suffisent pas à mesurer la couverture causale ; ajouter des pages de dépannage pertinentes si nécessaire, avant de figer les questions.
- Ne pas assimiler un contrôle lexical réussi à une approbation scientifique. L'utilisateur vérifie la fidélité documentaire ; l'aptitude opérationnelle industrielle reste hors périmètre.
- Figer PDF/édition, conversion, pages, sources ambiguës, claims, décisions humaines et liens claim-preuve par SHA-256. Aucun résultat de référence ni verdict de test n'entre dans les index.
- Les adaptateurs v0.2 vers le moteur de recherche et le rendu commun restent à implémenter et vérifier. Si un prérequis manque, enregistrer « non prêt » ; ne pas produire de score factice.

### Témoin existant et comparaison sur corpus commun

`tools.query_graph` utilise un index anglais de symptômes, un seuil Lucene de 2,5 et le meilleur symptôme, puis les chemins `INDICATES` / `RESOLVED_BY`. Ce n'est pas du Text2Cypher généré par LLM.

**A0, témoin inchangé** : conserver code, seed et seuil actuels et rejouer les cas existants séparément. La suite de développement est déjà connue ; ses scores ne constituent pas un nouveau résultat indépendant. Sans source précise retrouvable dans le corpus commun, un fait du seed n'est pas une preuve comparable. Les résultats A0 ne participent pas au classement à couverture égale.

**A, famille actuelle sur corpus commun** : créer une copie d'évaluation utilisant la même logique lexicale sur symptômes approuvés et parcours paramétrés, avec un adaptateur explicite depuis les claims v0.2. Conserver les procédures sans chemin causal dans l'inventaire de couverture ; ne pas inventer de cause pour les rendre accessibles. A est une adaptation expérimentale, jamais présentée comme l'application actuelle inchangée. Aucun changement du graphe de service.

Publier les résultats sur deux strates préassignées : questions compatibles avec le parcours causal et questions procédurales/synthétiques plus larges. Pour chaque strate, distinguer couverture représentable et qualité de recherche. Une impossibilité structurelle compte dans la couverture globale, mais ne prouve pas un mauvais classement lexical.

## 3. Trois approches principales

| Bras | Index et recherche | Ce qui reste identique |
|---|---|---|
| A — famille actuelle | Recherche lexicale anglaise sur symptômes, parcours des claims approuvés, liens vers leurs passages sources ; seuil initial 2,5, éventuel réglage sur développement uniquement | Corpus approuvé, preuves, normalisation des questions, sortie canonique |
| B — passages simples | Un embedding local multilingue par passage canonique ; classement par similarité cosinus, sans extraction d'entités, graphe, reranker ou expansion LLM | Même modèle d'embedding et mêmes passages que C ; même budget de contexte |
| C — LightRAG | Import des mêmes passages et d'une projection des claims approuvés via `insert_custom_kg`, recherche `mix`, récupération du contexte sans réponse finale | Même graphe documentaire que A, mêmes embeddings que B, même sortie canonique |

B est volontairement une recherche vectorielle simple, pas un second framework complet. Un témoin BM25 sur les passages peut être ajouté comme ablation B-lexical, avec résultats séparés et coût déclaré ; ne pas remplacer B après lecture des résultats de test.

Pour C, épingler un commit/release et un lock de dépendances avant l'essai. Tester les API de cette version : la documentation actuelle décrit `insert_custom_kg`, `only_need_context` et `aquery_data`, mais leur disponibilité ne remplace pas un test d'intégration. Retourner les objets et preuves exploitables, plutôt que dépendre d'une analyse fragile d'un contexte mis en forme.

Le mode contexte seul supprime la génération finale, mais ne garantit pas zéro appel LLM : extraction des mots-clés, fusion ou résumé peuvent encore en utiliser. Comptabiliser et journaliser chaque rôle. Aucun appel de reconstruction ne doit réintroduire des claims refusés ou en quarantaine.

Si C gagne, effectuer les ablations `naive` / `mix` avec les mêmes passages, embeddings et budgets, puis avec mots-clés figés. Sans ces contrôles, conclure sur le système LightRAG testé, pas sur l'effet causal du graphe seul. L'extraction automatique native et le chunking propre à LightRAG sont des expériences ultérieures distinctes.

## 4. Corpus, chunking et conservation des conditions

Utiliser notre stratégie fondée sur la structure documentaire et la hiérarchie. Les trois bras partagent exactement le même manifeste de passages :

- Regrouper paragraphes/listes par section et sous-section ; viser 150–350 tokens, plafond 512, sans découper une instruction de sa condition, sa négation ou son unité. Une instruction plus longue devient un cas exceptionnel déclaré, pas une troncature silencieuse.
- Conserver document/version, titre et chemin hiérarchique, pages PDF/imprimées, item_refs, offsets et empreintes des textes. Les tableaux gardent leurs en-têtes et associations de lignes ; les légendes restent distinguées du protocole.
- Garder le lien enfant-parent pour rétablir le contexte. Toute expansion vers un parent est appliquée par le même assembleur aux trois bras et consomme le même budget ; elle ne doit pas fournir des passages supplémentaires uniquement à C.
- Affecter des IDs canoniques stables aux passages et aux preuves. La projection LightRAG doit préserver les IDs de claims, force, portée produit/phase, conditions AND/OR, quantités et liens vers ces preuves. Si une information ne tient pas dans une arête, conserver une représentation de Claim distincte et un registre externe versionné ; ne pas l'aplatir en résumé faisant autorité.
- Vérifier l'export aller-retour sur des cas de négation, alternatives, produits voisins et nombres. Une perte de preuve ou de condition bloque le bras C avant les mesures.

Un passage peut contenir un texte ambigu utile pour expliquer une abstention ; il garde son drapeau et ne devient jamais une recommandation autorisée. Le filtre commun de publication/revue s'applique aux trois bras. Si l'unité source mélange clair et ambigu, appliquer le blocage conservateur existant ou créer une nouvelle segmentation revue, identique pour tous.

## 5. Questions et référence humaine

Préparer 24 intentions, chacune en français et en anglais : 48 formulations au total. Répartition prévue, à confirmer sur les sources réelles avant gel :

| Famille | Intentions | Attendu |
|---|---:|---|
| Dépannage causal direct | 6 | Symptôme, causes possibles et actions documentées |
| Conditions, nécessité et négation | 4 | Application conditionnelle ou demande de contexte, sans permission inventée |
| Quantités et frontières de produit/phase | 4 | Valeurs/unités exactes, refus de transfert à un produit voisin |
| Preuves dispersées entre plusieurs passages | 4 | Toutes les preuves indispensables, sans relation nouvelle inférée |
| Hors couverture, manque de contexte ou source ambiguë | 4 | Refus, clarification ou signalement d'ambiguïté selon le cas |
| Injection directe ou portée par un document de test | 2 | Instruction hostile traitée comme donnée, aucune dérogation aux preuves |

Une variante documentaire injectée est une fixture synthétique distincte, marquée comme telle, jamais attribuée au PDF original ni publiée dans le graphe. Tous les bras voient la même variante et le même statut de revue.

Réserver huit intentions (16 formulations) au développement et 16 intentions (32 formulations) à l'évaluation verrouillée. Choisir une graine, répartir les familles et conserver les deux langues et toutes les variantes d'une intention dans le même groupe. Éviter les quasi-doublons entre groupes. Les questions de test sont cachées pendant le réglage ; le corpus reste indexé pour tous. Puisque les pages ont été inspectées, ne pas appeler cela un manuel inédit ou une évaluation totalement aveugle.

Pour chaque question, l'utilisateur valide avant exécution : IDs de passages pertinents et indispensables, preuves alternatives acceptables, claims autorisés, produit/phase, paramètres essentiels, contexte manquant, statut attendu (`answer`, `clarify`, `refuse`, `source_ambiguity`) et justification. Un passage sans lien causal explicite ne justifie pas une cause inventée.

Les deux formulations doivent avoir le même sens. Les métriques des deux langues restent séparées puis agrégées par intention ; elles ne constituent pas 48 observations indépendantes. Conserver les 33 cas actuels comme contrôle de développement séparé, pas comme jeu neuf.

## 6. Configuration et déroulement

### Étape 0 — Faisabilité, avant tout score

Créer des espaces d'évaluation isolés, sauvegarder les configurations et vérifier que le graphe de service est inchangé. Ne pas utiliser de procédure de suppression globale. Vérifier import, provenance aller-retour, mode contexte seul et absence de fournisseurs cloud non configurés.

Sélectionner et figer un seul embedding local multilingue compatible avec le PC (nom, révision, dimension, tokenizer, quantification et préfixes). Mesurer sa mémoire sur deux questions de développement. Ne pas choisir son modèle après lecture du test. S'il ne tient pas en mémoire, arrêter et déclarer le candidat non viable dans ce profil matériel.

Pour les mots-clés LightRAG, employer un modèle local disponible, préciser nom/révision/quantification et paramètres. Une bibliothèque open source ne donne pas accès à l'abonnement ChatGPT depuis ses appels API : aucune clé API ou dépense supplémentaire n'est autorisée ici. L'extraction par abonnement reste une étape documentaire séparée, partagée par tous les bras.

### Étape 1 — Recherche seule, comparaison principale

- Fournir à chaque bras la même question originale. Pour A et son index anglais, utiliser une reformulation anglaise figée, préparée sans les réponses et appliquée également comme entrée à B/C dans la piste contrôlée. Pour un texte anglais, garder l'original. Archiver les deux versions et la règle de reformulation.
- Une piste secondaire FR/EN native peut laisser B/C traiter le français directement et utiliser le pont modèle réel pour A : comptabiliser ce pont et publier ces scores séparément. Ne pas mélanger les deux pistes.
- A conserve le meilleur symptôme ; ses chemins sont projetés vers les passages cités. B et C classent des passages ; chaque résultat est converti en unités canoniques de preuve. Dédupliquer avant calcul des métriques. Fixer le départage des ex aequo (ID) et l'ordre des preuves d'un chemin.
- Exporter au plus cinq passages canoniques, puis appliquer un plafond commun de 2 048 tokens de contexte, titres compris, avec un même tokenizer de mesure. Retirer les passages entiers qui dépassent le budget, sans tronquer une condition ou une quantité ; enregistrer les exclusions. Mesurer le classement avant assemblage et la couverture effective après plafond ; ne pas appeler un top-k d'entités LightRAG un top-k de passages.
- Régler seuils sur le développement seulement ; ne pas comparer directement un score Lucene, cosinus et LightRAG. Si le moteur ne fournit pas de score calibrable, fixer sa règle de sélection sur développement et la déclarer.
- Désactiver le reranking pour la comparaison principale. Toute future activation est une variante dédiée avec son coût.
- Figer tout réglage avant le test : un passage principal, puis trois répétitions chronométrées de recherche par question, en alternant l'ordre A/B/C. Ne pas sélectionner la meilleure répétition.
- Séparer démarrage à froid (mesure distincte), régime chaud avec caches de réponses/requêtes désactivés et profil cache activé éventuel. Les caches d'index restent des artefacts figés ; déclarer les caches non désactivables et ne pas les confondre avec des calculs frais.

### Étape 2 — Réponse complète, seulement après les adaptateurs

Réutiliser les contextes enregistrés à l'étape 1. Même modèle local de réponse, révision, paramètres, prompt, limite de sortie et politique de refus pour les trois bras ; une génération par question/bras, aucun choix parmi plusieurs essais. Les erreurs et sorties tronquées restent dans les dénominateurs. La même graine ne rend pas les exécutions parfaitement déterministes.

Le rendu actuel rejette la prose technique libre : la comparaison principale de réponse doit conserver cette contrainte. Un adaptateur commun transforme les preuves retrouvées en claims approuvés admissibles, avec leurs conditions et leur portée ; le modèle sélectionne leurs IDs et le même validateur/rendu produit la sortie. Les preuves retrouvées seules ne valent pas approbation. Cet adaptateur est à construire : tant qu'il manque, limiter les conclusions à la recherche, sans annoncer de score de génération comparable.

Une expérience de génération libre classique est possible ensuite avec un prompt identique et des contrôles explicites, mais ses scores sont séparés de ceux du rendu contraint. Ragas, avec juges/embeddings locaux explicitement configurés, complète les vérifications déterministes ; ses verdicts ne deviennent pas des décisions humaines. Si le juge local n'est pas calibré sur quelques cas relus, publier ses scores comme exploratoires et privilégier la revue manuelle masquée par bras.

## 7. Mesures et dénominateurs

| Niveau | Mesures | Conditions de lecture |
|---|---|---|
| Recherche | Precision@5, Recall@5, MRR, NDCG@5 | Sur les questions ayant une référence pertinente ; pertinence graduée 0/1/2 gelée par l'annotation. Absence d'une preuve = score nul, pas exclusion de la question |
| Preuves complètes | Fraction des questions où toutes les preuves indispensables (ou un ensemble alternatif accepté) sont présentes | Mesurer avant et après budget de contexte ; ne pas pénaliser une alternative de preuve validée comme une omission |
| Couverture | Questions représentables par A, preuves mappables, échecs par famille | Séparer limites structurelles, pertes d'adaptateur et défauts de classement |
| Réponse | Claims justifiés, erreurs de relation/force/condition/quantité/produit, exactitude des citations | Comparaison des sorties et de leurs preuves par vérification déterministe puis revue humaine |
| Abstention | Bons refus, bonnes clarifications, fausses acceptations et refus excessifs | Matrice des quatre statuts attendus ; les questions sans preuve n'ont pas un Recall@5 artificiel de zéro |
| Exploitation | Temps d'indexation et de revue, latence médiane/p95, RAM pic du système et processus, taille des index | Faible échantillon : p95 exploratoire, pas de p99 ni promesse de production |
| Appels/coût | Appels par rôle, tokens rapportés/estimés, échecs et reprises, cache, coût estimé | Prix inconnu = inconnu ; abonnements/électricité/temps humain ne sont pas des coûts nuls démontrés |

Pour un top-5, diviser Precision@5 par 5, en comptant les positions non rendues comme non pertinentes. Recall@5 porte sur les preuves de référence canoniques ; publier séparément la couverture des ensembles alternatifs minimaux. MRR mesure la première preuve pertinente et ne suffit pas pour une procédure nécessitant plusieurs preuves. NDCG utilise les mêmes annotations graduées pour tous les bras.

Présenter les comptes bruts et résultats appariés par intention, famille et langue. Un éventuel bootstrap rééchantillonne les intentions avec leurs langues, pas les répétitions de timing. Petit jeu documentaire : aucune généralisation à l'ensemble du manuel ou au secteur régulé. Échec/OOM/timeout = cas visible ; budget de temps identique par requête, décidé sur développement puis gelé.

## 8. Traçabilité, ressources et budget

Conserver un manifeste du run : commit du projet et de LightRAG, environnement verrouillé, SHA-256 corpus/claims/passages/questions, matériels, modèles et poids, paramètres, seuils, budgets de contexte, caches et ordre des exécutions. Fixer les plafonds exacts de temps et de RAM après le test de faisabilité, avant les questions verrouillées. Sur le PC de 16 Go, réserver une marge pour Windows/WSL ; une exécution qui provoque une pression mémoire durable ou compromet le PC est arrêtée, sans cacher les échecs.

Chaque résultat contient `run_id`, bras/piste, `question_id`, `intent_id`, langue, passages/claims ordonnés, scores natifs, raisons de filtre, contexte exact et empreinte, résultat/erreur, latences, RAM, appels et tokens par rôle. Le journal de benchmark est local et contrôlé ; les traces opérationnelles restent des métadonnées par défaut, sans secrets ni texte intégral exporté vers un service tiers.

Budget additionnel API de ce protocole : **0 EUR**. Tous les modèles d'exécution sont locaux ; aucun fournisseur distant de repli. Le plafond projet inférieur à 10 EUR/mois reste une contrainte, pas une autorisation de dépenser. Arrêter plutôt que changer silencieusement de fournisseur. Compter séparément construction d'index/embeddings, requêtes, génération, juges et temps humain. L'absence de facture API n'établit pas la gratuité totale.

Enregistrer les données de run sous un nouveau `data/experiments/retrieval/<run_id>/`, ignoré par Git. Garder manifestes, résultats, métriques et notes de revue séparés des entrées figées. Ne pas indexer les réponses attendues ni les sorties d'un autre bras.

## 9. Règle de décision à geler avant le test

Conditions minimales : aucune sortie publiée avec faux produit, quantité dangereusement altérée, condition supprimée, preuve inventée ou quarantaine contournée dans le jeu vérifié ; provenance vérifiable et respect des limites matérielles. Les erreurs de recherche restent mesurées même si le filtre les bloque. L'absence d'erreur sur ce petit jeu ne constitue pas une certification.

Pour justifier un pilote LightRAG, seuil de travail proposé à figer après annotation mais avant exécution : au moins deux intentions d'évaluation supplémentaires avec preuves complètes sur les 16, face au meilleur bras plus simple, sans régression sur les fausses acceptations et avec une latence médiane au plus deux fois celle de ce concurrent et sans dépassement des plafonds de ressources. Le nombre de deux est un seuil pratique de pilote, pas une significativité statistique. Publier aussi les variantes perdantes et la sensibilité aux cas individuels ; aucune adoption générale sur ce seul résultat.

Si B suffit, privilégier B. Si A suffit, conserver A. Si le gain de C n'apparaît que sur les questions plus larges, envisager un complément documentaire borné plutôt qu'un remplacement du moteur de dépannage. Si la projection C perd des conditions ou réclame des reprises manuelles disproportionnées, ne pas poursuivre malgré un bon score moyen. Les corrections faites après déverrouillage deviennent une nouvelle expérience, jamais une amélioration rétroactive du score.

## 10. Livrables et ordre de travail

1. Revue humaine des sources et claims, inventaire de couverture et manifeste de passages commun.
2. Questions annotées, groupes développement/évaluation et plan des mesures gelés.
3. Adaptateurs A/C et pilote de faisabilité locale ; compléter les champs de configuration encore non choisis avant toute mesure verrouillée.
4. Résultats de recherche A/B/C, témoins A0 et ablations nécessaires ; journal de ressources et erreurs.
5. Réponses comparables seulement après disponibilité du rendu commun ; revue masquée et Ragas exploratoire.
6. Rapport décisionnel avec comptes bruts, limites, coût d'entretien et recommandation motivée.

Le présent document prépare la méthode. Il ne prétend pas fournir déjà les questions validées, les adaptateurs ou un benchmark exécutable. Aucun commit ni push sans accord.

## Sources techniques consultées le 2026-10-19

- [LightRAG README](https://github.com/HKUDS/LightRAG/blob/main/README.md) : rôles de modèles et modes de recherche.
- [Programmation du cœur](https://github.com/HKUDS/LightRAG/blob/main/docs/ProgramingWithCore.md) : graphe personnalisé, contexte seul, limites de contexte et stockage. Ces capacités sont à revérifier sur la version épinglée ; contexte seul ne signifie pas absence de tout appel LLM.
- [ADR multilingue historique](../ADR-002-multilingual-retrieval.md) : résultats antérieurs à distinguer du nouvel essai.
- [Contrat v0.2](../CLAIM-CONTRACT-V02.md) et [roadmap](../ROADMAP.md) : provenance, conditions et limites de publication.
