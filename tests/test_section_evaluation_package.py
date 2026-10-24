"""Portable selected H export checks without private local artifacts or tokenizers."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from experiments.cytiva import verify_section_evaluation_package as v


class SectionEvaluationPackageTests(unittest.TestCase):
    def test_portable_export_verifies(self):
        result=v.verify();self.assertEqual(result['bilingual_complete'],8)
        self.assertFalse(result['benchmark_executed_by_verifier'])

    def test_event_quote_change_is_detected(self):
        p=v.ROOT/v.PACKAGE;events=deepcopy(v.frozen.read(p/'events.json'));events[0]['decision']['human_quote']='changed'
        qs={q['id']:q for q in v.frozen.read(v.ROOT/v.frozen.PACKAGE/'questions.json')['questions']}
        refs={r['question_id']:r for r in v.frozen.read(v.ROOT/v.frozen.PACKAGE/'references.json')['references']}
        review=v.frozen.read(p/'review.json')
        with self.assertRaises(ValueError):v.check_review(review,events,qs,refs,review['manifest_sha256_lf'])

    def test_quote_and_dependency_changes_are_detected(self):
        corpus,_=v.source_corpus(v.ROOT)
        row=deepcopy(v.frozen.read(v.ROOT/v.PACKAGE/'results.json')['contexts'][0])
        row['assembled']['context']+='changed'
        with self.assertRaises(ValueError):v.check_context(row,corpus)

    def test_missing_formulation_is_not_removed_from_denominator(self):
        results=deepcopy(v.frozen.read(v.ROOT/v.PACKAGE/'results.json'));results['contexts'].pop()
        corpus,_=v.source_corpus(v.ROOT)
        refs=v.frozen.read(v.ROOT/v.frozen.PACKAGE/'references.json')['references']
        with self.assertRaises(ValueError):v.check_h_results(results,corpus,refs)

    def test_package_file_hash_is_lf_crlf_portable(self):
        with tempfile.TemporaryDirectory() as temp:
            a,b=Path(temp)/'a',Path(temp)/'b';a.write_bytes(b'a\n');b.write_bytes(b'a\r\n')
            self.assertEqual(v.frozen.digest(a),v.frozen.digest(b))

    def test_lot_a_has_no_lot_b_support_dependency(self):
        self.assertFalse(any('section_navigation' in n or 'scoped_passage' in n for n in v.SUPPORT))


if __name__=='__main__':unittest.main()
