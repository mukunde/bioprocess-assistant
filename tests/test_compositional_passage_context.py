"""Known V/C/H development regressions; never a fresh prospective benchmark."""
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch

from experiments.cytiva import v03b_evaluation as frozen
from experiments.cytiva.cleaning_retrieval import build_corpus,token_counter
from ingestion.compositional_passage_context import CompositionalContextIndex,navigation_plan,phase_mentions
from ingestion.local_passage_retrieval import closure,serialize


class CompositionalContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=frozen.ROOT
        cls.config=frozen.read(root/'experiments/cytiva/section_navigation_v04.json')
        cls.candidate=frozen.read(root/frozen.PACKAGE/'candidate.json')
        cls.corpus=build_corpus(frozen.read(root/'experiments/cytiva/contaminants-pilot-v01/evidence.json'),cls.candidate['source_runtime_policy'])
        counter,_=token_counter();cls.counter=staticmethod(counter)

    def setUp(self):
        self.index=CompositionalContextIndex(self.corpus,self.candidate['source_runtime_policy']['retrieval'],self.config)

    def test_known_v_questions_complete_and_within_explicit_scope(self):
        qs=frozen.read(frozen.ROOT/frozen.PACKAGE/'questions.json')['questions']
        refs={r['question_id']:r for r in frozen.read(frozen.ROOT/frozen.PACKAGE/'references.json')['references']}
        for q in qs:
            for lang in ('en','fr'):
                with self.subTest(question=q['id'],language=lang):
                    result=self.index.retrieve(q['question_'+lang],self.counter);ids=set(result['assembled']['ids']);ref=refs[q['id']]
                    self.assertTrue(any(set(s)<=ids for s in ref['required_evidence_sets']),result)
                    self.assertFalse(ids & set(ref['unrequested_context_ids']))
                    self.assertFalse(ids- set(ref['acceptable_context_ids']))

    def test_existing_h_c_coverage_is_preserved(self):
        root=frozen.ROOT
        h=frozen.read(root/'experiments/cytiva/section-evaluation-v01/questions.json')['questions']
        hr={r['question_id']:r for r in frozen.read(root/'experiments/cytiva/section-evaluation-v01/references.json')['references']}
        c=frozen.read(root/'experiments/cytiva/contaminants-pilot-v01/questions.json')['questions']
        for q in h+c:
            for lang in ('en','fr'):
                with self.subTest(question=q['id'],language=lang):
                    ref=hr[q['id']] if q['id'].startswith('H') else q
                    result=self.index.retrieve(q['question_'+lang],self.counter)
                    self.assertTrue(any(set(s)<=set(result['assembled']['ids']) for s in ref['required_evidence_sets']))
                    if q['id'].startswith('H'):
                        self.assertFalse(set(result['assembled']['ids'])-set(ref['acceptable_context_ids']))

    def test_negations_across_languages_and_clauses(self):
        cases=[("Don't include loading or elution. Washing only.",{'washing'},{'loading','elution'}),
               ('No loading; washing only.',{'washing'},{'loading'}),
               ('Not only washing but elution.',{'washing','elution'},set()),
               ('Not loading or elution. Only washing.',{'washing'},{'loading','elution'}),
               ('Je ne demande ni chargement ni elution. Seulement le lavage.',{'washing'},{'loading','elution'}),
               ('Equilibration rather than loading or washing.',{'equilibration'},{'loading','washing'}),
               ('Pas de chargement; lavage uniquement.',{'washing'},{'loading'}),
               ('Do not substitute loading, washing or elution.',set(),{'loading','washing','elution'}),
               ('Sans chargement mais avec lavage.',{'washing'},{'loading'})]
        for text,pos,neg in cases:
            with self.subTest(text=text):
                p=phase_mentions(text,self.config)
                self.assertEqual(set(p['positive']),pos);self.assertEqual(set(p['negative']),neg)

    def test_positive_multi_phase_requests_are_retained(self):
        for text in ('HiTrap Blue HP loading, washing and elution', 'HiTrap Blue HP chargement et lavage et elution'):
            roles=navigation_plan(text,self.config)['routes'][0]['roles']
            self.assertEqual(set(roles),{'sample_application','wash_conditions','elution_alternatives'})

    def test_buffer_name_alone_does_not_activate_elution_phase(self):
        for text in ('HiTrap Blue HP elution-buffer formulations','HiTrap Blue HP formulations des tampons d elution'):
            p=navigation_plan(text,self.config)
            self.assertEqual(p['routes'][0]['roles'],['buffer_alternatives'])

    def test_formulation_and_phase_are_composed(self):
        roles=navigation_plan('HiTrap Blue HP buffer formulations, then linear gradient elution',self.config)['routes'][0]['roles']
        self.assertEqual(roles,['buffer_alternatives','elution_alternatives'])

    def test_negative_only_request_does_not_fall_back_to_phases(self):
        r=self.index.retrieve('HiTrap Blue HP without loading or washing or elution',self.counter)
        self.assertFalse({'E121-L','E121-W','E121-E','E121-F'} & set(r['assembled']['ids']))

    def test_conflicting_mentions_are_observable(self):
        p=phase_mentions('Do not include elution. Include elution.',self.config)
        self.assertEqual(p['conflicts'],['elution'])
        r=self.index.retrieve('HiTrap Blue HP do not include elution. Include elution.',self.counter)
        self.assertFalse(r['navigation_complete'])

    def test_generic_hitrap_is_not_automatically_blue(self):
        p=navigation_plan('HiTrap column pressure',self.config)
        self.assertEqual(p['routes'],[])
        r=self.index.retrieve('HiTrap syringe note drops',self.counter)
        self.assertEqual(r['navigation_plan']['reason'],'unique_supported_footnote_family')
        self.assertFalse({'E121-W','E121-E'} & set(r['assembled']['ids']))

    def test_unknown_footnote_family_does_not_force_product(self):
        with patch.object(self.index.index,'search',return_value=[]):
            r=self.index.retrieve('HiTrap syringe note drops',self.counter)
        self.assertEqual(r['assembled']['ids'],[])
        self.assertTrue(r['unavailable_source_roles'])

    def test_pressure_and_pending_sources_are_explicit_limits(self):
        for text in ('HiTrap Blue HP maximum pressure','cation exchange pH relative to pI','HiTrap Blue HP equilibration'):
            r=self.index.retrieve(text,self.counter)
            self.assertFalse(r['source_support_complete'])
            self.assertFalse({'E118-I','E121-EQ','E121-L','E121-W','E121-E'} & set(r['assembled']['ids']))

    def test_source_quotes_and_atomic_dependencies_are_unchanged(self):
        self.assertEqual(self.index.passages,{p['id']:p for p in self.corpus})
        r=self.index.retrieve('HiTrap Blue HP washing and elution',self.counter);a=r['assembled']
        self.assertEqual(a['context'],serialize(self.index.passages,a['ids']))
        for pid in a['accepted_seeds']:self.assertTrue(set(closure(self.index.passages,pid))<=set(a['ids']))
        self.assertLessEqual(a['tokens'],2048)
        self.assertFalse({'E118-I','E121-EQ'} & self.index.docs.keys())

    def test_quarantined_warning_blocks_dependent_protocol(self):
        corpus=deepcopy(self.corpus);next(p for p in corpus if p['id']=='E120-W')['quarantined']=True
        index=CompositionalContextIndex(corpus,self.candidate['source_runtime_policy']['retrieval'],self.config)
        self.assertEqual(index.retrieve('HiTrap Blue HP washing',self.counter)['assembled']['ids'],[])

    def test_low_budget_preserves_whole_bundles(self):
        config=deepcopy(self.config);config['max_tokens']=30
        index=CompositionalContextIndex(self.corpus,self.candidate['source_runtime_policy']['retrieval'],config)
        r=index.retrieve('HiTrap Blue HP washing and elution',self.counter)
        self.assertEqual(r['assembled']['ids'],[]);self.assertTrue(r['assembled']['excluded'])

    def test_unrelated_unknown_query_does_not_force_context(self):
        self.assertEqual(self.index.retrieve('unidentified quasar zephyrium',self.counter)['assembled']['ids'],[])

    def test_ambiguous_footnote_families_do_not_choose_one(self):
        self.index.members['another_product']=set(self.index.members['blue'])
        r=self.index.retrieve('HiTrap syringe note drops',self.counter)
        self.assertEqual(r['assembled']['ids'],[])
        self.assertTrue(r['unavailable_source_roles'])

    def test_source_family_fairness_is_observable_when_cap_is_exceeded(self):
        r=self.index.retrieve('Selection Kit screening and Blue Sepharose albumin warning',self.counter)
        self.assertTrue({'E119-S','E119-X','E120-A','E120-W'}<=set(r['assembled']['ids']))
        self.assertLessEqual(len(r['scope_selected_seeds']),6)
        self.assertTrue(r['source_navigation_over_top_k'])
        self.assertFalse(r['navigation_complete'])

    def test_unannotated_scope_is_not_reported_as_zero_errors(self):
        from experiments.cytiva.compositional_navigation_retrieval import annotated_count
        self.assertIsNone(annotated_count([{'extra':[]}],[{}],'extra','acceptable'))
        self.assertEqual(annotated_count([{'extra':[]}],[{'acceptable':[]}],'extra','acceptable'),0)
        self.assertEqual(annotated_count([{'extra':['unexpected']}],[{'acceptable':[]}],'extra','acceptable'),1)

    def test_runner_refuses_old_outputs_and_paths_outside_its_directory(self):
        from experiments.cytiva.compositional_navigation_retrieval import run
        root=frozen.ROOT
        with self.assertRaisesRegex(ValueError,'inside the v04'):
            run(root/'data/experiments/cytiva/v03b-evaluation-v01/locked-run')
        with self.assertRaisesRegex(ValueError,'Existing development run'):
            run(root/'data/experiments/cytiva/scoped-navigation-v04')

    def test_unreviewed_input_preserves_existing_run_in_isolated_fixture(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);package=root/frozen.PACKAGE;package.mkdir(parents=True)
            for name in ('candidate.json','questions.json','references.json'):
                (package/name).write_bytes((frozen.ROOT/frozen.PACKAGE/name).read_bytes())
            candidate=frozen.read(package/'candidate.json')
            output=root/candidate['run_directory'];output.mkdir(parents=True)
            marker=output/'completed.json';marker.write_text('preserve existing results')
            verified=frozen.verify();review=root/'incomplete-review.json'
            frozen.dump(review,{'manifest_sha256_lf':verified['preparation_manifest_sha256_lf'],
                                'method_lock_sha256_lf':verified['method_lock_sha256_lf'],'decisions':[]})
            with patch.object(frozen,'verify',return_value=verified),patch.object(frozen,'make_runtime') as factory:
                with self.assertRaisesRegex(ValueError,'twelve questions'):
                    frozen.run(review,root=root)
                factory.assert_not_called()
            self.assertEqual(marker.read_text(),'preserve existing results')
            self.assertEqual(list(output.iterdir()),[marker])

    def test_original_freeze_remains_valid(self):
        self.assertEqual(frozen.verify()['integrity'],'verified')


if __name__=='__main__':unittest.main()
