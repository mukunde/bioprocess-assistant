"""X preparation integrity and synthetic harness tests; never search real X text."""
from contextlib import ExitStack,contextmanager
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from experiments.cytiva import v05_evaluation as subject


class V05EvaluationTests(unittest.TestCase):
    def test_clarification_diagnostic_is_read_from_plan_without_planning(self):
        row={'navigation_plan':{'clarification_required':False}}
        self.assertEqual(subject.diagnostic_failures(row,{'clarification_required':False}),[])
        self.assertEqual(subject.diagnostic_failures(row,{'clarification_required':True}),['clarification_required'])
        self.assertEqual(subject.diagnostic_failures({}, {'clarification_required':False}),['clarification_required'])

    def test_required_source_bundles_cannot_drop_warning_dependencies(self):
        original=subject.read
        refs=deepcopy(original(subject.ROOT/subject.PACKAGE/'references.json'))
        row=next(r for r in refs['references'] if r['question_id']=='X03')
        row['required_evidence_sets'][0].remove('E120-W')
        def changed(path):
            if Path(path)==subject.ROOT/subject.PACKAGE/'references.json':return refs
            return original(path)
        with patch.object(subject,'read',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'dependency closure'):subject.verify()

    def test_integrity_does_not_create_runtime_search_or_plan(self):
        with patch.object(subject,'make_runtime',side_effect=AssertionError('No runtime')), \
             patch('ingestion.local_passage_retrieval.BM25.search',side_effect=AssertionError('No search')), \
             patch('ingestion.polarity_passage_context.navigation_plan',side_effect=AssertionError('No planning')):
            result=subject.verify()
        self.assertEqual(result['intents'],12);self.assertEqual(result['pending_reference_reviews'],12)
        self.assertFalse(result['evaluation_executed_by_this_command'])

    def test_candidate_is_exact_v05_with_original_source_policy(self):
        c=subject.read(subject.ROOT/subject.PACKAGE/'candidate.json')
        self.assertEqual(c['config'],subject.read(subject.ROOT/'experiments/cytiva/section_navigation_v05.json'))
        old=subject.read(subject.ROOT/subject.base.PACKAGE/'candidate.json')
        self.assertEqual(c['source_runtime_policy'],old['source_runtime_policy'])
        self.assertEqual(c['pending_source_ids'],['E118-I','E121-EQ'])
        self.assertEqual(c['timing_repetitions'],3)

    def test_changed_method_blocks_preparation_verification(self):
        original=subject.digest
        def changed(path):
            return 'changed' if Path(path).as_posix().endswith('ingestion/polarity_passage_context.py') else original(path)
        with patch.object(subject,'digest',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'Frozen input'):subject.verify()

    def test_active_tests_are_not_immutable_method_dependencies(self):
        lock=subject.read(subject.ROOT/subject.PACKAGE/'method-lock.json')
        manifest=subject.read(subject.ROOT/subject.PACKAGE/'manifest.json')
        self.assertNotIn('tests/test_v05_evaluation.py',manifest['file_sha256_lf'])
        self.assertFalse(any(n.startswith('tests/') for n in lock['file_sha256_lf']))
        self.assertIn('experiments/cytiva/v05_evaluation.py',manifest['file_sha256_lf'])

    def test_incomplete_review_preserves_absent_and_existing_temporary_output(self):
        verified=subject.verify()
        for existing in (False,True):
            with self.subTest(existing=existing),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);packet=root/subject.PACKAGE;packet.mkdir(parents=True)
                for name in ('questions.json','references.json','candidate.json'):
                    (packet/name).write_bytes((subject.ROOT/subject.PACKAGE/name).read_bytes())
                candidate=subject.read(packet/'candidate.json');output=root/candidate['run_directory']
                if existing:
                    output.mkdir(parents=True);(output/'old.txt').write_bytes(b'preserve')
                review=root/'review.json';subject.dump(review,{
                    'manifest_sha256_lf':verified['preparation_manifest_sha256_lf'],
                    'method_lock_sha256_lf':verified['method_lock_sha256_lf'],'decisions':[]})
                with patch.object(subject,'verify',return_value=verified),patch.object(subject,'make_runtime') as factory:
                    with self.assertRaisesRegex(ValueError,'twelve questions'):subject.run(review,root)
                    factory.assert_not_called()
                self.assertEqual(output.exists(),existing)
                if existing:self.assertEqual((output/'old.txt').read_bytes(),b'preserve')

    def test_wrong_freeze_and_duplicate_human_decisions_are_rejected(self):
        verified=subject.verify()
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'review.json';subject.dump(p,{'manifest_sha256_lf':'other'})
            with self.assertRaisesRegex(ValueError,'another freeze'):subject.review_gate(p,verified,{}, {})
            subject.dump(p,{'manifest_sha256_lf':verified['preparation_manifest_sha256_lf'],
                            'method_lock_sha256_lf':verified['method_lock_sha256_lf'],
                            'decisions':[{'question_id':'X01'}]*12})
            with self.assertRaisesRegex(ValueError,'twelve questions'):subject.review_gate(p,verified,{}, {})

    def test_reference_binding_reservations_and_utc_are_required(self):
        queries={q['id']:q for q in subject.read(subject.ROOT/subject.PACKAGE/'questions.json')['questions']}
        refs={r['question_id']:r for r in subject.read(subject.ROOT/subject.PACKAGE/'references.json')['references']}
        verified=subject.verify()
        rows=[{'question_id':qid,'decision':'validated_with_reservation',
            'human_quote':'SYNTHETIC UNIT FIXTURE, NOT HUMAN APPROVAL',
            'reviewed_at_utc':datetime.now(timezone.utc).isoformat(),
            'question_sha256_canonical':subject.canonical(queries[qid]),
            'reference_sha256_canonical':subject.canonical(refs[qid]),
            'retained_reservations':refs[qid]['reservations']} for qid in subject.IDS]
        review={'manifest_sha256_lf':verified['preparation_manifest_sha256_lf'],
                'method_lock_sha256_lf':verified['method_lock_sha256_lf'],'decisions':rows}
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'synthetic-review.json';subject.dump(p,review)
            self.assertEqual(len(subject.review_gate(p,verified,queries,refs)['decisions']),12)
            for key,value in [('question_sha256_canonical','wrong'),('reference_sha256_canonical','wrong'),
                              ('retained_reservations',[]),('reviewed_at_utc','2026-10-24T10:00:00')]:
                wrong=deepcopy(review);wrong['decisions'][0][key]=value;subject.dump(p,wrong)
                with self.subTest(key=key),self.assertRaises(ValueError):subject.review_gate(p,verified,queries,refs)

    @staticmethod
    def synthetic_grid():
        refs=[{'question_id':qid,'required_evidence_sets':[['needed']],
               'acceptable_context_ids':['needed'],'unrequested_context_ids':['other'],
               'expected_diagnostics':{},'expected_status':'answer'} for qid in subject.IDS]
        contexts=[{'question_id':qid,'language':lang,'assembled':{'ids':['needed']}} for qid in subject.IDS for lang in ('en','fr')]
        return contexts,refs

    def test_metrics_distinguish_missing_evidence_phase_noise_and_metadata(self):
        rows,refs=self.synthetic_grid();before=deepcopy((rows,refs))
        self.assertEqual(subject.score(rows,refs)['complete_both_languages'],12)
        self.assertEqual((rows,refs),before)
        rows[0]['assembled']['ids']=[]
        self.assertEqual(subject.score(rows,refs)['complete_both_languages'],11)
        rows[0]['assembled']['ids']=['needed','other']
        self.assertEqual(subject.score(rows,refs)['explicit_scope_failures'],1)
        refs[0]['expected_diagnostics']={'phase_conflicts_contains':['elution'],'navigation_complete':False}
        measured=subject.score(rows,refs)
        self.assertEqual(measured['diagnostic_failure_formulations'],2)
        self.assertEqual(measured['answer_quality'],'not_evaluated')
        self.assertFalse(measured['automatic_adoption'])
        self.assertEqual(measured['pilot_gate'],'blocked_missing_evidence_scope_or_diagnostics')

    def test_incomplete_or_duplicate_grid_cannot_score(self):
        rows,refs=self.synthetic_grid()
        for bad in (rows[:-1],rows[2:],rows+[rows[0]]):
            with self.assertRaisesRegex(ValueError,'grid'):subject.score(bad,refs)

    def test_diagnostic_conditions_are_checked_from_saved_metadata_only(self):
        row={'source_support_complete':False,'navigation_complete':False,
             'navigation_plan':{'phase_mentions':{'conflicts':['elution']}},
             'source_limitations':[{'role':'maximum_pressure'}],
             'unavailable_source_roles':[{'role':'equilibration'}]}
        expected={'source_support_complete':False,'navigation_complete':False,
                  'phase_conflicts_contains':['elution'],'source_limitations_contains':['maximum_pressure'],
                  'unavailable_roles_contains':['equilibration']}
        self.assertEqual(subject.diagnostic_failures(row,expected),[])
        self.assertEqual(len(subject.diagnostic_failures({},expected)),5)

    @contextmanager
    def synthetic_runtime(self):
        with tempfile.TemporaryDirectory() as tmp,ExitStack() as stack:
            root=Path(tmp);p=root/subject.PACKAGE;p.mkdir(parents=True)
            candidate=subject.read(subject.ROOT/subject.PACKAGE/'candidate.json')
            lock=subject.read(subject.ROOT/subject.PACKAGE/'method-lock.json')
            queries=[{'id':qid,'question_en':'synthetic EN','question_fr':'synthetic FR'} for qid in subject.IDS]
            _,refs=self.synthetic_grid()
            for name,value in [('candidate.json',candidate),('method-lock.json',lock),
                               ('questions.json',{'questions':queries}),('references.json',{'references':refs}),
                               ('manifest.json',{'file_sha256_lf':{}})]:subject.dump(p/name,value)
            review=root/'synthetic-review.json';subject.dump(review,{'scope':'SYNTHETIC FIXTURE, NOT APPROVAL'})
            output=root/candidate['run_directory'];calls=[]
            def retrieve(text,counter):
                self.assertIn(text,('synthetic EN','synthetic FR'));calls.append(text)
                return {'assembled':{'ids':['needed'],'tokens':1,'excluded':[],'context':'fixed synthetic'},
                        'navigation_complete':True,'unavailable_source_roles':[]}
            index=SimpleNamespace(passages={},retrieve=retrieve)
            stack.enter_context(patch.object(subject,'verify',return_value={
                'preparation_manifest_sha256_lf':'synthetic','method_lock_sha256_lf':'synthetic-method'}))
            stack.enter_context(patch.object(subject,'review_gate',return_value=subject.read(review)))
            stack.enter_context(patch.object(subject.platform,'python_version',return_value=lock['python_version']))
            stack.enter_context(patch.object(subject.importlib.metadata,'version',return_value=lock['tokenizer']['tiktoken_version']))
            stack.enter_context(patch.dict(os.environ,{'PYTHONHASHSEED':'0'}))
            stack.enter_context(patch('experiments.cytiva.visual_validation.network_guard',return_value=[]))
            earlier=root/'earlier.txt';earlier.write_bytes(b'preserve old trial')
            stack.enter_context(patch.object(subject.base,'protected_files',return_value={'earlier.txt':hashlib.sha256(earlier.read_bytes()).hexdigest()}))
            factory=stack.enter_context(patch.object(subject,'make_runtime',return_value=(index,len,lock['tokenizer'])))
            stack.enter_context(patch.object(subject.base,'validate_context'))
            yield root,review,output,calls,index,factory

    def test_synthetic_contexts_are_saved_before_scoring_and_old_trial_survives(self):
        with self.synthetic_runtime() as (root,review,output,calls,index,factory):
            actual=subject.score
            def check(rows,refs):
                self.assertEqual(len(subject.read(output/'contexts-unscored.json')),24)
                return actual(rows,refs)
            with patch.object(subject,'score',side_effect=check):result=subject.run(review,root)
            self.assertEqual(len(calls),72);self.assertEqual(result['complete_both_languages'],12)
            self.assertEqual((root/'earlier.txt').read_bytes(),b'preserve old trial')
            with self.assertRaisesRegex(ValueError,'Existing evaluation'):subject.run(review,root)
            self.assertEqual(len(calls),72)

    def test_changed_repeat_metadata_is_preserved_as_failure_without_retry(self):
        with self.synthetic_runtime() as (root,review,output,calls,index,factory):
            number=[0]
            def unstable(text,counter):
                number[0]+=1
                return {'assembled':{'context':'same'},'navigation_complete':number[0]%2==0}
            index.retrieve=unstable
            with self.assertRaisesRegex(ValueError,'Repeated result changed'):subject.run(review,root)
            failure=subject.read(output/'failure.json')
            self.assertEqual(failure['completed_formulations'],0)
            self.assertEqual(failure['unexecuted_formulations'],24)
            self.assertEqual((root/'earlier.txt').read_bytes(),b'preserve old trial')
            with self.assertRaisesRegex(ValueError,'Existing evaluation'):subject.run(review,root)

    def test_pressure_absence_is_bounded_and_original_sources_are_retained(self):
        packet=subject.read(subject.ROOT/subject.PACKAGE/'references.json')
        source=subject.read(subject.ROOT/'experiments/cytiva/contaminants-pilot-v01/evidence.json')
        lookup={s['id']:s for s in source['passages']}
        for s in packet['source_passages']:self.assertEqual(s,lookup[s['id']])
        ref=next(r for r in packet['references'] if r['question_id']=='X09')
        self.assertEqual(set(ref['absence_assertion']['eligible_source_ids']),set(packet['eligible_source_ids']))
        self.assertEqual(len(packet['eligible_source_ids']),25)
        self.assertFalse(any('pressure' in s['quote'].lower() for s in packet['source_passages']))


if __name__=='__main__':unittest.main()
