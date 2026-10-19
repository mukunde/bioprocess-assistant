# Fidélité documentaire et choix du modèle — 19 octobre 2026

Rapport conservé de l’essai v0.1. Les artefacts bruts sont locaux sous `data/experiments/cytiva/pages-097-099-v01/` ; les outils sont dans [experiments/cytiva](../../experiments/cytiva/README.md). Le contrat courant est v0.2.

**Recommandation : retenir provisoirement GPT‑6.1 Sol pour l’extraction avec ce prompt et cet effort.** Il préserve mieux les conditions, distingue mieux les objectifs des restrictions d’applicabilité et signale deux ambiguïtés réellement présentes dans le PDF. Son résultat nécessite néanmoins trois corrections de représentation et la quarantaine d’une instruction contradictoire avant de préparer une intégration au graphe.

Ce choix repose sur une revue par l’assistant des 49 propositions, pas sur le nombre brut de relations. Les réponses ont été lues avec les textes cités, les trois pages PDF rendues en entier et les définitions de l’ontologie v0.1. La revue n’est pas aveugle ; les décisions sont explicitées pour permettre leur contestation par Gaël. Les huit fiches antérieures restent un catalogue de développement, sans approbation humaine. Aucun claim n’a été approuvé dans la base ni modifié dans les originaux.

## Bilan des propositions

| Décision proposée par l’assistant | Sonnet 5.5 | GPT‑6.1 Sol |
|---|---:|---:|
| Fidèle, sans correction identifiée dans ce claim | 10 | 22 |
| Contenu fidèle avec réserve de représentation/force normative | 2 | 3 |
| À corriger avant usage dans notre ontologie | 8 | 3 |
| Fidèle à un passage ambigu, à mettre en quarantaine | 0 | 1 |
| Total examiné | 20 | 29 |

Ce ne sont pas des taux de précision comparables : les unités extraites diffèrent, notamment 6 PROCEDURE chez Sonnet contre 19 chez Sol. « À corriger » inclut des reformulations logiques ou ontologiques, pas seulement des affirmations inventées. Les notes d’incertitude des modèles sont prises en compte ; elles ne neutralisent pas une arête qui reste exploitable avec un mauvais sens.

Certaines exigences de v0.1, notamment RECOMMENDED_FOR limité au symptôme observé et la distinction explicite nettoyage/CIP, n’étaient pas aussi précises dans le prompt du benchmark. Les corrections correspondantes désignent donc aussi un défaut de notre contrat d’extraction ; elles ne peuvent pas toutes être attribuées à une faiblesse intrinsèque du modèle. Les règles ont été appliquées aux deux candidats de la même façon.

Les deux résultats ont un JSON conforme et aucune référence d’item inexistante. La seule erreur de domaine/portée détectée automatiquement est Sonnet c20. Les contrôles de types ne détectent ni son mauvais prédicat c15 ni la substitution « nettoyage → CIP » de Sol cl8.

## Différences qui motivent le choix

| Point vérifié | Sonnet | Sol | Conclusion |
|---|---|---|---|
| IgG sensibles à l’acide, p.98, items 59–60 | c13 impose acid-labile IgG sous applicability ; l’étape générale de préparation des tubes est ainsi restreinte | cl14 conserve la préparation générale et le motif dans stated_purpose_context | Avantage Sol. Les quantités sont exactes dans les deux. |
| Prévention de la dénaturation, p.99, item 70 | c15 invente une prévention de « l’accumulation » d’exposition au pH bas ; c14 emploie aussi RECOMMENDED_FOR | cl11 conserve une cause possible ; cl12 emploie également RECOMMENDED_FOR pour une prévention | Avantage Sol, mais cl12 doit aussi devenir une procédure avec objectif déclaré. RECOMMENDED_FOR signifie dans notre v0.1 une recommandation lorsque le symptôme est observé. |
| Pression accrue, p.99, item 78 | c9 conserve nettoyer la colonne | cl8 remplace le nettoyage par le CIP | Avantage Sonnet. Le contexte CIP rend le choix de Sol plausible, mais l’ontologie interdit cette équivalence automatique. |
| Contamination croisée, p.97, item 1 | c20 force RECOMMENDED_FOR vers une Cause ; le modèle l’admet | cl10 garde un objectif de procédure | Avantage Sol. |
| Baisse du débit, p.99, item 71 | c16 perd « peut être nécessaire » dans la proposition elle-même ; la réserve est seulement dans uncertainties | cl13 conserve cette possibilité dans le paramètre et dans le nom de l’action | Avantage Sol. |
| Réutilisation, p.99, item 75 | c18 encode Reuse sous condition sans conserver que la réutilisation est seulement à envisager et dépend de la nature de l’échantillon | cl15 conserve explicitement la condition nécessaire, non suffisante | Avantage Sol. |
| Préparation échantillon, p.98, item 53 | c19 associe not_equals à une phrase entière, non évaluable comme condition | cl17 conserve if required ; cl16 a toutefois un sujet trop large et apparemment inconditionnel | Les deux demandent une correction ; celle de Sol est localisée au nom/sujet de cl16. |
| Blank run, p.99, item 78 | c10 transforme un objectif de recommandation en CAN_REMOVE, malgré une modalité et une note prudentes | cl9 représente une procédure et son objectif ; il manque une représentation explicite de la force « recommandé » | Avantage Sol. Conserver la force normative dans le futur schéma. |

## Quantités, unités, comparateurs et séquences

**Aucune valeur numérique erronée identifiée parmi les paramètres présents.** Une omission de paramètre n’est pas comptée comme une valeur fausse. Le produit/phase, les conditions, l’alternative et le dénominateur font partie du contrôle : « même chiffre » ne signifie pas « instruction fidèle ».

| Paramètre du PDF | Sonnet | Sol | Vérification |
|---|---|---|---|
| Tubes : 60–200 µL de Tris-HCl 1 M, pH 9,0 **par mL de fraction**, p.98 | c13 | cl14 | Exact des deux côtés ; condition d’applicabilité de Sonnet à corriger. pH final approximativement neutre préservé. |
| CIP si nécessaire directement après élution : **au moins 2 CV**, NaOH **0,1–0,5 M**, contact **10–15 min**, puis **5 CV** de tampon de liaison, p.99 | c11 | cl20 | Tous les nombres, le minimum, le contexte et l’ordre sont conservés. Le critère « si nécessaire » n’est pas défini par le manuel. |
| Sans CIP prévu : **5 CV** de tampon d’élution **et/ou 3 CV** de tampon de liaison, p.99 | c12 | cl19 | Exact ; chez Sonnet, et/ou est dans le nom de paramètre/de l’action, représentation fragile pour une exécution logique. |
| pH échantillon **6–9** avant chargement, p.98 | c19 | cl16 | Nombre exact ; logique de condition Sonnet et sujet d’action Sol à corriger. |
| Centrifugation **10 000 × g**, **10 min**, puis filtre **0,45 µm**, p.98 | Non extrait | cl22 | Exact ; aucune conversion en tr/min. |
| Tampon liaison **0,02 M** phosphate, **0,15 M** NaCl, **pH 7,2** ; élution **0,1 M** citrate, **pH 3,0–3,6**, p.98 | Pas de fiche de composition complète | cl17, cl19–21, cl25–27 | Exact et correctement associé au protocole. |
| Filtration tampons **0,45 µm** avant usage, p.98 | Non extrait | cl23 | Exact. |
| Chargement : **0,2–1 mL/min** pour colonne **1 mL**, **0,5–5 mL/min** pour **5 mL**, p.98 | Non extrait | cl24 | Exact, sans mélange avec l’exemple de figure. |
| Lavage : généralement au moins **5–10 CV**, jusqu’à baseline stable ou absence de matière dans l’effluent ; débits **1–2 / 5–10 mL/min** pour **1 / 5 mL**, p.98 | Non extrait | cl25 | Chiffres, tailles de colonnes et critère d’arrêt conservés. |
| Élution par paliers **5 CV** habituellement suffisants ; gradient **10–20 CV** habituellement suffisants ; débits **1–2 / 5–10 mL/min**, p.98 | Pas de paramètre chiffré | cl26–27 | Exact ; usually est conservé, pas de garantie de suffisance. |
| Seringue : **2–5 CV de binding buffer**, p.98 | Non extrait | cl28 | Copie fidèle d’une ambiguïté du PDF : quarantaine obligatoire avant usage. |
| Rééquilibrage : **5–10 CV OU jusqu’au même pH que le tampon**, p.99 | Non extrait | cl21 | Alternative et séquence conservées. |
| Stockage : éthanol **20 %**, **2–8 °C**, p.99 | Non extrait | cl29 | Exact ; base du pourcentage non spécifiée, pas d’invention de v/v. |

CV signifie volume de colonne : aucune conversion automatique en mL sans volume de colonne renseigné. Les µ et μ sont deux caractères typographiques pour micro, pas une différence de quantité.

## Ambiguïtés de la source et omissions

Deux difficultés signalées par Sol sont visibles dans le PDF :

1. P.98, étape 5, item 64 : la phrase contient effectivement « with at 10 column volumes ». Sol s’abstient sur ce volume. Ne pas résoudre automatiquement « exactement 10 » ou « au moins 10 ». Les débits recommandés de cette étape restent extractibles séparément.
2. P.98, étape 8, item 67 : l’instruction générale demande le tampon d’élution, puis la phrase sur la seringue mentionne le tampon de liaison. Sol reproduit ce dernier et signale le problème. C’est une ambiguïté documentaire, pas une hallucination du modèle. Toutefois, une simple note globale ne bloque pas le claim : ajouter à cl28 un statut source_conflict interdisant sa mise à disposition comme consigne jusqu’à clarification.

Les deux modèles séparent correctement le protocole p.98 de l’exemple de figure p.97 : pH 7,4/glycine-HCl pH 3,5 de la figure ne sont pas fusionnés avec pH 7,2/citrate pH 3,0–3,6 du protocole. Ils ne transfèrent pas les instructions HiTrap MabSelect SuRe à SuRe LX, dont le titre ouvre un autre périmètre p.99. Aucun seuil numérique de pression ni intervalle numérique de CIP n’est inventé.

Sol omet notamment le changement global des propriétés chromatographiques (présent chez Sonnet c1) et les bénéfices descriptifs de l’élution par paliers (Sonnet c17). Les deux omettent le rinçage initial de l’éthanol à 3–5 CV, les correspondances approximatives en gouttes/minute et le transfert/dessalage final. Ce ne sont pas nécessairement des omissions prioritaires pour notre assistant de dépannage. Aucune extraction n’est un protocole opératoire complet.

## Couverture des huit fiches de développement

« Présent » signifie que le fait attendu a été retrouvé ; ce n’est pas un score de rappel sur l’ensemble du passage. Le catalogue est connu du développement et n’a pas été validé comme référence indépendante.

| Fiche | Sonnet | Sol |
|---|---|---|
| C01 encrassement sévère → pression | c5, fidèle | cl4, fidèle |
| C02 encrassement sévère → débit | c6, fidèle | cl5, fidèle |
| C03 encrassement sévère → obstruction | c4, fidèle | cl3, fidèle |
| C04 nettoyage recommandé si pression accrue | c9, fidèle | cl8, nettoyage à distinguer du CIP |
| C05 CIP peut enlever les contaminants décrits | c7, fidèle | cl6, contenu fidèle, cible à normaliser |
| C06 CIP régulier prévient l’accumulation | c8, contenu fidèle, cible à normaliser | cl7, contenu fidèle, cible à normaliser |
| C07 CIP chiffré après élution si nécessaire | c11, fidèle | cl20, fidèle |
| C08 tubes de collecte, quantité par mL et motif | c13, nombres fidèles mais filtre d’applicabilité indu | cl14, fidèle |

Ainsi, les deux retrouvent les huit sujets ; chacun a un de ces huit éléments à corriger. Le choix de Sol vient surtout de la conservation des nuances dans l’ensemble des propositions et de son traitement des ambiguïtés, pas d’un prétendu 8/8 contre 7/8.

## Corrections proposées avant la prochaine extraction

1. Conserver les trois corrections Sol dans une couche de propositions de revue : cl8 = nettoyer la colonne ; cl12 = procédure préventive ; cl16 = cible pH avant chargement, distincte de l’ajustement conditionnel cl17. Ne pas écraser les originaux.
2. Mettre cl28 en quarantaine explicite. Garder la citation et la contradiction, sans corriger le manuel par intuition.
3. Clarifier le contrat de schéma : force normative (recommandé, nécessaire, possibilité) séparée du motif ; instruction et bénéfice descriptif séparés ; nettoyage distinct du CIP ; un objectif n’est pas une arête de capacité ou un traitement de symptôme constaté.
4. Représenter les alternatives et les conditions avec un opérateur adapté, et un état non résolu. `equals`/`not_equals` sur des phrases ne permet pas d’exécuter des comparaisons numériques fiables.
5. Associer chaque claim à un produit et une phase explicites, en plus des scope_refs. Les sujets « encrassement sévère » portent actuellement leur sévérité dans le nom ; ne pas la perdre lors de la normalisation des entités.
6. Après validation des corrections et d’un petit référentiel humain, tester le même contrat révisé sur quelques pages encore non utilisées, à budget maîtrisé. Cet essai ne permet pas de conclure sur tout le manuel, les coûts API ou la vitesse réelle.

## Décision de projet

Prendre **GPT‑6.1 Sol comme extracteur provisoire de référence pour la suite**, avec contrôle déterministe des types/références/quantités puis revue documentaire humaine ciblée. Garder Sonnet comme candidat de comparaison, sans payer deux extractions à chaque édition. Aucune nécessité de changer le modèle léger de l’assistant quotidien à partir de cet essai.

Les compteurs ci-dessus proviennent de `audit-fidelite.json`. `AUDIT-DETAILLE.md` contient une fiche pour chacun des 49 claims, ses valeurs et conditions originales, le verdict motivé et les pages/items à vérifier. Le statut humain reste pending. Les horodatages de capture ne sont pas une mesure de latence d’inférence ; aucune facture API n’a été mesurée. Aucun nouvel appel de modèle, commit ou push pendant cette revue.
