"""Experiment safety contracts; no conversion model, LLM or network required."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from experiments.cytiva.visual_validation import ROOT, choose_blocks, convert, chunk, validate_review, digest, preflight


class VisualValidationTests(unittest.TestCase):
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
