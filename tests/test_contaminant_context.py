"""Lexical views, section routing, atomic budgets and four-arm experiment binding."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ingestion.lexical_section_context import VocabularyIndex, lexical_view, overview_plan, assemble_overviews
from ingestion.local_passage_retrieval import closure, serialize
from experiments.cytiva import contaminant_context_retrieval as runner
from experiments.cytiva.cleaning_retrieval import read, build_corpus


class LexicalSectionContextTests(unittest.TestCase):
    def setUp(self):
        self.config = read(runner.CONFIG)
        self.spec = read(runner.ROOT / runner.PREPARATION / 'source_context.json')
        pending = read(runner.PACKAGE / 'manifest.json')['not_individually_reviewed_source_ids']
        self.corpus = build_corpus(read(runner.ROOT / runner.PREPARATION / 'evidence.json'),
                                  runner.base.runtime_policy(self.spec, pending))
        self.index = VocabularyIndex(self.corpus, self.spec['retrieval'], self.config['vocabulary'])
        self.hits = [{'passage_id':'E119-I', 'score':1.0}]

    def test_bilingual_terms_and_abbreviations_have_one_lexical_form(self):
        vocab = self.config['vocabulary']
        self.assertEqual(lexical_view('Albumine transferrine IEX HIC SEC', vocab),
                         lexical_view('Albumin transferrin ion exchange hydrophobic interaction size exclusion', vocab))
        self.assertEqual(lexical_view('échange d’ions', vocab), 'ionexchange')
        self.assertEqual(lexical_view('IEXtreme SECURE chic', vocab), 'iextreme secure chic')

    def test_lexical_projection_never_changes_source_quotes(self):
        for p in self.corpus:
            self.assertEqual(self.index.passages[p['id']], p)
        self.assertFalse({'E118-I','E121-EQ'} & self.index.docs.keys())
        self.assertTrue(all('quote_sha256' not in p for p in self.index.index.passages.values()))
        self.assertNotEqual(self.index.docs, VocabularyIndex(self.corpus, self.spec['retrieval']).docs)

    def test_explicit_section_intro_uses_source_mapping(self):
        plan = overview_plan(self.index.passages,self.hits,'albumine et transferrine après IEX',self.config)
        self.assertEqual(plan['sections'],['albumin-transferrin'])
        self.assertEqual(plan['anchor_ids'],['E119-A'])

    def test_named_blue_unknown_multimethod_request_reserves_conditions(self):
        text='Contaminant inconnu : IEX, HIC ou colonne Blue ?'
        plan=overview_plan(self.index.passages,self.hits,text,self.config)
        self.assertTrue(plan['general_unknown_context'])
        self.assertTrue({'E118-USE','E118-C','E118-M','E120-A','E120-U','E120-W'} <= set(plan['anchor_ids']))

    def test_general_context_requires_unknown_marker_and_multiple_methods(self):
        for text in ('Unknown contaminant; IEX only', 'Compare IEX and HIC for albumin'):
            self.assertFalse(overview_plan(self.index.passages,self.hits,text,self.config)['general_unknown_context'])

    def test_unnamed_blue_does_not_force_named_product_conditions(self):
        plan=overview_plan(self.index.passages,[{'passage_id':'E121-L'}],
                           'Unknown contaminant; compare IEX and HIC',self.config)
        self.assertNotIn('E120-U',plan['anchor_ids'])
        self.assertTrue(plan['general_unknown_context'])

    def test_no_positive_source_hit_does_not_add_overview(self):
        plan=overview_plan(self.index.passages,[],'albumin transferrin Blue Sepharose',self.config)
        self.assertFalse(plan['triggered'])

    def test_overview_is_atomic_under_budget(self):
        text='albumin and transferrin'
        plan=overview_plan(self.index.passages,self.hits,text,self.config)
        ids=list(dict.fromkeys(p for seed in plan['anchor_ids'] for p in closure(self.index.passages,seed)))
        result=assemble_overviews(self.index.passages,self.hits,text,len,self.config,
                                 len(serialize(self.index.passages,ids))-1)
        self.assertEqual(result['overview_status'],'unavailable')
        self.assertFalse(result['budget_complete'])
        self.assertEqual(result['excluded'][0]['reason'],'whole_overview_over_budget')

    def test_quarantined_intro_never_forced(self):
        passages=deepcopy(self.index.passages);passages['E119-A']['quarantined']=True
        result=assemble_overviews(passages,self.hits,'albumin transferrin',len,self.config,100000)
        self.assertEqual(result['overview_status'],'unavailable')
        self.assertNotIn('E119-A',result['ids'])

    def test_both_user_pending_sources_are_blocked_even_in_overview(self):
        for pid in ('E118-I','E121-EQ'):
            config=deepcopy(self.config);config['sections'][1]['overview_ids'].append(pid)
            result=assemble_overviews(self.index.passages,self.hits,'albumin transferrin',len,config,100000)
            self.assertNotIn(pid,result['ids'])
            self.assertEqual(result['overview_status'],'unavailable')

    def test_overview_conserves_quotes_unique_ids_and_dependencies(self):
        result=assemble_overviews(self.index.passages,self.hits,'albumin transferrin',len,self.config,100000)
        self.assertEqual(result['overview_status'],'included')
        runner.base.check_context(self.index.passages,result,len,100000,['E118-I','E121-EQ'])
        self.assertEqual(result['context'],serialize(self.index.passages,result['ids']))


class ContextAblationRunnerTests(unittest.TestCase):
    @staticmethod
    def rows():
        return [{'question_id':'probe','language':lang,'variant':variant,'hits':[],
                 'reference_coverage':1.0,'complete_evidence':True,
                 'assembled':{'ids':[],'context':'{}','tokens':10,'excluded':[]},
                 'timings':[{'retrieval_ms':1,'assembly_ms':1}]}
                for variant in runner.VARIANTS for lang in ('en','fr')]

    def test_grid_and_same_retrieval_pair_checks(self):
        rows=self.rows()
        self.assertEqual(runner.summarize(rows,['probe'])['combined']['complete_both_languages'],1)
        changed=deepcopy(rows);next(r for r in changed if r['variant']=='section')['hits']=[{'passage_id':'x'}]
        for broken in (rows[:-1],rows+[rows[0]],rows+[{**rows[0],'variant':'unknown'}],changed):
            with self.assertRaises(ValueError):runner.summarize(broken,['probe'])

    def test_existing_output_refused_before_guard(self):
        with tempfile.TemporaryDirectory(dir=runner.ROOT/'tmp') as temp, patch.object(runner,'network_guard') as guard:
            with self.assertRaisesRegex(ValueError,'already exists'):runner.run(Path(temp))
            guard.assert_not_called()

    def test_reference_failure_blocks_tokenizer(self):
        with tempfile.TemporaryDirectory(dir=runner.ROOT/'tmp') as temp, \
             patch.object(runner,'network_guard',return_value=[]), \
             patch.object(runner.base,'protected_files',return_value={}), \
             patch.object(runner.base,'verify_reference',side_effect=ValueError('Invalid review')), \
             patch.object(runner,'token_counter') as counter:
            with self.assertRaisesRegex(ValueError,'Invalid review'):runner.run(Path(temp)/'run')
            counter.assert_not_called()

    def test_smoke_run_binds_inputs_and_preserves_pending_states(self):
        with tempfile.TemporaryDirectory(dir=runner.ROOT/'tmp') as temp, \
             patch.object(runner,'network_guard',return_value=[]), \
             patch.object(runner,'token_counter',return_value=(len,{'name':'test_character_count'})):
            output=Path(temp)/'run';runner.run(output)
            m=read(output/'manifest.json');rows=read(output/'results.json')
            self.assertEqual(len(rows),80)
            self.assertEqual(m['pending_source_ids'],['E118-I','E121-EQ'])
            self.assertEqual(m['pending_source_leakage'],0)
            self.assertFalse(m['benchmark_results_human_validated'])
            for f,h in m['code_and_input_sha256_lf'].items():
                self.assertEqual(runner.digest(output/'input-snapshot'/f),h)


if __name__=='__main__':
    unittest.main()
