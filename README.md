# Bioprocess Troubleshooting Assistant

Démonstrateur d'assistant IA pour le **troubleshooting de la chromatographie de capture sur Protein A** (étape downstream du bioprocédé). À partir d'un symptôme décrit en langage naturel, l'agent renvoie les causes probables et les actions correctives - chaque réponse ancrée dans un knowledge graph et sourcée sur un handbook public.

Le projet valide une hypothèse simple : *peut-on produire un agent crédible pour un ingénieur procédé, avec citations vérifiables et zéro hallucination tolérée, dans le contexte régulé de la biopharma ?*

## Trois couches d'architecture cibles

Ce POC implémente uniquement la couche causale. Les deux autres sont l'évolution naturelle pour un usage industriel réel.

| Couche | Ce qu'elle modélise | Approche | Statut |
|---|---|---|---|
| **Causale** | Symptôme → Cause → Action | Knowledge graph Neo4j manuel + agent Claude | ✅ ce POC |
| **Topologique** | Équipements, connexions, instrumentation | Pattern ChatP&ID (extraction depuis P&ID) | À venir |
| **Opérationnelle** | Phases, états, KPI, alarmes | Ontologie type *Fabric IQ* sur data fabric industriel | À venir |

Le défi central pour passer d'un POC mono-couche à un système multi-couches est l'**alignement d'entités** : faire en sorte que la même colonne C-101 soit le même nœud (ou des nœuds explicitement liés) dans les trois couches, avec une identité partagée non ambiguë.

## Architecture du POC

Walking skeleton minimal en trois briques découplées :

1. **Knowledge graph Neo4j** (AuraDB Free) - connaissance métier modélisée comme `(:Symptom)-[:INDICATES]->(:Cause)-[:RESOLVED_BY]->(:Action)`. Chaque nœud porte un champ `source` obligatoire pointant vers une page précise d'un handbook public.
2. **Agent Claude** (Anthropic SDK, Sonnet 4.6) avec un seul outil exposé : `query_graph(symptom)`. Le prompt système impose : *répondre uniquement à partir des données retournées par l'outil, citer chaque source, déclarer explicitement « je n'ai pas cette information » hors périmètre.*
3. **UI Chainlit** qui route les messages utilisateur vers l'agent.

Le détail des choix d'architecture est dans [`docs/ADR-001-knowledge-graph-grounding.md`](docs/ADR-001-knowledge-graph-grounding.md).

## Stack

- Python 3.11+ (testé 3.10+)
- Neo4j AuraDB Free (offre gratuite illimitée, ~200k nœuds autorisés - largement au-dessus du besoin POC)
- Anthropic SDK + Claude Sonnet 4.6
- Chainlit pour l'UI conversationnelle
- Configuration via variables d'environnement (`.env`, non commité)

## Setup

### 1. Provisionner une instance Neo4j AuraDB Free

- Aller sur [console.neo4j.io](https://console.neo4j.io/), créer un compte
- Créer une instance **AuraDB Free**
- ⚠️ Le password n'est affiché qu'une seule fois à la création - sauvegarder le fichier `.txt` de connexion

### 2. Cloner et installer

```bash
git clone <ce-repo>
cd bioprocess-assistant
python3 -m venv .venv
source .venv/bin/activate          # sur Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurer

```bash
cp .env.example .env
```

Éditer `.env` avec les valeurs de l'instance AuraDB et la clé Anthropic (depuis [console.anthropic.com](https://console.anthropic.com)).

### 4. Charger le graphe

```bash
python scripts/load_graph.py
```

Le script applique le schéma (contraintes d'unicité + index full-text avec analyseur français) puis le seed (6 symptômes / 12 causes / 12 actions, tous sourcés). Il valide en sortie en affichant les 12 chemins causaux.

## Démarrer

```bash
chainlit run app.py -w
```

L'app s'ouvre sur [http://localhost:8000](http://localhost:8000).

Sous chaque réponse, l'UI affiche le **score Lucene du match** et le **seuil actuel**. Le seuil est ajustable en runtime via l'icône ⚙️ Settings dans la boîte de saisie - pratique en démo pour illustrer le trade-off précision / rappel (voir *Sous le capot* plus bas).

## Questions de démo

L'agent couvre six symptômes types de la capture Protein A :

- Chute du rendement de capture
- Pression élevée sur la colonne
- Agrégats / HMW dans le pool d'élution
- Fuite de Protein A (leaching) dans l'éluat
- HCP résiduels dans le pool d'élution
- Bioburden / contamination microbienne

Prompts qui marchent :

- *« Mon rendement de capture a chuté, qu'est-ce qui peut le causer ? »*
- *« La pression de ma colonne est anormalement élevée, comment je règle ça ? »*
- *« J'ai trop d'agrégats dans mon pool d'élution. »*

Pour stresser la garantie anti-hallucination - trois patterns de refus distincts, tous testés :

- *« J'ai un taux d'endotoxines élevé dans mon pool d'élution, comment je le réduis ? »* → **in-domain miss** : symptôme non couvert par le graphe, l'agent répond « Je n'ai pas cette information dans ma base de connaissance »
- *« Comment optimiser mon procédé d'ultrafiltration / diafiltration ? »* → **autre opération unitaire** : l'agent signale le hors-scope
- *« Quelle est la météo aujourd'hui ? »* → **hors sujet total** : l'agent refuse poliment

## Sous le capot - comment fonctionne le retrieval

### Matching : full-text Lucene avec analyseur français

Le knowledge graph est interrogé via un **index full-text Neo4j** posé sur `Symptom.name` et `Symptom.description`, avec l'**analyseur Lucene `french`** qui applique :

- Tokenization sur whitespace + ponctuation
- Suppression des stop-words français (`de`, `le`, `à`, `ou`, ...)
- Stemming (`rendement` ≡ `rendements` ; `chuter` ≡ `chuté` ≡ `chute`)
- Normalisation des accents

C'est ce qui permet à une question naturelle comme *« Mon rendement de capture a chuté »* de matcher le nœud `"Chute du rendement de capture"` sans formulation strictement identique.

### Score BM25 - pertinence d'un match

Chaque match reçoit un **score BM25** (algorithme par défaut de Lucene moderne), qui combine :

- **TF** (term frequency) - fréquence de chaque terme de la requête dans le document indexé
- **IDF** (inverse document frequency) - les termes rares pèsent plus que les communs
- **Normalisation de longueur** - les documents très longs sont légèrement pénalisés

En pratique sur ce graphe :

- *« rendement chute »* sur le nœud yield drop → 2 termes rares matchent → score ~5
- *« endotoxines pool »* sur le nœud HCP → 0 terme rare matche (`endotoxine` n'est dans aucun document), seul `pool` matche (terme commun) → score ~2

### Le seuil de match (`min_score`)

`query_graph` applique un **seuil minimum** (par défaut 2.5, ajustable via le slider Settings dans l'UI) :

- Score **≥** seuil → match retenu, l'outil retourne le nœud avec causes + actions
- Score **<** seuil → l'outil retourne `found: false`, l'agent applique la règle anti-hallucination

Le seuil 2.5 a été calibré empiriquement sur les 6 symptômes du graphe pour rejeter les faux positifs faibles (type endotoxines→HCP via mots-clés génériques partagés) sans rejeter les questions in-scope reformulées librement.

### Trois comportements distincts côté agent

Le prompt système (voir `agent.py`) ancre 4 règles, qui produisent trois comportements observables en démo :

| Cas | Mécanisme | Réponse |
|---|---|---|
| **Match valide** | Score BM25 ≥ seuil → tool retourne `found: true` | Causes + actions structurées avec citations des sources |
| **In-domain miss** | Tool retourne `found: false` (graphe ne contient rien au-dessus du seuil) | « Je n'ai pas cette information dans ma base de connaissance » (Règle 3) |
| **Hors périmètre** | LLM juge sémantiquement que la question sort du domaine (autre unit op, sujet non-troubleshooting) | « Cette question sort de mon périmètre » (Règle 4) |

La distinction in-domain miss vs hors périmètre repose sur **deux mécanismes différents** :

- **Score Lucene** déclenche la Règle 3 - décision *numérique* sur la qualité du match.
- **Jugement sémantique du LLM** déclenche la Règle 4 - décision *qualitative* sur la nature de la question.

Les deux peuvent coexister (une question hors périmètre ne match probablement rien non plus), mais le LLM prioritise la Règle 4 quand c'est sémantiquement net (par exemple *« quelle est la météo aujourd'hui ? »* est refusée comme hors périmètre avant même un appel au tool).

### Pourquoi un knowledge graph et pas un RAG vectoriel ?

Trois raisons (détails dans [`docs/ADR-001-knowledge-graph-grounding.md`](docs/ADR-001-knowledge-graph-grounding.md)) :

1. **Auditabilité** : chaque réponse remonte à une page identifiée d'un PDF, pas à un chunk parmi N
2. **Structure causale explicite** : `symptôme → cause → action` est une relation, pas une proximité sémantique
3. **Anti-hallucination par construction** : l'agent n'a accès au monde qu'au travers du tool ; il ne peut pas *« compléter avec ses connaissances générales »* sans violer le prompt système

## Limites assumées

- POC démonstrateur, **pas un système de niveau GxP**
- Périmètre restreint à **une seule opération unitaire** (capture Protein A)
- Sources publiques uniquement (handbooks Cytiva), pas de données internes
- AuraDB Free met l'instance en pause après quelques jours d'inactivité - réveillable en un clic depuis la console
- La qualité des réponses dépend entièrement de la curation du graphe : *garbage in, garbage out*

## Roadmap

- **Court terme** : épaissir le graphe avec d'autres handbooks publics (Merck-Millipore, Sartorius)
- **Moyen terme** : ajouter la couche **topologique** (pattern ChatP&ID - extraction de P&ID en KG)
- **Moyen terme** : ajouter la couche **opérationnelle** (ontologie sur data fabric industriel), avec gestion d'identité partagée entre couches
- **Évolution complémentaire possible** : couche RAG vectoriel par-dessus le graphe pour traiter les questions ouvertes non couvertes par le modèle relationnel - en complément, jamais en remplacement de la vérité structurée

## Structure du repo

```
bioprocess-assistant/
├── agent.py                                # boucle agent Claude + prompt anti-hallucination
├── app.py                                  # UI Chainlit
├── chainlit.md                             # welcome page Chainlit
├── tools.py                                # outil query_graph (full-text Neo4j)
├── requirements.txt
├── scripts/
│   └── load_graph.py                       # loader schema + seed Cypher (idempotent)
├── graph/
│   ├── schema.cypher                       # contraintes d'unicité + index full-text français
│   └── seed.cypher                         # 6 symptômes × 2 causes × 2 actions, sourcés
├── docs/
│   └── ADR-001-knowledge-graph-grounding.md  # décision d'architecture
├── references/                             # PDFs handbooks (gitignoré)
└── CLAUDE.md                               # contexte projet pour Claude Code
```

---

*Projet créé comme démonstrateur d'entretien - fabricant d'équipements de bioprocédé.*
