# Bioprocess Troubleshooting Assistant

Démonstrateur d'assistant IA spécialisé sur le **troubleshooting de la chromatographie de capture sur Protein A** (étape downstream du bioprocédé).

## Comment ça marche

Décris un symptôme observé sur ton étape de capture. L'assistant te propose les causes probables et les actions correctives, **chacune sourcée sur un handbook public** - Cytiva *Affinity Chromatography Vol. 1: Antibodies Handbook* (CY13981-25Jan21-HB, 2021) et *MabSelect SuRe Data File* (CY12754-10Jul20-DF, 2020).

## Fonctionnement et limites

- **Réponse encadrée** : le modèle sélectionne des résultats du graphe. L'application vérifie cette sélection et affiche les faits et leurs citations. La pertinence du résultat et l'exactitude scientifique des connaissances demandent une validation métier.
- **Auditabilité native** : chaque cause et chaque action remontent à la page précise du PDF source.
- **Périmètre actuel** : 6 symptômes types de la capture Protein A - chute de rendement, pression élevée, agrégats dans le pool d'élution, leaching de Protein A, HCP résiduels, bioburden.

## Questions à essayer

- *« Mon rendement de capture a chuté, qu'est-ce qui peut le causer ? »*
- *« La pression de ma colonne est anormalement élevée. »*
- *« J'ai trop d'agrégats dans mon pool d'élution. »*
- *« Comment réduire le leaching de Protein A dans l'éluat ? »*
- *« J'ai des HCP résiduels au-dessus de la spec. »*
- *« J'ai détecté du bioburden dans ma colonne. »*

Formule ta question en français ou en anglais. Les titres et refus suivent ta langue ; les descriptions techniques restent en anglais, la langue du graphe.

---

*POC démonstrateur - sources publiques uniquement, pas un système de niveau GxP. Architecture détaillée dans `/docs/ADR-001-knowledge-graph-grounding.md`.*
