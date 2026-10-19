"""Build draft evidence cards from immutable existing conversion; no LLM or network."""
import argparse
import os
import hashlib
import json
from pathlib import Path

from experiments.cytiva.paths import ROOT
RUN = ROOT / 'data/ingestion/a325aff86fd8-5bb7c2d10264'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build(output: Path):
    """Generate a new draft only; never replace review records or ontology files."""
    HERE = output.resolve()
    if HERE.exists():
        raise ValueError('Choose a new output directory; reference drafts are never overwritten')
    HERE.mkdir(parents=True, exist_ok=False)
    document = json.loads((RUN / 'document.json').read_text(encoding='utf-8'))
    mapping = json.loads((ROOT / 'references/cytiva-hitrap-sure-pages-097-099.source-map.json').read_text(encoding='utf-8'))
    manifest = json.loads((RUN / 'manifest.json').read_text(encoding='utf-8'))
    assert sha(RUN / 'document.json') == manifest['files']['document.json']
    assert sha(RUN / 'source.pdf') == mapping['excerpt_sha256']
    assert sha(Path(mapping['original_pdf'])) == mapping['original_sha256']
    items = {t['self_ref']: t for t in document['texts']}

    def evidence(ref, quote=None, role='content'):
        item = items[ref]
        text = item['text']
        quote = text if quote is None else quote
        start = text.index(quote)
        assert text.count(quote) == 1
        pages = [p['page_no'] for p in item['prov']]
        assert len(set(pages)) == 1
        page = pages[0]
        original = mapping['pages'][page-1]['original_pdf_page']
        return dict(role=role, item_ref=ref, quote=quote, start=start, end=start+len(quote),
                    offset_unit='python_unicode_codepoint', text_sha256=hashlib.sha256(text.encode()).hexdigest(),
                    excerpt_page_number=page, excerpt_page_index=page-1,
                    original_pdf_page_number=original, original_pdf_page_index=original-1,
                    printed_page_label=mapping['pages'][page-1]['printed_page_label'],
                    item_provenance=item['prov'])

    scope = [evidence('#/texts/0', role='product_scope'), evidence('#/texts/1', role='product_scope')]
    rows = []
    def add(cid, title, subject, predicate, obj, refs, conditions, note, modality, parameters=None):
        rows.append(dict(id=cid, title_fr=title, subject=subject, predicate=predicate, object=obj,
                         claim_type='relation' if predicate else 'procedure', source_modality=modality,
                         polarity='positive', product_id='product:hitrap-mabselect-sure',
                         conditions=dict(operator='all',items=conditions), parameters=parameters or [],
                         evidence=[evidence(*r) for r in refs], scope_evidence=scope,
                         review=dict(status='pending',reviewer=None,date=None,note=None),
                         review_focus=note, annotation_origin='assistant_prepared_documentary_draft'))

    def condition(field, value, refs, role='applicability'):
        return dict(field=field,operator='equals',value=value,evidence_item_refs=refs,role=role)

    q='If the fouling is severe, it can block the column, increase back pressure, and reduce flow rate.'
    for cid, target, title in [('C01','symptom:backpressure-increase','Encrassement sévère → augmentation possible de contre-pression'),('C02','symptom:flow-reduction','Encrassement sévère → diminution possible du débit'),('C03','symptom:column-blockage','Encrassement sévère → obstruction possible de la colonne')]:
        add(cid,title,'cause:fouling','MAY_CAUSE',target,[('#/texts/77',q)],
            [condition('fouling_severity','severe',['#/texts/77'])],
            'Vérifier « severe » et « can ». Le symptôme seul ne prouve ni la présence ni la sévérité de cet encrassement.', 'possible')
    add('C04','Nettoyer la colonne lorsque la contre-pression augmente','action:clean-column','RECOMMENDED_FOR','symptom:backpressure-increase',
        [('#/texts/78','When an increase in backpressure is seen, the column should be cleaned.')],
        [condition('observed_symptom','symptom:backpressure-increase',['#/texts/78'],'trigger')],
        'Pas de cause intermédiaire dans cette phrase. Elle ne prescrit pas à elle seule une concentration, une durée ou un seuil de pression.', 'recommended')
    add('C05','Le CIP peut retirer les substances ciblées du milieu','action:cip','CAN_REMOVE','cause:retained-substances',
        [('#/texts/77','CIP can be performed to remove very tightly bound, precipitated, or denatured substances from the medium.')],[],
        'Conserver le « or » entre les catégories. Cette cible est un état candidat de la classe Cause ; aucun lien causal vers un symptôme n’est ajouté par cette fiche.', 'possible')
    add('C06','Le CIP régulier prévient l’accumulation de contaminants','action:cip','PREVENTS_BUILDUP_OF','cause:contaminant-buildup',
        [('#/texts/78','Regular CIP prevents the build-up of contaminants and helps to maintain the capacity, flow properties, and general performance of HiTrap MabSelect SuRe.')],
        [condition('frequency','regular',['#/texts/78'])],
        'Prévention d’une accumulation ; la fréquence reste qualitative. Aucune garantie individuelle ni fréquence par cycle n’est déduite.', 'source_assertion')
    add('C07','Paramètres du CIP de l’étape 9, si nécessaire après élution','action:cip',None,None,
        [('#/texts/72','If required, perform cleaning in place directly after elution with at least 2 column volumes of 0.1 to 0.5 M sodium hydroxide ensuring a contact time of 10 to 15 min. Wash with 5 column volumes of binding buffer.')],
        [condition('cip_required',True,['#/texts/72']),condition('timing','directly_after_elution',['#/texts/72'])],
        'Vérifier tous les paramètres ensemble et le rinçage qui suit. « If required » n’a pas de critère défini ici. Ne pas déduire de C04 que ce protocole est automatiquement applicable.', 'conditional_instruction',
        [dict(name='cip_reagent',value='sodium hydroxide',evidence_item_refs=['#/texts/72']),
         dict(name='cip_concentration',min=0.1,max=0.5,unit='M',evidence_item_refs=['#/texts/72']),
         dict(name='cip_volume',operator='>=',value=2,unit='column_volume',evidence_item_refs=['#/texts/72']),
         dict(name='contact_time',min=10,max=15,unit='min',evidence_item_refs=['#/texts/72']),
         dict(name='following_wash',value=5,unit='column_volume',material='binding buffer',sequence='after_CIP',evidence_item_refs=['#/texts/72'])])
    add('C08','Préparer les tubes de collecte : quantité par millilitre de fraction','action:prepare-collection-tubes',None,None,
        [('#/texts/59',None),('#/texts/60',None)],
        [condition('antibody_property','acid_labile_IgG',['#/texts/60'],'stated_purpose_context')],
        'L’étape 1 fournit le dénominateur « per milliliter ». La note suivante donne le motif pour les IgG sensibles à l’acide ; ce motif n’est pas présenté comme une restriction exclusive de l’étape 1. Le pH 9,0 est celui du Tris, pas le pH final de la fraction.', 'instruction_with_stated_purpose',
        [dict(name='added_Tris_volume_per_fraction_volume',min=60,max=200,unit='µL',denominator=dict(value=1,unit='mL',material='fraction to be collected'),evidence_item_refs=['#/texts/59']),
         dict(name='Tris_HCl_concentration',value=1,unit='M',evidence_item_refs=['#/texts/59']),
         dict(name='Tris_HCl_pH',value=9.0,unit=None,evidence_item_refs=['#/texts/59']),
         dict(name='stated_final_sample_pH',value='approximately neutral',unit=None,evidence_item_refs=['#/texts/60'])])

    entities = [
     ('product:hitrap-mabselect-sure','Product','HiTrap MabSelect SuRe'),
     ('cause:fouling','Cause','Fouling'),('cause:retained-substances','Cause','Very tightly bound, precipitated, or denatured substances'),
     ('cause:contaminant-buildup','Cause','Build-up of contaminants'),
     ('symptom:backpressure-increase','Symptom','Increase in backpressure'),('symptom:flow-reduction','Symptom','Reduced flow rate'),
     ('symptom:column-blockage','Symptom','Column blockage'),('action:clean-column','Action','Clean the column'),
     ('action:cip','Action','Cleaning in place'),('action:prepare-collection-tubes','Action','Prepare collection tubes')]
    allowed={'MAY_CAUSE':('Cause','Symptom'),'RECOMMENDED_FOR':('Action','Symptom'),'CAN_REMOVE':('Action','Cause'),'PREVENTS_BUILDUP_OF':('Action','Cause')}
    kinds={i:k for i,k,_ in entities}
    for row in rows:
        assert row['review']['status']=='pending'
        if row['predicate']:
            assert (kinds[row['subject']],kinds[row['object']])==allowed[row['predicate']]
        refs={e['item_ref'] for e in row['evidence']}
        for value in row['conditions']['items']+row['parameters']:
            assert set(value['evidence_item_refs']) <= refs
        for e in row['evidence']+row['scope_evidence']:
            assert items[e['item_ref']]['text'][e['start']:e['end']]==e['quote']

    payload=dict(ontology_version='0.1-draft',status='pending_human_review',
                 source=dict(document_reference=mapping['document_reference'],original_pdf=mapping['original_pdf'],
                             original_sha256=mapping['original_sha256'],excerpt_pdf=str(RUN/'source.pdf'),
                             excerpt_sha256=mapping['excerpt_sha256'],conversion_json=str(RUN/'document.json'),
                             conversion_sha256=sha(RUN/'document.json')),
                 entity_catalog=[dict(id=i,kind=k,label_en=n,review_status='pending') for i,k,n in entities],claims=rows)
    (HERE/'exemples.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    lines=['# Fiches de vérification Cytiva — v0.1','',
           '**Toutes les fiches sont en attente.** Elles sont proposées par l’assistant ; les citations sont localisées automatiquement dans la conversion existante. Les pages PDF rendues 97–99 ont été inspectées visuellement pendant la préparation. Aucune approbation humaine n’est présumée.','',
           'Source : *Affinity Chromatography Vol. 1: Antibodies*, CY13981-25Jan21-HB. Pages originales/numéros imprimés 97–99 = pages 1–3 de l’extrait.','',
           f'[Ouvrir l’extrait local des pages 97–99]({Path(os.path.relpath(ROOT / "references/cytiva-hitrap-sure-pages-097-099.pdf", HERE)).as_posix()})','',
           'Périmètre commun proposé : **HiTrap MabSelect SuRe**. Vérifier le titre et l’introduction p.97 ; les sections p.98–99 se poursuivent jusqu’au nouveau titre « MabSelect SuRe LX ». Les preuves de ce périmètre sont conservées séparément dans le JSON.','',
           'Ordre de revue conseillé : **C04 → C01 → C07 → C08**, puis C02/C03/C05/C06. Pour chaque fiche, répondre approuvé / rejeté / à préciser, avec une note.','']
    for row in rows:
        lines += [f'## {row["id"]} — {row["title_fr"]}','',f'**Statut : pending.** Modalité : `{row["source_modality"]}`.','',
                  f'Proposition : `{row["subject"]}`'+(f' — `{row["predicate"]}` → `{row["object"]}`.' if row['predicate'] else ' — procédure contextualisée.'),'']
        for e in row['evidence']:
            lines += [f'**Page {e["original_pdf_page_number"]}** (extrait {e["excerpt_page_number"]}), élément `{e["item_ref"]}`, offsets `{e["start"]}:{e["end"]}` :','',f'> {e["quote"]}','']
        lines += ['Conditions / contexte : '+ (' ; '.join(f'`{c["field"]}` = `{c["value"]}` ({c["role"]})' for c in row['conditions']['items']) or 'périmètre produit commun ; aucune condition supplémentaire ajoutée.'),'']
        if row['parameters']:
            lines += ['Paramètres à vérifier :','', '```json',json.dumps(row['parameters'],ensure_ascii=False,indent=2),'```','']
        lines += ['**Point de vigilance :** '+row['review_focus'],'',
                  '- [ ] Citation et page vérifiées dans le PDF.','- [ ] Sens, direction, modalité et conditions fidèles.','- [ ] Périmètre produit vérifié.',
                  '- Décision : … ; note : …','']
    lines += ['## Contre-exemples à rejeter','',
     '- « Une contre-pression accrue prouve un encrassement sévère » : inversion abusive de C01.',
     '- « Le nettoyage résout toujours la hausse de pression » : C04 ne garantit pas la résolution.',
     '- « Utiliser exactement 2 mL de NaOH » : C07 parle d’au moins deux volumes de colonne.',
     '- « Appliquer les paramètres C07 à MabSelect SuRe LX » : autre produit, instructions distinctes p.99.',
     '- « Ajouter 60–200 µL au total, quel que soit le volume collecté » : dénominateur perdu dans C08.',
     '- « La fraction finale doit avoir un pH de 9,0 » : confusion entre pH du Tris et pH final.',
     '- « Le CIP régulier signifie un CIP à chaque cycle » : fréquence inventée.',
     '- « Le tampon de la figure p.97 et celui du protocole p.98 ont le même pH » : contextes différents, 7,4 et 7,2.', '',
     'Ce lot est destiné au développement et à la discussion de l’ontologie. Il ne constitue pas une annotation exhaustive des trois pages ni un test indépendant de performance.']
    (HERE/'examples-v0.1.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    result=dict(claims=len(rows),relation_claims=sum(bool(r['predicate']) for r in rows),procedure_claims=sum(not r['predicate'] for r in rows),
                all_pending=True,source_hashes_verified=True,quote_offsets_verified=True,domain_range_verified=True,
                condition_parameter_evidence_refs_verified=True,llm_calls=0)
    (HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New draft directory; existing directories are refused')
    args = parser.parse_args()
    build(args.output)


if __name__ == '__main__':
    main()
