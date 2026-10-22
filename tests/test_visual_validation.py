"""Experiment safety contracts; no conversion model, LLM or network required."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from experiments.cytiva.visual_validation import ROOT, choose_blocks, convert, conversion_worker, chunk, validate_review, digest, preflight, main


class VisualValidationTests(unittest.TestCase):
    def test_public_runner_forwards_matching_to_both_profile_workers(self):
        selection = {'source': {'pdf_page_count': 1}, 'blocks': [
            {'id': 'p088', 'pdf_pages_1based': [1], 'printed_pages': ['88']}]}
        class Writer:
            def add_page(self, page): pass
            def write(self, stream): stream.write(b'%PDF-test')
        pdf = ModuleType('pypdf')
        pdf.PdfReader = lambda path: SimpleNamespace(pages=[object()])
        pdf.PdfWriter = Writer
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='.visual-validation-test-') as temp:
            root = Path(temp); selected = root/'selection.json'
            selected.write_text(json.dumps(selection), encoding='utf-8')
            for enabled in (True, False):
                with self.subTest(enabled=enabled):
                    args = argparse.Namespace(source=root/'source.pdf', artifacts=root/'models',
                        blocks=['p088'], output=root/str(enabled), cell_matching=enabled)
                    with patch.dict(sys.modules, {'pypdf': pdf}), patch(
                            'experiments.cytiva.visual_validation.SELECTION', selected), patch(
                            'experiments.cytiva.visual_validation.preflight', return_value={'source_sha256': '0'*64}), patch(
                            'experiments.cytiva.visual_validation.network_guard', return_value=[]), patch(
                            'experiments.cytiva.visual_validation.supervised', return_value={'status': 'success'}) as worker, patch('builtins.print'):
                        convert(args)
                    self.assertEqual(worker.call_count, 2)
                    commands = [call.args[0] for call in worker.call_args_list]
                    self.assertEqual([cmd[cmd.index('--profile')+1] for cmd in commands], ['T0', 'T1'])
                    for cmd in commands:
                        self.assertEqual(cmd[-1], '--cell-matching' if enabled else '--no-cell-matching')
                        self.assertNotIn('--no-cell-matching' if enabled else '--cell-matching', cmd)

    def test_worker_serializes_concrete_table_options_without_loading_models(self):
        # Real Pydantic polymorphism reproduces the original erased-subclass bug;
        # only the Docling runtime is stubbed. Conversion stops before inference.
        from pydantic import BaseModel, ConfigDict
        class BaseTableOptions(BaseModel):
            kind: str = 'docling_tableformer'
        class TableOptions(BaseTableOptions):
            mode: str
            do_cell_matching: bool
        class PipelineOptions(BaseModel):
            model_config = ConfigDict(extra='allow')
            table_structure_options: BaseTableOptions
            do_table_structure: bool
        converter = Mock()
        converter.convert.side_effect = RuntimeError('stop before inference')
        factory = Mock(return_value=converter)
        options = ModuleType('docling.datamodel.pipeline_options')
        options.PdfPipelineOptions = PipelineOptions
        options.TableStructureOptions = TableOptions
        options.TableFormerMode = SimpleNamespace(ACCURATE='accurate')
        accelerator = ModuleType('docling.datamodel.accelerator_options')
        accelerator.AcceleratorOptions = lambda **kwargs: kwargs
        accelerator.AcceleratorDevice = SimpleNamespace(CPU='cpu')
        formats = ModuleType('docling.datamodel.base_models')
        formats.InputFormat = SimpleNamespace(PDF='pdf')
        runtime = ModuleType('docling.document_converter')
        runtime.DocumentConverter = factory
        runtime.PdfFormatOption = lambda **kwargs: kwargs
        modules = {'docling': ModuleType('docling'), 'docling.datamodel': ModuleType('docling.datamodel'),
            'docling.datamodel.pipeline_options': options, 'docling.datamodel.accelerator_options': accelerator,
            'docling.datamodel.base_models': formats, 'docling.document_converter': runtime}
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='.visual-validation-test-') as temp:
            for enabled in (True, False):
                for profile in ('T0', 'T1'):
                    with self.subTest(enabled=enabled, profile=profile):
                        output = Path(temp)/(str(enabled)+profile)
                        args = argparse.Namespace(profile=profile, cell_matching=enabled,
                            artifacts=Path(temp)/'models', source=Path(temp)/'source.pdf', output=output)
                        with patch.dict(sys.modules, modules), patch(
                                'experiments.cytiva.visual_validation.network_guard', return_value=[]):
                            with self.assertRaisesRegex(RuntimeError, 'stop before inference'):
                                conversion_worker(args)
                        saved = json.loads((output/'profile.json').read_text(encoding='utf-8'))
                        self.assertEqual(saved['table_structure_options'], {'kind': 'docling_tableformer',
                            'mode': 'accurate', 'do_cell_matching': enabled})
                        self.assertEqual(saved['do_table_structure'], profile=='T1')
                        effective = factory.call_args.kwargs['format_options']['pdf']['pipeline_options']
                        self.assertEqual(effective.table_structure_options.do_cell_matching, enabled)

    def test_cell_matching_cli_keeps_default_and_allows_explicit_ablation(self):
        for command, handler in (('convert', 'convert'), ('_convert', 'conversion_worker')):
            for flag, expected in (([], True), (['--cell-matching'], True),
                                   (['--no-cell-matching'], False)):
                with self.subTest(command=command, flag=flag):
                    argv = ['visual_validation', command, '--source', 'source.pdf',
                            '--output', 'new-run', '--artifacts', 'cached-models']
                    if command == '_convert':
                        argv += ['--profile', 'T1']
                    with patch.object(sys, 'argv', argv + flag), patch(
                            'experiments.cytiva.visual_validation.' + handler) as run:
                        main()
                    run.assert_called_once()
                    self.assertIs(run.call_args.args[0].cell_matching, expected)

    def test_noncontiguous_blocks_stay_separate(self):
        selection = {'blocks': [{'id':'p077','pages':[77]}, {'id':'p088','pages':[88]}]}
        self.assertEqual([b['pages'] for b in choose_blocks(selection,['p077','p088'])],[[77],[88]])
        for names in ([],['p077','p077'],['unknown']):
            with self.assertRaises(ValueError):
                choose_blocks(selection,names)

    def test_existing_output_preserved_before_loading_runtime(self):
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='.visual-validation-test-') as temp:
            output = Path(temp); sentinel = output/'sentinel'; sentinel.write_text('keep')
            for fn in (convert,chunk):
                with self.assertRaises(FileExistsError):
                    fn(argparse.Namespace(output=output))
            self.assertEqual(sentinel.read_text(),'keep')

    def test_review_cannot_approve_or_change_conversion(self):
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='.visual-validation-test-') as temp:
            root=Path(temp); folder=root/'p077/T1';folder.mkdir(parents=True)
            doc=folder/'document.json';doc.write_text('{}')
            review={'purpose':'diagnostic_chunking_only','human_approved':False,
                    'blocks':{'p077':{'status':'usable_for_diagnostic','document_sha256':digest(doc)}}}
            self.assertEqual(validate_review(review,root),['p077'])
            review['human_approved']=True
            with self.assertRaises(ValueError):validate_review(review,root)
            review['human_approved']=False;doc.write_text('{"changed":true}')
            with self.assertRaisesRegex(ValueError,'hash mismatch'):validate_review(review,root)

    def test_uninspected_conversion_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='.visual-validation-test-') as temp:
            root=Path(temp);folder=root/'p077/T1';folder.mkdir(parents=True)
            doc=folder/'document.json';doc.write_text('{}')
            review={'purpose':'diagnostic_chunking_only','human_approved':False,
                    'blocks':{'p077':{'status':'pending','document_sha256':digest(doc)}}}
            with self.assertRaisesRegex(ValueError,'not been inspected'):validate_review(review,root)

    def test_network_audit_blocks_dns_without_network_access(self):
        code = ('from experiments.cytiva.visual_validation import network_guard; '
                'import socket; attempts=network_guard(); '
                '\ntry: socket.getaddrinfo("example.invalid",443)'
                '\nexcept RuntimeError: print(attempts[0])'
                '\nelse: raise AssertionError("DNS was not blocked")')
        result=subprocess.run([sys.executable,'-c',code],capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.strip(),'socket.getaddrinfo')

    def test_wrong_manual_rejected_before_model_or_package_loading(self):
        with tempfile.TemporaryDirectory(dir=ROOT, prefix='.visual-validation-test-') as temp:
            source=Path(temp)/'source.pdf';source.write_bytes(b'%PDF-wrong-source')
            with self.assertRaisesRegex(ValueError,'Source SHA-256'):
                preflight(source,Path(temp),{'source':{'sha256':'0'*64}})


if __name__ == '__main__':
    unittest.main()
