"""Preparation safety checks, independent of PDF conversion and model calls."""
import contextlib
import hashlib
import io
import json
import os
import tempfile
from datetime import datetime, timezone
from types import ModuleType, SimpleNamespace
from unittest.mock import patch
import unittest
from pathlib import Path

from ingestion.prepare_claim_test import prepare
from ingestion.claim_bundle import digest, verify_bundle
from experiments.cytiva import build_reference_cards as cards
from experiments.cytiva.v01 import build_fidelity_audit as audit


class ExperimentPreparationTests(unittest.TestCase):
    def test_existing_output_is_preserved_before_conversion(self):
        workspace = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=workspace, prefix='.experiment-preparation-test-') as folder:
            self.assertTrue(Path(folder).resolve().is_relative_to(workspace))
            with self.assertRaisesRegex(ValueError, 'never overwritten'):
                prepare(Path('not-a-real-pdf.pdf'), Path(folder), [100])

    def test_reference_builder_preserves_existing_json_and_markdown(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1], prefix='.experiment-preparation-test-') as temp:
            output = Path(temp) / 'reviewed'
            output.mkdir()
            for name in ('exemples.json', 'examples-v0.1.md', 'verification.json'):
                (output / name).write_text('human annotation sentinel', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'never overwritten'):
                cards.build(output)
            self.assertEqual(sorted(p.name for p in output.iterdir()),
                             ['examples-v0.1.md', 'exemples.json', 'verification.json'])
            for path in output.iterdir():
                self.assertEqual(path.read_text(encoding='utf-8'), 'human annotation sentinel')

    def test_reference_builder_does_not_touch_repository_ontology(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1], prefix='.experiment-preparation-test-') as temp:
            root = Path(temp)
            ontology = root / 'docs/ontology/examples-v0.1.md'
            ontology.parent.mkdir(parents=True)
            ontology.write_text('reviewed ontology', encoding='utf-8')
            with patch.object(cards, 'ROOT', root), patch.object(cards, 'RUN', root / 'missing-conversion'):
                with self.assertRaises(FileNotFoundError):
                    cards.build(root / 'new-draft')
            self.assertEqual(ontology.read_text(encoding='utf-8'), 'reviewed ontology')

    def audit_fixture(self, root):
        bundle = root / 'bundle'
        bundle.mkdir()
        refs = root / 'references'
        refs.mkdir()
        paths = {name: bundle / name for name in audit.REVIEWED_INPUT_HASHES}
        paths['source.pdf'] = refs / 'cytiva-hitrap-sure-pages-097-099.pdf'
        paths['source-map.json'] = refs / 'cytiva-hitrap-sure-pages-097-099.source-map.json'
        for name, path in paths.items():
            content = {'claims': [{'id': 'cl29', 'value_text': '20% ethanol at 2-8 C'}]} if name.startswith('resultat') else {'source_text': '20% ethanol at 2-8 C'}
            path.write_text(json.dumps(content), encoding='utf-8')
        hashes = {name: digest(path) for name, path in paths.items()}
        return bundle, paths, hashes

    def test_audit_accepts_exact_reviewed_bytes(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1], prefix='.experiment-preparation-test-') as temp:
            root = Path(temp)
            bundle, paths, hashes = self.audit_fixture(root)
            with patch.object(audit, 'ROOT', root), patch.object(audit, 'HERE', bundle), patch.object(audit, 'REVIEWED_INPUT_HASHES', hashes):
                self.assertEqual(audit.verify_reviewed_inputs(), hashes)

    def test_audit_rejects_changed_answers_and_sources_before_output(self):
        for changed in audit.REVIEWED_INPUT_HASHES:
            with self.subTest(file=changed), tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1], prefix='.experiment-preparation-test-') as temp:
                root = Path(temp)
                bundle, paths, hashes = self.audit_fixture(root)
                output = bundle / 'audit-fidelite.json'
                output.write_text('existing review sentinel', encoding='utf-8')
                # IDs stay identical: only the quantity or evidence text changes.
                paths[changed].write_text(json.dumps({'claims': [{'id': 'cl29', 'value_text': '99% ethanol at 80 C'}]}), encoding='utf-8')
                with patch.object(audit, 'ROOT', root), patch.object(audit, 'HERE', bundle), patch.object(audit, 'REVIEWED_INPUT_HASHES', hashes):
                    with self.assertRaisesRegex(ValueError, 'Reviewe[d] input changed'):
                        audit.main()
                self.assertEqual(output.read_text(encoding='utf-8'), 'existing review sentinel')
                self.assertFalse((bundle / 'AUDIT-DETAILLE.md').exists())

    def test_preparation_requires_explicit_metadata_before_writing(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1], prefix='.experiment-preparation-test-') as temp:
            output = Path(temp) / 'new'
            for metadata in ({}, dict(document_reference='OTHER-REF', document_version=' ', selection_reason='chosen pages')):
                with self.assertRaisesRegex(ValueError, 'Explicit document_reference'):
                    prepare(Path('missing.pdf'), output, [1], **metadata)
                self.assertFalse(output.exists())

    def fake_conversion(self):
        class Item:
            def model_dump(self, **kwargs):
                return dict(self_ref='#/texts/0', label='text', text='Different handbook edition', prov=[{'page_no': 1}])
        class Document:
            def model_dump(self, **kwargs): return dict(body={}, groups=[])
            def iterate_items(self): return [(Item(), 0)]
        class Converter:
            def __init__(self, **kwargs): pass
            def convert(self, source):
                return SimpleNamespace(status=SimpleNamespace(value='success'), document=Document())
        def module(name, **attrs):
            m = ModuleType(name)
            for k, v in attrs.items(): setattr(m, k, v)
            return m
        return {
            'docling.document_converter': module('docling.document_converter', DocumentConverter=Converter, PdfFormatOption=SimpleNamespace),
            'docling.datamodel.base_models': module('docling.datamodel.base_models', InputFormat=SimpleNamespace(PDF='pdf')),
            'docling.datamodel.pipeline_options': module('docling.datamodel.pipeline_options', PdfPipelineOptions=SimpleNamespace),
            'docling.datamodel.accelerator_options': module('docling.datamodel.accelerator_options', AcceleratorOptions=SimpleNamespace, AcceleratorDevice=SimpleNamespace(CPU='cpu')),
        }

    def pdf_fixture(self, root):
        from pypdf import PdfWriter
        pdf = root / 'different-edition.pdf'
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        with pdf.open('wb') as stream: writer.write(stream)
        artifacts = root / 'artifacts'
        layout = artifacts / 'docling-project--docling-layout-heron'
        layout.mkdir(parents=True)
        (layout / 'model.safetensors').write_bytes(b'fixture - never loaded')
        return pdf, artifacts

    def test_prepared_bundle_preserves_other_edition_metadata_and_current_date(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1], prefix='.experiment-preparation-test-') as temp:
            root = Path(temp)
            pdf, artifacts = self.pdf_fixture(root)
            output = root / 'new'
            metadata = dict(document_reference='OTHER-MANUAL', document_version='edition-2031', selection_reason='Test a new troubleshooting table')
            frozen = datetime(2031, 4, 5, 12, tzinfo=timezone.utc)
            with patch.dict('sys.modules', self.fake_conversion()), patch.dict(os.environ, {'DOCLING_SERVE_URL': ''}), patch('ingestion.prepare_claim_test.datetime') as clock, patch('importlib.metadata.version', return_value='fixture'), contextlib.redirect_stdout(io.StringIO()):
                clock.now.return_value = frozen
                result = prepare(pdf, output, [1], artifacts=artifacts, **metadata)
            self.assertTrue(result['prepared'])
            plan = verify_bundle(output)
            corpus = json.loads((output / 'input.json').read_text(encoding='utf-8'))
            mapping = json.loads((output / 'source-map.json').read_text(encoding='utf-8'))
            for key in ('document_reference', 'document_version'):
                self.assertEqual(corpus[key], metadata[key])
                self.assertEqual(mapping[key], metadata[key])
                self.assertEqual(plan[key], metadata[key])
            self.assertEqual(mapping['original_sha256'], digest(pdf))
            self.assertEqual(mapping['pages'], [dict(excerpt_pdf_page=1, original_pdf_page=1)])
            self.assertEqual(plan['selection_reason'], metadata['selection_reason'])
            self.assertEqual(plan['prepared_on'], '2031-04-05')
            self.assertEqual(plan['prepared_date_timezone'], 'UTC')
            self.assertFalse(plan['publication_allowed'])
            self.assertEqual(corpus['metadata_status'], 'supplied_by_operator_not_independently_verified')
            self.assertEqual(json.loads((output / 'status.json').read_text())['api_calls'], 0)

    def test_resume_rejects_changed_edition_without_replacing_files(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1], prefix='.experiment-preparation-test-') as temp:
            root = Path(temp)
            pdf, artifacts = self.pdf_fixture(root)
            output = root / 'incomplete'
            output.mkdir()
            (output / 'status.json').write_text(json.dumps({'status': 'preparation_failed'}))
            previous = dict(original_sha256=digest(pdf), pages=[{'original_pdf_page': 1}], document_reference='OTHER', document_version='v1', selection_reason='chosen pages')
            (output / 'source-map.json').write_text(json.dumps(previous))
            before = {p.name: p.read_bytes() for p in output.iterdir()}
            with patch.dict(os.environ, {'DOCLING_SERVE_URL': ''}), self.assertRaisesRegex(ValueError, 'identical document metadata'):
                prepare(pdf, output, [1], resume_failed=True, artifacts=artifacts, document_reference='OTHER', document_version='v2', selection_reason='chosen pages')
            self.assertEqual({p.name: p.read_bytes() for p in output.iterdir()}, before)


if __name__ == '__main__':
    unittest.main()
