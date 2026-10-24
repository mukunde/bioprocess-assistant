"""Portable development export verification and corruption regressions."""
from copy import deepcopy
import unittest
from experiments.cytiva import verify_section_navigation_package as v


class SectionNavigationPackageTests(unittest.TestCase):
    def test_portable_export_verifies_without_local_runs(self):
        result=v.verify();self.assertEqual(result['measured_contexts'],80)
        self.assertFalse(result['independent_evaluation'])

    def test_archived_a_code_corruption_is_detected(self):
        p=v.h.frozen.read(v.ROOT/v.PACKAGE/'provenance.json')
        a=deepcopy(p['original_runs']['development-a']);name=next(iter(a['archived_code_overrides']))
        a['archived_code_overrides'][name]+='changed'
        with self.assertRaises(ValueError):v.check_input_versions(v.ROOT,a)

    def test_native_metric_corruption_is_detected(self):
        results=v.h.frozen.read(v.ROOT/v.PACKAGE/'results.json');p=v.h.frozen.read(v.ROOT/v.PACKAGE/'provenance.json')
        changed=deepcopy(results['development-b']);changed['metrics']['H_new']['mean_context_tokens']=0
        corpus,_=v.h.source_corpus(v.ROOT)
        with self.assertRaises(ValueError):v.check_run('development-b',changed,p['original_runs']['development-b'],corpus,{})

    def test_missing_complete_intent_is_detected(self):
        rows=v.h.frozen.read(v.ROOT/v.PACKAGE/'results.json')['development-b']['rows']
        rows=[r for r in rows if r['question_id']!='H10']
        with self.assertRaises(ValueError):v.runtime.validate_grid(rows,[f'H{i:02d}' for i in range(1,11)]+[f'C{i:02d}' for i in range(1,11)])

    def test_a_and_b_versions_are_distinct_and_preserved(self):
        p=v.h.frozen.read(v.ROOT/v.PACKAGE/'provenance.json')
        self.assertEqual(len(p['original_runs']['development-a']['archived_code_overrides']),3)
        self.assertEqual(p['original_runs']['development-b']['archived_code_overrides'],{})

    def test_source_quarantine_is_not_human_approval(self):
        corpus,_=v.h.source_corpus(v.ROOT)
        self.assertTrue(corpus['E118-I']['quarantined']);self.assertTrue(corpus['E121-EQ']['quarantined'])
        for name,run in v.h.frozen.read(v.ROOT/v.PACKAGE/'results.json').items():
            if isinstance(run,dict) and 'rows' in run:
                for row in run['rows']:self.assertFalse({'E118-I','E121-EQ'} & set(row['assembled']['ids']))


if __name__=='__main__':unittest.main()
