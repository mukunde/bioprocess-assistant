"""Portable replay and documentary-scope regressions for eight reviewed intents."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from experiments.cytiva.verify_section_questions_package import (
    ROOT, PACKAGE, SUPPORT, DEPENDENCIES, BASE, read, file_digest, verify)


class SectionQuestionsPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'tmp', prefix='section-review-package-')
        self.addCleanup(self.temp.cleanup)
        self.package = Path(self.temp.name) / 'package'
        shutil.copytree(PACKAGE, self.package)

    def change(self, name, mutation):
        path = self.package / name
        value = read(path); mutation(value)
        path.write_text(json.dumps(value, ensure_ascii=False) + '\n', encoding='utf-8')
        manifest = read(self.package / 'manifest.json')
        if name in manifest['files']:
            manifest['files'][name] = file_digest(path)
            (self.package / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')

    def test_standard_library_replay_and_prior_source(self):
        result = verify(self.package)
        self.assertEqual(result['validated_with_reservation'], 8)
        self.assertTrue(result['event_chain_replayed'] and result['prior_source_package_verified'])
        self.assertFalse(result['benchmark_results_human_validated'])

    def test_portable_package_and_dependencies_lf_crlf(self):
        root = Path(self.temp.name) / 'root'
        prior = read(ROOT / BASE / 'manifest.json')
        paths = SUPPORT | DEPENDENCIES | set(prior['supporting_files']) | {
            BASE + '/' + name for name in prior['files']}
        for name in paths:
            target = root / name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)
        for ending in (b'\n', b'\r\n'):
            for path in list(self.package.iterdir()) + [root / name for name in paths]:
                path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', ending))
            self.assertTrue(verify(self.package, root=root)['event_chain_replayed'])

    def test_original_french_message_cannot_be_reworded(self):
        self.change('events.json', lambda x: x['events'][0].update(original_human_message='Reworded'))
        with self.assertRaisesRegex(ValueError, 'Original event'): verify(self.package)

    def test_reservations_cannot_be_removed(self):
        self.change('events.json', lambda x: x['events'][2]['reservations'].pop())
        with self.assertRaisesRegex(ValueError, 'Original event'): verify(self.package)

    def test_required_pressure_warning_preserved(self):
        self.change('events.json', lambda x: x['events'][6]['evidence_sha256'].pop('E167-W'))
        with self.assertRaisesRegex(ValueError, 'Indispensable evidence'): verify(self.package)

    def test_event_order_cannot_change(self):
        def swap(x): x['events'][0], x['events'][1] = x['events'][1], x['events'][0]
        self.change('events.json', swap)
        with self.assertRaisesRegex(ValueError, 'Event order'): verify(self.package)

    def test_final_review_matches_replay(self):
        self.change('review.json', lambda x: x['decisions'][4].update(reservations=[]))
        with self.assertRaisesRegex(ValueError, 'Final state'): verify(self.package)

    def test_benchmark_approval_not_inferred(self):
        self.change('events.json', lambda x: x['state_metadata'][0].update(benchmark_results_human_validated=True))
        with self.assertRaisesRegex(ValueError, 'Review scope'): verify(self.package)

    def test_publication_not_inferred(self):
        self.change('manifest.json', lambda x: x.update(publication_allowed=True))
        with self.assertRaisesRegex(ValueError, 'Package scope'): verify(self.package)

    def test_n05_failure_cannot_be_erased(self):
        self.change('provenance.json', lambda x: x['experiment']['n05_outcomes'][0].update(complete_evidence=True))
        with self.assertRaisesRegex(ValueError, 'N05 failure'): verify(self.package)

    def test_historical_metrics_cannot_be_replaced_with_success(self):
        self.change('provenance.json', lambda x: x['experiment']['metrics']['new_candidate']['v03'].update(complete_both_languages=8))
        with self.assertRaisesRegex(ValueError, 'Recorded metrics'): verify(self.package)

    def test_source_dependency_digest_required(self):
        self.change('manifest.json', lambda x: x['dependencies'].update({next(iter(x['dependencies'])): '0' * 64}))
        with self.assertRaisesRegex(ValueError, 'File digest'): verify(self.package)

    def test_frozen_policy_audit_bound(self):
        self.change('provenance.json', lambda x: x['reference_freeze']['files'].update({'experiments/cytiva/cleaning_source_context_v03.json': '0' * 64}))
        with self.assertRaisesRegex(ValueError, 'Original freeze'): verify(self.package)

    def test_historical_state_cannot_be_omitted(self):
        self.change('manifest.json', lambda x: x['historical_files'].pop('review-after-004.json'))
        with self.assertRaisesRegex(ValueError, 'Initial/history'): verify(self.package)


if __name__ == '__main__':
    unittest.main()
