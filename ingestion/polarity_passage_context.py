"""Opt-in v05 development variant; v04 and all frozen outputs stay unchanged.

The retrieval executor is intentionally versioned with its planner: changing the
frozen executor to introduce a hook would invalidate earlier method locks.
"""
import re
from itertools import zip_longest

from ingestion.lexical_section_context import folded, phrase_pattern
from ingestion.local_passage_retrieval import assemble, eligible
from ingestion.scoped_passage_context import ScopedContextIndex, matched
from ingestion.compositional_passage_context import PHASES, BLUE, GENERAL


def clauses(text):
    """Normalize a bounded grammar; retain clause boundaries for auditability."""
    text=folded(text).replace("\u2019", "'")
    text=text.replace("don't", 'do not').replace('not only', 'also')
    text=text.replace('pas seulement','aussi').replace('non seulement','aussi')
    return [c.strip() for c in re.split(
        r"[.!?;]|\b(?:but|mais|then|puis|rather than|plutot que)\b", text) if c.strip()]


def buffer_mask(text):
    """Mask complete noun phrases, including coordinated FR/EN buffer names."""
    text=re.sub(r"\b(?:binding\s+and\s+)?elution[ -]+buffers?\b", 'buffer',text)
    text=re.sub(r"\bbinding[ -]+buffers?\b", 'buffer',text)
    return re.sub(r"\btampons?\s+(?:de\s+liaison\s+et\s+)?d[' ]elution\b|\btampons?\s+de\s+liaison\b", 'tampon',text)


PREFIX_NEG=r"\b(?:not|no|neither|never|without|excluding|exclude|excludes|exclus|exclure|ecarte|ecarter|sans|pas\s+de|ni|ne\s+(?:les\s+)?(?:demande|remplace))\b"
POST_NEG=r"\b(?:outside\s+(?:the\s+)?scope|out\s+of\s+scope|hors\s+(?:du\s+)?perimetre|(?:is|are)\s+not\s+(?:requested|needed)|ne\s+sont\s+pas\s+demandes|n'est\s+pas\s+demande)\b"


def mentions(text,config,keys,mask_buffers=False):
    """Attach polarity to bounded clauses, not to whole-document keywords.

    Prefix exclusions affect following mentions, postposed exclusions affect
    preceding mentions in the same clause. Coordinated positive and negative
    clauses remain separate. Unsupported constructions remain observable limits.
    """
    pos=set();neg=set();trace=[]
    # Preserve the established explicit contrast semantics.
    text=re.sub(r'\b(?:rather than|plutot que)\b', 'without', folded(text))
    for clause in clauses(text):
        part=buffer_mask(clause) if mask_buffers else clause
        prefix=re.search(PREFIX_NEG,part)
        post=re.search(POST_NEG,part)
        leave=re.search(r"\b(?:leave|laisse|laisser)\b.*(?:\bout\b|de\s+cote)",part)
        found=[]
        for key in keys:
            for alias in config['signals'][key]:
                for hit in re.finditer(phrase_pattern(alias),part):
                    negative=bool((prefix and hit.start()>=prefix.start()) or
                                  (post and hit.end()<=post.start()) or leave)
                    (neg if negative else pos).add(key)
                    found.append({'signal':key,'alias':alias,'negative':negative})
        if found:trace.append({'clause':clause,'mentions':found})
    return {'positive':sorted(pos),'negative':sorted(neg),'conflicts':sorted(pos & neg),'clauses':trace}


def phase_mentions(text,config):
    return mentions(text,config,PHASES,mask_buffers=True)


def navigation_plan(text,config):
    has=lambda key:matched(text,config,key)
    phases=phase_mentions(text,config)
    products=mentions(text,config,['blue'])
    blue='blue' in products['positive']
    routes={};reasons=[];limitations=[]
    def add(group,roles,reason):
        routes[group]=list(dict.fromkeys(routes.get(group,[])+roles));reasons.append(reason)
    if has('unknown') and has('purification_context'):
        add('general',GENERAL,'uncertainty_context')
    elif has('general_reason') and sum(has(k) for k in ('albumin','transferrin','immunoglobulin'))>=2:
        add('general',GENERAL,'general_characteristics')
    # A separate product request must not suppress a direct-use condition.
    if has('direct_use'):add('general',['applicability'],'application_scope')
    if has('iex') and has('source_condition'):
        add('general',['method_selection'],'conditional_iex_source_boundary')
        limitations.append({'group':'general','role':'conditional_iex','reason':'source_not_approved'})
    if has('screen'):
        add('bovine',['screening_advice','scoped_example'],'screening')
        if has('bovine') and has('immunoglobulin'):
            add('bovine',['method_alternatives'],'named_immunoglobulin_methods')
    elif has('bovine') and has('immunoglobulin') and not blue and 'general' not in routes:
        add('bovine',['source_context','method_alternatives'],'immunoglobulin_context')
    if has('albumin') and has('transferrin') and (has('iex') or has('hic')):
        roles=['albumin_specific_alternative'] if blue else []
        if not blue or has('method_explanation'):
            roles+=['method_alternatives']
            if has('iex'):roles.append('residual_contaminants')
            if has('hic'):roles.append('conditional_hic')
        add('albumin',roles,'contaminant_methods')
    conflicts=phases['conflicts']+products['conflicts']
    if blue:
        if conflicts:
            # Withhold operating instructions until contradictory scope is clarified.
            add('blue',['cross_page_protocol_scope','protocol_heading'],'clarification_required')
        else:
            roles=[]
            if has('formulation') or (has('buffer') and not phases['positive']):
                roles.append('buffer_alternatives')
            roles += [PHASES[k] for k in PHASES if k in phases['positive']]
            if has('completion') and 'sample_application' in roles and 'washing' not in phases['negative']:
                roles.append('wash_conditions')
            if has('pressure'):
                roles+=['cross_page_protocol_scope','protocol_heading']
                limitations.append({'group':'blue','role':'maximum_pressure','reason':'not_in_selected_corpus'})
            if roles:add('blue',roles,'product_roles')
            elif phases['negative']:add('blue',['cross_page_protocol_scope','protocol_heading'],'excluded_phases_only')
            else:add('blue',BLUE,'product_applicability')
    return {'reason':'+'.join(dict.fromkeys(reasons)) or 'no_explicit_scope',
            'routes':[{'group':g,'roles':r} for g,r in routes.items() if r],
            'phase_exclusion_applied':bool(phases['negative']),'phase_mentions':phases,
            'product_mentions':products,'clarification_required':bool(conflicts),
            'source_limitations':limitations,
            'discover_footnote_family':has('generic_hitrap') and has('drop_note') and not blue and not products['negative']}


class CompositionalContextIndex(ScopedContextIndex):
    def retrieve(self,text,count_tokens):
        c=self.config;ranking=self.index.search(text,len(self.docs))
        plan=navigation_plan(text,c);queues=[];unavailable=[]
        if 'blue' in plan['product_mentions']['negative'] and 'blue' not in plan['product_mentions']['positive']:
            ranking=[h for h in ranking if h['passage_id'] not in self.members['blue']]
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
                'navigation_complete':not unavailable and not dropped and not result['excluded'] and not plan['clarification_required'],
                'source_support_complete':not unavailable and not limitations,
                'filtered_ranked_ids':[h['passage_id'] for h in ranking if h['passage_id'] not in seeds],
                'assembled':result}


def phases_negative(plan):
    return set(plan['phase_mentions']['negative'])-set(plan['phase_mentions']['positive'])
