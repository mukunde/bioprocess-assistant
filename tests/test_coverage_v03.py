"""Coverage contract regressions; no model/API or historical rescoring."""
from copy import deepcopy
import hashlib
import unittest
from jsonschema import ValidationError
from unittest.mock import patch

from ingestion.coverage_v03 import summarize, validate_summary
from ingestion.structured_request_v03 import StructuredControlV03, CoverageStructuredCore
from ingestion.structured_sources import ROOT, read, compact


class CoverageV03Tests(unittest.TestCase):
    def test_support_without_eligible_covered_context_is_rejected(self):
        for eligible,covered in ((['a'],['a']),(['a','b'],['a']),([],[])):
            with self.subTest(eligible=eligible,covered=covered),self.assertRaises(ValueError):
                summarize(['a','b'],['a','b'],supported_keys=['a','b'],
                          eligible_keys=eligible,covered_keys=covered)

    def test_numeric_validator_rejects_excess_support_even_without_full_service(self):
        good=summarize(['a','b'],['a','b'],supported_keys=['a'],eligible_keys=['a'],covered_keys=['a'])
        for full in (False,True):
            bad=deepcopy(good);bad['request_support']['supported_units']=2
            bad['request_support']['all_requested_units_supported']=full;bad['full_service']=full
            bad['has_unserved_known_units']=False
            with self.subTest(full=full),self.assertRaises(ValueError):validate_summary(bad)

    def test_unknown_error_denominator_preserves_valid_sibling_support(self):
        summary=summarize(['a','b'],['a','b'],supported_keys=['a'],eligible_keys=None,
                          assessment_complete=False,has_assessment_error=True)
        validate_summary(summary)
        self.assertEqual(summary['request_support']['supported_units'],1)
        self.assertIsNone(summary['eligible_ready_context_coverage']['covered_units'])
        self.assertFalse(summary['full_service'])

    def test_twelve_approved_semantic_design_boundaries(self):
        for example in read(ROOT/'docs/technical/coverage-summary-v03-examples.json')['examples']:
            x=example['summary'];k=x['known_requested_units'];a=x['accounted_units']
            c=x['eligible_ready_context_coverage'];s=x['request_support']['supported_units']
            known=list(range(k));eligible=None if c['eligible_ready_units'] is None else list(range(c['eligible_ready_units']))
            covered=[] if c['covered_units'] is None else list(range(c['covered_units']))
            with self.subTest(case=example['id']):
                actual=summarize(known,list(range(a)),supported_keys=list(range(s)),
                    eligible_keys=eligible,covered_keys=covered,inventory_complete=x['inventory_complete'],
                    assessment_complete=x['assessment_complete'],has_assessment_error=x['has_assessment_error'])
                self.assertEqual(actual,x)
                validate_summary(actual)

    def test_duplicate_outcome_is_not_hidden_by_equal_lengths(self):
        x=summarize(['a','b'],['a','a'],eligible_keys=[])
        self.assertFalse(x['all_known_units_accounted_for'])
        self.assertEqual(x['accounted_units'],0)
        self.assertEqual(x['eligible_ready_context_coverage']['state'],'error')

    def test_orphan_and_duplicate_requested_keys_are_errors(self):
        for known,rows in ((['a'],['a','orphan']),(['a','a'],['a','a'])):
            x=summarize(known,rows,eligible_keys=[])
            self.assertFalse(x['full_service']);self.assertTrue(x['has_assessment_error'])

    def test_unknown_denominator_cannot_be_replaced_by_zero(self):
        x=summarize(['a'],['a'],eligible_keys=None,assessment_complete=False)
        self.assertIsNone(x['eligible_ready_context_coverage']['eligible_ready_units'])
        self.assertEqual(x['eligible_ready_context_coverage']['state'],'not_assessed')

    def test_invalid_summary_counts_or_full_service_rejected(self):
        x=summarize(['a','b'],['a','b'],supported_keys=['a'],eligible_keys=['a'],covered_keys=['a'])
        for target in ('denominator','full','covered'):
            bad=deepcopy(x)
            if target=='denominator':bad['request_support']['known_requested_units']=1
            elif target=='full':bad['full_service']=True
            else:bad['eligible_ready_context_coverage']['covered_units']=2
            with self.subTest(target=target),self.assertRaises((ValueError,ValidationError)):
                validate_summary(bad)

    def test_real_budget_rejection_stays_in_preassembly_denominator(self):
        core=CoverageStructuredCore()
        form=deepcopy(read(ROOT/'experiments/cytiva/free-text-v02-comparison-v01/submissions.json')['submissions'][0]['input_en'])
        # Real planner execution with a deliberately tiny internal test budget.
        core.adapter.config['execution_policy']['max_serialized_context_tokens']=64
        result=core.evaluate(form)
        summary=core.coverage_for(result)
        self.assertEqual(summary['eligible_ready_context_coverage']['eligible_ready_units'],3)
        self.assertEqual(summary['eligible_ready_context_coverage']['covered_units'],0)
        self.assertEqual(summary['eligible_ready_context_coverage']['state'],'partial')
        self.assertEqual(summary['known_requested_units'],3)

    def test_structured_fv06_new_metric_and_legacy_flag_are_separate(self):
        control=StructuredControlV03()
        forms=read(ROOT/'experiments/cytiva/free-text-v02-comparison-v01/submissions.json')['submissions']
        form=next(x['input_en'] for x in forms if x['id']=='FV06')
        out=control.evaluate(form)
        self.assertIsNone(out['failure'])
        self.assertFalse(out['compatibility_result']['plan']['all_supported_ready_units_covered'])
        self.assertEqual(out['coverage_summary']['eligible_ready_context_coverage'],
                         {'state':'complete','scope':'complete_request','eligible_ready_units':1,'covered_units':1})
        self.assertEqual(out['coverage_summary']['request_support']['supported_units'],1)
        self.assertEqual(out['coverage_summary']['known_requested_units'],3)
        self.assertFalse(out['coverage_summary']['full_service'])

    def test_runtime_failure_accounts_for_each_known_request(self):
        control=StructuredControlV03()
        form=read(ROOT/'experiments/cytiva/free-text-v02-comparison-v01/submissions.json')['submissions'][0]['input_en']
        with patch.object(control.core,'evaluate',side_effect=RuntimeError('not exposed')):
            out=control.evaluate(form)
        self.assertEqual(len(out['unit_errors']),3)
        self.assertTrue(out['coverage_summary']['all_known_units_accounted_for'])
        self.assertEqual(out['coverage_summary']['eligible_ready_context_coverage']['state'],'error')
        self.assertEqual(out['coverage_summary']['request_support']['supported_units'],0)
        self.assertNotIn('not exposed',str(out))

    def test_context_forgery_cannot_count_as_support(self):
        control=StructuredControlV03();evaluate=control.core.evaluate
        form=read(ROOT/'experiments/cytiva/free-text-v02-comparison-v01/submissions.json')['submissions'][0]['input_en']
        def forged(*a,**kw):
            result=evaluate(*a,**kw)
            result['plan']['context']['source_passages'][0]['quote']='forged'
            return result
        with patch.object(control.core,'evaluate',side_effect=forged):out=control.evaluate(form)
        self.assertTrue(out['coverage_summary']['has_assessment_error'])
        self.assertEqual(out['coverage_summary']['request_support']['supported_units'],0)
        self.assertFalse(out['coverage_summary']['full_service'])

    def test_rehashed_binding_or_missing_warning_still_fails_semantic_validation(self):
        form=read(ROOT/'experiments/cytiva/free-text-v02-comparison-v01/submissions.json')['submissions'][0]['input_en']
        for defect in ('binding','warning','input'):
            control=StructuredControlV03();evaluate=control.core.evaluate
            def forged(*a,**kw):
                result=evaluate(*a,**kw);context=result['plan']['context']
                if defect=='binding':context['bindings'][0]['column']['value']['bed_volume']['value']='5'
                elif defect=='warning':context['source_passages']=[p for p in context['source_passages'] if p['id']!='E120-W']
                else:result['canonical_request']['input_snapshot']['tasks'][0]['product']['value']='HiTrap Blue HP 5 mL'
                result['audit']['context_sha256']=hashlib.sha256(compact(context).encode('utf-8')).hexdigest()
                result['plan']['context_tokens']=control.core._count_tokens(compact(context))
                return result
            with self.subTest(defect=defect),patch.object(control.core,'evaluate',side_effect=forged):out=control.evaluate(form)
            self.assertTrue(out['coverage_summary']['has_assessment_error'])
            self.assertEqual(out['coverage_summary']['request_support']['supported_units'],0)

    def test_eligibility_snapshot_is_per_request_without_cross_call_state(self):
        core=CoverageStructuredCore();forms=read(ROOT/'experiments/cytiva/free-text-v02-comparison-v01/submissions.json')['submissions']
        first=core.evaluate(forms[0]['input_en']);saved=deepcopy(first['audit']['coverage_basis_v03'])
        second=core.evaluate(next(x['input_fr'] for x in forms if x['id']=='FV06'))
        self.assertEqual(first['audit']['coverage_basis_v03'],saved)
        self.assertEqual(core.coverage_for(first)['eligible_ready_context_coverage']['eligible_ready_units'],3)
        self.assertEqual(core.coverage_for(second)['eligible_ready_context_coverage']['eligible_ready_units'],1)


if __name__=='__main__':unittest.main()
