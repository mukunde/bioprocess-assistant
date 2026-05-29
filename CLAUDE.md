# CLAUDE.md — Bioprocess Troubleshooting Assistant

Contexte persistant pour Claude Code. Lu à chaque session. Garder concis.

## Objectif du projet

Prototype d'assistant IA de troubleshooting pour la **chromatographie de capture sur Protein A** (opération unitaire downstream du bioprocédé). À partir d'un symptôme décrit en langage naturel, l'agent renvoie les causes probables et les actions correctives, **chaque réponse étant ancrée dans un knowledge graph et sourcée**.

C'est un démonstrateur pour un entretien (client : fabricant d'équipements de bioprocédé). Il sera aussi un repo GitHub vitrine. Priorité : un prototype léger qui **tourne de bout en bout**, pas l'exhaustivité.

## Décision d'architecture (voir ADR-001)

Agent LLM ancré sur un **knowledge graph Neo4j** comme source de vérité unique — pas de RAG vectoriel, pas de connaissance paramétrique. Raison : la connaissance de troubleshooting est causale (symptôme → causes → actions), et le contexte biopharma exige auditabilité + zéro hallucination. Le graphe détient la connaissance ; l'agent n'est qu'une interface en langage naturel par-dessus.

## Stack

- Python 3.11+
- **Neo4j AuraDB Free** (cloud, offre gratuite illimitée). Driver : `neo4j` (officiel Python). Repli possible vers Neo4j Community Edition en local.
- **Chainlit** pour l'UI conversationnelle.
- **Anthropic SDK** (`anthropic`) — agent Claude avec tool use. Modèle : un Claude récent (vérifier le nom de modèle courant dans la doc API).
- Config via variables d'environnement (`.env`) : `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`, `ANTHROPIC_API_KEY`. **Ne jamais committer le `.env`.**

## Modèle du graphe

Trois types de nœuds, deux relations :

- `(:Symptom {name, description, source})`
- `(:Cause {name, description, source})`
- `(:Action {name, description, source})`
- `(:Symptom)-[:INDICATES]->(:Cause)`
- `(:Cause)-[:RESOLVED_BY]->(:Action)`

Le champ `source` (note d'application / handbook d'origine) est obligatoire sur chaque nœud et doit remonter dans les réponses de l'agent. Cible de volume après épaississement : ~6 symptômes, ~12 causes, ~15 actions. Sources publiques uniquement (handbooks Protein A type Cytiva/Merck-Millipore). **Pas de niveau GxP — c'est un POC.**

## Contrat de l'agent (anti-hallucination — NON NÉGOCIABLE)

L'agent expose **un seul outil** : `query_graph(symptom: str)` qui traduit la requête en Cypher, récupère les causes classées + leurs actions, et renvoie un résultat structuré.

Règles du prompt système :
- Répondre **uniquement** à partir des données retournées par le graphe.
- **Citer la `source`** de chaque cause/action mentionnée.
- Si le graphe ne contient rien de pertinent, dire explicitement « je n'ai pas cette information dans ma base » — **ne jamais inventer**.
- Ton clair, structuré, pour un ingénieur procédé.

## Plan de build (walking skeleton / tracer bullet)

Construire dans cet ordre, valider chaque étape avant la suivante :

1. **Seed minimal + schéma** : script Cypher avec 1 symptôme, 2 causes, 2 actions (toutes sourcées). Vérifier le graphe dans le navigateur Neo4j.
2. **Balle traçante end-to-end** : agent Chainlit + outil `query_graph` + prompt anti-hallucination. Objectif : une question traverse le graphe et revient en réponse sourcée. C'est le « wow moment » à sécuriser en premier.
3. **Épaissir le graphe** jusqu'à la cible de volume.
4. **Polish** : soigner les 3 premières interactions, préparer 2-3 questions de démo qui marchent à coup sûr, faire une **capture vidéo de secours** (démo hors-ligne, wifi invité non fiable).

## Conventions

- Code commenté sobrement, noms explicites.
- README clair (setup Neo4j local, install, lancement Chainlit, requête d'exemple).
- Committer l'ADR-001 dans `/docs`.
- Garder l'architecture légère et réutilisable : la brique « agent + outil de requête sur graphe » doit pouvoir resservir pour d'autres usages (c'est un argument d'entretien : boîte à outils commune).

## Hors scope (ne pas faire)

- Pas d'authentification, pas de déploiement cloud, pas de CI/CD pour ce POC.
- Pas de RAG vectoriel (évolution future possible, en complément, pas maintenant).
- Pas de données internes réelles — sources publiques seulement.
