"""Tamper detection, state replay and portability of the C01-C10 reference package."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from experiments.cytiva.verify_contaminant_questions_package import (
    ROOT, PACKAGE, SUPPORT, DEPENDENCIES, file_digest, load, verify)


class ContaminantQuestionsPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'tmp', prefix='contaminant-review-')
        self.addCleanup(self.temp.cleanup)
        self.package = Path(self.temp.name) / 'package'
        shutil.copytree(PACKAGE, self.package)

    def change(self, name, mutate):
        path = self.package / name
        value = load(path)
        mutate(value)
        path.write_text(json.dumps(value, ensure_ascii=False) + '\n', encoding='utf-8')
        manifest = load(self.package / 'manifest.json')
        if name in manifest['files']:
            manifest['files'][name] = file_digest(path)
            (self.package / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')

    def test_complete_replay_and_unreviewed_scope(self):
        result = verify(self.package)
        self.assertEqual(result['validated_with_reservation'], 10)
        self.assertEqual(result['required_source_passages'], 25)
        self.assertEqual(result['not_individually_reviewed_source_ids'], ['E118-I', 'E121-EQ'])
        self.assertTrue(result['event_chain_replayed'])
        self.assertFalse(result['benchmark_executed'] or result['publication_allowed'])

    def test_standard_library_cli(self):
        result = subprocess.run([sys.executable, '-S', '-m',
            'experiments.cytiva.verify_contaminant_questions_package', '--package', str(self.package)],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'passed')

    def test_portable_without_local_artifacts_lf_and_crlf(self):
        root = Path(self.temp.name) / 'root'
        for name in SUPPORT | DEPENDENCIES:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, path)
        for ending in (b'\n', b'\r\n'):
            for path in list(self.package.iterdir()) + [root / name for name in SUPPORT | DEPENDENCIES]:
                path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', ending))
            self.assertTrue(verify(self.package, root=root)['event_chain_replayed'])

    def test_original_french_message_cannot_be_reworded(self):
        self.change('events.json', lambda x: x['events'][0].update(original_human_message='Reworded'))
        with self.assertRaisesRegex(ValueError, 'Original event'): verify(self.package)

    def test_reservations_cannot_be_removed(self):
        self.change('events.json', lambda x: x['events'][8]['reservations'].pop())
        with self.assertRaisesRegex(ValueError, 'Original event'): verify(self.package)

    def test_required_warning_cannot_be_removed(self):
        self.change('events.json', lambda x: x['events'][9]['evidence_sha256'].pop('E120-W'))
        with self.assertRaisesRegex(ValueError, 'Required source'): verify(self.package)

    def test_event_order_cannot_change(self):
        def swap(x): x['events'][0], x['events'][1] = x['events'][1], x['events'][0]
        self.change('events.json', swap)
        with self.assertRaisesRegex(ValueError, 'Event order'): verify(self.package)

    def test_question_and_evidence_bindings_are_checked(self):
        for field, expected in [('question_sha256', 'Question binding'), ('evidence_sha256', 'Evidence binding')]:
            with self.subTest(field=field):
                shutil.copy2(PACKAGE / 'events.json', self.package / 'events.json')
                def change(x):
                    if field == 'question_sha256': x['events'][0][field] = '0' * 64
                    else: x['events'][0][field]['E119-B'] = '0' * 64
                self.change('events.json', change)
                with self.assertRaisesRegex(ValueError, expected): verify(self.package)

    def test_final_review_cannot_diverge_from_replay(self):
        self.change('review.json', lambda x: x['decisions'][9].update(reservations=[]))
        with self.assertRaisesRegex(ValueError, 'Final state'): verify(self.package)

    def test_publication_and_measurement_not_inferred(self):
        for field in ('publication_allowed', 'benchmark_executed', 'benchmark_results_human_validated'):
            shutil.copy2(PACKAGE / 'manifest.json', self.package / 'manifest.json')
            self.change('manifest.json', lambda x: x.update({field: True}))
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'Package scope'):
                verify(self.package)

    def test_two_source_records_cannot_be_promoted_as_reviewed(self):
        self.change('manifest.json', lambda x: x.update(not_individually_reviewed_source_ids=[]))
        with self.assertRaisesRegex(ValueError, 'Unreviewed source scope'): verify(self.package)

    def test_missing_historical_state_rejected(self):
        self.change('manifest.json', lambda x: x['historical_files'].pop('review-after-004.json'))
        with self.assertRaisesRegex(ValueError, 'Initial/history'): verify(self.package)

    def test_provenance_cannot_claim_experiment_or_scientific_validation(self):
        for field in ('benchmark_executed', 'scientific_validation', 'production_retrieval_validated'):
            shutil.copy2(PACKAGE / 'provenance.json', self.package / 'provenance.json')
            self.change('provenance.json', lambda x: x.update({field: True}))
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'Provenance scope'):
                verify(self.package)

    def test_source_text_replay_is_optional_and_detects_tampering(self):
        from experiments.cytiva.verify_contaminant_questions_package import PREPARATION
        evidence = load(ROOT / PREPARATION / 'evidence.json')
        textdir = Path(self.temp.name) / 'text'; textdir.mkdir()
        # Identity must be checked before any span comparison; never use a model.
        for page in evidence['extraction']['pages']:
            (textdir / f"page-{page['pdf_page_1based']}.txt").write_text('changed', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Local page text identity'):
            verify(self.package, source_text_dir=textdir)


if __name__ == '__main__':
    unittest.main()
