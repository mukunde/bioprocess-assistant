"""Integrity/review gates and synthetic execution; never retrieve H01-H10."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from experiments.cytiva import section_evaluation as subject


class SectionEvaluationTests(unittest.TestCase):
    def test_integrity_never_searches_prospective_queries(self):
        with patch('ingestion.local_passage_retrieval.BM25.search',side_effect=AssertionError('Prospective search forbidden')):
            result=subject.verify()
        self.assertEqual(result['intents'],10)
        self.assertFalse(result['benchmark_executed'])

    def test_original_section_variant_is_preserved(self):
        c=subject.read(subject.ROOT/subject.PACKAGE/'candidate.json')
        original=subject.read(subject.ROOT/'experiments/cytiva/contaminant_context_v02.json')
        for key in c['config']:self.assertEqual(c['config'][key],original[key])
        self.assertEqual(c['origin_retrieve_arguments'],{'sections':True,'vocabulary':None})
        self.assertEqual((c['config']['top_k'],c['config']['max_tokens']),(6,2048))

    def test_changed_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/subject.PACKAGE;p.mkdir(parents=True)
            target=root/'method.py';target.write_text('before',encoding='utf-8')
            subject.dump(p/'manifest.json',{'file_sha256_lf':{'method.py':subject.digest(target)}})
            target.write_text('after',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'Frozen file'):subject.verify(root)

    def test_hash_is_lf_crlf_portable(self):
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a',Path(tmp)/'b';a.write_bytes(b'x\r\n');b.write_bytes(b'x\n')
            self.assertEqual(subject.digest(a),subject.digest(b))

    def test_pending_sources_remain_excluded(self):
        c=subject.read(subject.ROOT/subject.PACKAGE/'candidate.json');pending=set(c['pending_source_ids'])
        self.assertTrue(pending<=set(c['source_runtime_policy']['quarantined_ids']))
        self.assertFalse(pending & set(c['source_runtime_policy']['searchable_ids']))
        for ref in subject.read(subject.ROOT/subject.PACKAGE/'references.json')['references']:
            self.assertFalse(pending & set(ref['acceptable_context_ids']))
            self.assertEqual(ref['human_review_status'],'pending')

    def test_missing_review_blocks_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'review.json';subject.dump(path,{'manifest_sha256_lf':'correct','decisions':[]})
            with patch.object(subject,'verify',return_value={'manifest_sha256_lf':'correct'}):
                with self.assertRaisesRegex(ValueError,'ten new questions'):subject.run(path,root=tmp)
            self.assertEqual([p.name for p in Path(tmp).iterdir()],['review.json'])

    def test_wrong_or_rejected_review_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'review.json';subject.dump(path,{'manifest_sha256_lf':'wrong'})
            with self.assertRaisesRegex(ValueError,'not bound'):subject.review_gate(path,'correct')
            rows=[{'question_id':qid,'decision':'rejected','human_quote':'synthetic test only',
                   'reviewed_at_utc':'2026-10-24T00:00:00Z'} for qid in subject.IDS]
            subject.dump(path,{'manifest_sha256_lf':'correct','decisions':rows})
            with self.assertRaisesRegex(ValueError,'Pending/rejected'):subject.review_gate(path,'correct')

    def test_scoring_keeps_failures_and_rejects_incomplete_grid(self):
        refs=[{'question_id':qid,'required_evidence_sets':[['needed']],
              'acceptable_context_ids':['needed'],'expected_status':'answer'} for qid in subject.IDS]
        rows=[{'question_id':qid,'language':lang,'assembled':{'ids':['needed','noise']}}
              for qid in subject.IDS for lang in ('en','fr')]
        rows[0]['assembled']['ids']=[];result=subject.score(rows,refs)
        self.assertEqual(result['complete_both_languages'],9)
        self.assertEqual(result['pilot_gate'],'blocked_incomplete_evidence')
        self.assertEqual(result['rows'][1]['outside_acceptable_context_ids'],['noise'])
        self.assertFalse(result['automatic_adoption'])
        for invalid in (rows[:-1],rows+[rows[0]]):
            with self.assertRaises(ValueError):subject.score(invalid,refs)

    def test_synthetic_execution_separates_retrieval_and_scoring_and_refuses_rerun(self):
        from experiments.cytiva import contaminant_context_retrieval as method
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/subject.PACKAGE;p.mkdir(parents=True)
            c=copy.deepcopy(subject.read(subject.ROOT/subject.PACKAGE/'candidate.json'))
            subject.dump(p/'candidate.json',c)
            queries=[{'id':qid,'question_en':'synthetic EN','question_fr':'synthetic FR'} for qid in subject.IDS]
            subject.dump(p/'questions.json',{'questions':queries})
            refs=[{'question_id':qid,'required_evidence_sets':[['needed']],
                   'acceptable_context_ids':['needed'],'expected_status':'answer'} for qid in subject.IDS]
            subject.dump(p/'references.json',{'references':refs})
            evidence=root/'experiments/cytiva/contaminants-pilot-v01/evidence.json';evidence.parent.mkdir(parents=True)
            subject.dump(evidence,{})
            review=root/'synthetic-review.json'
            subject.dump(review,{'manifest_sha256_lf':'test-only','decisions':[{'question_id':qid,
                'decision':'validated','human_quote':'SYNTHETIC TEST FIXTURE, NOT USER APPROVAL',
                'reviewed_at_utc':'2026-10-24T00:00:00Z'} for qid in subject.IDS]})
            output=root/c['run_directory'];real_score=subject.score
            def retrieve(index,text,counter,config,sections):
                self.assertIn(text,('synthetic EN','synthetic FR'))
                self.assertEqual(config,c['config']);self.assertTrue(sections)
                return {'assembled':{'ids':['needed'],'tokens':1},'hits':[],'timings':[]}
            def score(rows,refs):
                self.assertEqual(len(subject.read(output/'contexts-unscored.json')),20)
                return real_score(rows,refs)
            with patch.object(subject,'verify',return_value={'manifest_sha256_lf':'test-only'}), \
                 patch.dict(os.environ,{'PYTHONHASHSEED':'0'}), \
                 patch.object(method,'network_guard',return_value=[]), \
                 patch.object(method.base,'protected_files',return_value={}), \
                 patch.object(method,'build_corpus',return_value=[]), \
                 patch.object(method,'VocabularyIndex',return_value=SimpleNamespace(docs={},passages={})) as index, \
                 patch.object(method,'token_counter',return_value=(len,c['tokenizer'])), \
                 patch.object(method.base,'check_context'), \
                 patch.object(method,'retrieve',side_effect=retrieve) as runtime, \
                 patch.object(subject,'score',side_effect=score):
                result=subject.run(review,root)
                self.assertEqual(result['complete_both_languages'],10)
                self.assertEqual(index.call_args.args[2],None)
                self.assertEqual(runtime.call_count,20)
                with self.assertRaises(FileExistsError):subject.run(review,root)
                self.assertEqual(runtime.call_count,20)
            self.assertTrue((output/'review-snapshot.json').is_file())
            self.assertEqual(subject.read(output/'verification.json')['status'],'completed')


if __name__=='__main__':unittest.main()
