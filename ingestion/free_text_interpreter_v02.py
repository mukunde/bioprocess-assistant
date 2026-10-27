"""Candidate v02: bounded EN/FR grammar, separate from the frozen v01.

Deliberate versioned snapshot: v01 source bytes remain replayable.
Never reads example/gold records.

All matching uses a mapped view; every stored origin uses the untouched string.
Unrecognized substantive text is retained and prevents a complete-service claim.
"""
from copy import deepcopy
import re
import unicodedata

from ingestion.free_text_contract import Contracts, FreeTextValidationError, LedgerBuilder, na, slot


class MappedText:
    def __init__(self, text):
        self.original=text;chars=[];self.starts=[];self.ends=[]
        # Group combining marks with their preceding code point so decomposed
        # characters retain the complete original code-point interval.
        for m in re.finditer(r'.[\u0300-\u036f]*', text, re.DOTALL):
            value=unicodedata.normalize('NFKD',m.group().casefold())
            for c in value:
                if not unicodedata.combining(c):
                    chars.append({'’':"'",'–':'-','—':'-'}.get(c,c));self.starts.append(m.start());self.ends.append(m.end())
        self.text=''.join(chars)

    def span(self, start, end):
        return self.starts[start], self.ends[end-1]


PHASES = {'washing':r'\b(?:wash(?:ing)?|lavage)\b',
          'sample_application':r'\b(?:load(?:ing)?|chargement|application de l.echantillon)\b',
          'elution':r'\b(?:elution)\b', 'equilibration':r'\b(?:equilibration|equilibrage)\b'}
SELECTORS = {'stopping_criteria':r'\b(?:stopping criteria|(?:les )?criteres de fin(?: du lavage)?|fin du lavage)\b',
             'flow_rate':r'\b(?:flow(?: rate)?|debit)\b',
             'buffer_formulation':r'\b(?:formulations?|composition(?:s)?)\b',
             'column_volumes':r'\b(?:column volumes?|volumes? de colonne|cv)\b',
             'maximum_pressure':r'\b(?:maximum pressure|pression maximale)\b',
             'principle':r'\b(?:principle|principe)(?: general| de separation)?\b'}
COMMAND = r'\b(?:give|explain|list|liste|listez|what|which|donne|donnez|quel|quelle|quels|quelles|explique|expliquez|demande|asks?|(?:i\s+)?need|il\s+me\s+faut|veux|souhaite)\b'
EXCLUDE = r"(?:\b(?:exclude|exclus|exclure|excluez)\b|\bdo not (?:include|give)\b|\bn'exclus pas\b|\bne pas inclure\b|\bne donnez? pas\b|\bdo not exclude\b|\bdo not choose\b|\bne choisis pas\b)"
SCOPE = r"\b(?P<id>[a-z])\b\s*(?::|(?:is named|est nomme|on|sur|utilise|uses?|demande|asks? for)\b)"
LABEL = r"\b[a-z]\b\s*(?::|(?:is named|est nomme|on|sur|utilise|uses?)\b)\s*([^,;.!?]+?)(?=\s+(?:but|mais|give|donne|and|et)\b|[,;.!?]|$)"
MINOR_FACT = r"(?:minor contaminants (?:do not interfere|interfere) with the intended application|(?:les )?contaminants mineurs (?:n'interferent pas|interferent) avec l'application prevue)"


def instruction_spans(text):
    """Split instructions without changing the text or its offset coordinate space.

    A restriction/policy directive never consumes the preceding positive request.
    Conversely a later positive command is not parsed as part of a restriction.
    """
    for sentence in re.finditer(r'.+?(?:[.!?;](?!\d)|$)',text,re.DOTALL):
        clause=sentence.group();base=sentence.start()
        markers=list(re.finditer(EXCLUDE+r'|\b(?:treat|declare|considere|declarez)\b',clause))
        starts={0,*[m.start() for m in markers]}
        for command in re.finditer(COMMAND,clause):
            if any(m.start()<=command.start()<m.end() for m in markers):continue
            if any(m.end()<=command.start() for m in markers):
                # Keep a named owner attached to its following command.
                scopes=[s for s in re.finditer(SCOPE,clause) if s.start()<=command.start()<s.end()]
                starts.add(scopes[-1].start() if scopes else command.start())
        starts=sorted(starts)
        for i,start in enumerate(starts):
            end=starts[i+1] if i+1<len(starts) else len(clause)
            if clause[start:end].strip():yield base+start,base+end


def restriction_affects(exclusion, unit):
    owners=([exclusion['task_id']] if exclusion['task_id'] is not None else exclusion['candidate_task_ids'])
    if not owners:return True
    owner=unit['owner']
    if owner['state']=='resolved':return owner['task_id'] in owners
    return not owner['candidate_task_ids'] or bool(set(owner['candidate_task_ids'])&set(owners))


class DeterministicInterpreter:
    def __init__(self, core, contracts=None):
        self.core=core;self.contracts=contracts or Contracts(core.adapter.root)

    def interpret(self, envelope, request_id, identity):
        self.contracts.validate('input', envelope)
        # JSON Schema accepts lone surrogates; exact UTF-8 encoding must not.
        b=LedgerBuilder(envelope,request_id,identity);l=b.value
        view=MappedText(envelope['text']);text=view.text
        scope_origins={};current=[];ambiguous=[];current_phase=None;phase_origin=None;ambiguity_origins=[];unknown=[]
        products=self.core.adapter.catalog.products
        labels=sorted(products, key=len, reverse=True)
        product_pattern=re.compile(r'(?<!\w)(?:'+ '|'.join(re.escape(MappedText(x).text) for x in labels)+r')(?!\w)')

        def residual(clause):
            """Closed grammar coverage, not a bag-of-keywords success heuristic.

            Fixed function words only are ignored. Any remaining substantive token
            is kept as an unresolved clause, including in otherwise recognized text.
            """
            masked=list(clause)
            patterns=[SCOPE,LABEL,r'\b(?:for|pour)\s+[a-z]\b',product_pattern.pattern,COMMAND,EXCLUDE,*PHASES.values(),*SELECTORS.values(),
                r'\b(?:in documentary |dans le )?scenario(?: documentaire)?\s+[a-z]\b',r'\b[a-z] and [a-z] are (?:separate|distinct)\b',
                r"je parle de l'une de ces deux preparations sans preciser si c'est [a-z] ou [a-z]",
                r'je ne precise pas la preparation',r"s'applique a cette preparation",
                r'but i have not specified whether this exclusion concerns [a-z] or [a-z]',
                r'column field says\s+(?:unknown|\d+(?:[.,]\d+)?\s*ml)',
                r'\bson (?=volume de (?:la )?colonne(?: est)?\s+\d+(?:[.,]\d+)?\s*ml\b)',
                r'(?:column(?: size| volume)?(?: is)?|(?:format|volume) de (?:la )?colonne(?: est)?)\s+(?:unknown|inconnu|\d+(?:[.,]\d+)?\s*ml)',
                r'(?:my observed flow is|(?:le )?debit observe est(?: de)?)\s+\d+(?:[.,]\d+)?\s*ml/min',
                r'(?:contient|available sample volume is)\s+\d+(?:[.,]\d+)?\s*ml(?: disponibles)?',
                # Recognized wrappers only, not a general stop-word whitelist.
                r"l'echantillon\s+contient\s+\d+(?:[.,]\d+)?\s*ml(?: disponibles)?",
                r'\bdoes the manual give\b',r'\ble manuel indique-t-il\b',
                r'\ble volume de lavage en (?=volumes? de colonne\b)',
                r"\bd'(?=(?:equilibrage|elution)\b)",
                r'(?:loaded volume is|(?:le )?volume charge est)\s+(?:unknown|inconnu)',
                MINOR_FACT,
                r'omit every mandatory warning',r'sans (?:les )?avertissements obligatoires',
                r'(?:treat|declare|considere|declarez)\s+e\d+-[a-z]+\s+(?:as )?(?:approved|approuve)',
                r'do not choose a purification technique for this sample',
                r'\bnot only\b',
                r'\b(?:binding[- ]buffers?|buffers?|tampons?|binding|fixation|liaison)\b',r'\b(?:general separation|general|operating|operatoire)\b',
                r"l'echantillon etiquete",r'\b(?:sec|iex|hic)\b']
            for pat in patterns:
                for match in re.finditer(pat,clause):
                    masked[match.start():match.end()]=' '*(match.end()-match.start())
            rest=''.join(masked)
            fillers={'a','for','pour','on','of','the','le','la','les','du','de','des','au','aux','l','un','une',
                     'and','et','but','mais','also','only','both','its','that','this','ce','cette','ces','two','deux',
                     'preparation','preparations','independently','separately','independamment','separement','please','svp','uniquement'}
            return any(m.group() not in fillers for m in re.finditer(r'[\w]+',rest))

        def origin(start,end):
            return b.origin(*view.span(start,end))

        def add_task(tid, oid):
            found=next((t for t in l['tasks'] if t['task_id']==tid),None)
            if found:return found
            task={'task_id':tid,'order':len(l['tasks']),'product':slot(),'column':slot(),'facts':[],'assertion_ids':[]}
            l['tasks'].append(task);scope_origins[tid]=oid
            return task

        def fragment(start,end,units,detail):
            if start>=end:return
            oid=origin(start,end);fid='f'+str(len(l['unresolved_fragments'])+1)
            iid=b.issue('incomplete_inventory',detail,[oid],units,[fid])
            l['unresolved_fragments'].append({'fragment_id':fid,'origin_ids':[oid],'may_contain_request':True,'issue_ids':[iid]})
            l['inventory_complete']=False

        # Boundaries exclude decimal punctuation. A semicolon is also a clause.
        for start,end in instruction_spans(text):
            clause=text[start:end];base=start
            if residual(clause):unknown.append((start,end))
            active=[];scope_matches=list(re.finditer(SCOPE,clause))
            # Named documentary scenario and coordinated preparations.
            sm=re.search(r'\b(?:scenario(?: documentaire)?|preparation)\s+([a-z])\b',clause)
            if sm:
                tid=sm.group(1).upper();add_task(tid,origin(base+sm.start(),base+sm.end()));active.append(tid)
            both=re.search(r'\b([a-z]) and ([a-z]) are (?:separate|distinct)\b',clause)
            if both:
                for tid in (both.group(1).upper(),both.group(2).upper()):
                    add_task(tid,origin(base+both.start(),base+both.end()));active.append(tid)
            for sm in scope_matches:
                tid=sm.group('id').upper()
                add_task(tid,origin(base+sm.start(),base+sm.end()));active.append(tid)
            explicit_owners=list(re.finditer(r'\b(?:for|pour)\s+([a-z])\b',clause))
            for sm in explicit_owners:
                tid=sm.group(1).upper()
                add_task(tid,origin(base+sm.start(),base+sm.end()));active.append(tid)
            active=list(dict.fromkeys(active))
            is_ban=bool(re.search(EXCLUDE,clause))
            if active and not is_ban:
                if active!=current:current_phase=None;phase_origin=None
                current=active;ambiguous=[];ambiguity_origins=[]
            # Qualified labels only in positive context. A near-match is never
            # repaired by selecting the known substring of a longer label.
            if not is_ban:
                pmatches=list(product_pattern.finditer(clause));accepted_products=0
                declared=list(re.finditer(LABEL,clause))
                for pm in pmatches:
                    # Reject a trailing name token or unsupported format rather than
                    # selecting the base catalog label from a misspelled full label.
                    tail=clause[pm.end():]
                    # A catalog label is only accepted when it is the complete
                    # explicit label slot, not a prefix of an unknown name.
                    container=next((d for d in declared if d.start(1)<=pm.start()<d.end(1)),None)
                    if container:
                        da,dz=container.span(1)
                        while da<dz and clause[da].isspace():da+=1
                        while dz>da and clause[dz-1].isspace():dz-=1
                        if (pm.start(),pm.end())!=(da,dz):continue
                    if re.match(r'\s+(?:\d+(?:[.,]\d+)?\s*ml|xtra|plus|typo)\b',tail):continue
                    accepted_products+=1
                    owners=active or current
                    if scope_matches and not both:
                        preceding=[sm for sm in scope_matches if sm.start()<pm.start()]
                        owners=[preceding[-1].group('id').upper()] if preceding else owners
                    oid=origin(base+pm.start(),base+pm.end());label=envelope['text'][view.span(base+pm.start(),base+pm.end())[0]:view.span(base+pm.start(),base+pm.end())[1]]
                    for tid in owners:
                        task=add_task(tid,oid)
                        aid=b.assertion('product',[tid],oid,label)
                        if task['product']['state']=='provided' and task['product']['value']!=label:
                            b.issue('conflicting_assertions','Multiple positive labels require clarification; no last-wins replacement.',[oid],blocking=False)
                        else:task['product']=slot(label)
                        task['assertion_ids'].append(aid)
                        ti=l['tasks'].index(task);b.fields(task['product'],f'/tasks/{ti}/product',[oid])
                # Explicit unknown/misspelled identity: pass literal to catalog, not fuzzy selection.
                if not accepted_products:
                    um=re.search(LABEL,clause)
                    if um and (active or current) and not re.search(COMMAND,um.group(1)):
                        a,z=um.span(1)
                        while a<z and clause[a].isspace():a+=1
                        while z>a and clause[z-1].isspace():z-=1
                        raw=envelope['text'][view.span(base+a,base+z)[0]:view.span(base+a,base+z)[1]]
                        if raw and not raw.endswith('preparations'):
                            oid=origin(base+a,base+z)
                            for tid in active or current:
                                t=add_task(tid,oid)
                                if t['product']['state']!='provided':t['product']=slot(raw)
                                t['assertion_ids'].append(b.assertion('product',[tid],oid,raw))
                                b.fields(t['product'],f"/tasks/{l['tasks'].index(t)}/product",[oid])
            # Explicit column and observations are distinct, never derived from a label.
            column=re.search(r'(?:column field says|column(?: size| volume)?(?: is)?|(?:format|volume) de (?:la )?colonne(?: est)?)\s+(?:(\d+(?:[.,]\d+)?)\s*ml\b|(unknown|inconnu)\b)',clause)
            for tid in current:
                task=next(t for t in l['tasks'] if t['task_id']==tid);ti=l['tasks'].index(task)
                if column:
                    oid=origin(base+column.start(),base+column.end());q={'value':column.group(1).replace(',','.'),'unit':'mL'} if column.group(1) else None
                    if task['column']['state']=='not_supplied':task['column']=slot({'bed_volume':q}) if q else slot(state='unknown')
                    task['assertion_ids'].append(b.assertion('column',[tid],oid,q))
                    b.fields(task['column'],f'/tasks/{ti}/column',[oid])
                fact_patterns=[('observed_flow',r'(?:my observed flow is|(?:le )?debit observe est(?: de)?)\s+(\d+(?:[.,]\d+)?)\s*ml/min', 'mL/min'),
                               ('sample_volume',r'(?:contient|available sample volume is)\s+(\d+(?:[.,]\d+)?)\s*ml(?: disponibles)?','mL'),
                               ('loaded_volume',r'(?:loaded volume is|(?:le )?volume charge est)\s+(unknown|inconnu)','mL')]
                for key,pat,unit in fact_patterns:
                    for fm in re.finditer(pat,clause):
                        oid=origin(base+fm.start(),base+fm.end());val=None if fm.group(1) in ('unknown','inconnu') else {'value':fm.group(1).replace(',','.'),'unit':unit}
                        fact={'key':key,'input_role':'user_observation','value':slot(val,'unknown' if val is None else 'provided')}
                        task['facts'].append(fact);task['assertion_ids'].append(b.assertion('fact',[tid],oid,val))
                        b.fields(fact,f"/tasks/{ti}/facts/{len(task['facts'])-1}",[oid])
                fm=re.search(MINOR_FACT,clause)
                if fm:
                    oid=origin(base+fm.start(),base+fm.end());val=not bool(re.search(r"do not|n'interferent pas",fm.group()))
                    fact={'key':'minor_contaminants_interfere','input_role':'documentary_scenario','value':slot(val)}
                    task['facts'].append(fact);task['assertion_ids'].append(b.assertion('fact',[tid],oid,val))
                    b.fields(fact,f"/tasks/{ti}/facts/{len(task['facts'])-1}",[oid])
            am=re.search(r"je parle.*sans preciser.*|not specified whether.*|ne precise pas.*|not specified the preparation.*",clause)
            if am:
                ambiguous=list(current);current=[]
                ambiguity_origins=[origin(base+am.start(),base+am.end())]
            # Attempted source approval is a rejected directive, never a selector.
            override=re.search(r'(?:treat|declare|considere|declarez).*(?:e\d+-[a-z]+).*(?:approved|approuve)',clause)
            if override:
                oid=origin(base+override.start(),base+override.end())
                b.issue('policy_override_rejected','Caller text cannot approve a documentary source.',[oid],blocking=False)
                continue
            if is_ban:
                negated=bool(re.search(r"n'exclus pas|do not exclude",clause))
                phases=[p for p,pat in PHASES.items() if re.search(pat,clause)]
                # Anaphoric 'that flow' remains ambiguous if scope is explicit unknown.
                if not phases and re.search(r'that flow|ce debit',clause):
                    antecedents={u['stage']['code'] for u in l['requested_units'] if u['information']=='flow_rate' and u['stage']}
                    if len(antecedents)==1:phases=list(antecedents)
                oid=origin(base+re.search(EXCLUDE,clause).start(),end)
                owners=active or current or ambiguous
                unresolved=bool(re.search(r'not specified whether|sans preciser',clause)) or len(owners)!=1
                selectors=[info for _,info in sorted((m.start(),info) for info,pat in SELECTORS.items() for m in re.finditer(pat,clause))]
                selectors=list(dict.fromkeys(selectors))
                selection=selectors or 'all'
                selector={'kind':'operating_phase','code':phases[0],'information':selection} if len(phases)==1 else None
                if re.search(r'do not choose|ne choisis pas',clause) and re.search(r'technique',clause):
                    selector={'kind':'general_topic','code':'method_selection','information':['clarification_context']}
                # A coordinated phase-only ban can be faithfully represented as
                # typed restrictions on the same known owner, never a global ban.
                typed=[selector]
                if len(phases)>1 and not selectors:
                    typed=[{'kind':'operating_phase','code':p,'information':'all'} for p in phases]
                for selector in typed:
                    x={'exclusion_id':'x'+str(len(l['exclusions'])+1),'task_id':owners[0] if len(owners)==1 and not unresolved else None,
                       'candidate_task_ids':owners if unresolved else [],'target_item_ids':[],
                       'polarity':'negated_ban' if negated else 'active_ban','active':not negated,'selector':selector,'origin_ids':[oid]}
                    l['exclusions'].append(x);b.assertion('exclusion',owners,oid,'negated_ban' if negated else 'active_ban')
                    if not negated and (unresolved or selector is None):
                        affected=[u for u in l['requested_units'] if restriction_affects(x,u)]
                        b.issue('ambiguous_restriction_scope','Restriction cannot be assigned or represented without changing meaning.',[oid],affected)
                continue
            request=bool(re.search(COMMAND,clause))
            if not request:
                # Prefix for an explicitly unresolved following washing question.
                phases=[p for p,pat in PHASES.items() if re.search(pat,clause)]
                if len(phases)==1:
                    current_phase=phases[0]
                    match=re.search(r'pour le '+PHASES[current_phase]+'|'+PHASES[current_phase],clause)
                    phase_origin=origin(base+match.start(),base+match.end())
                continue
            phase_matches=sorted((m.start(),m.end(),p) for p,pat in PHASES.items() for m in re.finditer(pat,clause))
            matches=sorted((m.start(),m.end(),info) for info,pat in SELECTORS.items() for m in re.finditer(pat,clause))
            new=[]
            for match_index,(a,z,info) in enumerate(matches):
                # Only positive requests; observed-flow assertions preceding the command are not selectors.
                command=re.search(COMMAND,clause)
                if a<command.start():continue
                # Bind local explicit owners to this selector, rather than using
                # every owner mentioned anywhere in the sentence.
                previous_end=matches[match_index-1][1] if match_index else re.search(COMMAND,clause).end()
                next_start=matches[match_index+1][0] if match_index+1<len(matches) else len(clause)
                local_after=[m for m in explicit_owners if z<=m.start()<next_start and
                             not re.search(r'\b(?:and|et|but|mais)\b',clause[z:m.start()])]
                # A preceding 'for X' applies locally only after a conjunction or
                # before the first selector; a suffix of the previous selector
                # must not be reused as this one's prefix.
                local_before=[m for m in explicit_owners if previous_end<=m.start()<a and
                              (match_index==0 or re.search(r'\b(?:and|et|but|mais)\b',clause[previous_end:m.start()]))]
                local_owners=list(dict.fromkeys(m.group(1).upper() for m in local_after or local_before))
                candidates=local_owners or (active or current)
                if re.search(r'for both|pour les deux',clause):candidates=active or current
                general=info=='principle'
                if general:stage={'kind':'general_topic','code':'method_selection'}
                elif info=='buffer_formulation':stage={'kind':'preparation','code':'buffer_preparation'}
                elif info=='maximum_pressure':
                    # Do not inherit washing from an adjacent flow selector.
                    # An explicitly attached phase is retained, even if the
                    # documentary catalog cannot support that combination.
                    before=[x for x in phase_matches if previous_end<=x[0]<a
                            and not re.search(r'\b(?:and|et|but|mais)\b',clause[x[1]:a])]
                    after=[x for x in phase_matches if z<=x[0]<next_start
                           and re.fullmatch(r'\s+(?:for|of|de|du)\s+(?:le\s+|la\s+|l.)?',clause[z:x[0]])]
                    attached=after or before
                    stage=({'kind':'operating_phase','code':attached[-1][2]} if attached
                           else {'kind':'general_topic','code':'operating_limits'})
                else:
                    preceding=[x for x in phase_matches if x[0]<=a]
                    next_info=matches[match_index+1][0] if match_index+1<len(matches) else len(clause)
                    following=[x for x in phase_matches if a<=x[0]<next_info and x[0]-z<35]
                    explicit_right=[x for x in following if re.search(r'\b(?:for|of|de|du)\s+(?:l.|le |la )?$',clause[z:x[0]])]
                    phase=explicit_right[0][2] if explicit_right else preceding[-1][2] if preceding else following[0][2] if following else current_phase
                    stage={'kind':'operating_phase','code':phase} if phase else None
                oid=origin(base+a,base+z);support=[oid];stage_oid=None
                if stage and phase_matches and not general:
                    for x,y,p in phase_matches:
                        if p==stage['code']:
                            stage_oid=origin(base+x,base+y);support.append(stage_oid)
                if stage and not phase_matches and current_phase==stage['code']:
                    if phase_origin:stage_oid=phase_origin;support.append(phase_origin)
                support += [origin(base+m.start(),base+m.end()) for m in local_after or local_before]
                both_requested=bool(re.search(r'for both|pour les deux',clause))
                owner_candidates=list(ambiguous)
                if len(candidates)>1 and not both_requested:
                    owner_candidates=list(candidates);owners=[None]
                else:owners=candidates if candidates else [None]
                for tid in owners:
                    owner={'state':'resolved','task_id':tid,'candidate_task_ids':[]} if tid else {'state':'unresolved','task_id':None,'candidate_task_ids':owner_candidates}
                    subject=[tid] if tid else owner_candidates
                    aid=b.assertion('requested_information',subject,oid,info)
                    if tid:support_for_unit=list(dict.fromkeys(support+[scope_origins[tid]]))
                    else:support_for_unit=list(dict.fromkeys(support+[scope_origins[t] for t in owner_candidates]+ambiguity_origins))
                    aids=[aid]
                    if stage_oid:aids.append(b.assertion('stage',subject,stage_oid,stage['code']))
                    item_id=f'{tid}-{stage["code"]}' if tid and stage else None
                    u={'unit_id':'u'+str(len(l['requested_units'])+1),'order':len(l['requested_units']),'owner':owner,'item_id':item_id,
                       'stage':stage,'information':info,'origin_ids':support_for_unit,'assertion_ids':aids,'issue_ids':[],'dispatch':'project' if tid and stage else 'preblock'}
                    l['requested_units'].append(u);new.append(u)
                    if not tid:b.issue('unresolved_owner','Preparation owner is not specified unambiguously.',support_for_unit,[u])
                    elif not stage:b.issue('unsupported_construction','Requested operating phase is not explicit.',support_for_unit,[u])
                    if general and tid:
                        task=next(t for t in l['tasks'] if t['task_id']==tid)
                        if task['product']['state']=='not_supplied':task['product']=na();task['column']=na()
            if re.search(r'omit.*(?:warning|avertissement)|sans.*avertissement',clause):
                oid=origin(start,end);b.issue('presentation_policy_conflict','Mandatory warnings cannot be suppressed.',[oid],new)
            if not new:unknown.append((start,end))
            used_phases={u['stage']['code'] for u in new if u['stage']}
            # A phase word inside an explicit buffer noun phrase describes its
            # use, not another requested operating step. Do not consume a bare
            # extra 'and elution' merely because a formulation was requested.
            buffer_uses=list(re.finditer(r"\b(?:elution[- ]buffers?|tampon d'elution)\b",clause)) if any(
                u['information']=='buffer_formulation' for u in new) else []
            if any(p not in used_phases and not any(m.start()<=a<z<=m.end() for m in buffer_uses)
                   for a,z,p in phase_matches):
                unknown.append((start,end))
        for start,end in sorted(set(unknown)):
            # Unbounded unknown clauses might carry a restriction. Unlike the
            # reviewed preclassified E12 fixture, runtime prose supplies no proof
            # that the fragment is independent of earlier known requests.
            fragment(start,end,l['requested_units'],'Unsupported substantive text may change scope or add a request; no complete inventory claim.')
        for task in l['tasks']:
            for role in ('product','column'):
                assertions=[a for a in l['assertions'] if a['role']==role and a['subject_candidates']==[task['task_id']]]
                if len({repr(a['normalized_value']) for a in assertions})>1:
                    units=[u for u in l['requested_units'] if u['owner']['task_id']==task['task_id']]
                    b.issue('conflicting_assertions','Repeated context slot cannot preserve every assertion in one structured slot; clarify rather than choose last-wins.',[i for a in assertions for i in a['origin_ids']],units)
        # Apply bans to units parsed later as well. Unresolved scope cannot be guessed.
        for x in l['exclusions']:
            if not x['active']:continue
            if x['task_id'] is None or x['selector'] is None:
                affected=[u for u in l['requested_units'] if restriction_affects(x,u)]
                if affected and not all(u['dispatch']=='preblock' for u in affected):
                    b.issue('ambiguous_restriction_scope','Unresolved restriction affects possible dependent requests.',x['origin_ids'],affected)
        # Add field-specific missing/default and generated-field origins, never broad snapshot fallbacks.
        for ti,t in enumerate(l['tasks']):
            for key in ('product','column'):
                prefix=f'/tasks/{ti}/{key}'
                if not any(f['target_pointer'].startswith(prefix+'/') for f in l['field_origins']):
                    value=t[key];oid=b.origin(reason=prefix+': not stated in this preparation scope.',scope=[scope_origins[t['task_id']]]) if value['state']=='not_supplied' else b.origin(rule='general-principle-context',reason=prefix+': no product or column is required for a general method principle.')
                    b.fields(value,prefix,[oid])
            gen=b.origin();b.fields({'task_id':t['task_id'],'order':t['order']},f'/tasks/{ti}',[gen])
        for ui,u in enumerate(l['requested_units']):b.fields(u,f'/requested_units/{ui}',u['origin_ids'])
        if len(l['tasks'])>16 or len(l['requested_units'])>64:
            raise FreeTextValidationError('Declared intake capacity exceeded; no truncation')
        l['interpretation_status']='partial' if any(u['dispatch']=='project' for u in l['requested_units']) and l['issues'] else 'needs_clarification' if l['issues'] else 'ready'
        self.contracts.check_ledger(l,identity)
        return deepcopy(l)
