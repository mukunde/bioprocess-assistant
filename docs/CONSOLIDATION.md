# Consolidation en quatre lots — état et historique

**Les quatre lots et le README sont fusionnés dans `main`.** Les modifications documentaires post-fusion restent locales jusqu’à accord explicite pour un commit et un push.

| Livraison | État | Référence |
|---|---|---|
| Lot 1 | Fusionné | [PR #3](https://github.com/mukunde/bioprocess-assistant/pull/3) |
| Lot 2 | Fusionné | [PR #4](https://github.com/mukunde/bioprocess-assistant/pull/4) |
| Lot 3 | Fusionné | [PR #5](https://github.com/mukunde/bioprocess-assistant/pull/5) |
| Lot 4 | Fusionné, 23 fichiers | [PR #6](https://github.com/mukunde/bioprocess-assistant/pull/6), commit `0f76d14` |
| README | Fusionné séparément, un fichier | [PR #7](https://github.com/mukunde/bioprocess-assistant/pull/7), commit `521088a` |

Le README figurait dans la liste initiale du lot 4 ; il a été livré séparément et n’a pas été recommitté dans ce lot. La PR #6 contient les 22 autres fichiers initiaux et la mise à jour de compatibilité de `docs/CLAIM-CONTRACT-V02.md` avec les arguments du lanceur PDF. Le manifeste conserve ce périmètre dans `lot_4_delivery_files` ; `pending_review_files` est vide pour les quatre lots livrés.

Vérification finale de main au commit `937a656dc478e14c91f1c3e92321cf6f520a5e0a` : les cinq commits de livraison sont présents et le contenu attendu des 69 fichiers est confirmé. Les 106 tests principaux passent sur une copie propre ; les sept contrôles historiques passent avec le jeu local et sont ignorés sans ce jeu. Aucun appel modèle/API payant ni écriture de base pendant cette vérification. Détails locaux : `data/consolidation/main-final-verification.json`.

Les lots ont été intégrés dans l’ordre 1 → 2 → 3 → 4. Les listes initiales affectaient chaque fichier une seule fois ; les livraisons et la correction de compatibilité ci-dessus explicitent les écarts ultérieurs. Dans ce découpage initial, les règles d’exclusion relevaient du lot 2, le README et le plan général du lot 4 ; le README a ensuite été livré séparément. Les liens documentaires entre lots sont désormais disponibles sur main.

## Rangement effectué

| Contenu | Emplacement courant |
|---|---|
| Code applicatif et évaluations | fichiers existants, `grounding.py`, `eval/`, `tests/` |
| Ingestion et contrat de claims | `ingestion/`, `docs/INGESTION.md`, `docs/CLAIM-CONTRACT-V02.md` |
| Ontologie et exemples lisibles | `docs/ontology/` |
| Code des expérimentations | `experiments/cytiva/` |
| Rapports de diagnostic et comparaison | `docs/experiments/` |
| Plan actif unique | `docs/ROADMAP.md` |
| Revue méthodologique historique | `docs/decisions/2026-10-roadmap-review.md` |
| Résultats bruts des pages 97–99 | `data/experiments/cytiva/pages-097-099-v01/` (ignoré) |
| Archive non exécutée des pages 100–102 (ancien prompt) | `data/experiments/cytiva/pages-100-102-v02/` (ignoré) |
| Fiches de référence JSON | `data/experiments/cytiva/reference-v01/` (ignoré) |
| Checkout Docling Graph de consultation | `.local-tools/docling-graph-reference/` (ignoré) |
| Inventaire, empreintes et journal des déplacements | `data/consolidation/` (ignoré) |

## Doublons et recouvrements

- **Doublon exact confirmé :** ancien `resultat-sonnet.json` identique à `resultat-sonnet-original.json`. L’original est la référence ; l’alias est conservé sous `archive/resultat-sonnet-alias.json`. Les scripts ne recréent plus cet alias.
- **Capture dégradée :** ancien `resultat-sonnet-brut.txt`, avec guillemets typographiques. Conservé sous `archive/resultat-sonnet-accessibility.txt`, exclu de la notation.
- **Roadmaps qui se recouvraient :** ROADMAP.md est le plan courant ; la revue française antérieure est une archive de décision, explicitement signalée.
- **Ontologie et schéma :** complémentaires, pas des doublons à supprimer. La première définit le sens métier ; le contrat v0.2 définit la sérialisation et ses contrôles.
- **Markdown et JSON de revue :** deux rendus à fonctions différentes, conservés. Les données complètes restent locales ; les rapports sélectionnés sont versionnables.
- Aucun original de modèle, PDF ou décision humaine n’a été supprimé ou réécrit. Les textes de navigation ont été adaptés aux nouveaux chemins. Les entrées figées et les réponses ont gardé leurs empreintes.

## Lots initiaux et messages de livraison

### Lot 1 — Fiabilité et évaluations (23 fichiers)

Message proposé :

```text
fix: enforce grounded answers and reliable evaluations

Render only validated graph selections, fail malformed evaluations and make seed loading additive and transactional. Preserve explicit refusal and threshold behavior.
```

Fichiers :

- `.chainlit/config.toml`
- `AGENTS.md`
- `CLAUDE.md`
- `agent.py`
- `app.py`
- `chainlit.md`
- `docs/ADR-001-knowledge-graph-grounding.md`
- `docs/ADR-002-multilingual-retrieval.md`
- `eval/README.md`
- `eval/cases.yaml`
- `eval/judge.py`
- `eval/requirements.txt`
- `eval/run_eval.py`
- `eval/threshold_sweep.py`
- `graph/schema.cypher`
- `graph/seed.cypher`
- `grounding.py`
- `scripts/load_graph.py`
- `tests/test_reliability.py`
- `tests/test_app.py`
- `tools.py`
- `compose.neo4j.yaml`
- `docs/LOCAL-NEO4J.md`

Vérifications :

- `python -m unittest discover -s tests -p test_reliability.py -v`
- `python -m unittest discover -s tests -p test_app.py -v`

### Lot 2 — Ingestion PDF, provenance et revue (15 fichiers)

Message proposé :

```text
feat: stage PDF extractions with provenance and manual review

Isolate the optional Docling Graph runtime, ground extraction evidence in immutable PDF conversions and require append-only manual review before exporting a separate evidence graph.
```

Fichiers :

- `.dockerignore`
- `.gitignore`
- `docs/INGESTION.md`
- `ingestion/__init__.py`
- `ingestion/__main__.py`
- `ingestion/evidence.py`
- `ingestion/local.example.json`
- `ingestion/pipeline.py`
- `ingestion/publish.py`
- `ingestion/review.html`
- `ingestion/review.py`
- `ingestion/schema.py`
- `ingestion/store.py`
- `requirements-ingestion.txt`
- `tests/test_ingestion.py`

Vérifications :

- `python -m unittest discover -s tests -p test_ingestion.py -v`

### Lot 3 — Ontologie, contrat v0.2 et quarantaine (8 fichiers)

Message proposé :

```text
feat: define versioned troubleshooting claims and source quarantine

Separate normative force, purpose, applicability and quantities. Validate evidence and typed conditions, block source conflicts per claim, and keep all candidates pending human review.
```

Fichiers :

- `docs/CLAIM-CONTRACT-V02.md`
- `docs/ontology/examples-v0.1.md`
- `docs/ontology/v0.1.md`
- `ingestion/claim_bundle.py`
- `ingestion/claim_contract.py`
- `ingestion/claim_prompt_v02.txt`
- `ingestion/claim_validation.py`
- `tests/test_claim_contract.py`

Vérifications :

- `python -m unittest discover -s tests -p test_claim_contract.py -v`

### Lot 4 — Expérimentations et documentation consolidées (liste initiale de 23 fichiers)

Message proposé :

```text
test: consolidate Cytiva experiments and prepare the v0.2 benchmark

Keep experiment tooling and curated reports in the repository, move local evidence into ignored data directories, archive duplicate captures and prepare a frozen new-page test without model calls.
```

Fichiers :

- `README.md`
- `docs/CONSOLIDATION.md`
- `docs/README.md`
- `docs/ROADMAP.md`
- `docs/commit-lots.json`
- `docs/decisions/2026-10-roadmap-review.md`
- `docs/experiments/cytiva-local-extraction-diagnostic.md`
- `docs/experiments/cytiva-v01-fidelity.md`
- `docs/experiments/cytiva-v01-results.md`
- `experiments/__init__.py`
- `experiments/cytiva/README.md`
- `experiments/cytiva/__init__.py`
- `experiments/cytiva/build_reference_cards.py`
- `experiments/cytiva/paths.py`
- `experiments/cytiva/requirements.txt`
- `experiments/cytiva/v01/__init__.py`
- `experiments/cytiva/v01/build_fidelity_audit.py`
- `experiments/cytiva/v01/check_result.py`
- `experiments/cytiva/v01/compare_saved.py`
- `experiments/cytiva/v01/prepare.py`
- `experiments/cytiva/v01/test_preparation.py`
- `ingestion/prepare_claim_test.py`
- `tests/test_experiment_preparation.py`

Vérifications :

- `python -m unittest discover -s tests -v`
- `python -m unittest discover -s experiments/cytiva/v01 -p test_*.py -v`

## Contre-revue du lot 4

- Audit historique lié aux empreintes exactes des réponses, corpus, prompt, extrait PDF et source-map : changement refusé avant écriture des verdicts.
- Génération des fiches uniquement dans un nouveau dossier `--output`, sans écrasement des annotations ni du document d’ontologie du dépôt.
- Métadonnées de document/version et justification des pages obligatoires, enregistrées comme fournies par l’opérateur ; date calculée en UTC. La reprise exige la même source, les mêmes pages et métadonnées.
- Ancien paquet `pages-100-102-v02` conservé sans changement ; nouvelle préparation `pages-100-102-v02-r2` à réaliser avec le prompt corrigé. Aucun nouveau modèle lancé.
- Suite actuelle : 106 tests principaux (34 fiabilité, 6 Chainlit, 29 ingestion, 29 contrat, 8 préparation/audit/fiches). Sept contrôles historiques supplémentaires utilisent le jeu local ; ils sont ignorés explicitement sans ce jeu. La contre-revue est conservée dans `data/consolidation/lot-4-fixed-review.json` ; la vérification après fusion est dans `data/consolidation/main-final-verification.json`.

## Validation historique (à ne pas confondre avec la suite actuelle)

Révision du lot 1 après intégration : gestion des pannes ajoutée dans `app.py`, six tests dans `tests/test_app.py`. Les 34 tests de fiabilité et les six tests applicatifs passent ; les 14 contrôles HTTP/callbacks Chainlit locaux passent avec modèle et résultats Neo4j simulés. À cette étape historique, l'intégration Neo4j réelle restait bloquée par la résolution DNS de l'hôte configuré. Aucun appel API payant, commit ni push.

Suite à la vérification de la console Aura, l'utilisateur a choisi Neo4j local dans Docker. Les 16 contrôles sur une base temporaire Neo4j Community 5.26.32 passent, dont les neuf cas lexicaux, l'idempotence et le rollback réel. L'aller-retour Chainlit emploie Neo4j réel et un modèle simulé. La base temporaire est supprimée ; `compose.neo4j.yaml` et `docs/LOCAL-NEO4J.md` décrivent la base de travail persistante. Le blocage de l'ancienne URI Aura ne bloque plus la validation locale. L'ancien graphe distant n'a pas été récupéré.

Lors de la consolidation initiale, chaque lot a été appliqué dans une copie jetable du dernier commit, sans création de commit ni modification de l’index. Résultats cumulés historiques, antérieurs à la correction des erreurs Chainlit :

| Copie vérifiée | Tests principaux | Résultat |
|---|---:|---|
| Lots 1 à 1 | 34 | OK |
| Lots 1 à 2 | 58 | OK |
| Lots 1 à 3 | 81 | OK |
| Lots 1 à 4 | 82 | OK |

Les sept contrôles historiques du comparatif passent aussi sur le jeu local. Les entrées figées v0.1/v0.2 et les réponses originales ont gardé leurs empreintes. Aucun nouveau modèle n’a été appelé. Les tests utilisent des mocks pour les modèles et la base ; les tests de revue HTTP restent locaux. Les liens Markdown locaux et la syntaxe Python ont été contrôlés.

## Hors des commits

Les manuels/PDF, conversions, réponses complètes, décisions de revue, modèles et outils locaux ne doivent pas être ajoutés à Git. Les exclusions ont été vérifiées ; ne pas utiliser `git add .` pour préparer cette série.

Le lot 4 garde uniquement les outils et rapports sélectionnés. Une nouvelle copie du dépôt n’aura pas les données privées : les tests principaux utilisent des fixtures synthétiques, les sept tests historiques savent signaler leur absence.

Les autres fichiers du dossier parent concernent un autre projet et n’ont pas été inclus. Les anciens répertoires devenus vides peuvent rester visibles sous OneDrive : Windows en a refusé la suppression ; ils ne contiennent plus les travaux déplacés et ne sont pas versionnables comme répertoires vides.

Le résultat des vérifications de consolidation est consigné localement dans `data/consolidation/validation.json` après leur exécution. Les listes machine se trouvent dans [commit-lots.json](commit-lots.json).
