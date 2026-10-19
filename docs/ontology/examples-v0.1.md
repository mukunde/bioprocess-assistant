# Fiches de vérification Cytiva — v0.1

**Toutes les fiches sont en attente.** Elles sont proposées par l’assistant ; les citations sont localisées automatiquement dans la conversion existante. Les pages PDF rendues 97–99 ont été inspectées visuellement pendant la préparation. Aucune approbation humaine n’est présumée.

Source : *Affinity Chromatography Vol. 1: Antibodies*, CY13981-25Jan21-HB. Pages originales/numéros imprimés 97–99 = pages 1–3 de l’extrait.

[Ouvrir l’extrait local des pages 97–99](<../../references/cytiva-hitrap-sure-pages-097-099.pdf>)

Périmètre commun proposé : **HiTrap MabSelect SuRe**. Vérifier le titre et l’introduction p.97 ; les sections p.98–99 se poursuivent jusqu’au nouveau titre « MabSelect SuRe LX ». Les preuves de ce périmètre sont conservées séparément dans le JSON.

Ordre de revue conseillé : **C04 → C01 → C07 → C08**, puis C02/C03/C05/C06. Pour chaque fiche, répondre approuvé / rejeté / à préciser, avec une note.

## C01 — Encrassement sévère → augmentation possible de contre-pression

**Statut : pending.** Modalité : `possible`.

Proposition : `cause:fouling` — `MAY_CAUSE` → `symptom:backpressure-increase`.

**Page 99** (extrait 3), élément `#/texts/77`, offsets `294:390` :

> If the fouling is severe, it can block the column, increase back pressure, and reduce flow rate.

Conditions / contexte : `fouling_severity` = `severe` (applicability)

**Point de vigilance :** Vérifier « severe » et « can ». Le symptôme seul ne prouve ni la présence ni la sévérité de cet encrassement.

- [ ] Citation et page vérifiées dans le PDF.
- [ ] Sens, direction, modalité et conditions fidèles.
- [ ] Périmètre produit vérifié.
- Décision : … ; note : …

## C02 — Encrassement sévère → diminution possible du débit

**Statut : pending.** Modalité : `possible`.

Proposition : `cause:fouling` — `MAY_CAUSE` → `symptom:flow-reduction`.

**Page 99** (extrait 3), élément `#/texts/77`, offsets `294:390` :

> If the fouling is severe, it can block the column, increase back pressure, and reduce flow rate.

Conditions / contexte : `fouling_severity` = `severe` (applicability)

**Point de vigilance :** Vérifier « severe » et « can ». Le symptôme seul ne prouve ni la présence ni la sévérité de cet encrassement.

- [ ] Citation et page vérifiées dans le PDF.
- [ ] Sens, direction, modalité et conditions fidèles.
- [ ] Périmètre produit vérifié.
- Décision : … ; note : …

## C03 — Encrassement sévère → obstruction possible de la colonne

**Statut : pending.** Modalité : `possible`.

Proposition : `cause:fouling` — `MAY_CAUSE` → `symptom:column-blockage`.

**Page 99** (extrait 3), élément `#/texts/77`, offsets `294:390` :

> If the fouling is severe, it can block the column, increase back pressure, and reduce flow rate.

Conditions / contexte : `fouling_severity` = `severe` (applicability)

**Point de vigilance :** Vérifier « severe » et « can ». Le symptôme seul ne prouve ni la présence ni la sévérité de cet encrassement.

- [ ] Citation et page vérifiées dans le PDF.
- [ ] Sens, direction, modalité et conditions fidèles.
- [ ] Périmètre produit vérifié.
- Décision : … ; note : …

## C04 — Nettoyer la colonne lorsque la contre-pression augmente

**Statut : pending.** Modalité : `recommended`.

Proposition : `action:clean-column` — `RECOMMENDED_FOR` → `symptom:backpressure-increase`.

**Page 99** (extrait 3), élément `#/texts/78`, offsets `153:224` :

> When an increase in backpressure is seen, the column should be cleaned.

Conditions / contexte : `observed_symptom` = `symptom:backpressure-increase` (trigger)

**Point de vigilance :** Pas de cause intermédiaire dans cette phrase. Elle ne prescrit pas à elle seule une concentration, une durée ou un seuil de pression.

- [ ] Citation et page vérifiées dans le PDF.
- [ ] Sens, direction, modalité et conditions fidèles.
- [ ] Périmètre produit vérifié.
- Décision : … ; note : …

## C05 — Le CIP peut retirer les substances ciblées du milieu

**Statut : pending.** Modalité : `possible`.

Proposition : `action:cip` — `CAN_REMOVE` → `cause:retained-substances`.

**Page 99** (extrait 3), élément `#/texts/77`, offsets `0:105` :

> CIP can be performed to remove very tightly bound, precipitated, or denatured substances from the medium.

Conditions / contexte : périmètre produit commun ; aucune condition supplémentaire ajoutée.

**Point de vigilance :** Conserver le « or » entre les catégories. Cette cible est un état candidat de la classe Cause ; aucun lien causal vers un symptôme n’est ajouté par cette fiche.

- [ ] Citation et page vérifiées dans le PDF.
- [ ] Sens, direction, modalité et conditions fidèles.
- [ ] Périmètre produit vérifié.
- Décision : … ; note : …

## C06 — Le CIP régulier prévient l’accumulation de contaminants

**Statut : pending.** Modalité : `source_assertion`.

Proposition : `action:cip` — `PREVENTS_BUILDUP_OF` → `cause:contaminant-buildup`.

**Page 99** (extrait 3), élément `#/texts/78`, offsets `0:152` :

> Regular CIP prevents the build-up of contaminants and helps to maintain the capacity, flow properties, and general performance of HiTrap MabSelect SuRe.

Conditions / contexte : `frequency` = `regular` (applicability)

**Point de vigilance :** Prévention d’une accumulation ; la fréquence reste qualitative. Aucune garantie individuelle ni fréquence par cycle n’est déduite.

- [ ] Citation et page vérifiées dans le PDF.
- [ ] Sens, direction, modalité et conditions fidèles.
- [ ] Périmètre produit vérifié.
- Décision : … ; note : …

## C07 — Paramètres du CIP de l’étape 9, si nécessaire après élution

**Statut : pending.** Modalité : `conditional_instruction`.

Proposition : `action:cip` — procédure contextualisée.

**Page 99** (extrait 3), élément `#/texts/72`, offsets `165:377` :

> If required, perform cleaning in place directly after elution with at least 2 column volumes of 0.1 to 0.5 M sodium hydroxide ensuring a contact time of 10 to 15 min. Wash with 5 column volumes of binding buffer.

Conditions / contexte : `cip_required` = `True` (applicability) ; `timing` = `directly_after_elution` (applicability)

Paramètres à vérifier :

```json
[
  {
    "name": "cip_reagent",
    "value": "sodium hydroxide",
    "evidence_item_refs": [
      "#/texts/72"
    ]
  },
  {
    "name": "cip_concentration",
    "min": 0.1,
    "max": 0.5,
    "unit": "M",
    "evidence_item_refs": [
      "#/texts/72"
    ]
  },
  {
    "name": "cip_volume",
    "operator": ">=",
    "value": 2,
    "unit": "column_volume",
    "evidence_item_refs": [
      "#/texts/72"
    ]
  },
  {
    "name": "contact_time",
    "min": 10,
    "max": 15,
    "unit": "min",
    "evidence_item_refs": [
      "#/texts/72"
    ]
  },
  {
    "name": "following_wash",
    "value": 5,
    "unit": "column_volume",
    "material": "binding buffer",
    "sequence": "after_CIP",
    "evidence_item_refs": [
      "#/texts/72"
    ]
  }
]
```

**Point de vigilance :** Vérifier tous les paramètres ensemble et le rinçage qui suit. « If required » n’a pas de critère défini ici. Ne pas déduire de C04 que ce protocole est automatiquement applicable.

- [ ] Citation et page vérifiées dans le PDF.
- [ ] Sens, direction, modalité et conditions fidèles.
- [ ] Périmètre produit vérifié.
- Décision : … ; note : …

## C08 — Préparer les tubes de collecte : quantité par millilitre de fraction

**Statut : pending.** Modalité : `instruction_with_stated_purpose`.

Proposition : `action:prepare-collection-tubes` — procédure contextualisée.

**Page 98** (extrait 2), élément `#/texts/59`, offsets `0:115` :

> Prepare collection tubes by adding 60 to 200 µL of 1 M Tris-HCl, pH 9.0 per milliliter of fraction to be collected.

**Page 98** (extrait 2), élément `#/texts/60`, offsets `0:198` :

> To preserve the activity of acid-labile IgG, we recommend adding 60 to 200 µL of 1 M Tris-HCl pH 9.0 to collection tubes, which ensures that the final pH of the sample will be approximately neutral.

Conditions / contexte : `antibody_property` = `acid_labile_IgG` (stated_purpose_context)

Paramètres à vérifier :

```json
[
  {
    "name": "added_Tris_volume_per_fraction_volume",
    "min": 60,
    "max": 200,
    "unit": "µL",
    "denominator": {
      "value": 1,
      "unit": "mL",
      "material": "fraction to be collected"
    },
    "evidence_item_refs": [
      "#/texts/59"
    ]
  },
  {
    "name": "Tris_HCl_concentration",
    "value": 1,
    "unit": "M",
    "evidence_item_refs": [
      "#/texts/59"
    ]
  },
  {
    "name": "Tris_HCl_pH",
    "value": 9.0,
    "unit": null,
    "evidence_item_refs": [
      "#/texts/59"
    ]
  },
  {
    "name": "stated_final_sample_pH",
    "value": "approximately neutral",
    "unit": null,
    "evidence_item_refs": [
      "#/texts/60"
    ]
  }
]
```

**Point de vigilance :** L’étape 1 fournit le dénominateur « per milliliter ». La note suivante donne le motif pour les IgG sensibles à l’acide ; ce motif n’est pas présenté comme une restriction exclusive de l’étape 1. Le pH 9,0 est celui du Tris, pas le pH final de la fraction.

- [ ] Citation et page vérifiées dans le PDF.
- [ ] Sens, direction, modalité et conditions fidèles.
- [ ] Périmètre produit vérifié.
- Décision : … ; note : …

## Contre-exemples à rejeter

- « Une contre-pression accrue prouve un encrassement sévère » : inversion abusive de C01.
- « Le nettoyage résout toujours la hausse de pression » : C04 ne garantit pas la résolution.
- « Utiliser exactement 2 mL de NaOH » : C07 parle d’au moins deux volumes de colonne.
- « Appliquer les paramètres C07 à MabSelect SuRe LX » : autre produit, instructions distinctes p.99.
- « Ajouter 60–200 µL au total, quel que soit le volume collecté » : dénominateur perdu dans C08.
- « La fraction finale doit avoir un pH de 9,0 » : confusion entre pH du Tris et pH final.
- « Le CIP régulier signifie un CIP à chaque cycle » : fréquence inventée.
- « Le tampon de la figure p.97 et celui du protocole p.98 ont le même pH » : contextes différents, 7,4 et 7,2.

Ce lot est destiné au développement et à la discussion de l’ontologie. Il ne constitue pas une annotation exhaustive des trois pages ni un test indépendant de performance.
