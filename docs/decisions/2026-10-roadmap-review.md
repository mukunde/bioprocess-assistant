# Revue méthodologique — archive du 18 octobre 2026

Archive du raisonnement et des alternatives discutées. Le plan actif unique est [ROADMAP.md](../ROADMAP.md) ; ce document ne constitue pas une seconde roadmap à maintenir.

Statut : proposition de travail ajustée aux réponses de Gaël. Usage prioritaire : dépannage, avec symptômes, causes possibles et actions. Objectif professionnel : AI/LLM engineer et data/knowledge engineer. Fonctionnement exclusivement local par défaut ; cloud privé envisageable si ses garanties et son coût sont acceptables. Budget déclaré : moins de 10 € maximum, interprété comme mensuel puisque la question portait sur un budget mensuel. Disponibilité : libre en semaine, avec autant de temps que nécessaire pour le projet ; aucune limite globale de 5 h/semaine. Aucun hébergement ni achat n'est engagé. Aucun commit ni push.

## Ce que révèle la revue

La roadmap existante [la roadmap](../ROADMAP.md) prévoyait correctement l'instrumentation (phase 1), puis le modèle métier et une référence annotée (phase 2), avant l'ingestion (phase 3). L'exécution a anticipé la phase 3 sans satisfaire ces prérequis. L'ontologie n'était donc pas oubliée du plan ; elle a été insuffisamment définie avant son utilisation. Les tests synthétiques ont vérifié des contrats techniques, pas la qualité d'extraction réelle.

Le test réel reste utile : 29 entités, aucune relation métier, 13 fiches bloquées, 55 min 49 s. Il invalide le choix actuel comme configuration par défaut, sans démontrer que Docling Graph ou le modèle local seraient inadaptés en général. Un essai unique ne suffit pas à sélectionner une architecture ou à mesurer un taux de fiabilité.

Les points solides à conserver sont la séparation ingestion/application, les sources immuables, la revue humaine, les contrôles déterministes, le rendu borné des réponses et le refus de publier automatiquement les extractions.

## Critique du périmètre et des hypothèses

- Trois objectifs sont mêlés : assistant utile, plateforme d'ingestion de graphes, démonstrateur pour un secteur régulé. Choisir un scénario utilisateur principal ; les deux autres deviennent des contraintes ou extensions.
- Le graphe et Neo4j sont imposés avant comparaison avec une référence documentaire simple. Garder l'existant comme candidat, pas comme conclusion expérimentale. KAG ne doit pas être un objectif indépendant du besoin.
- Un modèle de dépannage n'a pas à représenter tous les objets du manuel. Les figures, tampons et marqueurs ne doivent pas être forcés dans les cinq classes disponibles. Un graphe partiel peut être correct si son périmètre est explicite et les passages restent consultables.
- La chaîne Symptom→Cause→Action encourage une causalité plus forte que certains énoncés. Distinguer cause possible, effet décrit, action recommandée et conditions d'application. Une consigne « nettoyer si la pression augmente » ne justifie pas d'inventer une cause intermédiaire.
- L'absence d'expert n'empêche pas de vérifier la fidélité au manuel, mais empêche d'appeler cette revue une validation d'adéquation à un procédé industriel. Remplacer ce prérequis inaccessible dans le prototype par une validation documentaire explicite et une catégorie « ambigu/non évalué ». Maintenir l'expertise comme prérequis d'un usage opérationnel éventuel.
- Une source citée et un rendu déterministe n'éliminent ni erreur de sélection, ni mauvaise condition, ni erreur du graphe. Remplacer les promesses absolues de type « zero hallucination » par des critères mesurables et leurs limites.
- Les conclusions historiques sur les embeddings portent sur six symptômes et un jeu de développement. Elles ne démontrent pas qu'une recherche vectorielle sur des passages serait inutile. La similarité de recherche et la décision de répondre/refuser doivent être évaluées séparément.
- Le pipeline de publication produit un graphe de preuves séparé, encore non consommé par le chatbot. La connexion entre connaissance approuvée et réponse utilisateur doit devenir un jalon explicite. Prévoir aussi l'activation d'une version et sa révocation ; stocker les snapshots ne suffit pas à retirer une connaissance du service.
- Le coût principal peut être le temps de revue, pas les tokens. Comparer l'annotation manuelle assistée à l'extraction automatique sur le même lot. Ne pas investir dans l'automatisation si elle coûte davantage en corrections pour le volume visé.

## Alternatives à comparer

| Approche | Intérêt | Coût/limite | Décision proposée |
|---|---|---|---|
| Recherche de passages + réponse sourcée/abstention | Référence simple pour les questions documentaires | Relations et conditions à vérifier dans les passages | Baseline obligatoire, commencer lexical puis tester une extension seulement si nécessaire |
| Petit graphe renseigné manuellement avec preuves | Référence fiable pour le dépannage ciblé ; coût initial prévisible | Maintenance et couverture limitées | Baseline obligatoire pour les faits sélectionnés |
| Extraction assistée par section + revue + graphe | Évalue réellement le gain d'automatisation | Peut coûter plus en correction que la saisie manuelle | Candidat principal à tester après les deux références |
| Graphe et passages combinés | Exploite des relations validées et restitue leur contexte | Routage, cohérence et évaluations supplémentaires | Cible possible si le gain est mesuré |
| KAG complet, règles et inférences étendues | Peut servir des questions exigeant plusieurs étapes de raisonnement | Coût de modélisation et d'exploitation élevé | Différer tant qu'aucune question concrète n'en démontre le besoin |

Conserver Docling pour la conversion dans les essais. Comparer le contrat direct par contexte borné au dense compact pour l'extraction ; ce sont des variantes, pas des engagements. L'ontologie métier doit rester indépendante de la bibliothèque d'extraction.

## Nouvelle séquence avec critères de passage

| Jalon | Livrable | Critère de passage |
|---|---|---|
| 0 — Usage et budget | Scénario principal, utilisateur, corpus, limites de réponse ; budgets de latence interactive, ingestion et revue séparés | Choix explicités avec Gaël ; critères fixés avant comparaison |
| 1 — Questions et ontologie minimale | 10–15 questions représentatives proposées, classes/relations définies, exemples et contre-exemples, conditions, identité et provenance | Chaque concept répond à un besoin ; exemples vérifiés dans le PDF ; ambiguïtés signalées |
| 2 — Référence et mesures | Petit lot annoté indépendant des sorties du modèle ; traces OTel et budget d'exécution minimal | Mesure reproductible des faits/relations manqués, erreurs, temps de revue et ressources |
| 3 — Baselines | Recherche de passages et graphe manuel sur le même périmètre | Scores et coûts observés ; refus et demandes de précision testés ; limites explicites |
| 4 — Extraction expérimentale | Micro-test CIP puis pages variées ; source→faits→preuves→revue | Gain par rapport à la saisie manuelle mesuré ; aucun élément publié sans preuve et revue ; erreurs critiques analysées |
| 5 — Tranche complète utile | Une question utilise les faits approuvés d'un snapshot précis et affiche les preuves | Publication, activation, reprise, correction et révocation testées ; contextes incomplets traités |
| 6 — Évaluation et démonstration | Jeu réservé, Ragas calibré, attaques de régression, rapport qualité/latence/coût, démarrage reproductible | Résultats du système actuel ; décisions architecturales justifiées ; aucun ancien score présenté comme nouveau |

Le nombre de questions est une proposition pour démarrer, pas une taille statistiquement suffisante pour établir la fiabilité industrielle. Les seuils de performance et budgets restent à fixer selon l'usage ; ne pas inventer des cibles de précision ou de latence sans acceptation.

## Méthode expérimentale

1. Définir des questions que l'ontologie et le système doivent pouvoir traiter : « quelle action le manuel recommande-t-il pour ce symptôme sur ce produit ? », « sous quelles conditions ? », « que ne permet pas de conclure le passage ? ».
2. Annoter les faits attendus avant de consulter les réponses du modèle. Vérifier aussi les faits absents des extractions : la revue des seules propositions ne mesure pas le rappel.
3. Séparer développement et test par section ou famille de questions ; éviter de placer des paraphrases du même fait des deux côtés. Avec un seul manuel, annoncer clairement la limite de généralisation.
4. Utiliser les mêmes sources, modèle, contexte et budgets pour la première comparaison des méthodes ; changer ensuite un facteur à la fois. Faire quelques répétitions pour les variantes finalistes et distinguer démarrage à froid et fonctionnement à chaud.
5. Mesurer par étape : conversion, extraction, localisation, validation sémantique, retrieval, réponse. Les scores globaux seuls ne permettent pas d'attribuer une régression.
6. Évaluer relations avec types, direction, conditions et preuve ; compter explicitement les erreurs de nombre, unité, négation et produit. Mesurer la couverture des faits attendus, pas le nombre total de nœuds.
7. Enregistrer durée, appels, tokens lorsqu'ils sont disponibles, RAM, minutes de revue et coût par fait accepté. Les tokens inconnus restent inconnus, les ressources locales ne sont pas assimilées à une absence de coût.
8. Poser des règles d'arrêt : dépassement de budget, échec de schéma, troncature ou citation non résolue produisent un état incomplet/échoué observable, jamais une réussite silencieuse. Conserver la possibilité d'une reprise ciblée.

## Place des outils retenus

- **OpenTelemetry** : avant le prochain benchmark, spans aux frontières conversion/extraction/validation/recherche/réponse, identifiants de versions et erreurs. Export local simple d'abord ; OTLP/Collector et démonstration vers deux backends ensuite. Le format portable ne garantit pas la portabilité des tableaux de bord ou calculs de coûts.
- **Ragas** : conservé, mais utilisé pour la recherche et les réponses avec contextes et références préparés. Ajouter des mesures spécifiques pour la fidélité des relations extraites. Calibrer les juges sur des cas revus ; ne pas définir le succès par un unique score de faithfulness, particulièrement avec le rendu actuel qui recopie les faits du graphe.
- **Red-teaming** : commencer par des fixtures reproductibles et contrôles déterministes : injection dans le document, mauvaise résine, négation, conditions manquantes, fausse preuve, nombres altérés et épuisement de budget. Ajouter Promptfoo comme orchestration lorsque le contrat de l'application est stabilisé ; garder des cas bénins pour détecter le sur-refus.
- **Modèles locaux** : conserver le modèle déjà installé pour isoler d'abord les effets du schéma et de l'orchestration. Un modèle plus fort sur des textes publics peut servir de comparaison si Gaël l'autorise ; ce n'est pas une référence de vérité. Fine-tuning différé jusqu'à disposer d'erreurs récurrentes et d'annotations suffisantes.
- **Ontologie et visualisation** : une définition versionnée et des exemples de relations suffisent au début. OWL/Protégé devient pertinent si une question de raisonnement ou d'interopérabilité le justifie ; un diagramme du graphe observé ne remplace pas la définition des relations autorisées.
- **Employabilité** : privilégier une tranche complète démontrable, une évaluation indépendante, un diagnostic d'échec et des choix mesurés. La quantité d'outils intégrés est secondaire.

## Corrections documentaires à reporter après choix

Mettre à jour `docs/ROADMAP.md` et `docs/INGESTION.md` : matériel désormais connu, premier test réel effectué, qualité insuffisante, provenance imparfaite, instrumentation et référence encore manquantes. Marquer explicitement « implémenté », « testé sur fixtures », « mesuré sur un manuel » et « accepté » comme des états différents. Réviser les promesses du README et garder les anciens scores uniquement comme historique. Ne pas déclarer la phase 0 entièrement validée pour le déploiement tant que les contrôles live requis ne sont pas réalisés.

## Choix confirmés et conséquences

- **Produit** : assistant documentaire de dépannage de la capture Protein A. Il présente des causes possibles et des actions décrites dans les sources, demande les conditions nécessaires et distingue recommandation documentaire et diagnostic établi.
- **Portfolio** : deux dimensions dans un seul produit. Knowledge engineering : ontologie versionnée, faits et preuves, conditions, revue, publication et révocation. AI/LLM engineering : extraction mesurée, recherche, gestion de contexte, abstention, traces et évaluations.
- **Exécution** : conversion, modèle, recherche, stockage, revue et évaluations locales pour le parcours de référence. L'application existante avec Claude et AuraDB ne satisfait pas encore cette contrainte : conserver ce parcours comme historique et prévoir explicitement un parcours local complet. Examiner licences et limites des composants locaux avant distribution.
- **Cloud privé** : option ultérieure et conditionnelle. Une API distante ou un GPU partagé bon marché n'est pas assimilé à un environnement privé. Évaluer isolation, accès, stockage, rétention, région et coûts complets avant toute proposition. La réussite du projet ne dépend pas de trouver une offre GPU gratuite.
- **Budget** : aucun service payant nécessaire au prochain jalon. Les frais API locaux peuvent être nuls, mais matériel et électricité restent des coûts réels. Tout benchmark distant ou hébergement exige un choix explicite ultérieur ; moins de 10 €/mois reste un plafond, pas un objectif de dépense.
- **Temps** : Gaël est disponible en semaine et peut consacrer au projet autant de temps que nécessaire. Avancer par jalons, sans plafond hebdomadaire ni répartition horaire imposée. Mesurer néanmoins le temps de revue et les temps machine pour comparer les méthodes et éviter du travail inutile.

## Premier cycle proposé : quatre étapes, sans durée imposée

Ces étapes suivent leurs dépendances et peuvent être enchaînées dès que leurs critères sont satisfaits. Elles ne correspondent plus à des semaines calendaires. Les critères de qualité priment sur la vitesse ; les temps machine sont mesurés séparément.

| Étape | Travail prioritaire | Livrable |
|---|---|---|
| 1 | Cadrer 2–3 symptômes, préparer environ 10 questions ; définir les relations et vérifier un petit lot de faits | Ontologie minimale et exemples documentaires revus, avec ambiguïtés |
| 2 | Rendre ces faits consultables localement, sans extraction automatique indispensable ; préparer tests et traces minimales | Une question mène à une réponse sourcée ou à une demande de précision, sur un snapshot connu |
| 3 | Micro-test d'extraction instrumenté, en réutilisant la conversion ; comparer au temps de saisie manuelle | Choix motivé entre extraction assistée et maintien d'une saisie manuelle pour ce périmètre |
| 4 | Évaluer des cas réservés, y compris mauvaises conditions, négations et injections ; documenter les résultats | Démonstration locale reproductible et rapport des limites |

Si un jalon échoue, réduire le périmètre ou prolonger le cycle. Ne pas compenser par davantage d'outils. Ragas est conservé comme évaluation complémentaire locale, introduite lorsque les références sont prêtes et le coût de son juge mesuré. L'export OTel vers plusieurs plateformes et le red-team automatisé étendu restent des étapes suivantes.

### Ontologie : décisions à préparer avant le prochain test

Définir Symptom, PossibleCause, RecommendedAction et le contexte produit/phase ; autoriser une recommandation Symptom→Action lorsque la source ne donne aucune cause intermédiaire. Séparer ces concepts métier du Document, de sa Version, des Evidence et des Claim qui portent la provenance. Les noms définitifs et les correspondances avec le schéma existant seront documentés. Définir les conditions inconnues, les contradictions et le retrait d'une affirmation. Préparer les exemples avant de demander leur revue à Gaël.

### Critère de réussite du premier cycle

Un petit assistant de dépannage fonctionne entièrement en local, sur quelques faits vérifiés, et expose exactement les preuves et conditions de ses réponses. Son rapport distingue ce qui est testé, mesuré, revu et encore inconnu. Le graphe peut être petit et alimenté manuellement au départ ; l'automatisation est retenue seulement si sa valeur est mesurée.

Sources : roadmap et guides locaux lus le 18 octobre 2026 ; diagnostic du test Cytiva dans `diagnostic-extraction-cytiva.md`. Documentation primaire consultée : https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/ ; https://opentelemetry.io/docs/specs/semconv/gen-ai/ ; https://github.com/docling-project/docling-graph/blob/main/docs/fundamentals/extraction-process/dense-extraction.md
