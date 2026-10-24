"""Prospective safeguards: real V01–V12 text is never passed to retrieval."""
from contextlib import ExitStack,contextmanager
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from experiments.cytiva import v03b_evaluation as subject


class V03bEvaluationTests(unittest.TestCase):
    def test_verify_does_not_search_or_plan_new_questions(self):
        with patch('ingestion.local_passage_retrieval.BM25.search',side_effect=AssertionError('No new query search')), \
             patch('ingestion.scoped_passage_context.ScopedContextIndex.retrieve',side_effect=AssertionError('No new query retrieval')), \
             patch('ingestion.scoped_passage_context.navigation_plan',side_effect=AssertionError('No new query planning')):
            result=subject.verify()
        self.assertEqual(result['intents'],12);self.assertEqual(result['formulations'],24)
        self.assertFalse(result['evaluation_executed_by_this_command'])

    def test_candidate_is_exact_v03b_and_pending_sources_stay_excluded(self):
        c=subject.read(subject.ROOT/subject.PACKAGE/'candidate.json')
        self.assertEqual(c['config'],subject.read(subject.ROOT/'experiments/cytiva/section_navigation_v03.json'))
        self.assertEqual((c['config']['top_k'],c['config']['max_tokens'],c['config']['fallback_relative_score']),(6,2048,0.65))
        packet=subject.read(subject.ROOT/subject.PACKAGE/'references.json')
        self.assertEqual(len(packet['source_passages']),25)
        self.assertFalse({'E118-I','E121-EQ'} & set(packet['eligible_source_ids']))
        self.assertTrue(all(r['human_review_status']=='pending' for r in packet['references']))

    def test_method_hash_change_blocks_integrity(self):
        real=subject.digest
        def changed(path):
            return 'changed' if Path(path).as_posix().endswith('ingestion/scoped_passage_context.py') else real(path)
        with patch.object(subject,'digest',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'Frozen file'):subject.verify()

    def test_unreviewed_input_blocks_runtime_and_real_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'review.json'
            verification=subject.verify()
            subject.dump(path,{'manifest_sha256_lf':verification['preparation_manifest_sha256_lf'],
                              'method_lock_sha256_lf':verification['method_lock_sha256_lf'],'decisions':[]})
            with patch.object(subject,'make_runtime') as factory:
                with self.assertRaisesRegex(ValueError,'twelve questions'):subject.run(path)
                factory.assert_not_called()
        candidate=subject.read(subject.ROOT/subject.PACKAGE/'candidate.json')
        self.assertFalse((subject.ROOT/candidate['run_directory']).exists())

    def test_review_for_other_freeze_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'review.json';subject.dump(path,{'manifest_sha256_lf':'other'})
            with self.assertRaisesRegex(ValueError,'another freeze'):
                subject.review_gate(path,{'preparation_manifest_sha256_lf':'here','method_lock_sha256_lf':'method'},{},{})

    @staticmethod
    def synthetic_rows():
        refs=[{'question_id':qid,'required_evidence_sets':[['needed']],
               'acceptable_context_ids':['needed'],'unrequested_context_ids':['other_phase'],
               'expected_status':'clarify'} for qid in subject.IDS]
        rows=[{'question_id':qid,'language':lang,'assembled':{'ids':['needed']}}
              for qid in subject.IDS for lang in ('en','fr')]
        return rows,refs

    def test_missing_evidence_or_unrequested_phase_blocks_gate(self):
        rows,refs=self.synthetic_rows();rows[0]['assembled']['ids']=[]
        measured=subject.score(rows,refs)
        self.assertEqual(measured['complete_both_languages'],11)
        self.assertEqual(measured['pilot_gate'],'blocked_missing_evidence_or_scope')
        rows,refs=self.synthetic_rows();rows[0]['assembled']['ids'].append('other_phase')
        measured=subject.score(rows,refs)
        self.assertEqual(measured['complete_both_languages'],12)
        self.assertEqual(measured['explicit_scope_failures'],1)
        self.assertEqual(measured['pilot_gate'],'blocked_missing_evidence_or_scope')
        self.assertTrue(all(not r['response_status_evaluated'] for r in measured['rows']))

    def test_whole_intents_and_language_pairs_remain_in_denominator(self):
        rows,refs=self.synthetic_rows()
        for invalid in (rows[:-1],rows[2:],rows+[rows[0]]):
            with self.assertRaisesRegex(ValueError,'grid'):subject.score(invalid,refs)

    def test_pressure_absence_reference_is_finitely_scoped(self):
        p=subject.read(subject.ROOT/subject.PACKAGE/'references.json')
        ref=next(r for r in p['references'] if r['question_id']=='V07')
        self.assertEqual(set(ref['absence_assertion']['eligible_source_ids']),set(p['eligible_source_ids']))
        self.assertIn('Full manual',ref['absence_assertion']['does_not_cover'])
        self.assertFalse(any('pressure' in r['quote'].lower() for r in p['source_passages']))

    @contextmanager
    def synthetic_runtime(self):
        with tempfile.TemporaryDirectory() as tmp,ExitStack() as stack:
            root=Path(tmp);p=root/subject.PACKAGE;p.mkdir(parents=True)
            candidate=deepcopy(subject.read(subject.ROOT/subject.PACKAGE/'candidate.json'))
            lock=deepcopy(subject.read(subject.ROOT/subject.PACKAGE/'method-lock.json'))
            queries=[{'id':qid,'question_en':'synthetic EN','question_fr':'synthetic FR'} for qid in subject.IDS]
            _,refs=self.synthetic_rows()
            for name,value in [('candidate.json',candidate),('method-lock.json',lock),('questions.json',{'questions':queries}),
                               ('references.json',{'references':refs}),('manifest.json',{'file_sha256_lf':{}})]:subject.dump(p/name,value)
            review=root/'synthetic-review.json';subject.dump(review,{'scope':'SYNTHETIC FIXTURE, NOT HUMAN APPROVAL'})
            verification={'preparation_manifest_sha256_lf':'synthetic','method_lock_sha256_lf':'synthetic-method'}
            output=root/candidate['run_directory'];calls=[]
            def retrieve(text,counter):
                self.assertIn(text,('synthetic EN','synthetic FR'));calls.append(text)
                return {'assembled':{'ids':['needed'],'tokens':1,'excluded':[],'context':'same synthetic context'},
                        'unavailable_source_roles':[]}
            index=SimpleNamespace(passages={},retrieve=retrieve)
            stack.enter_context(patch.object(subject,'verify',return_value=verification))
            stack.enter_context(patch.object(subject,'review_gate',return_value=subject.read(review)))
            stack.enter_context(patch.object(subject.platform,'python_version',return_value=lock['python_version']))
            stack.enter_context(patch.object(subject.importlib.metadata,'version',return_value=lock['tokenizer']['tiktoken_version']))
            stack.enter_context(patch.dict(os.environ,{'PYTHONHASHSEED':'0'}))
            stack.enter_context(patch('experiments.cytiva.visual_validation.network_guard',return_value=[]))
            stack.enter_context(patch.object(subject,'protected_files',return_value={}))
            factory=stack.enter_context(patch.object(subject,'make_runtime',return_value=(index,len,lock['tokenizer'])))
            stack.enter_context(patch.object(subject,'validate_context'))
            yield root,review,output,calls,factory,index

    def test_synthetic_contexts_saved_before_scoring_and_rerun_blocked(self):
        with self.synthetic_runtime() as (root,review,output,calls,factory,index):
            real=subject.score
            def score(rows,refs):
                self.assertEqual(len(subject.read(output/'contexts-unscored.json')),24)
                return real(rows,refs)
            with patch.object(subject,'score',side_effect=score):result=subject.run(review,root)
            self.assertEqual(result['complete_both_languages'],12)
            self.assertEqual(len(calls),72)
            self.assertFalse(result['automatic_adoption'])
            with self.assertRaisesRegex(ValueError,'Existing evaluation'):subject.run(review,root)
            self.assertEqual(len(calls),72)

    def test_changed_repeat_preserves_failed_trial_without_retry(self):
        with self.synthetic_runtime() as (root,review,output,calls,factory,index):
            n=[0]
            def unstable(text,counter):
                n[0]+=1
                return {'assembled':{'context':str(n[0])}}
            index.retrieve=unstable
            with self.assertRaisesRegex(ValueError,'Repeated context changed'):subject.run(review,root)
            self.assertEqual(subject.read(output/'failure.json')['unexecuted_formulations'],24)
            with self.assertRaisesRegex(ValueError,'Existing evaluation'):subject.run(review,root)

    def test_scoring_does_not_change_reference_or_context_inputs(self):
        rows,refs=self.synthetic_rows();before=deepcopy((rows,refs))
        measured=subject.score(rows,refs)
        self.assertEqual((rows,refs),before)
        self.assertEqual(measured['answer_quality'],'not_evaluated')


if __name__=='__main__':unittest.main()
