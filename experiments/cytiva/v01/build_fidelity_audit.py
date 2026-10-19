"""Render a source-based assistant review. Judgments are authored, not computed scores.

No model calls, no edits to candidates, no human approvals or database writes.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

from experiments.cytiva.paths import ROOT, V01 as HERE, candidate_path

def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8-sig'))

# F = faithful documentary proposition; N = faithful with modeling/force caveat;
# C = correction required before use; Q = source ambiguity, quarantine.
# These are assistant judgments, not user decisions or industrial validation.
SONNET = {
    'c1': ('F', 'L’accumulation peut modifier les propriétés chromatographiques ; la possibilité est conservée.', ''),
    'c2': ('F', 'La réduction de capacité est explicitement reliée à l’accumulation ; aucune cause réelle n’est diagnostiquée.', ''),
    'c3': ('F', 'La contamination possible des purifications suivantes est explicitement décrite.', ''),
    'c4': ('F', 'L’obstruction est possible en cas d’encrassement sévère ; severe reste dans le nom du sujet.', ''),
    'c5': ('F', 'L’augmentation de contre-pression est possible en cas d’encrassement sévère.', ''),
    'c6': ('F', 'La réduction de débit est possible en cas d’encrassement sévère.', ''),
    'c7': ('F', 'Le CIP peut retirer les substances très liées, précipitées ou dénaturées. CAN_REMOVE conserve la capacité, sans garantie.', ''),
    'c8': ('N', 'Le CIP régulier prévient l’accumulation ; aucune fréquence numérique n’est inventée.', 'Comme pour Sol cl7, normaliser la cible « contaminants » plutôt que « accumulation de contaminants », sans changer le fait.'),
    'c9': ('F', 'La source recommande de nettoyer lorsque la contre-pression augmente. Le sujet reste bien « Clean the column ». Aucun seuil inventé.', ''),
    'c10': ('C', 'Le motif et le moment du blank run sont conservés, mais CAN_REMOVE présente une capacité alors que la source donne le but d’une recommandation. La modalité et la note d’incertitude atténuent cet écart sans supprimer l’arête.', 'Représenter une PROCEDURE : blank run incluant CIP, recommandé avant la première purification ; objectif déclaré = éliminer d’éventuelles traces de protéine A.'),
    'c11': ('F', 'Si nécessaire, directement après élution : au moins 2 CV de NaOH 0,1–0,5 M, contact 10–15 min, puis 5 CV de tampon de liaison. Tous ces éléments sont préservés.', 'Le critère de nécessité reste inconnu ; ne pas déduire automatiquement une autorisation de CIP de toute augmentation de pression.'),
    'c12': ('F', 'La condition « pas de CIP prévu après élution », 5 CV de tampon d’élution et/ou 3 CV de tampon de liaison sont présents.', 'Le and/or n’est porté que par le nom du paramètre et de l’action : le conserver explicitement dans une future représentation logique.'),
    'c13': ('C', 'Les quantités et le dénominateur sont exacts, mais acid-labile IgG devient une condition d’applicabilité. L’étape 1 donne une instruction générale ; la note explique son motif. La perte d’activité est aussi inférée comme symptôme.', 'PROCEDURE de préparation des tubes ; 60–200 µL de Tris-HCl 1 M pH 9,0 par mL de fraction ; sensibilité à l’acide sous stated_purpose_context, sans filtre d’éligibilité.'),
    'c14': ('C', 'Le choix du pH le plus élevé permettant l’élution est fidèle. RECOMMENDED_FOR signifie cependant, dans notre ontologie, une action face à un symptôme observé ; ici la dénaturation est à prévenir.', 'PROCEDURE pendant l’optimisation de l’élution, avec objectif déclaré de prévenir la dénaturation ; ne pas suggérer de traiter une dénaturation déjà survenue.'),
    'c15': ('C', 'PREVENTS_BUILDUP_OF est détourné : le passage ne parle pas d’accumulation d’une exposition au pH bas. Le modèle reconnaît la difficulté, mais conserve l’arête.', 'Supprimer cette arête du candidat destiné au graphe ; le but de prévention est porté par la procédure corrigée de c14.'),
    'c16': ('C', 'Le contexte de forte concentration après élution par paliers est conservé, mais le claim dit simplement diminuer le débit. Le « might be necessary » n’est conservé que dans uncertainties, pas dans la proposition.', 'Conserver dans la proposition « une diminution du débit peut être nécessaire », sans rendre l’action obligatoire et sans inventer un débit.'),
    'c17': ('N', 'Les bénéfices de l’élution par paliers sont fidèles. Le passage décrit un avantage, pas un ordre général de choisir cette méthode.', 'Conserver comme justification descriptive, ou employer une assertion descriptive plutôt qu’une instruction ; aucune quantité n’est inventée.'),
    'c18': ('C', 'La restriction aux échantillons identiques est présente, mais l’action « Reuse » sous condition perd « should only be considered » et la dépendance à la nature de l’échantillon.', 'Exprimer que la réutilisation ne peut être envisagée que pour des échantillons identiques et dépend de leur nature ; ce n’est pas une permission suffisante.'),
    'c19': ('C', 'La plage pH 6–9 et les méthodes d’ajustement sont exactes. L’opérateur not_equals appliqué à une phrase entière n’exprime pas une condition évaluable et risque de transformer la plage en déclencheur exclusif.', 'Séparer la recommandation pH avant chargement de l’ajustement « if required » au pH et à la force ionique du tampon ; conserver la condition libre comme non résolue.'),
    'c20': ('C', 'RECOMMENDED_FOR vise une Cause au lieu d’un Symptom. Le texte soutient le but du CIP, pas cette relation. L’erreur est déjà détectée structurellement et admise par le modèle.', 'PROCEDURE avec objectif déclaré de minimiser les contaminations croisées entre purifications d’anticorps différents, et nettoyage général après purification.'),
}

SOL = {
    'cl1': ('F', 'L’accumulation peut réduire la capacité ; la possibilité et la cible sont soutenues.', ''),
    'cl2': ('F', 'L’accumulation peut contaminer les purifications suivantes ; aucune certitude n’est ajoutée.', ''),
    'cl3': ('F', 'Encrassement sévère → obstruction possible : sens et sévérité préservés.', ''),
    'cl4': ('F', 'Encrassement sévère → augmentation possible de contre-pression.', ''),
    'cl5': ('F', 'Encrassement sévère → réduction possible du débit.', ''),
    'cl6': ('N', 'La capacité du CIP à retirer ces substances est fidèle ; la cible est nommée accumulation, alors que le paramètre removal_target conserve les substances exactes.', 'Pour normaliser les entités, distinguer contaminants retirés et processus d’accumulation. Ce n’est pas une quantité erronée ni une relation causale inventée.'),
    'cl7': ('N', 'Le CIP régulier prévient l’accumulation et aucune périodicité chiffrée n’est ajoutée.', 'Même normalisation de cible que cl6 : éviter littéralement « accumulation de l’accumulation ». Le sens reste lisible dans le claim complet.'),
    'cl8': ('C', 'Le déclencheur et le symptôme sont exacts. La phrase source demande de nettoyer ; le sujet devient directement effectuer un CIP. Le contexte de section rend ce choix plausible, mais notre ontologie interdit l’équivalence automatique.', 'Créer une Action distincte « nettoyer la colonne », recommandée pour l’augmentation de contre-pression ; conserver les procédures CIP dans leurs propres claims.'),
    'cl9': ('N', 'Le blank run incluant CIP, avant la première purification, est bien présenté avec son objectif et les traces possibles de protéine A.', 'Conserver aussi explicitement la force « nous recommandons » ; la catégorie instruction_with_stated_purpose ne distingue pas à elle seule recommandation et obligation.'),
    'cl10': ('F', 'Le motif de minimisation des contaminations et le nettoyage général sont conservés comme objectifs de procédure, sans arête forcée.', ''),
    'cl11': ('F', 'L’exposition au pH bas peut dénaturer les anticorps sensibles : causalité explicitement soutenue, aucune observation réelle n’est prétendue.', 'Symptom désigne ici une manifestation potentielle, pas un diagnostic sur un échantillon.'),
    'cl12': ('C', 'Le paramètre restitue correctement le pH le plus élevé compatible avec une élution efficace. Mais RECOMMENDED_FOR est réservé dans v0.1 au symptôme observé ; le passage décrit une prévention.', 'PROCEDURE pendant l’optimisation de l’élution, objectif déclaré = prévenir la dénaturation due au pH bas.'),
    'cl13': ('F', 'Le contexte d’élution par paliers, la forte concentration et le « might be necessary » sont tous conservés dans le claim. Aucun débit inventé.', ''),
    'cl14': ('F', 'Instruction générale de préparation des tubes, motif distinct, 60–200 µL de Tris-HCl 1 M pH 9,0 par mL de fraction et pH final approximativement neutre : fidèle.', ''),
    'cl15': ('F', 'La réutilisation est seulement à envisager pour des échantillons identiques ; sa dépendance à leur nature et le caractère non suffisant de cette condition sont explicités.', ''),
    'cl16': ('C', 'Le paramètre pH 6–9 avant chargement est fidèle, mais le sujet de la procédure est « Adjust sample pH and ionic strength » sans condition. Il est plus large que la simple propriété cible citée.', 'Renommer l’action « vérifier/assurer le pH de l’échantillon avant chargement » ; laisser l’ajustement conditionnel et la force ionique dans cl17.'),
    'cl17': ('F', 'L’ajustement si nécessaire, les méthodes et la composition du tampon de liaison du protocole sont préservés, sans emprunter le pH de la figure.', ''),
    'cl18': ('F', 'Connexion drop to drop, eau distillée et but d’éviter l’air : contenu et ordre fidèles à l’étape 2.', 'Ce claim représente l’étape 2, pas toute la préparation de colonne ; les étapes 3–5 ne sont pas implicitement couvertes.'),
    'cl19': ('F', 'Sans CIP prévu : 5 CV de tampon d’élution et/ou 3 CV de tampon de liaison ; compositions contextualisées du protocole correctes.', ''),
    'cl20': ('F', 'Si nécessaire après élution : ≥2 CV NaOH 0,1–0,5 M, 10–15 min, puis 5 CV de tampon de liaison. Séquence et comparateur fidèles.', 'Ne pas relier automatiquement cette procédure à toute hausse de contre-pression ; la nécessité n’est pas définie par l’étape 9.'),
    'cl21': ('F', 'Après l’étape 9, rééquilibrage avec 5–10 CV de tampon de liaison OU jusqu’au même pH ; alternative et séquence conservées.', ''),
    'cl22': ('F', '10 000 × g pendant 10 min puis filtration 0,45 μm : valeurs et ordre fidèles. Il ne s’agit pas de tr/min.', ''),
    'cl23': ('F', 'Haute pureté des ingrédients et filtration des tampons à 0,45 μm avant usage : fidèle.', ''),
    'cl24': ('F', 'Chargement : 0,2–1 mL/min pour colonne 1 mL et 0,5–5 mL/min pour 5 mL ; méthode et phase correctement associées.', ''),
    'cl25': ('F', 'Lavage : généralement au moins 5–10 CV et critère d’effluent/baseline, débits 1–2 et 5–10 mL/min selon le volume de colonne : fidèle.', ''),
    'cl26': ('F', 'Élution par paliers : 5 CV habituellement suffisants, débits associés aux tailles de colonne et citrate 0,1 M pH 3,0–3,6 du protocole : fidèle.', 'Les 5 CV ne doivent pas devenir une garantie universelle de suffisance.'),
    'cl27': ('F', 'Gradient linéaire : 10–20 CV habituellement suffisants et mêmes débits/composition de protocole : fidèle.', ''),
    'cl28': ('Q', 'La mention 2–5 CV de binding buffer pour élution à la seringue figure bien dans le PDF p.98, étape 8. Elle est reproduite fidèlement et signalée dans uncertainties ; elle contredit apparemment l’instruction générale d’élution avec elution buffer.', 'Conserver le texte source et mettre le claim en quarantaine source_conflict ; demander clarification documentaire avant utilisation. Ne pas remplacer binding par elution automatiquement.'),
    'cl29': ('F', 'Stockage en éthanol 20 % à 2–8 °C : fidèle. Le modèle ne choisit pas arbitrairement une base v/v ou m/m.', 'Conserver la base du pourcentage comme non spécifiée.'),
}

LABELS = {'F': 'Fidèle', 'N': 'Fidèle avec réserve de représentation', 'C': 'À corriger avant usage', 'Q': 'Fidèle à une source ambiguë — quarantaine'}

# These authored judgments apply only to the exact bytes reviewed on 2026-10-19.
# New responses or evidence need a new documentary review, never a hash refresh alone.
REVIEWED_INPUT_HASHES = {
    'input.json': 'a957572e7c0afe4881e79fe6960cc80e1588b7cb738e6c1c6ac911da3add0b80',
    'manual-prompt.txt': '8f44df5246b7c596a6cbd4b5fb3b0bf40c4d87c620cc3cf56071d20bb960c747',
    'resultat-sonnet-original.json': '1e71561c52611b5e89c5231ed17637ce8d34f03c5c7ed0bb70bcc7d390cb195c',
    'resultat-sol.json': 'f3fe8663662d5f4ce7ba18d041cec4bed824d106de4f284a88359105c85b20ea',
    'source.pdf': 'a325aff86fd820a6534fb282d82d3f58861d6f1a720a754622d0f45fd1114419',
    'source-map.json': '79a9a244efc2b1667e6a721b7b0e1d50b68fd5d642e9637dbe9265fcd373093f',
}


def verify_reviewed_inputs():
    paths = {name: HERE / name for name in REVIEWED_INPUT_HASHES}
    paths['source.pdf'] = ROOT / 'references/cytiva-hitrap-sure-pages-097-099.pdf'
    paths['source-map.json'] = ROOT / 'references/cytiva-hitrap-sure-pages-097-099.source-map.json'
    for name, path in paths.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != REVIEWED_INPUT_HASHES[name]:
            raise ValueError(f'Reviewed input changed: {name}; a new documentary review is required')
    return dict(REVIEWED_INPUT_HASHES)


def main():
    reviewed_hashes = verify_reviewed_inputs()
    corpus = read('input.json')
    items = {e['item_ref']: e for e in corpus['elements']}
    meta = read('execution-abonnements.json')
    prompt_hash = hashlib.sha256((HERE / 'manual-prompt.txt').read_bytes()).hexdigest()
    assert prompt_hash == meta['prompt_sha256'], 'Prompt changed since the UI test'
    source_map = json.loads((ROOT / 'references/cytiva-hitrap-sure-pages-097-099.source-map.json').read_text(encoding='utf8'))
    excerpt = ROOT / 'references/cytiva-hitrap-sure-pages-097-099.pdf'
    assert hashlib.sha256(excerpt.read_bytes()).hexdigest() == source_map['excerpt_sha256']
    assert (HERE / 'archive/resultat-sonnet-alias.json').read_bytes() == candidate_path('sonnet').read_bytes()
    audit = {
        'review_date': '2026-10-19', 'reviewer': 'assistant',
        'method': 'All 49 candidate claims read against supplied items, full rendered PDF pages 97–99 and ontology v0.1. Authored semantic judgments, not an automatic entailment proof.',
        'user_manual_approval': False, 'reference_status': 'draft_not_gold',
        'candidate_files_unchanged': True, 'reviewed_input_hashes': reviewed_hashes,
        'prompt_sha256': prompt_hash,
        'pdf_excerpt_sha256': source_map['excerpt_sha256'],
        'recommendation': 'GPT-6.1 Sol provisionally for this extraction configuration, with corrections and source quarantine; no general/API superiority established.',
        'candidates': {},
    }
    for model, notes in [('sonnet', SONNET), ('sol', SOL)]:
        candidate = json.loads(candidate_path(model).read_text(encoding='utf8'))
        assert set(notes) == {c['id'] for c in candidate['claims']}
        entities = {e['id']: e for e in candidate['entities']}
        rows = []
        for claim in candidate['claims']:
            cid = claim['id']
            verdict, reason, correction = notes[cid]
            refs = set(claim['evidence_refs'] + claim['scope_refs'])
            for field in ('conditions', 'parameters'):
                for entry in claim[field]:
                    refs.update(entry['evidence_refs'])
            assert refs <= items.keys(), f'{model}/{cid} unknown evidence'
            rows.append({
                'claim_id': cid, 'verdict': verdict, 'verdict_label': LABELS[verdict],
                'rationale': reason, 'proposed_correction_or_note': correction,
                'claim_as_extracted': claim,
                'subject': entities[claim['subject_id']],
                'object': entities.get(claim['object_id']),
                'source_items': [items[r] for r in sorted(refs, key=lambda x: int(x.split('/')[-1]))],
                'human_review_status': 'pending',
            })
        counts = dict(Counter(r['verdict'] for r in rows))
        audit['candidates'][model] = {
            'source_file_sha256': hashlib.sha256(candidate_path(model).read_bytes()).hexdigest(),
            'counts': counts, 'claims': rows,
        }
    (HERE / 'audit-fidelite.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf8')
    lines = ['# Revue détaillée des 49 propositions', '',
        'Revue documentaire par l’assistant du 19 octobre 2026. Les trois pages PDF ont été rendues et examinées en entier. Chaque proposition a été confrontée à ses preuves, conditions, paramètres et à l’ontologie v0.1. Ce document ne constitue pas une approbation humaine. Les originaux restent inchangés.', '',
        'F = fidèle ; N = contenu fidèle avec réserve de représentation ; C = correction avant usage ; Q = texte fidèle à une source ambiguë à mettre en quarantaine. Ces catégories distinguent fidélité au document, représentation dans l’ontologie et utilisabilité.', '']
    for model in ('sonnet', 'sol'):
        lines += [f'## {model}', '']
        for row in audit['candidates'][model]['claims']:
            c = row['claim_as_extracted']
            subject = row['subject']['name']
            obj = row['object']['name'] if row['object'] else '(instruction contextualisée)'
            lines += [f"### {row['claim_id']} — {row['verdict_label']}", '',
                f"**Extraction :** {subject} → `{c['predicate']}` → {obj}. Modalité : `{c['modality']}`.", '',
                f"**Vérification :** {row['rationale']}", '']
            if row['proposed_correction_or_note']:
                lines += [f"**Correction proposée / réserve :** {row['proposed_correction_or_note']}", '']
            refs = ', '.join(f"`{e['item_ref']}` (p.{','.join(map(str, e['original_pages']))})" for e in row['source_items'])
            lines += [f'**Preuves de contenu, périmètre et paramètres :** {refs}.', '']
            for title, field in [('Conditions extraites', 'conditions'), ('Paramètres extraits', 'parameters')]:
                if c[field]:
                    lines += [f'**{title} :**', '']
                    for entry in c[field]:
                        key = entry.get('field', entry.get('name'))
                        details = f" ; rôle {entry['role']} ; opérateur {entry['operator']}" if 'role' in entry else ''
                        lines += [f"- {key} : {entry['value_text']}{details} ; preuves {', '.join(entry['evidence_refs'])}."]
                    lines += ['']
    (HERE / 'AUDIT-DETAILLE.md').write_text('\n'.join(lines), encoding='utf8')
    print(json.dumps({m: v['counts'] for m, v in audit['candidates'].items()}, ensure_ascii=False))

if __name__ == '__main__':
    main()
