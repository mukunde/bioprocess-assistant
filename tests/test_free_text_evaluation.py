"""Freeze/review gates and pure scoring; never execute the prospective arms."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from experiments.cytiva import free_text_evaluation as selected


def gate_data():
    questions={cid:{'id':cid,'synthetic_gate_test_only':True} for cid in selected.IDS}
    forms=deepcopy(questions)
    refs={cid:{'id':cid,'reservations':['Synthetic gate fixture only.']} for cid in selected.IDS}
    review={'method_lock_sha256_lf':'locked-test-only','decisions':[]}
    for cid in selected.IDS:
        review['decisions'].append({'case_id':cid,'decision':'validated_with_reservations',
            'human_quote':'Synthetic unit-test approval, not a real review.',
            'reviewed_at_utc':'2026-10-26T00:00:00+00:00',
            'question_sha256_canonical':selected.canonical(questions[cid]),
            'submission_sha256_canonical':selected.canonical(forms[cid]),
            'reference_sha256_canonical':selected.canonical(refs[cid]),
            'retained_reservations':refs[cid]['reservations']})
    return questions,forms,refs,review


class FreeTextEvaluationTests(unittest.TestCase):
    def test_review_gate_requires_twelve_actual_content_bindings(self):
        q,s,r,review=gate_data();selected.review_gate(review,'locked-test-only',q,s,r)
        for key,value in (('decision','pending'),('human_quote',None),('reference_sha256_canonical','wrong')):
            bad=deepcopy(review);bad['decisions'][0][key]=value
            with self.assertRaises(ValueError):selected.review_gate(bad,'locked-test-only',q,s,r)

    def test_review_gate_rejects_wrong_freeze_and_removed_case(self):
        q,s,r,review=gate_data()
        with self.assertRaises(ValueError):selected.review_gate(review,'another-freeze',q,s,r)
        review['decisions'].pop()
        with self.assertRaises(ValueError):selected.review_gate(review,'locked-test-only',q,s,r)

    def test_pending_review_blocks_initialization_and_output(self):
        q,s,r,review=gate_data();review['decisions'][0]['decision']='pending'
        def read(path):
            return {'questions':list(q.values())} if path.name=='questions.json' else {'submissions':list(s.values())} if path.name=='submissions.json' else {'references':list(r.values())} if path.name=='references.json' else review
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with patch.object(selected,'verify',return_value={'method_lock_sha256_lf':'locked-test-only'}),patch.object(selected,'verify_method',return_value={'run_directory':'new-output'}),patch.object(selected,'read',side_effect=read),patch.object(selected,'make_runtimes') as runtime:
                with self.assertRaises(ValueError):selected.run(root/'review.json',root)
            runtime.assert_not_called();self.assertFalse((root/'new-output').exists())

    def test_existing_output_refused_without_initialization_or_overwrite(self):
        q,s,r,review=gate_data()
        def read(path):
            return {'questions':list(q.values())} if path.name=='questions.json' else {'submissions':list(s.values())} if path.name=='submissions.json' else {'references':list(r.values())} if path.name=='references.json' else review
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);out=root/'existing';out.mkdir();(out/'marker').write_bytes(b'keep')
            with patch.object(selected,'verify',return_value={'method_lock_sha256_lf':'locked-test-only'}),patch.object(selected,'verify_method',return_value={'run_directory':'existing'}),patch.object(selected,'read',side_effect=read),patch.object(selected,'make_runtimes') as runtime:
                with self.assertRaises(ValueError):selected.run(root/'review.json',root)
            runtime.assert_not_called();self.assertEqual((out/'marker').read_bytes(),b'keep')

    def test_default_cli_only_verifies(self):
        with patch.object(selected,'verify',return_value={'static_only':True}),patch.object(selected,'run') as run,patch('builtins.print'):
            self.assertEqual(selected.main([]),0)
        run.assert_not_called()

    def test_missing_ledger_and_incomplete_inventory_do_not_pass(self):
        form={'tasks':[]}
        self.assertFalse(selected.intent_score({'interpretation_ledger':None},form)[0]['passed'])
        output={'interpretation_ledger':{'inventory_complete':False,'tasks':[],'requested_units':[],'exclusions':[]},'projection':{'submission':None}}
        self.assertFalse(selected.intent_score(output,form)[0]['passed'])

    def test_meaning_keeps_unknown_false_and_original_units_distinct(self):
        self.assertEqual(selected.meaning({'value':'1.0','unit':'mL'}),selected.meaning({'value':'1','unit':'mL'}))
        self.assertNotEqual(selected.meaning({'value':'1','unit':'mL'}),selected.meaning({'value':'1','unit':'L'}))
        self.assertNotEqual(selected.meaning({'state':'unknown','value':None}),selected.meaning({'state':'not_supplied','value':None}))
        self.assertNotEqual(selected.meaning({'value':False}),selected.meaning({'value':None}))

    def test_reviewed_delivery_manifest_and_decision_bindings(self):
        folder=selected.ROOT/selected.PACKAGE
        manifest=selected.read(folder/'package-manifest.json')
        self.assertEqual(len(manifest['files_sha256_lf']),32)
        for name,sha in manifest['files_sha256_lf'].items():
            self.assertEqual(selected.digest(selected.ROOT/name),sha,name)
            self.assertFalse(name.startswith('docs/experiments/cytiva-structured-control-s-'))
        q={x['id']:x for x in selected.read(folder/'questions.json')['questions']}
        forms={x['id']:x for x in selected.read(folder/'submissions.json')['submissions']}
        refs={x['id']:x for x in selected.read(folder/'references.json')['references']}
        review=selected.read(folder/'review.json')
        selected.review_gate(review,selected.digest(folder/'method-lock.json'),q,forms,refs)
        for row in review['decisions']:
            self.assertEqual(selected.read(folder/row['decision_record'])['actual_decision'],row)

    def test_compact_results_preserve_complete_frozen_denominators(self):
        folder=selected.ROOT/selected.PACKAGE
        results=selected.read(folder/'results.json');scores=results['scores']
        self.assertEqual(selected.canonical(scores),results['scores_sha256_canonical'])
        audit=selected.read(selected.ROOT/'docs/experiments/free-text-comparison-v01-results-checks.json')
        self.assertEqual(results['native_scores_sha256_lf'],audit['scores_sha256_lf'])
        self.assertEqual({(r['case_id'],r['language']) for r in scores['observations']},
                         {(cid,lang) for cid in selected.IDS for lang in ('en','fr')})
        self.assertEqual(len(scores['observations']),24)
        self.assertEqual(sum(r['S']['passed'] for r in scores['observations']),24)
        self.assertEqual(sum(r['passed'] for r in scores['observations']),12)
        self.assertEqual((scores['passed_bilingual_pairs'],scores['pair_denominator']),(4,12))
        self.assertEqual(results['completion']['outputs'],48)
        self.assertEqual(results['completion']['network_attempts'],[])


if __name__=='__main__':unittest.main()
