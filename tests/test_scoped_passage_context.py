"""Development regressions for scoped source navigation, not a fresh holdout."""
from copy import deepcopy
from pathlib import Path
import unittest
from experiments.cytiva import section_evaluation as frozen
from experiments.cytiva.cleaning_retrieval import build_corpus,token_counter
from ingestion.local_passage_retrieval import closure,serialize
from ingestion.scoped_passage_context import ScopedContextIndex,navigation_plan
from ingestion.lexical_section_context import lexical_view

CONFIG=frozen.ROOT/'experiments/cytiva/section_navigation_v03.json'


def source_fixture():
    candidate=frozen.read(frozen.ROOT/frozen.PACKAGE/'candidate.json')
    evidence=frozen.read(frozen.ROOT/'experiments/cytiva/contaminants-pilot-v01/evidence.json')
    return build_corpus(evidence,candidate['source_runtime_policy']),candidate


class ScopedContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus,cls.candidate=source_fixture()
        cls.config=frozen.read(CONFIG)
        counter,_=token_counter()
        cls.counter=staticmethod(counter)

    def setUp(self):self.index=ScopedContextIndex(self.corpus,self.candidate['source_runtime_policy']['retrieval'],self.config)

    def test_vocabulary_aligns_french_and_english_without_changing_quotes(self):
        self.assertEqual(lexical_view('albumine transferrine anticorps bovines',self.config['vocabulary']),
                         lexical_view('albumin transferrin antibody bovine',self.config['vocabulary']))
        self.assertEqual(self.index.passages,{p['id']:p for p in self.corpus})

    def test_h02_and_h09_both_languages_have_their_required_sources(self):
        queries=frozen.read(frozen.ROOT/frozen.PACKAGE/'questions.json')['questions']
        refs={r['question_id']:r for r in frozen.read(frozen.ROOT/frozen.PACKAGE/'references.json')['references']}
        for query in queries:
            if query['id'] not in ('H02','H09'):continue
            for lang in ('en','fr'):
                with self.subTest(question=query['id'],language=lang):
                    result=self.index.retrieve(query['question_'+lang],self.counter)
                    required=set(refs[query['id']]['required_evidence_sets'][0])
                    self.assertTrue(required<=set(result['assembled']['ids']))

    def test_all_seen_h_and_c_cases_preserve_reference_coverage(self):
        h=frozen.read(frozen.ROOT/frozen.PACKAGE/'questions.json')['questions']
        hrefs={r['question_id']:r for r in frozen.read(frozen.ROOT/frozen.PACKAGE/'references.json')['references']}
        c=frozen.read(frozen.ROOT/'experiments/cytiva/contaminants-pilot-v01/questions.json')['questions']
        for query in h+c:
            reference=hrefs[query['id']] if query['id'].startswith('H') else query
            for lang in ('en','fr'):
                with self.subTest(question=query['id'],language=lang):
                    result=self.index.retrieve(query['question_'+lang],self.counter)
                    self.assertTrue(any(set(s)<=set(result['assembled']['ids']) for s in reference['required_evidence_sets']))

    def test_h_context_stays_within_annotated_scope_and_budget(self):
        # Portable source assertion: no private saved run is required for tests.
        qs=frozen.read(frozen.ROOT/frozen.PACKAGE/'questions.json')['questions']
        refs={r['question_id']:r for r in frozen.read(frozen.ROOT/frozen.PACKAGE/'references.json')['references']}
        for q in qs:
            for lang in ('en','fr'):
                with self.subTest(question=q['id'],language=lang):
                    result=self.index.retrieve(q['question_'+lang],self.counter)
                    self.assertFalse(set(result['assembled']['ids'])-set(refs[q['id']]['acceptable_context_ids']))
                    self.assertLessEqual(result['assembled']['tokens'],2048)

    def test_unknown_identity_does_not_require_named_methods(self):
        for text in ('I do not know what this protein signal is after affinity purification',
                     'Je ne sais pas de quoi provient ce signal protéique après purification'):
            plan=navigation_plan(text,self.config)
            self.assertEqual(plan['reason'],'unspecified_contaminant_context')
            self.assertEqual(plan['routes'][0]['group'],'general')

    def test_named_blue_unknown_retains_conditions(self):
        result=self.index.retrieve('Unknown contaminant after affinity purification; IEX or Blue Sepharose?',self.counter)
        self.assertTrue({'E118-USE','E118-C','E118-M','E120-U','E120-W'}<=set(result['assembled']['ids']))

    def test_loading_with_buffer_is_not_a_buffer_formulation_request(self):
        plan=navigation_plan('HiTrap Blue HP sample loading with binding buffer: what flow?',self.config)
        self.assertEqual(plan['routes'][0]['roles'],['sample_application'])

    def test_pending_equilibration_returns_only_reviewed_scope(self):
        result=self.index.retrieve('HiTrap Blue HP equilibration flow rate?',self.counter)
        self.assertTrue(result['unavailable_source_roles'])
        self.assertFalse({'E118-I','E121-EQ','E121-L','E121-W','E121-E'} & set(result['assembled']['ids']))
        self.assertTrue({'E120-P','E121-PH','E120-W'}<=set(result['assembled']['ids']))

    def test_explicit_other_phase_contrast_does_not_supply_other_phase_parameters(self):
        questions=frozen.read(frozen.ROOT/frozen.PACKAGE/'questions.json')['questions']
        q=next(q for q in questions if q['id']=='H10')
        for lang in ('en','fr'):
            result=self.index.retrieve(q['question_'+lang],self.counter)
            self.assertTrue(result['navigation_plan']['phase_exclusion_applied'])
            self.assertEqual(result['navigation_plan']['routes'][0]['roles'],['equilibration'])
            self.assertFalse({'E121-L','E121-W','E121-E','E121-EQ'} & set(result['assembled']['ids']))
            self.assertTrue({'E120-P','E121-PH','E120-W'}<=set(result['assembled']['ids']))

    def test_no_positive_hit_produces_no_forced_general_context(self):
        result=self.index.retrieve('unidentified quasar zephyrium',self.counter)
        self.assertEqual(result['assembled']['ids'],[])

    def test_no_named_scope_does_not_append_a_section_overview(self):
        result=self.index.retrieve('purification',self.counter)
        self.assertEqual(result['navigation_plan']['reason'],'no_explicit_scope')
        self.assertLessEqual(len(result['scope_selected_seeds']),6)

    def test_atomic_dependencies_and_exact_source_provenance(self):
        result=self.index.retrieve('HiTrap Blue HP loading and washing flow',self.counter)
        a=result['assembled'];self.assertEqual(a['context'],serialize(self.index.passages,a['ids']))
        self.assertEqual(len(a['ids']),len(set(a['ids'])))
        for seed in a['accepted_seeds']:self.assertTrue(set(closure(self.index.passages,seed))<=set(a['ids']))
        self.assertFalse({'E118-I','E121-EQ'} & self.index.docs.keys())

    def test_over_budget_bundle_is_not_truncated(self):
        config=deepcopy(self.config);config['max_tokens']=30
        index=ScopedContextIndex(self.corpus,self.candidate['source_runtime_policy']['retrieval'],config)
        result=index.retrieve('HiTrap Blue HP loading and washing flow',self.counter)
        self.assertTrue(result['assembled']['excluded'])
        self.assertEqual(result['assembled']['ids'],[])
        self.assertFalse(result['navigation_complete'])

    def test_quarantined_scope_warning_blocks_all_dependent_protocols(self):
        corpus=deepcopy(self.corpus)
        next(p for p in corpus if p['id']=='E120-W')['quarantined']=True
        index=ScopedContextIndex(corpus,self.candidate['source_runtime_policy']['retrieval'],self.config)
        result=index.retrieve('HiTrap Blue HP loading flow',self.counter)
        self.assertFalse({'E120-W','E121-L'} & set(result['assembled']['ids']))

    def test_source_role_inventory_is_validated(self):
        config=deepcopy(self.config);config['source_roles'].pop('E118-C')
        with self.assertRaises(ValueError):ScopedContextIndex(self.corpus,self.candidate['source_runtime_policy']['retrieval'],config)

    def test_frozen_method_and_references_still_verify(self):
        self.assertEqual(frozen.verify()['integrity'],'verified')


if __name__=='__main__':unittest.main()
