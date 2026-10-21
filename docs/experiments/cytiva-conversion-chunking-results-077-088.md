# Cytiva 77 et 88 : premier comparatif conversion et chunking

Date : 2026-10-21. **Diagnostic technique exécuté ; validation humaine et publication non autorisées.** Le test suit le [protocole](cytiva-conversion-chunking-protocol.md) sur deux blocs séparés. Référence transcrite par l'assistant depuis les rendus avant conversion, gelée localement, en attente de confirmation utilisateur. Les autres pages et K600/K1400 n'ont pas été exécutés.

## Conclusion

Activer TableFormer améliore fortement la structure. **Le profil T1 n'est cependant pas validé globalement** : la ligne « Available formats » de la page 88 est incorrectement regroupée dans une seule cellule produit. Le tableau reste en quarantaine. À 800 tokens, aucune perte supplémentaire des cellules converties ni des notes ciblées n'a été observée sur ces deux pages ; cela ne corrige pas une conversion erronée.

## Conditions et traçabilité

- Source : SHA-256 `a6fd949e904ec0bafbcc7d85a3be1660f2bea8949098e86c57ae43d06492946a`, 183 pages. Extraits indépendants de 77 et 88 ; page locale 1 reliée à la page originale dans chaque carte source.
- Docling 2.140.0, docling-core 2.101.1, Docling Graph 1.9.1 au commit épinglé par le projet, tiktoken 0.12.0, pypdf 6.21.1 ; poids locaux layout Heron et TableFormer V1 `accurate`, cell matching activé pour T1. CPU, quatre threads, OCR désactivé, images conservées à l'échelle 2.
- T0 : reconnaissance de structure désactivée ; T1 : activée. Le reste du profil est identique. Chaque conversion utilise un processus distinct, avec démarrage/imports comptés.
- K0 : DocLang complet ; K800 : HybridChunker natif via Docling Graph, tiktoken `cl100k_base`, `merge_peers=True`, format DocLang sans géométrie dans le texte. Même JSON T1 gelé pour le diagnostic.
- Aucun extracteur LLM, aucune API payante et aucune base Neo4j appelée. Aucun téléchargement : caches vérifiés ; zéro tentative réseau dans les journaux des workers sous garde Python. Ce mécanisme n'est pas un pare-feu pour code natif.

Artefacts complets locaux et ignorés sous `data/experiments/cytiva/visual-validation-v01/` : `reference-20261021/`, `convert-20261021-a/`, `chunks-20261021-a/`, `conversion-checks-20261021.json`, `chunk-checks-20261021.json`, `review-20261021.csv` et les revues de conversion versionnées. PDF, rendus, cellules complètes et sorties ne sont pas distribués par ce rapport.

## Conversion : observations

| Vérification | T0 | T1 |
|---|---|---|
| Page 77, tableau 3.5 | Une seule cellule contenant le texte aplati | 17 lignes dont l'en-tête, 4 colonnes |
| Page 88, tableau 3.6 | Une seule cellule contenant le texte aplati | 8 lignes dont l'en-tête, 5 colonnes |
| Légende/titre des deux tableaux | Présents | Présents et références résolues |
| Cellules, unités et notes ciblées | Texte parfois présent, structure insuffisante | Fort gain, avec les réserves ci-dessous |

**Page 77 :** comparaison de 48 champs sur les 16 lignes de données : 16 sous-classes et 32 champs de pH. Après normalisation déclarée des espaces des sous-classes, 46 correspondent exactement et deux `n.a.` ont perdu le point final. Aucune modification de valeur numérique ou d'opérateur observée sur ces champs. Les 10 cellules d'espèce laissées vides dans les lignes de continuation restent vides : le format ne fournit pas une relation explicite de portée vers chaque sous-classe. Ne pas remplir automatiquement tous les blancs par la valeur précédente sans une règle documentaire revue. Les remarques à droite restent du texte distinct, y compris la réserve sur la protéine libre et le matériau couplé.

**Page 88 :** les 12 contrôles ciblés sur les quatre capacités avec leurs marqueurs de note, les quatre vitesses et les quatre tailles de particules correspondent. Les cinq notes sont présentes et rattachées au tableau par références. Les réactifs CIP des deux familles restent distincts dans les cellules examinées. Mais la dernière ligne concatène les quatre textes de formats dans la cellule du premier produit et laisse les trois suivantes vides : **F01, défaut bloquant d'association entre colonnes**, repéré à l'examen au-delà des sondes initiales. La superposition des boîtes de cellules sur le rendu confirme ce regroupement incorrect.

Une première note de diagnostic a suspecté un caractère de remplacement dans l'unité de température de la note 4 à cause de l'affichage console. L'inspection UTF-8 et des points de code confirme que le signe degré U+00B0 est intact. Cette suspicion est retirée dans `conversion-review-20261021-v2.json`, qui conserve le lien à la version initiale. Elle ne compte pas comme erreur de conversion.

## Chunking : observations

| Mesure | Page 77 | Page 88 |
|---|---:|---:|
| K0, tokens DocLang complet | 1 469 | 1 003 |
| K800, chunks finaux | 2 | 2 |
| Tokens totaux des chunks contextualisés | 1 174 | 808 |
| Maximum par chunk | 760 | 793 |
| Découpes textuelles secondaires | 0 | 0 |
| Notes du tableau 3.6 dans son chunk | Sans objet | 5 sur 5 |

Les 58 cellules non vides converties de la page 77 et les 35 de la page 88 se retrouvent dans le chunk contenant leur tableau. **Cela mesure la préservation de la conversion, pas sa fidélité au PDF** : F01 reste présent dans K0 et K800. La page 77 garde sa première réserve d'applicabilité dans le même chunk que le tableau. Les en-têtes et les conditions ciblées sont présents ; les deux blocs ne sont jamais fusionnés.

Tous les item_refs vérifiés se résolvent ; les cartes de pages et les empreintes de conversion correspondent. Les 10 entrées de géométrie des chunks de 77 et les 8 de 88 se résolvent avec des boîtes dans les dimensions des pages. Les overlays de cellules ont été examinés. Les empreintes textuelles natives sont BLAKE2b sur 8 octets ; l'identité des fichiers est suivie séparément par SHA-256.

La différence de tokens entre K0 et les chunks inclut leur sérialisation et contextualisation différentes ; ce n'est pas un taux de compression ni, à elle seule, une mesure d'omission. L'audit compare les cellules et les notes. Le mécanisme de seconde découpe n'a pas été exercé ; sa sécurité sur des tableaux plus grands n'est pas démontrée.

## Temps et ressources

| Bloc/profil | Temps worker complet | Imports/préparation | Conversion, dont chargement différé des modèles |
|---|---:|---:|---:|
| 77/T0 | 123,0 s | 89,6 s | 30,6 s |
| 77/T1 | 79,2 s | 48,6 s | 27,9 s |
| 88/T0 | 51,1 s | 36,3 s | 12,8 s |
| 88/T1 | 52,0 s | 32,3 s | 17,5 s |

Total des quatre workers de conversion : **305,3 s**. Pic mémoire échantillonné processus et enfants : environ **1,15 Go décimal**. Ces premiers passages, avec caches système évoluant et export d'images, ne constituent pas une mesure contrôlée de surcoût de TableFormer : ne pas conclure qu'il accélère la conversion parce que 77/T1 est plus rapide que 77/T0.

Chunking : environ 79,4 s et 52,3 s imports compris ; traitement des deux passes (chunks bruts et voie native) de 0,086 s et 0,040 s. Le démarrage domine ces mesures. Aucun coût API. Ces durées **ne se comparent pas directement aux 56 minutes d'extraction LLM antérieure**, qui incluait d'autres traitements et appels.

## Décisions et prochaine expérience

- 11 sondes ciblées examinées techniquement : 10 satisfaites sur T1/K800, une ambiguë sur la portée d'espèce (V01). Les 21 sondes des autres pages restent non exécutées. F01 est un défaut supplémentaire hors de ces 11 sondes ; leur score ne permet donc pas d'approuver le tableau.
- Aucun résultat n'est une décision utilisateur. La grille locale reste `pending_user_review` ; le modèle CSV versionné conserve ses valeurs initiales en attente.
- Conserver 800 comme point de départ expérimental sur ces deux pages ; aucun motif mesuré pour changer globalement le budget à ce stade.
- Comparer ensuite, sur une **nouvelle** exécution, le cell matching activé/désactivé pour la page 88 : le regroupement actuel pourrait venir de la correspondance aux cellules PDF, mais cette cause reste une hypothèse. Ne pas modifier T1 ni ses sorties.
- Avant toute extraction de faits concernés par F01 : corriger puis revoir la ligne, ou la maintenir explicitement en quarantaine. Aucun remplissage automatique des trois cellules vides.
- Traiter séparément les groupes d'espèces et leur portée. Poursuivre ensuite sur 104 et 152–153 ; K600/K1400 et la seconde découpe seront évalués dans une tranche distincte. Les figures et leurs relations visuelles ne sont pas validées par ce test de tableaux.

## Vérification du lanceur

Six tests de sécurité sans modèles : sorties préservées, blocs non contigus séparés, rejet d'une revue sans inspection ou d'empreintes modifiées, absence d'approbation humaine implicite, blocage DNS avant réseau, rejet d'un autre manuel avant chargement des modèles. La suite principale avec les dépendances applicatives/PDF locales a passé **112 tests**, avec modèles/API externes simulés et serveurs HTTP de revue uniquement locaux. Les environnements applicatif et ingestion étant isolés, le contrôle complet réutilise leurs dépendances déjà installées ; il n'installe aucun paquet.
