"""Versioned local registry around the unchanged documentary handoff (stdlib)."""
from datetime import datetime, timezone
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import shutil
import tempfile
import threading

from demo import documentary as core
from demo import mabselect as selector
from experiments.cytiva import mabselect_handoff_freeze as freeze

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'local-registry-v01'
LOGGER = logging.getLogger(__name__)
LOCKS = {}
LOCKS_GUARD = threading.Lock()
LOCAL = {'mapping':'mapping.json', 'source-index':'source-index.json',
         'withdrawals':'withdrawals.json',
         'activation-decision':'activation-decision.json', 'catalog':'catalog.json'}
CODE = ('serving/__init__.py', 'serving/local_registry.py')


def sha(raw):
    return hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest()


def value_sha(value):
    return hashlib.sha256(core.canonical(value)).hexdigest()


def read(path):
    raw = Path(path).read_bytes()
    if len(raw)>2_000_000:
        raise ValueError('Registry artifact too large')
    def unique(pairs):
        d={}
        for key,value in pairs:
            if key in d:raise ValueError('Duplicate registry key')
            d[key]=value
        return d
    def invalid(_):raise ValueError('Nonfinite registry value')
    return json.loads(raw,object_pairs_hook=unique,parse_constant=invalid)


def identifier(value):
    if not isinstance(value,str) or not core.ID.fullmatch(value):
        raise ValueError('Invalid registry identifier')
    return value


def safe(base,name):
    path=(Path(base)/name).resolve()
    if not path.is_relative_to(Path(base).resolve()):
        raise ValueError('Path outside configured authority root')
    return path


def artifact_id(name):
    return Path(name).parent.name+'-'+Path(name).name.replace('.','-')


def binding(id_,path):
    return {'artifact_id':id_,'sha256':sha(Path(path).read_bytes()),'hash_convention':'sha256_lf'}


def write_new(path,value):
    with Path(path).open('x',encoding='utf-8',newline='\n') as f:
        f.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def withdrawal_content(release_id,inventory):
    return value_sha({'release_id':release_id,'inventory_id':inventory['inventory_id'],
                      'version':inventory['version'],
                      'entries':[{k:v for k,v in e.items() if k!='decision_ref'} for e in inventory['entries']]})


def release_content(release):
    return value_sha({k:v for k,v in release.items() if k not in ('stage','activation_decision_ref')})


def expected_catalog(release_id):
    names=freeze.inventory(ROOT)+[(freeze.PACKAGE/'method-lock.json').as_posix(),*CODE]
    catalog={artifact_id(n):{'namespace':'repository','path':n} for n in names}
    if len(catalog)!=len(names):raise ValueError('Artifact identifier collision')
    catalog.update({k:{'namespace':'release','path':v} for k,v in LOCAL.items()})
    catalog[release_id+'-withdrawal-decision']={'namespace':'release','path':'withdrawal-decision.json'}
    return {'kind':'local_registry_catalog/v1','artifacts':catalog}


def expected_mapping(service,release_id):
    entries=[]
    policies={'Q05':'all_general_alternatives','Q06':'separate_restricted_block',
              'N06':'detergent_alternative','N07':'solvent_alternatives','Q09':'context_only'}
    for scope,key in core.KEYS.items():
        products=list(selector.PRODUCTS) if scope=='Q09' else ['sure','sure_lx'] if scope=='Q06' else ['mabselect','sure','sure_lx']
        context='hydrophobic_deposits' if scope.startswith('N') else 'precipitated_substances'
        conditions=({'kind':'source_text','text':service._passages['E167-H']['quote'],'source_ids':['E167-H']}
                    if scope=='Q09' else {'kind':'all_of','children':[
                        {'kind':'product_in','values':products,'source_ids':['E167-SH'] if scope=='Q06' else ['E167-H']},
                        {'kind':'category_in','values':[context],'source_ids':['E167-LH'] if scope.startswith('N') else ['E167-PH']}]})
        entries.append({'bundle_key':key,'mapping_version':'staging-v1','review_scope':scope,
                        'allowed_products':products,'allowed_contexts':list(selector.CONTEXTS) if scope=='Q09' else [context],
                        'request_items':list(core.ITEMS) if scope=='Q09' else ['cleaning_options','restricted_sequence','followup_buffer_pH'] if scope=='Q06' else ['cleaning_options','followup_buffer_pH'],
                        'role':'clarification_context' if scope=='Q09' else 'procedure',
                        'required_source_ids':selector.REQUIRED[scope].copy(),
                        'review_ref':service._review(scope)['review_artifact'],
                        'conditions':conditions,'alternative_policy':policies[scope]})
    return {'kind':'reviewed_serving_mapping/v1','release_id':release_id,'entries':entries}


def expected_sources(service,release_id):
    ids=sorted(service._registered)
    return {'kind':'reviewed_serving_source_index/v1','release_id':release_id,
            'corpus_id':service._evidence['id'],'pdf_available':False,
            'passages':[service._passage(pid) for pid in ids],
            'reviews':[service._review(s) for s in core.KEYS],
            'source_artifacts':[service._binding('experiments/cytiva/retrieval-pilot-v01/evidence.json')]}


def prepare(data_root,release_id='mabselect-local-v01'):
    """Write a new staged candidate only. Never writes active.json or approval."""
    freeze.verify(environment=True)
    identifier(release_id)
    if len(release_id)>64:raise ValueError('Release identifier exceeds 64 characters')
    base=Path(data_root).resolve();releases=safe(base,'releases');releases.mkdir(parents=True,exist_ok=True)
    target=safe(releases,release_id)
    if target.exists():raise ValueError('Release exists; use a new immutable version')
    service=core.Handoff(preview=True)
    folder=Path(tempfile.mkdtemp(prefix='.preparing-',dir=releases))
    try:
        catalog=expected_catalog(release_id);write_new(folder/'catalog.json',catalog)
        write_new(folder/'mapping.json',expected_mapping(service,release_id))
        write_new(folder/'source-index.json',expected_sources(service,release_id))
        inventory={'kind':'reviewed_serving_withdrawals/v1','inventory_id':release_id+'-withdrawals-v01',
                   'version':1,'validator':'project_user_via_conversation','decision_ref':None,'entries':[]}
        decision={'kind':'local_registry_decision/v1','operation':'withdrawals','release_id':release_id,
                  'status':'proposed','validator':'project_user_via_conversation',
                  'content_sha256':withdrawal_content(release_id,inventory),'original_human_message':None}
        write_new(folder/'withdrawal-decision.json',decision)
        inventory['decision_ref']=binding(release_id+'-withdrawal-decision',folder/'withdrawal-decision.json')
        write_new(folder/'withdrawals.json',inventory)
        refs=[]
        for id_,entry in catalog['artifacts'].items():
            if entry['namespace']=='repository':refs.append(binding(id_,ROOT/entry['path']))
        refs.append(binding('catalog',folder/'catalog.json'))
        release={'kind':'reviewed_serving_release/v1','release_id':release_id,'stage':'staged',
                 'mode':'local_opt_in_no_model','contract_version':'1','prepared_on':datetime.now(timezone.utc).date().isoformat(),
                 'adapter_version':VERSION,'renderer_version':'frozen-documentary-preview-v01',
                 'design_decision_refs':[service._binding(n) for n in core.DECISIONS],
                 'activation_decision_ref':None,'mapping_ref':binding('mapping',folder/'mapping.json'),
                 'withdrawals_ref':binding('withdrawals',folder/'withdrawals.json'),
                 'source_index_ref':binding('source-index',folder/'source-index.json'),
                 'dependencies':refs,'limits':{'context_bytes':65536,'request_bytes':32768,'max_tasks':8}}
        write_new(folder/'release.json',release)
        if target.exists():raise ValueError('Concurrent release creation')
        os.rename(folder,target)
    except BaseException:
        # Only this function's fresh staging directory is eligible for cleanup.
        if folder.is_dir() and folder.parent.resolve()==releases.resolve():shutil.rmtree(folder)
        raise
    return target


class Registry:
    def __init__(self,data_root):
        self.root=Path(data_root).resolve()
        with LOCKS_GUARD:self.lock=LOCKS.setdefault(os.path.normcase(str(self.root)),threading.RLock())

    def _folder(self,rid):
        return safe(safe(self.root,'releases'),identifier(rid))

    def _resolve(self,folder,catalog,ref):
        if not isinstance(ref,dict) or set(ref)!={'artifact_id','sha256','hash_convention'} or ref['hash_convention']!='sha256_lf':
            raise ValueError('Invalid artifact reference')
        identifier(ref['artifact_id'])
        entry=catalog['artifacts'][ref['artifact_id']]
        path=safe(ROOT if entry['namespace']=='repository' else folder,entry['path'])
        if binding(ref['artifact_id'],path)!=ref:raise ValueError('Artifact binding mismatch')
        return path

    def _decision(self,folder,catalog,ref,operation,rid,content,staged):
        decision=read(self._resolve(folder,catalog,ref))
        if (set(decision)!={'kind','operation','release_id','status','validator','content_sha256','original_human_message'}
                or decision['kind']!='local_registry_decision/v1' or decision['operation']!=operation
                or decision['release_id']!=rid or decision['content_sha256']!=content
                or decision['validator']!='project_user_via_conversation'):
            raise ValueError('Decision binding mismatch')
        if staged:
            if decision['status']!='proposed' or decision['original_human_message'] is not None:
                raise ValueError('Candidate must not claim approval')
        elif decision['status']!='approved' or not isinstance(decision['original_human_message'],str) or not decision['original_human_message'].strip():
            raise ValueError('Explicit reviewed authorization unavailable')

    def _load(self,rid,*,staged=False,_trail=(),_cache=None):
        """Deduplicate full validation per immutable version/digest, within one operation."""
        identifier(rid)
        if rid in _trail or len(_trail)>50:raise ValueError('Cyclic or excessive decision history')
        cache={} if _cache is None else _cache
        key=(rid,staged,sha((self._folder(rid)/'release.json').read_bytes()))
        if key not in cache:
            cache[key]=self._load_uncached(rid,staged=staged,_trail=_trail,_cache=cache)
        return cache[key]

    def _load_uncached(self,rid,*,staged=False,_trail=(),_cache=None):
        identifier(rid)
        if len(rid)>64:raise ValueError('Release identifier exceeds 64 characters')
        if rid in _trail or len(_trail)>50:raise ValueError('Cyclic or excessive decision history')
        trail=(*_trail,rid)
        freeze.verify(environment=True)
        folder=self._folder(rid);catalog=read(folder/'catalog.json')
        if catalog!=expected_catalog(rid):raise ValueError('Unregistered artifact paths')
        release=read(folder/'release.json')
        keys={'kind','release_id','stage','mode','contract_version','prepared_on','adapter_version','renderer_version',
              'design_decision_refs','activation_decision_ref','mapping_ref','withdrawals_ref','source_index_ref','dependencies','limits'}
        if (set(release)!=keys or release['kind']!='reviewed_serving_release/v1' or release['release_id']!=rid
                or release['mode']!='local_opt_in_no_model' or release['contract_version']!='1'
                or release['adapter_version']!=VERSION or release['renderer_version']!='frozen-documentary-preview-v01'
                or not isinstance(release['prepared_on'],str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',release['prepared_on'])
                or release['limits']!={'context_bytes':65536,'request_bytes':32768,'max_tasks':8}
                or any(type(v) is not int for v in release['limits'].values())):
            raise ValueError('Release shape/policy mismatch')
        expected_ids={k for k,v in catalog['artifacts'].items() if v['namespace']=='repository'}|{'catalog'}
        if len(release['dependencies'])!=len(expected_ids) or {d['artifact_id'] for d in release['dependencies']}!=expected_ids:
            raise ValueError('Incomplete runtime inventory')
        for ref in release['dependencies']:self._resolve(folder,catalog,ref)
        service=core.Handoff(preview=True)
        if release['design_decision_refs']!=[service._binding(n) for n in core.DECISIONS]:raise ValueError('Design mismatch')
        for field,id_ in (('mapping_ref','mapping'),('source_index_ref','source-index'),('withdrawals_ref','withdrawals')):
            if release[field]['artifact_id']!=id_:raise ValueError('Wrong registered artifact')
        mapping=read(self._resolve(folder,catalog,release['mapping_ref']))
        sources=read(self._resolve(folder,catalog,release['source_index_ref']))
        if mapping!=expected_mapping(service,rid) or sources!=expected_sources(service,rid):raise ValueError('Mapping/source scope changed')
        withdrawals=read(self._resolve(folder,catalog,release['withdrawals_ref']))
        if (set(withdrawals)!={'kind','inventory_id','version','validator','decision_ref','entries'}
                or withdrawals['kind']!='reviewed_serving_withdrawals/v1'
                or withdrawals['validator']!='project_user_via_conversation'
                or type(withdrawals['version']) is not int or withdrawals['version']<1
                or not isinstance(withdrawals['entries'],list) or len(withdrawals['entries'])>1000):
            raise ValueError('Withdrawal inventory invalid')
        identifier(withdrawals['inventory_id'])
        self._decision(folder,catalog,withdrawals['decision_ref'],'withdrawals',rid,withdrawal_content(rid,withdrawals),staged)
        events=set()
        for e in withdrawals['entries']:
            if (set(e)!={'event_id','action','target_kind','target_id','target_release_id','target_sha256','decision_ref','reason'}
                    or e['action'] not in ('withdraw','reinstate') or e['target_kind'] not in ('bundle','review','source')
                    or not isinstance(e['reason'],str) or not e['reason'].strip()):raise ValueError('Invalid withdrawal event')
            identifier(e['event_id']);identifier(e['target_id']);identifier(e['target_release_id'])
            if e['event_id'] in events:raise ValueError('Duplicate withdrawal event')
            events.add(e['event_id'])
            if e['decision_ref']!=withdrawals['decision_ref']:
                ref=e['decision_ref'];suffix='-withdrawal-decision'
                if not isinstance(ref,dict) or not str(ref.get('artifact_id','')).endswith(suffix):raise ValueError('Unknown event decision')
                origin=identifier(ref['artifact_id'][:-len(suffix)])
                prior=self._load(origin,_trail=trail,_cache=_cache)
                if prior['withdrawals']['version']>=withdrawals['version'] or e not in prior['withdrawals']['entries']:
                    raise ValueError('Historical event is not preserved')
        if staged:
            if release['stage']!='staged' or release['activation_decision_ref'] is not None:raise ValueError('Candidate is not staged')
        else:
            if release['stage']!='activated':raise ValueError('Release not explicitly activated')
            self._decision(folder,catalog,release['activation_decision_ref'],'activate',rid,release_content(release),False)
        token=value_sha({'release':release,'catalog':catalog,'withdrawals':withdrawals})
        return {'release':release,'mapping':mapping,'sources':sources,'withdrawals':withdrawals,'token':token,'service':service}

    def _head(self):
        """Read the durable append-only activation chain, independent of active.json."""
        folder=safe(self.root,'authority-log')
        if not folder.exists():return None
        names=sorted(p.name for p in folder.iterdir())
        if not names or len(names)>10000:raise ValueError('Missing or excessive durable authority history')
        previous=None;last=None
        for generation,name in enumerate(names,1):
            if name!=f'{generation:020}.json':raise ValueError('Authority history is incomplete')
            path=safe(folder,name);record=read(path)
            if (set(record)!={'kind','generation','previous_sha256_lf','pointer','withdrawal_version'}
                    or record['kind']!='local_registry_activation_head/v1'
                    or type(record['generation']) is not int or record['generation']!=generation
                    or record['previous_sha256_lf']!=previous
                    or type(record['withdrawal_version']) is not int or record['withdrawal_version']<1
                    or not isinstance(record['pointer'],dict)):
                raise ValueError('Invalid durable authority history')
            if last and record['withdrawal_version']<=last['record']['withdrawal_version']:
                raise ValueError('Durable withdrawal authority rolled back')
            previous=sha(path.read_bytes());last={'record':record,'sha256_lf':previous}
        return last

    def _append_head(self,pointer,version,previous):
        folder=safe(self.root,'authority-log');folder.mkdir(exist_ok=True)
        generation=1 if previous is None else previous['record']['generation']+1
        record={'kind':'local_registry_activation_head/v1','generation':generation,
                'previous_sha256_lf':None if previous is None else previous['sha256_lf'],
                'pointer':pointer,'withdrawal_version':version}
        # Exclusive durable append. A partial write fails closed and is never ignored.
        path=safe(folder,f'{generation:020}.json')
        with path.open('x',encoding='utf-8',newline='\n') as out:
            out.write(json.dumps(record,indent=2)+'\n');out.flush();os.fsync(out.fileno())

    def _snapshot(self,*,candidate=None):
        cache={}
        if candidate is not None:
            state=dict(self._load(candidate,staged=True,_cache=cache));state['pointer']=None;state['_cache']=cache
            self._validate_targets(state,staged=True)
            return state
        pointer=read(safe(self.root,'active.json'))
        head=self._head()
        if head is None or head['record']['pointer']!=pointer:raise ValueError('Active pointer differs from durable authority head')
        if (set(pointer)!={'kind','release_id','manifest_sha256_lf','withdrawals_sha256_lf','activation_decision_ref','mode'}
                or pointer['kind']!='reviewed_serving_active/v1' or pointer['mode']!='local_opt_in_no_model'):
            raise ValueError('Invalid active pointer')
        rid=identifier(pointer['release_id']);state=dict(self._load(rid,_cache=cache));state['_cache']=cache
        if (sha((self._folder(rid)/'release.json').read_bytes())!=pointer['manifest_sha256_lf']
                or state['release']['withdrawals_ref']['sha256']!=pointer['withdrawals_sha256_lf']
                or state['release']['activation_decision_ref']!=pointer['activation_decision_ref']):raise ValueError('Active authority mismatch')
        if state['withdrawals']['version']!=head['record']['withdrawal_version']:raise ValueError('Withdrawal head mismatch')
        state['pointer']=pointer;state['head']=head
        state['token']=value_sha({'pointer':pointer,'head':head['sha256_lf'],'state':state['token']})
        self._validate_targets(state)
        return state

    def _validate_targets(self,state,*,staged=False):
        targets={e['target_release_id'] for e in state['withdrawals']['entries']}
        for rid in targets:
            target=state if rid==state['release']['release_id'] else self._load(rid,_cache=state.get('_cache'))
            self._held(target,state)

    def _held(self,target,current):
        rid=target['release']['release_id'];identities={}
        for entry in target['mapping']['entries']:identities[('bundle',entry['bundle_key'])]=value_sha(entry)
        for p in target['sources']['passages']:identities[('source',p['source_id'])]=value_sha(p)
        for d in target['sources']['reviews']:identities[('review',d['review_id'])]=value_sha(d)
        last={}
        for event in current['withdrawals']['entries']:
            if event['target_release_id']!=rid:continue
            identity=(event['target_kind'],event['target_id'])
            if identities.get(identity)!=event['target_sha256']:raise ValueError('Unknown or stale withdrawal target')
            if event['action']=='reinstate' and last.get(identity)!='withdraw':raise ValueError('Reinstatement without withdrawal')
            last[identity]=event['action']
        return {e['bundle_key'] for e in target['mapping']['entries']
                if last.get(('bundle',e['bundle_key']))=='withdraw'
                or last.get(('review',e['review_scope']))=='withdraw'
                or any(last.get(('source',p))=='withdraw' for p in e['required_source_ids'])}

    def _recheck(self,state,candidate):
        if self._snapshot(candidate=candidate)['token']!=state['token']:raise ValueError('Authority changed during request')

    def _failure(self,request,reason):
        out={'kind':'reviewed_documentary_bundle/v1','contract_version':'1','request_id':request['request_id'],
             'release_id':None,'authority_digest':None,'status':'unavailable','response_reason':reason,'items':[],
             'context':{'bundles':[],'passages':[],'reviews':[]},'citation_refs':[],
             'coverage':{k:0 for k in ('supported','needs_clarification','abstained','quarantined','unavailable','excluded')},
             'context_measure':{'convention':'utf8_json_sorted_keys_compact_unicode_preserved_no_nan','delivered_bytes':41,'limit_bytes':65536},
             'limits':{'diagnosis_established':False,'operational_suitability':'not_established','operational_authorization':False,'absence_scope':'selected_release_bundles_only'}}
        out['context_measure']['delivered_bytes']=len(core.canonical(out['context']));return out

    def _service_failure(self,request):
        """Use existing v1 item outcomes; do not alter either frozen machine schema."""
        out=self._failure(request,'item_outcomes')
        for i,task in enumerate(request['tasks']):
            for j,item in enumerate(task['requested_items']):
                excluded=item in task.get('excluded_items',[])
                state='excluded' if excluded else 'unavailable'
                origins=[{'field':f,'request_pointer':f'/tasks/{i}/{f}'} for f in ('product','deposit_context')]
                origins.append({'field':'requested_item','request_pointer':f'/tasks/{i}/requested_items/{j}'})
                if excluded:origins.append({'field':'exclusion','request_pointer':f'/tasks/{i}/excluded_items/{task["excluded_items"].index(item)}'})
                out['items'].append({'task_id':task['task_id'],'requested_item':item,'state':state,
                    'reason':'excluded_by_request' if excluded else 'required_dependency_unavailable',
                    'field_origins':origins,'bundle_keys':[],'bundle_refs':[],'withheld_bundle_keys':[],
                    'clarification_targets':[],'absence_scope':None})
                out['coverage'][state]+=1
        if not out['coverage']['unavailable']:out.update(status='abstained',response_reason='no_requested_item')
        return out

    def evaluate(self,value,*,candidate=None):
        try:request=core.validate_request(value)
        except core.RequestError as e:return core.validation_error(value,e)
        with self.lock:
            try:state=self._snapshot(candidate=candidate)
            except FileNotFoundError:
                reason='release_not_activated' if candidate is None and not (self.root/'active.json').exists() and not (self.root/'authority-log').exists() else 'invalid_authority'
                return self._failure(request,reason)
            except Exception:return self._failure(request,'invalid_authority')
            try:
                held=self._held(state,state)
                service=core.Handoff(preview=True,withdrawn=held)
                out=service.evaluate(request)
                if out['response_reason']=='invalid_authority':return self._failure(request,'invalid_authority')
                out['release_id']=state['release']['release_id'];out['authority_digest']=state['token']
                for ref in out['citation_refs']:
                    ref['release_id']=out['release_id'];ref['href']=f'/reviewed/v1/releases/{out["release_id"]}/sources/{ref["source_id"]}'
            except Exception as error:
                # Only a failed fresh authority check justifies authority_changed.
                try:self._recheck(state,candidate)
                except Exception:return self._failure(request,'authority_changed')
                LOGGER.error('Registry backend failure (%s)',type(error).__name__)
                return self._service_failure(request)
            try:self._recheck(state,candidate)
            except Exception:return self._failure(request,'authority_changed')
            return out

    def source(self,release_id,source_id,*,candidate=None):
        identifier(release_id);identifier(source_id)
        with self.lock:
            state=self._snapshot(candidate=candidate)
            target=state if state['release']['release_id']==release_id else self._load(release_id,_cache=state.get('_cache'))
            held=self._held(target,state)
            service=core.Handoff(preview=True,withdrawn=held)
            view=service.source(service.release_id,source_id)
            view['release_id']=release_id;view['authority_digest']=state['token']
            self._recheck(state,candidate)
            if target is not state and self._load(release_id)['token']!=target['token']:raise ValueError('Old release changed')
            return view

    def activate(self,release_id):
        """Requires already reviewed activated artifacts. Not exposed by candidate CLI."""
        with self.lock:
            state=self._load(release_id)
            self._validate_targets(state)
            active=self.root/'active.json'
            previous_head=self._head()
            previous_pointer=None
            if active.exists() or previous_head is not None:
                previous=self._snapshot();old=previous['withdrawals'];new=state['withdrawals']
                previous_pointer=previous['pointer']
                if (new['version']<=old['version'] or new['entries'][:len(old['entries'])]!=old['entries']):
                    raise ValueError('Withdrawal history cannot roll back or disappear')
            state['service']._check()
            release=state['release']
            pointer={'kind':'reviewed_serving_active/v1','release_id':release_id,
                     'manifest_sha256_lf':sha((self._folder(release_id)/'release.json').read_bytes()),
                     'withdrawals_sha256_lf':release['withdrawals_ref']['sha256'],
                     'activation_decision_ref':release['activation_decision_ref'],'mode':'local_opt_in_no_model'}
            fd,name=tempfile.mkstemp(prefix='.active-',dir=self.root)
            try:
                with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as f:
                    f.write(json.dumps(pointer,indent=2)+'\n');f.flush();os.fsync(f.fileno())
                if self._load(release_id)['token']!=state['token']:
                    raise ValueError('Activation inputs changed before pointer replacement')
                if self._head()!=previous_head or (read(active) if active.exists() else None)!=previous_pointer:
                    raise ValueError('Current authority changed before activation commit')
                self._append_head(pointer,state['withdrawals']['version'],previous_head)
                os.replace(name,active)
            finally:
                if Path(name).exists():Path(name).unlink()
            return pointer
