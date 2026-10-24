"""Safety gates and reference-only scoring for the new development runner."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from experiments.cytiva import section_navigation_retrieval as runner


class SectionNavigationRunnerTests(unittest.TestCase):
    def test_existing_trial_is_refused_before_guard(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(runner,'network_guard') as guard:
            with self.assertRaisesRegex(ValueError,'Output exists'):
                runner.run(tmp,Path(tmp)/'review.json')
            guard.assert_not_called()

    def test_unreviewed_reference_blocks_tokenizer_and_output(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict('os.environ',{'PYTHONHASHSEED':'0'}), \
             patch.object(runner,'network_guard',return_value=[]), \
             patch.object(runner.frozen,'verify',return_value={'manifest_sha256_lf':'test'}), \
             patch.object(runner.frozen,'review_gate',side_effect=ValueError('Pending review')), \
             patch.object(runner,'token_counter') as counter:
            output=Path(tmp)/'new-run'
            with self.assertRaisesRegex(ValueError,'Pending review'):runner.run(output,Path(tmp)/'review.json')
            counter.assert_not_called();self.assertFalse(output.exists())

    def test_all_expected_intents_stay_in_denominator(self):
        rows=[{'question_id':qid,'language':lang} for qid in ('a','b') for lang in ('en','fr')]
        runner.validate_grid(rows,['a','b'])
        for broken in (rows[:-1],rows+[rows[0]],rows[:2]):
            with self.assertRaises(ValueError):runner.validate_grid(broken,['a','b'])

    def test_score_is_after_runtime_and_does_not_rewrite_contexts(self):
        rows=[{'question_id':'probe','language':lang,'assembled':{'ids':['needed'],'tokens':10,'excluded':[]}}
              for lang in ('en','fr')]
        copy=deepcopy(rows)
        references={'probe':{'required_evidence_sets':[['needed','missing']],
                    'acceptable_context_ids':['needed','missing'],'expected_status':'clarify'}}
        result=runner.score_rows(rows,references,{},len)
        self.assertEqual(rows,copy)
        self.assertEqual(runner.summary(result)['complete_both_languages'],0)
        self.assertTrue(all(r['missing_ids']==['missing'] for r in result))
        self.assertTrue(all(not r['response_status_evaluated'] for r in result))

    def test_c_noise_is_unknown_without_annotated_acceptable_sources(self):
        rows=[{'question_id':'probe','language':lang,'assembled':{'ids':['needed'],'tokens':10,'excluded':[]}}
              for lang in ('en','fr')]
        refs={'probe':{'required_evidence_sets':[['needed']],'expected_status':'answer'}}
        result=runner.score_rows(rows,refs,{},len)
        self.assertIsNone(runner.summary(result)['contexts_outside_acceptable_reference'])


if __name__=='__main__':unittest.main()
