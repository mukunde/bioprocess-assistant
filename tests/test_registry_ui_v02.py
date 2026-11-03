"""Presentation v02 over disposable authority; private registry is never used."""
import contextlib
import io
import json
import shutil
import subprocess
import threading
import unittest
from unittest.mock import patch

from demo import registry_ui_v02 as variant
from tests import test_registry_ui as baseline_tests


class RegistryPresentationV02Tests(baseline_tests.RegistryUIIntegrationTests):
    # Inherited HTTP/DOM, withdrawal and deadline regressions exercise this variant.
    def start(self, root):
        server = variant.create_server(root, port=0)
        thread = threading.Thread(target=lambda: server.serve_forever(poll_interval=.02), daemon=True)
        thread.start()
        def stop():
            server.shutdown(); server.server_close(); thread.join(timeout=5)
        self.addCleanup(stop)
        return server

    def run_variant_dom(self, scenario):
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Node/jsdom required; no silent skip')
        result = subprocess.run([node, str(baseline_tests.ROOT/'tests/ui/registry-v02.cjs'),
                                 self.base, scenario], cwd=baseline_tests.ROOT,
                                capture_output=True, text=True, encoding='utf-8', timeout=40,
                                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertEqual(json.loads(result.stdout), {'status':'passed', 'scenario':scenario, 'requests':1})

    def test_all_eight_control_combinations_preserve_baseline_response_and_source_html(self):
        server = baseline_tests.ui.create_server(self.root, port=0)
        thread = threading.Thread(target=lambda: server.serve_forever(poll_interval=.02), daemon=True)
        thread.start()
        def stop():
            server.shutdown(); server.server_close(); thread.join(timeout=5)
        self.addCleanup(stop)
        cases = [
            ('sure', 'precipitated_substances', ['cleaning_options', 'pressure_limit']),
            ('sure_lx', 'precipitated_substances', ['cleaning_options']),
            ('sure_lx', 'hydrophobic_deposits', ['pressure_limit']),
            ('sure', 'hydrophobic_deposits', ['cleaning_options', 'pressure_limit']),
            ('family_unknown', 'hydrophobic_deposits', ['cleaning_options', 'pressure_limit']),
            ('sure', 'mixed_other', ['cleaning_options']),
            ('contradictory', 'precipitated_substances', ['pressure_limit']),
            ('other', 'mixed_other', ['cleaning_options', 'pressure_limit']),
        ]
        opened = set()
        for product, context, items in cases:
            with self.subTest(product=product, context=context, items=items):
                value = baseline_tests.request(product=product, context=context, items=items)
                status, _, original = self.evaluate(value, server=server)
                variant_status, _, actual = self.evaluate(value)
                self.assertEqual((variant_status, actual), (status, original))
                for ref in actual['citation_refs']:
                    if ref['href'] not in opened:
                        old_status, _, old_body = self.http(ref['href'], server=server)
                        new_status, _, new_body = self.http(ref['href'])
                        self.assertEqual((new_status, new_body), (old_status, old_body))
                        opened.add(ref['href'])
        self.assertEqual(len(opened), 13)

    def test_variant_cli_requires_explicit_authority(self):
        with patch.object(variant, 'create_server') as create, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit): variant.main([])
            create.assert_not_called()
        with self.assertRaises(ValueError): variant.create_server(None)

    def test_outside_scope_message_is_reason_and_item_specific(self):
        self.run_variant_dom('outside')

    def test_product_clarification_has_one_action_and_retains_all_sources(self):
        self.run_variant_dom('clarify-product')

    def test_context_clarification_retains_product_and_all_reservations(self):
        self.run_variant_dom('clarify-context')

    def test_conflicting_product_labels_are_not_resolved_by_presentation(self):
        self.run_variant_dom('clarify-conflict')

    def test_solvent_repetition_is_folded_but_complete_and_independent_warning_visible(self):
        self.run_variant_dom('solvent')

    def test_partial_warning_coverage_never_folds_away_new_text(self):
        self.run_variant_dom('partial-warning')

    def test_same_wording_with_different_provenance_is_not_folded(self):
        self.run_variant_dom('different-source-warning')


if __name__ == '__main__':
    unittest.main()
