# Cytiva r2 — revue documentaire de développement

Revue terminée le 20 octobre 2026, manuel CY13981-25Jan21-HB, pages 100–102.
**33 claims : 19 validés, 14 validés avec réserve, 0 en attente.**

Ce dossier est un export sélectionné des résultats locaux, autorisé pour préparer
leur versionnement. Il ne remplace ni le paquet source gelé ni les journaux locaux.
Il ne contient aucun PDF, conversion complète, conversation, chemin personnel ou
secret. Le texte des énoncés dérivés du manuel demeure dans le candidat.

| Fichier | Rôle |
|---|---|
| `claims.json` | Candidat corrigé v5, 47 entités et 33 claims ; seules les fins de ligne sont normalisées pour Git |
| `review.json` | 33 décisions humaines, empreintes par claim et réserves conservées |
| `manifest.json` | Empreintes, provenance des preuves sans leur texte, filiation, corrections et contrôles |

## Vérification sans modèle ni API

Depuis la racine du dépôt, avec les dépendances Python du contrat v0.2 :

```powershell
& '.\.venv-ingestion\Scripts\python.exe' -m experiments.cytiva.verify_review_package
& '.\.venv-ingestion\Scripts\python.exe' -m unittest experiments.cytiva.test_review_package -v
```

Le premier contrôle vérifie les fichiers, les 33 liens claim-décision, les réserves,
les références dans l’index de provenance et les sondes de conditions. Il ne rejoue
pas la validation lexicale des preuves : le corpus source complet n’est pas distribué.

Pour la rejouer avec le paquet local original (empreinte exacte obligatoire) :

```powershell
& '.\.venv-ingestion\Scripts\python.exe' -m experiments.cytiva.verify_review_package --corpus 'data/experiments/cytiva/pages-100-102-v02-r2/input.json'
```

Les empreintes détectent les incohérences ; elles ne sont pas une signature
cryptographique d’identité du réviseur. Git conserve l’historique du présent export.
Les empreintes des fichiers de ce paquet sont calculées en UTF-8 avec fins de ligne
LF : un checkout Windows en CRLF ne change pas leur identité. Les empreintes des
artefacts locaux et du corpus restent celles de leurs octets originaux. L’empreinte
du candidat local d’origine est conservée séparément ; les empreintes des claims
et toutes les décisions humaines restent inchangées.
Les messages humains et les versions intermédiaires restent dans le journal local
dont l’empreinte figure dans le manifeste. Aucun contrôle ne publie les claims.

## Corrections et limites

Une génération GPT-6.1 Sol, effort moyen, via abonnement a produit 32 claims.
La revue a corrigé la portée de c16 et séparé sa cible de pH dans c33. Les autres
corrections concernent le choix du matériel, les conditions, les modalités et la
représentation des alternatives/répétitions. Les précisions éditoriales de c1, c13
et c23 ont été retirées des énoncés et conservées dans `manifest.json` comme notes
de revue, distinctes des affirmations du manuel.

Les 14 réserves sont intégralement conservées dans `review.json` :

| Claims | Limite principale |
|---|---|
| c3, c4 | Choix du matériel conjoint ; interprétation des volumes |
| c7, c27, c28 | Répétitions et instructions composées non exécutables automatiquement |
| c12, c13 | Conditions d’incubation propres à l’échantillon ; critères qualitatifs |
| c14, c16, c17 | Nécessité de l’action et/ou méthode non déterminables automatiquement |
| c18 | Fidélité documentaire, sans validation scientifique indépendante de la formulation |
| c31 | Choix explicite de répéter l’élution |
| c32 | Aucun dosage de neutralisation calculable avec ce seul claim |
| c33 | Cible de pH sans tolérance numérique ni règle automatique d’ajustement |

La réserve de c16 mentionne historiquement c33 « encore en attente » : c33 a depuis
été validé avec réserve. Le texte historique n’est pas réécrit ; la décision courante
de chaque claim est celle de sa propre entrée.

Les claims restent `review_required` dans le contrat de staging : les décisions
humaines sont séparées, sans état `approved` ajouté au schéma. La revue est complète,
mais `publication_allowed` reste faux. Ce paquet n’implémente pas l’adaptateur vers
la base de revue, la publication Neo4j ni les contraintes à l’exécution.

Ce sont des pages de développement déjà inspectées, surtout procédurales, sans
symptômes ni causes extraits. Il n’y a ni référence exhaustive des faits omis,
ni mesure de rappel/F1, ni test aveugle, ni validation scientifique indépendante.
Le coût API additionnel est nul ; l’interface d’abonnement ne fournit pas de mesure
fiable des tokens ou de la vitesse d’inférence. Les 13 sondes de conditions sont
des contrôles techniques, pas une preuve d’applicabilité au laboratoire.

Étapes suivantes : conserver les réserves dans le futur import/rendu, annoter la
couverture avant de mesurer le rappel et évaluer de nouveaux passages de dépannage.
La clôture de cette revue n’autorise pas de nouvel import, appel de modèle ou déploiement.
