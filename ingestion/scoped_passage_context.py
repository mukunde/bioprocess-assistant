"""Opt-in source-scope/phase navigation; old retrievers and frozen trials stay intact."""
import re

from ingestion.lexical_section_context import VocabularyIndex, contains, folded, phrase_pattern
from ingestion.local_passage_retrieval import assemble, closure, eligible, serialize


def matched(text, config, key):
    return any(contains(text, alias) for alias in config['signals'][key])


def navigation_plan(text, config):
    """Declarative query signals only: no IDs, gold passages or expected answer input."""
    has=lambda key:matched(text,config,key)
    phase_keys=('loading','washing','elution','equilibration')
    phase_text=text
    phase_exclusion=False
    # Only an explicit contrast after a named main phase narrows phase selection.
    matches=[m for marker in config['phase_contrast_markers']
             if (m:=re.search(phrase_pattern(marker),folded(text))) is not None]
    if matches:
        prefix=folded(text)[:min(m.start() for m in matches)]
        if any(matched(prefix,config,k) for k in phase_keys):
            phase_text=prefix;phase_exclusion=True
    phase_has=lambda key:matched(phase_text,config,key)
    general=[('general',['applicability','contaminant_context','method_selection'])]
    blue=[('blue',['product_scope_and_mechanism','conditional_use','warning'])]
    if has('unknown') and has('purification_context'):
        routes=general+(blue if has('blue') else [])
        reason='unspecified_contaminant_context'
    elif has('general_reason') and sum(has(k) for k in ('albumin','transferrin','immunoglobulin'))>=2:
        routes=general;reason='general_contaminant_characteristics'
    elif has('direct_use') and not has('blue'):
        routes=[('general',['applicability'])];reason='application_scope'
    elif has('screen'):
        routes=[('bovine',['source_context','method_alternatives','screening_advice','scoped_example'])]
        reason='named_screening_context'
    elif has('albumin') and has('transferrin') and (has('iex') or has('hic')):
        roles=['method_alternatives']
        if has('iex'):roles.append('residual_contaminants')
        if has('hic'):roles.append('conditional_hic')
        if has('blue'):roles.append('albumin_specific_alternative')
        routes=[('albumin',roles)];reason='named_contaminant_methods'
    elif has('bovine') and has('immunoglobulin'):
        routes=[('bovine',['source_context','method_alternatives'])];reason='named_immunoglobulin_context'
    elif has('blue'):
        roles=[]
        # A buffer request describes formulations rather than the elution phase.
        phase_requested=any(phase_has(k) for k in phase_keys)
        formulation_request=has('buffer') and (not phase_requested or any(contains(text,x) for x in ('alternatives','formulations','buffer preparation','préparation des tampons')))
        if formulation_request:roles=['buffer_alternatives']
        else:
            for signal,role in [('loading','sample_application'),('washing','wash_conditions'),('elution','elution_alternatives'),('equilibration','equilibration')]:
                if phase_has(signal):roles.append(role)
        if roles:
            if has('completion') and 'sample_application' in roles:roles.append('wash_conditions')
            routes=[('blue',roles)];reason='named_product_phase'
        else:routes=blue;reason='named_product_applicability'
    else:
        routes=[];reason='no_explicit_scope'
    return {'reason':reason,'phase_exclusion_applied':phase_exclusion,'routes':[{'group':g,'roles':roles} for g,roles in routes]}


class ScopedContextIndex:
    def __init__(self, corpus, retrieval, config):
        self.config=config
        self.index=VocabularyIndex(corpus,retrieval,config['vocabulary'])
        self.passages=self.index.passages
        self.docs=self.index.docs
        if set(config['source_roles'])!=set(self.passages):
            raise ValueError('Source role inventory mismatch')
        self.members={name:{pid for pid in self.passages if
            (pid in rule['members'] if 'members' in rule else rule['root'] in closure(self.passages,pid))}
            for name,rule in config['groups'].items()}

    def retrieve(self,text,count_tokens):
        config=self.config
        ranking=self.index.search(text,len(self.docs))
        plan=navigation_plan(text,config)
        selected=[];unavailable=[]
        if ranking and plan['routes']:
            for route in plan['routes']:
                members=self.members[route['group']]
                # Do not activate a source family without positive lexical support.
                if not any(h['passage_id'] in members for h in ranking):
                    unavailable.append({'group':route['group'],'reason':'no_positive_scope_hit'})
                    continue
                for role in route['roles']:
                    ids=[pid for pid in self.passages if pid in members and config['source_roles'][pid]==role]
                    if not ids or any(not eligible(self.passages,pid) for pid in ids):
                        unavailable.append({'group':route['group'],'role':role,'reason':'source_missing_or_quarantined'})
                        # Return reviewed protocol scope, never another phase's settings.
                        if route['group']=='blue':
                            selected += [pid for pid in self.passages if pid in members and
                                config['source_roles'][pid] in ('cross_page_protocol_scope','protocol_heading') and eligible(self.passages,pid)]
                        continue
                    selected += ids
        elif ranking:
            # No first-section overview: keep strong hits within the best source family.
            top=ranking[0]
            family=next((name for name,ids in self.members.items() if top['passage_id'] in ids),None)
            selected=[h['passage_id'] for h in ranking if
                h['score']>=top['score']*config['fallback_relative_score'] and
                (family is None or h['passage_id'] in self.members[family])][:config['top_k']]
        # Preserve rank order for supported seeds; add source-navigation anchors last.
        selected=list(dict.fromkeys(selected))
        ordered=[h['passage_id'] for h in ranking if h['passage_id'] in selected]
        ordered += [pid for pid in selected if pid not in ordered]
        dropped=ordered[config['top_k']:]
        seeds=ordered[:config['top_k']]
        result=assemble(self.passages,[{'passage_id':pid} for pid in seeds],count_tokens,config['max_tokens'])
        return {'hits':ranking[:config['top_k']],'scope_selected_seeds':seeds,
            'navigation_plan':plan,'unavailable_source_roles':unavailable,
            'source_navigation_over_top_k':dropped,
            'navigation_complete':not unavailable and not dropped and not result['excluded'],
            'filtered_ranked_ids':[h['passage_id'] for h in ranking if h['passage_id'] not in seeds],
            'assembled':result}
