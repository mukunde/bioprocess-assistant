# Essai via abonnements — 19 octobre 2026

Rapport conservé de l’essai v0.1. Les artefacts bruts sont locaux sous `data/experiments/cytiva/pages-097-099-v01/` ; les outils sont dans [experiments/cytiva](../../experiments/cytiva/README.md). Le contrat courant est v0.2.

Une génération par modèle, dans deux nouvelles conversations Chrome, sur le même prompt comprenant les textes convertis des pages 97–99. Sonnet 5.5 et GPT‑6.1 Sol ont été sélectionnés avec l'effort « Moyen ». Aucun appel API, achat, commit ou push. Les réponses n'ont pas été réparées par une seconde génération.

| Contrôle local | Sonnet 5.5 | GPT‑6.1 Sol |
|---|---:|---:|
| JSON conforme au schéma | Oui | Oui |
| Entités | 29 | 29 |
| Propositions totales | 20 | 29 |
| Relations hors PROCEDURE | 14 | 10 |
| PROCEDURE | 6 | 19 |
| Références inexistantes détectées | 0 | 0 |
| Erreurs de types/direction détectées | 1 | 0 |

Sonnet c20 utilise RECOMMENDED_FOR avec une Cause comme objet ; l'ontologie exige un Symptom. Le modèle reconnaît ce choix dans ses uncertainties. Ne pas accepter cette proposition automatiquement. Le passage éventuel à une PROCEDURE avec objectif déclaré nécessite une revue, pas une correction silencieuse du résultat du test.

GPT‑6.1 Sol passe ces contrôles structurels. Son nombre supérieur de propositions vient surtout des procédures ; il ne démontre ni une meilleure précision ni une meilleure couverture du dépannage. L'existence de toutes les références signifie que les éléments cités sont retrouvables dans l'entrée, pas qu'ils justifient chaque affirmation.

## Fichiers et conservation

- `resultat-sonnet-original.json` : réponse copiée depuis Claude et enregistrée via le Bloc-notes, sans modification.
- `archive/resultat-sonnet-alias.json` : ancienne copie strictement identique, conservée pour traçabilité ; le vérificateur lit désormais directement l’original.
- `resultat-sol.json` : réponse copiée depuis ChatGPT Work et enregistrée via le Bloc-notes, sans modification.
- `verification-sonnet.json`, `verification-sol.json` : contrôles et textes des preuves résolues.
- `comparaison-structurelle.json` : tableau calculé ci-dessus.
- `execution-abonnements.json` : modèles, réglages, empreinte du prompt, liens des conversations et limites de mesure.
- `archive/resultat-sonnet-accessibility.txt` : première capture du texte d'accessibilité, avec guillemets typographiques ; ce fichier n'est pas l'original à évaluer.

Les huit fiches de référence restent des brouillons à valider. Aucun résultat n'est approuvé manuellement ni promu dans le graphe. La revue sémantique doit contrôler les quantités, conditions, modalités, frontières de produit et omissions, puis masquer autant que possible le nom du candidat pendant la notation.

Cet essai utilise les quotas des abonnements. Aucun coût API additionnel n'a été engagé. Les tokens facturables ne sont pas disponibles et les heures de fin observée incluent l'automatisation : aucune conclusion sur le coût API ou la vitesse relative. Le plafond de sortie de 8192 tokens prévu dans les requêtes API n'était pas imposable dans ces interfaces. Les instructions internes et la personnalisation des comptes ne sont pas contrôlées.

## Revue documentaire ajoutée

La revue par l’assistant des 49 propositions est disponible dans [le rapport de fidélité](cytiva-v01-fidelity.md). Les détails `AUDIT-DETAILLE.md` et `audit-fidelite.json` restent dans le dossier local de l’essai. Elle recommande provisoirement GPT‑6.1 Sol, avec corrections et quarantaine documentaire. Elle ne remplace pas les décisions humaines : aucun claim n’a été approuvé dans la base. Le présent document conserve le constat structurel initial.
