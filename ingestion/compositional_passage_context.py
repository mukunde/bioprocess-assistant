"""Opt-in compositional source navigation; frozen v03b is never patched."""
import re
from itertools import zip_longest

from ingestion.lexical_section_context import contains, folded, phrase_pattern
from ingestion.local_passage_retrieval import assemble, eligible
from ingestion.scoped_passage_context import ScopedContextIndex, matched

PHASES={'loading':'sample_application','washing':'wash_conditions',
        'elution':'elution_alternatives','equilibration':'equilibration'}
BLUE=['product_scope_and_mechanism','conditional_use','warning']
GENERAL=['applicability','contaminant_context','method_selection']


def phase_mentions(text,config):
    """Bounded FR/EN clause negation. Report conflicts; never claim full NLP."""
    text=folded(text).replace('\u2019',"'")
    text=text.replace("don't",'do not').replace('not only','also')
    # A buffer name alone is not an operating-phase request.
    text=re.sub(r'\b(?:binding|elution)[ -]+buffers?\b','buffer',text)
    text=re.sub(r"\btampons?\s+(?:de\s+liaison|d[' ]elution)\b",'tampon',text)
    positive=set();negative=set()
    clauses=re.split(r'[.!?;]|\b(?:but|mais|then|puis)\b',text)
    for clause in clauses:
        parts=re.split(r'\b(?:rather than|plutot que)\b',clause,maxsplit=1)
        for partno,part in enumerate(parts):
            # Covers coordinated exclusions up to the clause boundary.
            neg=re.search(r"\b(?:not|no|neither|never|without|excluding|sans|pas\s+de|ni|ne\s+(?:les\s+)?(?:demande|remplace))\b",part)
            for phase in PHASES:
                for alias in config['signals'][phase]:
                    for hit in re.finditer(phrase_pattern(alias),part):
                        excluded=partno==1 or (neg is not None and hit.start()>=neg.start())
                        (negative if excluded else positive).add(phase)
    conflicts=positive & negative
    # Explicit positive mentions are retained, but ambiguity is observable.
    return {'positive':sorted(positive),'negative':sorted(negative),
            'conflicts':sorted(conflicts)}


def navigation_plan(text,config):
    has=lambda key:matched(text,config,key)
    phases=phase_mentions(text,config)
    routes={};reasons=[];limitations=[]
    def add(group,roles,reason):
        routes.setdefault(group,[])
        routes[group]=list(dict.fromkeys(routes[group]+roles))
        reasons.append(reason)
    unknown=has('unknown') and has('purification_context')
    if unknown:add('general',GENERAL,'uncertainty_context')
    elif has('general_reason') and sum(has(k) for k in ('albumin','transferrin','immunoglobulin'))>=2:
        add('general',GENERAL,'general_characteristics')
    elif has('direct_use') and not has('blue'):
        add('general',['applicability'],'application_scope')
    conditional=has('iex') and has('source_condition')
    if conditional:
        add('general',['method_selection'],'conditional_iex_source_boundary')
        limitations.append({'group':'general','role':'conditional_iex','reason':'source_not_approved'})
    if has('screen'):
        add('bovine',['screening_advice','scoped_example','source_context','method_alternatives'],'screening')
    elif has('bovine') and has('immunoglobulin') and not has('blue') and 'general' not in routes:
        add('bovine',['source_context','method_alternatives'],'immunoglobulin_context')
    if has('albumin') and has('transferrin') and (has('iex') or has('hic')):
        roles=['albumin_specific_alternative'] if has('blue') else []
        # A Blue alternative question does not request every other method's details.
        if not has('blue') or has('method_explanation'):
            roles+=['method_alternatives']
            if has('iex'):roles.append('residual_contaminants')
            if has('hic'):roles.append('conditional_hic')
        add('albumin',roles,'contaminant_methods')
    if has('blue'):
        if has('pressure'):
            add('blue',['cross_page_protocol_scope','protocol_heading'],'unsupported_pressure_scope')
            limitations.append({'group':'blue','role':'maximum_pressure','reason':'not_in_selected_corpus'})
        else:
            roles=[]
            if has('formulation') or (has('buffer') and not phases['positive']):
                roles.append('buffer_alternatives')
            roles += [PHASES[k] for k in PHASES if k in phases['positive']]
            if has('completion') and 'sample_application' in roles and 'washing' not in phases['negative']:
                roles.append('wash_conditions')
            if roles:add('blue',roles,'product_roles')
            elif phases['negative']:add('blue',['cross_page_protocol_scope','protocol_heading'],'excluded_phases_only')
            else:add('blue',BLUE,'product_applicability')
    # Do not assume every HiTrap is Blue. Resolve a note only if source role
    # support identifies exactly one eligible family during retrieval.
    discovery=has('generic_hitrap') and has('drop_note') and not has('blue')
    return {'reason':'+'.join(dict.fromkeys(reasons)) or 'no_explicit_scope',
            'routes':[{'group':g,'roles':r} for g,r in routes.items() if r],
            'phase_exclusion_applied':bool(phases['negative']), 'phase_mentions':phases,
            'source_limitations':limitations,'discover_footnote_family':discovery}


class CompositionalContextIndex(ScopedContextIndex):
    def retrieve(self,text,count_tokens):
        c=self.config;ranking=self.index.search(text,len(self.docs))
        plan=navigation_plan(text,c);queues=[];unavailable=[]
        if plan['discover_footnote_family']:
            supported=[]
            for group,members in self.members.items():
                notes=[pid for pid in members if c['source_roles'][pid]=='sample_application_footnote' and eligible(self.passages,pid)]
                supported_parent=any(h['passage_id'] in members and c['source_roles'][h['passage_id']] in ('sample_application','sample_application_footnote') for h in ranking)
                if notes and supported_parent:supported.append(group)
            if len(supported)==1:
                plan['routes'].append({'group':supported[0],'roles':['sample_application_footnote','sample_application']})
                plan['reason']='unique_supported_footnote_family'
            else:
                unavailable.append({'reason':'ambiguous_or_unsupported_footnote_family','groups':supported})
        for route in plan['routes']:
            members=self.members[route['group']];selected=[]
            if not any(h['passage_id'] in members for h in ranking):
                unavailable.append({'group':route['group'],'reason':'no_positive_scope_hit'});continue
            for role in route['roles']:
                ids=[pid for pid in self.passages if pid in members and c['source_roles'][pid]==role]
                if not ids or any(not eligible(self.passages,pid) for pid in ids):
                    unavailable.append({'group':route['group'],'role':role,'reason':'source_missing_or_quarantined'})
                    if route['group']=='blue':
                        selected += [pid for pid in self.passages if pid in members and
                            c['source_roles'][pid] in ('cross_page_protocol_scope','protocol_heading') and eligible(self.passages,pid)]
                else:selected+=ids
            queues.append(list(dict.fromkeys(selected)))
        if not plan['routes'] and ranking and not plan['discover_footnote_family']:
            # Unknown queries get bounded lexical support, never disallowed phases.
            top=ranking[0];family=next((g for g,ids in self.members.items() if top['passage_id'] in ids),None)
            banned={PHASES[k] for k in phases_negative(plan)}
            if 'loading' in phases_negative(plan):banned.add('sample_application_footnote')
            queues=[[h['passage_id'] for h in ranking if h['score']>=top['score']*c['fallback_relative_score'] and
                     (family is None or h['passage_id'] in self.members[family]) and
                     c['source_roles'][h['passage_id']] not in banned]]
        # Round-robin route families before the cap; one named family cannot
        # consume the entire seed budget before another is represented.
        ordered=list(dict.fromkeys(pid for row in zip_longest(*queues) for pid in row if pid is not None))
        seeds=ordered[:c['top_k']];dropped=ordered[c['top_k']:]
        result=assemble(self.passages,[{'passage_id':pid} for pid in seeds],count_tokens,c['max_tokens'])
        limitations=plan['source_limitations']
        return {'hits':ranking[:c['top_k']],'scope_selected_seeds':seeds,'navigation_plan':plan,
                'unavailable_source_roles':unavailable,'source_limitations':limitations,
                'source_navigation_over_top_k':dropped,
                'navigation_complete':not unavailable and not dropped and not result['excluded'] and not plan['phase_mentions']['conflicts'],
                'source_support_complete':not unavailable and not limitations,
                'filtered_ranked_ids':[h['passage_id'] for h in ranking if h['passage_id'] not in seeds],
                'assembled':result}


def phases_negative(plan):
    return set(plan['phase_mentions']['negative'])-set(plan['phase_mentions']['positive'])
