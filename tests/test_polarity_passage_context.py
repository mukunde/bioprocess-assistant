"""Known-question development regressions, not prospective validation."""
from copy import deepcopy
import unittest
from unittest.mock import patch

from experiments.cytiva import v04_evaluation as frozen
from experiments.cytiva.cleaning_retrieval import build_corpus, token_counter
from ingestion.local_passage_retrieval import closure, serialize
from ingestion.polarity_passage_context import CompositionalContextIndex, phase_mentions


class PolarityContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config=frozen.read(frozen.ROOT/'experiments/cytiva/section_navigation_v05.json')
        cls.candidate=frozen.read(frozen.ROOT/frozen.PACKAGE/'candidate.json')
        cls.corpus=build_corpus(frozen.read(frozen.ROOT/'experiments/cytiva/contaminants-pilot-v01/evidence.json'),cls.candidate['source_runtime_policy'])
        counter,_=token_counter();cls.counter=staticmethod(counter)

    def setUp(self):
        self.index=CompositionalContextIndex(self.corpus,self.candidate['source_runtime_policy']['retrieval'],deepcopy(self.config))

    def test_known_w_completeness_scope_and_diagnostics(self):
        queries=frozen.read(frozen.ROOT/frozen.PACKAGE/'questions.json')['questions']
        refs=frozen.read(frozen.ROOT/frozen.PACKAGE/'references.json')['references']
        contexts=[]
        for q in queries:
            for lang in ('en','fr'):
                contexts.append(dict(question_id=q['id'],language=lang,**self.index.retrieve(q['question_'+lang],self.counter)))
        for row in frozen.score(contexts,refs)['rows']:
            with self.subTest(q=row['question_id'],lang=row['language']):
                self.assertTrue(row['complete_evidence'],row)
                self.assertFalse(row['unrequested_context_ids_present'],row)
                self.assertFalse(row['outside_acceptable_ids'],row)
                self.assertFalse(row['diagnostic_failures'],row)

    def test_new_synthetic_negation_forms(self):
        cases=[('Exclude loading and elution; washing only.',{'washing'},{'loading','elution'}),
               ('Elution is not needed. Loading is outside scope.',set(),{'elution','loading'}),
               ('Leave washing and elution out. Loading only.',{'loading'},{'washing','elution'}),
               ('Ecarter le chargement et l elution; lavage uniquement.',{'washing'},{'loading','elution'}),
               ('Elution rather than loading.',{'elution'},{'loading'}),
               ('Not only washing but elution.',{'washing','elution'},set()),
               ('Non seulement le lavage mais aussi l elution.',{'washing','elution'},set())]
        for text,pos,neg in cases:
            with self.subTest(text=text):
                result=phase_mentions(text,self.config)
                self.assertEqual(set(result['positive']),pos)
                self.assertEqual(set(result['negative']),neg)

    def test_known_v_h_c_coverage_and_annotated_scope(self):
        root=frozen.ROOT
        suites=[('v03b-evaluation-v01',False),('section-evaluation-v01',False),('contaminants-pilot-v01',True)]
        for folder,embedded in suites:
            package=root/'experiments/cytiva'/folder
            questions=frozen.read(package/'questions.json')['questions']
            refs=questions if embedded else frozen.read(package/'references.json')['references']
            byid={r.get('question_id',r.get('id')):r for r in refs}
            for q in questions:
                for lang in ('en','fr'):
                    with self.subTest(question=q['id'],lang=lang):
                        ref=byid[q['id']]
                        ids=set(self.index.retrieve(q['question_'+lang],self.counter)['assembled']['ids'])
                        self.assertTrue(any(set(s)<=ids for s in ref['required_evidence_sets']))
                        if 'acceptable_context_ids' in ref:
                            self.assertFalse(ids-set(ref['acceptable_context_ids']))
                        self.assertFalse(ids & set(ref.get('unrequested_context_ids',[])))

    def test_runner_preserves_existing_output_and_rejects_other_paths(self):
        import tempfile
        from pathlib import Path
        from experiments.cytiva import polarity_navigation_retrieval as runner
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            output=root/'data/experiments/cytiva/compositional-navigation-v05/existing'
            output.mkdir(parents=True)
            marker=output/'marker.txt';marker.write_text('preserve')
            with patch.object(runner,'ROOT',root),patch.object(runner,'verify') as verify:
                with self.assertRaisesRegex(ValueError,'Existing development run'):
                    runner.run(output)
                with self.assertRaisesRegex(ValueError,'inside the v05'):
                    runner.run(root/'elsewhere')
                verify.assert_not_called()
            self.assertEqual(marker.read_text(),'preserve')

    def test_coordinated_buffer_names_do_not_request_operating_elution(self):
        for text in ('HiTrap Blue HP binding and elution buffer alternatives',
                     "HiTrap Blue HP formulations des tampons de liaison et d’elution"):
            result=self.index.retrieve(text,self.counter)
            self.assertIn('E121-B',result['assembled']['ids'])
            self.assertNotIn('E121-E',result['assembled']['ids'])

    def test_contradictory_scope_withholds_operating_parameters(self):
        for text in ('HiTrap Blue HP include washing but exclude washing',
                     'HiTrap Blue HP inclus le lavage mais exclus le lavage'):
            result=self.index.retrieve(text,self.counter)
            self.assertTrue(result['navigation_plan']['clarification_required'])
            self.assertFalse(result['navigation_complete'])
            self.assertFalse({'E121-B','E121-L','E121-W','E121-E','E121-F'} & set(result['assembled']['ids']))

    def test_negative_product_does_not_fallback_to_excluded_family(self):
        result=self.index.retrieve('I am not asking for Blue Sepharose',self.counter)
        self.assertFalse(set(result['assembled']['ids']) & self.index.members['blue'])

    def test_no_lexical_family_support_does_not_force_a_route(self):
        with patch.object(self.index.index,'search',return_value=[]):
            result=self.index.retrieve('HiTrap Blue HP washing',self.counter)
        self.assertEqual(result['assembled']['ids'],[])
        self.assertFalse(result['navigation_complete'])

    def test_quarantined_dependency_blocks_protocol(self):
        corpus=deepcopy(self.corpus)
        next(p for p in corpus if p['id']=='E120-W')['quarantined']=True
        index=CompositionalContextIndex(corpus,self.candidate['source_runtime_policy']['retrieval'],self.config)
        self.assertEqual(index.retrieve('HiTrap Blue HP washing',self.counter)['assembled']['ids'],[])

    def test_context_is_exact_atomic_and_budgeted(self):
        result=self.index.retrieve('HiTrap Blue HP washing and elution',self.counter)['assembled']
        self.assertEqual(result['context'],serialize(self.index.passages,result['ids']))
        self.assertLessEqual(result['tokens'],2048)
        for pid in result['accepted_seeds']:
            self.assertTrue(set(closure(self.index.passages,pid))<=set(result['ids']))
        self.assertFalse({'E118-I','E121-EQ'} & self.index.docs.keys())
        self.index.config['max_tokens']=30
        small=self.index.retrieve('HiTrap Blue HP washing',self.counter)
        self.assertEqual(small['assembled']['ids'],[])
        self.assertTrue(small['assembled']['excluded'])

    def test_frozen_v04_is_unchanged(self):
        self.assertEqual(frozen.verify()['integrity'],'verified')


if __name__=='__main__':unittest.main()
