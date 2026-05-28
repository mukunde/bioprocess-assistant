# ADR-001 — Ancrer mon agent de troubleshooting sur un knowledge graph

**Statut :** Accepté
**Date :** 2026-05
**Contexte projet :** Prototype d'assistant IA pour le troubleshooting de la chromatographie de capture sur Protein A (opération unitaire *downstream* du bioprocédé).

---

## Contexte

Je veux bâtir un démonstrateur d'assistant capable d'aider un ingénieur procédé à diagnostiquer un problème de capture Protein A : à partir d'un symptôme observé (« mon rendement de capture a chuté »), l'agent propose les causes probables et les actions correctives associées.

Le contexte d'usage que je vise est la biopharma, un environnement régulé. J'en tire trois contraintes qui dominent toutes les autres :

- **Auditabilité.** Chaque réponse doit pouvoir être tracée jusqu'à sa source. Une affirmation sans provenance est inexploitable.
- **Zéro hallucination tolérée.** Un agent qui invente une cause plausible mais fausse est pire qu'inutile : il est dangereux.
- **Extensibilité par les experts métier.** La connaissance doit pouvoir s'enrichir au contact des ingénieurs bioprocédé, sans réécrire le système.

**Mon hypothèse la plus risquée (RAT) :** un agent peut-il produire une réponse qu'un ingénieur bioprocédé jugerait crédible et non hallucinée, avec ses sources ? C'est l'hypothèse que ce prototype existe pour valider. Pour moi, tout le reste (UI, volume du graphe) est secondaire.

## Options considérées

1. **LLM seul (connaissance paramétrique).** L'agent répond depuis ce qu'il a appris à l'entraînement.
   *Rejeté :* aucune traçabilité, hallucinations non bornées, connaissance figée et non auditable. Disqualifiant en contexte régulé.

2. **RAG vectoriel sur documents.** On indexe des notes d'application, l'agent récupère les chunks proches sémantiquement de la question.
   *Rejeté comme socle :* le RAG vectoriel renvoie des fragments de texte sans structure causale explicite. Or la connaissance de troubleshooting est intrinsèquement relationnelle — un symptôme a *plusieurs* causes, une cause a *plusieurs* actions. Le découpage en chunks casse ces relations et peut mélanger des sources sans que l'agent en ait conscience.

3. **Knowledge graph structuré (retenu).** Je modélise explicitement la connaissance en `Symptôme → Cause → Action`, je la stocke dans Neo4j, et l'agent l'interroge via un outil dédié.

## Décision

J'ancre l'agent sur un **knowledge graph Neo4j** comme source de vérité unique.

- **Hébergement : Neo4j AuraDB Free.** Offre gratuite sans limite de durée, largement dimensionnée pour le volume cible du POC (~6 symptômes / ~12 causes / ~15 actions, vs. 200k nœuds autorisés). Ça m'évite l'install locale et rend la base accessible depuis n'importe quelle machine. Je note qu'AuraDB Free met l'instance en pause après ~3 jours d'inactivité — réveillable en un clic, mais à prendre en compte côté démo (la vidéo de secours déjà prévue couvre ce risque).
- **Un seul outil exposé à l'agent**, `interroger_graphe(symptôme)`, qui traduit la question en requête Cypher et renvoie les causes classées et leurs actions correctives.
- **Prompt système strict.** J'impose la règle suivante : **répondre uniquement à partir du graphe, citer la source de chaque nœud, et déclarer explicitement « je n'ai pas cette information » hors périmètre.** Mon ancrage anti-hallucination tient dans cette contrainte.
- **Chaque nœud porte un champ `source`** (la note d'application d'origine), que je fais remonter dans la réponse.

Le modèle relationnel correspond à la nature causale du domaine : c'est le graphe, pas l'agent, qui détient la connaissance. Mon agent n'est qu'une interface en langage naturel par-dessus une vérité structurée et auditable.

## Conséquences

**Positives**
- Auditabilité native : chaque réponse remonte à une source identifiée.
- Anti-hallucination par construction : l'agent ne peut affirmer que ce que le graphe contient.
- Extensible : les experts métier enrichissent le graphe (nœuds, relations, sources) sans toucher au code.
- Les relations causales — le cœur du raisonnement de troubleshooting — sont explicites et requêtables.

**Limites assumées**
- La qualité des réponses dépend entièrement de la curation du graphe : *garbage in, garbage out*.
- Je restreins volontairement le périmètre initial à une seule opération unitaire (capture Protein A).
- Je m'appuie uniquement sur des **sources publiques** (handbooks et notes d'application), pas sur des données internes. C'est une preuve de concept, **pas un système de niveau GxP**.
- Dépendance à AuraDB Free : si Neo4j change les conditions de l'offre gratuite, je bascule sur Neo4j Community en local (seul l'URI change, le reste du code agent reste identique).

**Dette / évolutions futures**
- L'extension à d'autres opérations unitaires posera la question de l'**alignement d'entités** entre représentations (cf. le pattern ChatP&ID pour la topologie d'installation + une couche ontologique type Fabric IQ pour l'état opérationnel). C'est un vrai travail d'architecture, à ne pas sous-estimer — et c'est exactement pourquoi je le laisse hors scope ici.
- Une couche RAG vectoriel pourra *compléter* le graphe pour les questions ouvertes non couvertes par le modèle relationnel — en complément, jamais en remplacement de la vérité structurée.
