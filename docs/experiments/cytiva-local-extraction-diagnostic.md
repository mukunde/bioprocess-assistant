# Diagnostic du premier test Cytiva

Analyse des fichiers existants, sans nouvelle extraction, modification des décisions, commit ou push.

Run : `bioprocess-assistant-review/data/ingestion/a325aff86fd8-5bb7c2d10264`.
Pages originales 97–99, pages 1–3 de l'extrait. Modèle local Ministral 3B Q4, CPU i5, RAM 16 Go.

## Résultats et causes

29 entités, aucune relation sémantique. Les métadonnées natives donnent `skeleton_path_counts = {"": 1, "entities[]": 29}`. Il n'y a aucun nœud `relations[]` dès la découverte. `merge_orphans_dropped = 0`, aucune troncature ni aucun batch de découverte en échec. L'adaptateur ne filtre pas les relations : il reprend celles du modèle. Les 27 arêtes natives sont des liens structurels, pas des relations métier.

Le schéma place les relations dans une liste de modèles autonomes avec cinq champs d'identité (types et noms des deux extrémités, prédicat). Or la découverte dense demande des identifiants courts copiés du document, interdit de remplir les propriétés et indique que les relations seront traitées plus tard. Le remplissage n'est ensuite lancé que pour les chemins effectivement découverts ; ses sous-schémas retirent les listes enfants. Cette combinaison explique le blocage structurel et constitue une hypothèse forte sur la cause de l'omission par le modèle, pas une preuve d'une incapacité générale de Docling Graph.

Le modèle n'a extrait aucun Symptom/Cause malgré le texte explicite de `#/texts/77` (encrassement, obstruction, augmentation de la contre-pression, diminution du débit) et `#/texts/78` (nettoyer lorsque la contre-pression augmente). Ces textes sont présents dans le chunk CIP : le défaut ne vient pas de leur absence dans la conversion. Les objets extraits sont trop souvent mal typés : tampon classé Resin, eau distillée classée ProcessStep, marqueurs de masse moléculaire classés Resin. Le schéma Entity et Relation n'a pas de docstring de classification ; le guide de découverte ne transmet pas les énumérations de type et de prédicat. La docstring racine est tronquée à 240 caractères. Le découpage conserve la section CIP mais des titres locaux comme Lane remplacent le contexte produit ; le début du document est répété comme contexte global, ce qui peut favoriser l'exemple expérimental de la page 97. Cette dernière influence reste à tester.

## Citations : 13 fiches, 29 occurrences en échec, 26 textes distincts

Le contrôle actuel cherche une citation dans un seul élément Docling ou une ligne/cellule de tableau, avec seulement une tolérance aux espaces blancs. C'est une vérification de localisation, pas une preuve du sens de l'affirmation.

- Six occurrences deviennent des correspondances exactes dans un élément après retrait des seules balises. Exemple : `<text>(B) SDS-PAGE analysis</text>`. Ce test diagnostique ne modifie ni les résultats ni les approbations.
- Quatre autres occurrences deviennent des sous-chaînes exactes d'une concaténation globale après retrait des balises (Elution buffer et System, chacune deux fois). Cette concaténation sert uniquement au diagnostic : l'accepter comme preuve pourrait relier abusivement des pages ou des colonnes différentes.
- Les 19 autres occurrences présentent des causes parfois combinées : caractères de contrôle PDF rendus en texte `[U+0003]`/`[U+0007]`, étiquette et valeur séparées, marqueur de liste ajouté par le sérialiseur, changements de casse, reformulation ou suppression de mots.

Exemples vérifiés :

- `Column:` = `#/texts/4`, valeur = `#/texts/6` ; ce ne sont pas un élément contigu unique, et `Sample:` s'intercale dans l'ordre de lecture.
- Le sodium phosphate contient réellement un caractère U+0003 dans `#/texts/9`. Copier le texte affiché ou sa représentation échappée ne correspond plus au texte brut.
- `Pool eluted human MAb` diffère de `Pool eluted purified human MAb` dans `#/texts/48`.
- `backpressure` diffère de `back pressure` dans `#/texts/77`.
- Une citation de la figure retire `(SDS gel, lane 3)` avant le point final.
- `<ldiv><marker>1.</marker></ldiv>LMW markers` contient un numéro de liste ajouté par le sérialiseur ; enlever simplement les tags conserve `1.` qui n'existe pas dans l'élément `#/texts/46`.

Il ne faut donc ni appeler les 13 fiches des hallucinations, ni autoriser une correspondance approximative comme preuve. Les 16 fiches sans erreur de localisation nécessitent toujours une revue sémantique et des conditions.

## Décomposition des 55 min 49 s

| Étape | Temps observé |
|---|---:|
| Initialisation avant le début du pipeline natif | ~1 min 39 s |
| Conversion et préparation des chunks | ~46 s |
| Découverte initiale, 4 batches | ~14 min 08 s |
| Relecture de couverture, 1 batch | ~1 min 49 s |
| Remplissage, 30 jobs séquentiels | ~37 min 27 s |

Le remplissage représente environ 67 % du temps total. `dense_fill_nodes_cap=1` impose un appel par nœud, plus la racine. Les journaux montrent cinq batches de découverte en incluant la couverture, puis trente jobs de remplissage. La couverture dense est distincte du gleaning direct : `gleaning_enabled=false` ne la désactive pas. Les métadonnées ne montrent ni troncature ni batches de découverte en échec.

La conversion n'est pas le goulot principal. Un relevé ponctuel ne laissait que 0,5 Gio de RAM libre ; la pression mémoire est plausible mais sa contribution n'a pas été mesurée. Ne pas attribuer une durée précise au swap ni promettre un gain matériel. Il manque les tokens et durées prompt/génération par appel pour séparer leurs coûts.

## Corrections proposées, par priorité

1. **Preuves par références plutôt que citations régénérées.** Conserver `document.json` brut et ses empreintes. Produire une vue de texte destinée au modèle avec IDs d'éléments, paragraphes/phrases et correspondance des offsets vers le brut. Nettoyage limité, explicite et journalisé des contrôles de sérialisation. Le modèle sélectionne des IDs et, si nécessaire, des segments ; le code reconstruit les citations exactes et les coordonnées. Les preuves multi-éléments gardent leurs segments séparés et leurs rôles. Ne pas concaténer arbitrairement étiquette/valeur ou traverser des lignes de tableau. Une référence valide prouve la localisation seulement : la revue humaine reste obligatoire.

2. **Extraction des faits et relations dans un même petit contexte.** Conserver Docling pour la conversion et HybridChunker pour la structure. Pour ce schéma plat et ce petit modèle, tester une extraction directe par sous-section sémantique bornée plutôt qu'une découverte de nœuds suivie d'un remplissage individuel. Chaque sortie contient le symptôme, la cause/action explicitement citée, leurs conditions et les références de preuve. Un adaptateur attribue les IDs et construit les entités/relations canoniques. Le changement exige un orchestrateur de sections et ne se résume pas à remplacer `dense` par `direct` sur le PDF entier. Le budget de sortie de 2048 tokens peut être insuffisant pour tout le document.

3. **Ontologie et consignes compactes.** Définir chaque classe et chaque prédicat dans les descriptions réellement transmises au modèle. Exclure figures, instruments, marqueurs et tampons des classes métier qui ne les décrivent pas ; ne pas créer des classes supplémentaires sans besoin de recherche. Exemple de cible à vérifier manuellement : augmentation de contre-pression → nettoyage, ou symptôme → encrassement → nettoyage lorsque les passages soutiennent réellement ces liens. L'énoncé de nettoyage ne doit pas être transformé en diagnostic certain. Décider explicitement si une relation Symptom→Action est utile : le schéma actuel ne la permet pas directement. Préserver les distinctions entre les conditions de la figure et celles du protocole (notamment pH 7,4 et 7,2).

4. **Conserver le chunking documentaire/hierarchique.** Ajouter à chaque chunk le produit/section parent et les conditions pertinentes, sans répéter toute la figure initiale. Garder avertissements et étapes associées ensemble ; garder les tableaux avec leurs en-têtes et relations spatiales. Détecter les limites de produit, notamment MabSelect SuRe LX en fin de page. Limite en tokens calculée sur la totalité de la requête avec marge de sortie, pas seulement sur le texte et un proxy cl100k. Ne pas augmenter aveuglément la taille des chunks.

5. **Limiter et mesurer les appels.** Réutiliser la conversion immuable ; terminer le processus de conversion avant de charger le modèle d'extraction pour libérer les poids OCR/layout. Cache par empreinte PDF + versions + conversion + schéma + consignes + modèle + paramètres. Limites du nombre d'appels, temps total et tokens ; erreurs explicites et reprise des sections manquantes. Tracer par appel durée totale, chargement, prompt, génération, tokens, débit, section, tentative et validation ; distinguer zéro frais API locaux et consommation de ressources. Garder un seul worker CPU dans un premier temps.

6. **Comparaison dense minimale si nécessaire.** Tester `dense_fill_nodes_cap=3`, contexte scoped et descriptions corrigées sur un contexte réduit. Avec exactement les mêmes 29 entités et une racine, cela donnerait 11 jobs de remplissage au lieu de 30, donc environ 16 jobs au total si les cinq batches de découverte restaient identiques. C'est un calcul de jobs, pas une prédiction de durée : les sorties seront plus longues, les contextes peuvent grandir et il faut vérifier la troncature. Cela ne corrige pas à lui seul la découverte des relations. Éviter la déduplication LLM et le parallélisme comme premiers leviers sur ce PC.

## Protocole de validation avant toute nouvelle extraction complète

Commencer avec les deux paragraphes CIP de la page originale 99, en réutilisant la conversion existante. Établir une petite référence humaine avec chaque fait/relation attendu et sa preuve exacte ; les propositions préparées automatiquement restent non validées jusqu'à confirmation par le lecteur.

Comparer même modèle, même contexte et même référence : mode actuel, dense compact, extraction directe structurée par section. Instrumenter chaque appel, poser un budget explicite (par exemple trois appels maximum et dix minutes pour ce micro-test, arrêt si dépassé). Vérifier précision/rappel des relations, types, directions, conditions, entités parasites, taux de références résolues, tokens et durée. Toutes les preuves des fiches proposées à l'approbation doivent être localisées ; aucun gain de vitesse ne compense une perte de fidélité. Un LLM-as-a-judge/RAGAS peut compléter les contrôles, mais ne constitue pas la référence de vérité de cette extraction.

Ensuite seulement, comparer sur les trois pages, y compris figures, tampons et conditions divergentes. Aucun gain de durée n'a encore été mesuré pour les corrections proposées ; ne pas annoncer une réduction garantie à un nombre de minutes.

## Sources vérifiées

- Sources locales : `ingestion/schema.py`, `ingestion/pipeline.py`, `ingestion/evidence.py`, sortie `extraction.json`, `document.json`, `provenance.json`, métadonnées natives et `tmp/cytiva-first-extraction.log`.
- Code de la dépendance installée, révision épinglée : `docling_graph/core/extractors/contracts/dense/{catalog,prompts,orchestrator}.py` et `docling_graph/config.py`.
- Documentation officielle, contexte général (la version installée prime) : https://github.com/docling-project/docling-graph/blob/main/docs/fundamentals/extraction-process/dense-extraction.md ; https://github.com/docling-project/docling-graph/blob/main/docs/reference/config.md
