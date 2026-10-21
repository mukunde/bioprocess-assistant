# Cytiva : validation des tableaux, légendes, schémas et du chunking

Date : 2026-10-21. Statut : **première tranche exécutée sur 77 et 88 : T0/T1 et K0/K800 ; défaut bloquant en conversion, revue utilisateur en attente**. Voir le [rapport du premier essai](cytiva-conversion-chunking-results-077-088.md). Les autres pages et K600/K1400 restent non exécutés. Aucun appel LLM/API, aucune publication Neo4j et aucune modification du paquet r2.

## 1. Objectif et limites

Déterminer ce que le convertisseur conserve du PDF, puis ce que le chunker conserve de cette conversion. Ne pas confondre ces deux erreurs avec une erreur d'extraction d'un LLM. Cette phase ne lance pas `ingestion extract` : cette commande déclenche aussi l'extraction sémantique, inutile pour ce diagnostic.

Le test r2 désactivait `do_table_structure` et l'OCR. Il ne valide pas les tableaux ni l'interprétation des illustrations. Son profil reste gelé. Le pipeline local Docling Graph dispose de son propre chemin de conversion ; ne pas lui attribuer automatiquement les réglages du test r2.

Toutes les pages ci-dessous sont des données de **développement**. Leur examen et l'ajustement futur des réglages empêchent de les présenter comme un test indépendant. Ce protocole ne démontre ni aptitude industrielle ni validité scientifique des recommandations. Les tableaux choisis portent sur les propriétés, conditions et produits ; ils ne constituent pas une matrice complète symptôme/cause/action.

## 2. Source et sélection

Manuel local : `cytiva_affinity-chromatography-antibodies_hplc_technical-support.pdf`, 183 pages PDF, SHA-256 `a6fd949e904ec0bafbcc7d85a3be1660f2bea8949098e86c57ae43d06492946a`. Référence/version reprises du registre r2 : `CY13981-25Jan21-HB`, `25Jan21` ; ce sont des métadonnées documentaires déjà enregistrées, pas une nouvelle certification de l'édition.

Les numéros ci-dessous sont **des pages PDF comptées à partir de 1**. Les numéros imprimés visibles correspondent sur les huit pages sélectionnées. Pour une API indexée à zéro, soustraire 1 ; conserver les deux champs dans le manifeste. La sélection structurée est dans [cytiva-visual-validation-selection.json](cytiva-visual-validation-selection.json).

| Lot | Pages PDF / imprimées | Objet vérifié visuellement | Difficulté ciblée |
|---|---|---|---|
| Premier essai | 77 | Tableau 3.5 et remarques à droite | Espèce/sous-classe héritées, plages de pH, `≤`, `≥`, `Approx.`, `n.a.`, exception et limites d'applicabilité |
| Premier essai | 88 | Tableau 3.6 et cinq notes | Quatre produits voisins, unités, conditions expérimentales distinctes et renvois en exposant |
| Premier essai | 104 | Figure 3.29 et texte à gauche | Cinq chemins fragment → sous-type de chaîne → produit ; alternative distincte du produit recommandé |
| Premier essai | 152–153, ensemble | Tableau A1.7 et notes 1–3 | Continuation réelle, en-têtes répétés, variantes 1/5 mL, puces de compatibilité, cellules vides, `N/A` et notes |
| Complément | 53 | Tableau 3.1, légende des symboles et texte | Échelle `++++`/`++`/`—`, sous-classes et portée des mesures ; pas de score numérique inventé |
| Complément | 86 | Figure 3.22, légende et paragraphe | Quatre produits, trois séries de temps, axe et unités ; capture d'image distincte de lecture des barres |
| Complément | 142 | Figure 7.1 et texte | Processus à deux/trois étapes, alternatives parallèles, ordre, modes FT/B/E et annotation partagée |

Commencer par les cinq pages du premier essai. N'ajouter les trois compléments qu'après résolution des erreurs bloquantes. Ce choix couvre des formes de documents, pas un échantillon statistiquement représentatif du manuel entier.

Convertir des blocs séparés : `[77]`, `[88]`, `[104]`, `[152,153]`, puis `[53]`, `[86]`, `[142]`. Ne pas concaténer 77 et 88 comme si elles étaient contiguës. Ne pas fusionner des éléments de blocs différents. L'intégralité de chaque page est examinée pour l'ordre de lecture ; les sondes du manifeste sont une liste ciblée, non une annotation exhaustive de chaque cellule.

## 3. Référence humaine avant conversion

1. Vérifier l'empreinte du PDF, puis ouvrir les pages originales rendues. Utiliser Poppler ; les images d'inspection restent locales et ignorées. Augmenter la résolution si une unité ou une note est illisible.
2. Pour chaque sonde, relever la zone source et les valeurs/relations attendues sans regarder une conversion. Les attentes préparées dans le manifeste sont des **candidates à confirmer**, jamais des décisions déjà validées par l'utilisateur.
3. Dans les tableaux, identifier les cellules par en-têtes sémantiques et coordonnées de ligne/colonne, avec les cellules fusionnées et les champs hérités. Une cellule vide ne devient pas `false`, `0`, « identique à la précédente » ou `N/A` par défaut.
4. Dans un schéma, relever les boîtes, libellés, connexions dirigées et groupes. Garder séparés les chemins parallèles et les relations alternatives. Dans un graphique, annoter axes, unités, séries et légende ; ne pas lire des valeurs exactes à partir de la hauteur des barres.
5. Consigner ambiguïtés et contradictions éventuelles sans les résoudre par connaissance externe. Une note d'applicabilité n'est pas automatiquement un attribut de toutes les lignes voisines.
6. Geler les références locales par empreinte avant l'exécution. Toute correction ultérieure crée une nouvelle version, avec sa raison ; ne pas corriger une référence simplement pour faire passer un profil.

Utiliser [cytiva-visual-validation-review.csv](cytiva-visual-validation-review.csv) comme modèle de journal. Pour chaque exécution, copier ce modèle dans un nouveau dossier local, renseigner les identifiants de run et la référence gelée. Les décisions, captures et textes complets restent dans `data/experiments/cytiva/visual-validation-v01/<run-id>/`, jamais dans les fichiers versionnables de ce protocole.

## 4. Préparation et isolation

- PC de référence : i5-1135G7, 16 Go RAM, Iris Xe ; CPU, quatre threads. Figer Python, Docling, docling-core, docling-graph et leurs versions/commit installés dans le manifeste du run. Le profil historique utilisait Docling 2.140.0 et le projet épingle Docling Graph 1.9.1 au commit indiqué dans `requirements-ingestion.txt`.
- L'exécuteur **conversion/chunking uniquement** est disponible : `python -m experiments.cytiva.visual_validation`, avec commandes `convert` et `chunk` ; voir le [guide du lanceur](../../experiments/cytiva/README.md#local-table-conversion-and-chunking-no-llm). Il refuse un répertoire existant, un SHA source différent, des poids absents et les services distants ; tokenizer et sérialisation sont imposés. Ne pas présenter la commande historique `prepare_claim_test` comme capable d'activer les tableaux : ses réglages actuels les désactivent.
- Vérifier les options contre la version installée. Le profil T1 prévoit TableFormer V1, mode `accurate`, correspondance aux cellules PDF activée ; enregistrer la classe et le `kind` effectivement chargés. Ne pas basculer implicitement vers V2, un VLM ou un profil par défaut.
- Vérifier les poids de layout **et** de TableFormer, leurs empreintes et le cache tiktoken. Le préchargement historique du layout ne prouve pas la présence des poids de tableaux. En cas de manque : arrêter le prévol et identifier les fichiers ; tout téléchargement sera une étape distincte.
- Exécution locale sans réseau : caches préparés, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `HF_HUB_DISABLE_TELEMETRY=1`, `LITELLM_LOCAL_MODEL_COST_MAP=True`, aucun `DOCLING_SERVE_URL`, services distants désactivés. Ces variables ne prouvent pas seules l'isolation réseau : l'appliquer au processus si nécessaire.

## 5. Conversion : comparaison contrôlée

| Profil | Tableaux | OCR | Images | Usage |
|---|---|---|---|---|
| T0, témoin nouveau | Structure désactivée | Désactivé | Pages et figures conservées | Rejouer l'ablation sur ces mêmes pages, sans toucher à r2 |
| T1, candidat | Structure activée ; TableFormer V1 `accurate`, cell matching activé | Désactivé | Identique à T0 | Mesurer le gain réel de structure |
| T2, conditionnel | Identique à T1 | Activé avec moteur/version/langue explicites | Identique à T0 | Seulement si des caractères pertinents manquent ; comparaison séparée |

T0 et T1 partagent layout, CPU, ordre et blocs de pages, échelle des images fixée à 2, `generate_page_images=True`, `generate_picture_images=True`, description/classification d'images et enrichissements LLM désactivés. Exporter le document JSON complet, une représentation HTML/CSV des tableaux, le Markdown pour inspection, les figures recadrées et leurs références. Le Markdown seul ne fait pas référence pour les cellules fusionnées.

Une figure vectorielle doit rester vérifiable : si aucun PictureItem exploitable n'est créé, noter un échec de détection de figure et conserver la page rendue comme recours manuel. Ne pas compter cette page complète comme une figure correctement détectée/recadrée. Ne pas ajouter une description sémantique générée pour masquer une perte de conversion.

Pour chaque objet : vérifier texte et ordre, en-têtes et cellules, opérateurs/unités, lien titre/note, figure/légende, page et géométrie. Documenter le système de coordonnées, les dimensions et l'origine ; vérifier par superposition sur le rendu. Une simple présence du bon nombre quelque part dans la page ne valide pas son association.

## 6. Chunking : mesurer la perte après une conversion gelée

Ne chunker que des blocs dont T1 a été examiné ; bloquer les unités incorrectes ou ambiguës. Utiliser le **même JSON de conversion par bloc** pour toutes les variantes : aucun nouvel appel de conversion pendant le comparatif.

Un bloc incorrect peut être chunké uniquement pour diagnostiquer une perte supplémentaire, avec le statut explicite `quarantined_diagnostic_only` et une revue liée à l'empreinte exacte du JSON. Ce diagnostic ne rend pas le bloc admissible à l'extraction ou à la publication. Le lanceur n'infère aucune approbation humaine.

| Variante | Rôle |
|---|---|
| K0 | Sérialisation du bloc entier sans découpage ; témoin de préservation, pas une entrée LLM supposée compatible avec son contexte |
| K600 | HybridChunker structurel/hiérarchique, plafond 600 tokens |
| K800 | Même réglage, plafond 800 tokens ; correspond au budget local actuel |
| K1400 | Même réglage, plafond 1400 tokens ; observer le compromis contexte/taille |

Conserver `merge_peers=True`, format **DocLang sans géométrie dans le texte**, tokenizer tiktoken `cl100k_base`, et le même fournisseur de sérialisation que la voie locale épinglée. Les valeurs sont des hypothèses, pas des optima. Cette grille inclut 800 pour le diagnostic actuel ; elle ne remplace pas le budget distinct des passages de recherche du protocole LightRAG.

Tester le chunker **effectivement utilisé**, y compris la seconde découpe textuelle de Docling Graph, pas seulement les morceaux bruts de HybridChunker. Enregistrer avant/après : texte, texte contextualisé, tokens, IDs de parents/enfants, titres, item_refs, toutes les pages, géométrie, empreintes et `resplit_of`. Les métadonnées héritées du parent après seconde découpe ne démontrent pas que chaque enfant contient la note, la cellule ou la preuve indiquée. Vérifier le sous-passage exact et toutes les entrées `prov`, pas uniquement `prov[0]`.

Vérifier pour chaque unité :

- produit/espèce/sous-classe + propriété + valeur/opérateur/unité + condition restent associés ;
- une ligne de tableau garde ses en-têtes, sa note et son contexte de portée ; une séparation en lignes peut être acceptable si ces liens sont conservés ;
- les notes externes et titres ne sont pas supposés automatiquement répétés : vérifier la sortie native puis, séparément, un éventuel assembleur de contexte ;
- la continuation 152→153 est explicitement reliée ; aucune contiguïté artificielle n'est créée entre blocs ;
- figure, légende et passage qui la cite restent reliés par des identifiants ; un chunk textuel qui omet l'image ne valide pas la transmission des relations visuelles à un LLM ;
- chaque enfant retrouve sa page/zone réelle ; la duplication d'en-têtes est autorisée, la création de faits ou les associations croisées ne le sont pas.

Rapporter **contexte natif** et **contexte reconstruit** séparément. Si un parent doit être réinjecté, conserver les références explicites, mesurer à nouveau le budget complet et déclarer la dépendance à un assembleur futur. Un ensemble de chunks qui contient collectivement la note n'est pas équivalent à une entrée modèle qui la reçoit effectivement.

K0 permet aussi de repérer une perte due à la sérialisation DocLang : si le JSON est correct mais K0 omet des relations de cellules ou des images, l'erreur précède le découpage. Aucun LLM ne peut reconstituer de manière garantie une information visuelle absente de son entrée.

## 7. Contrôles, mesures et décision

**Déterministes :** SHA des sources/artefacts ; correspondance pages PDF/extrait/imprimées ; existence et résolution des item_refs ; nombres et opérateurs exacts, unités conservées ; validité des liens explicites ; décompte des tokens du texte réellement sérialisé ; absence de lignes perdues/dupliquées et de fusions entre blocs. Comparer des cellules alignées aux références, pas un sac de mots. Toute normalisation est explicite et réversible ; ne pas transformer `n.a.` ou une approximation en mesure exacte.

**Manuels :** comparaison des objets convertis et des chunks à la page rendue ; associations de lignes, portée des notes, flèches, groupes et ambiguïtés. Un juge LLM n'est pas requis pour cette phase et ne remplace pas ces décisions. Les sondes du CSV restent `not_run` jusqu'à exécution, puis nécessitent `pass`, `fail`, `ambiguous` ou `not_applicable` avec justification et identité/date du réviseur.

Mesures à produire, avec numérateurs et dénominateurs par type de contenu :

- objets attendus retrouvés / objets attendus dans la référence gelée ;
- cellules sélectionnées correctes (valeur **et** en-têtes) / cellules sélectionnées vérifiées ;
- liens titre/note/figure corrects / liens annotés ; relations visuelles uniquement si une voie de représentation est effectivement testée ;
- unités critiques intactes dans l'entrée finale / unités critiques examinées, et unités à reconstruire ou en quarantaine ;
- ancres effectivement résolues / ancres vérifiées, avec distinction géométrie parent et localisation enfant ;
- nombre de chunks, total/max de tokens, duplications et surcoût de contextualisation ;
- temps de chargement, conversion, sérialisation et chunking séparés ; pic mémoire processus et enfants si mesurable, sinon `unknown` ; temps de revue humaine.

Ne pas appeler le résultat « rappel du manuel » : il s'agit d'une sélection de développement. Compter les sondes ambiguës et non exécutées à part ; ne pas les retirer silencieusement pour améliorer un taux. Rapporter les résultats par tableau/figure, même si un score agrégé paraît bon.

**Critères bloquants sur les unités destinées à une extraction ultérieure :** zéro association erronée entre produits/lignes, zéro nombre/opérateur/unité modifié, zéro note critique perdue, zéro relation visuelle inventée et 100 % des ancres nécessaires résolubles. Une unité peut être explicitement mise en quarantaine ; cela réduit la couverture et n'autorise pas à déclarer la configuration globalement validée. Le succès sur les sondes ne certifie pas les cellules non annotées.

Arrêter un essai à 15 minutes par bloc/profil de conversion ou à pression mémoire excessive ; consigner `timeout`/`resource_limit`, pas un résultat de qualité. Ces limites sont des garde-fous proposés, pas des performances mesurées. Ne répéter une mesure que pour départager des candidats sans erreur bloquante ; distinguer démarrage à froid et cache chaud. Les coûts API restent nuls, le temps CPU et la mémoire sont rapportés.

## 8. Livrables et suite

Dans un nouveau dossier local : manifeste et versions ; PDF/extraits et cartes de pages ; rendus ; profils effectifs et poids ; conversions gelées ; tableaux et figures ; références humaines ; sorties K0/K600/K800/K1400 ; journal CSV et rapport des défauts. Aucun PDF, capture ou corpus complet dans Git.

Premier passage : T0/T1 sur 77 et 88, puis 104 et le bloc 152–153 ; K0/K800 sur les conversions relues. Ensuite seulement comparer K600/K1400 et ajouter 53/86/142. Une interprétation des diagrammes par VLM est une expérience séparée, avec ses propres références et mesures ; elle ne fait pas partie de cette préparation.

Décisions possibles : retenir T1 et un budget de chunking ; corriger une perte de contexte dans un adaptateur ; utiliser des unités par lignes avec en-têtes répétés ; conserver une page/image entière comme support manuel ; ou mettre des objets en quarantaine. Une correction du code fera l'objet de tests de régression dédiés. Aucun claim n'est approuvé ni publié par ce protocole.
