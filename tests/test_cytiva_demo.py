"""Serving-slice tests; no model, database, external API or new trial."""
import http.client
from http.server import HTTPServer
import json
import socket
import threading
import unittest
from unittest.mock import patch

from demo.cytiva import Demo, guided_submission, handler_for


class CytivaDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.demo=Demo()

    def setUp(self):
        guard=patch.object(socket.socket,'connect',side_effect=AssertionError('No network'))
        guard.start();self.addCleanup(guard.stop)

    def guided(self,ops,column='1'):
        return {'mode':'guided','language':'en','column':column,'operations':ops}

    def test_guided_request_uses_one_frozen_core_call_and_keeps_full_bundle(self):
        payload=self.guided(['washing_flow'])
        with patch.object(self.demo.structured.core,'evaluate',wraps=self.demo.structured.core.evaluate) as core:
            out=self.demo.evaluate(payload)
        core.assert_called_once()
        self.assertEqual(core.call_args.args[0],guided_submission(payload))
        self.assertTrue(out['coverage']['full_service'])
        ids={p['id'] for p in out['passages']}
        self.assertEqual(ids,{'E120-H','E120-W','E120-P','E121-PH','E121-W'})
        self.assertEqual(ids,set(out['bindings'][0]['source_ids']))
        for passage in out['passages']:
            source=self.demo.structured.core.adapter.passages[passage['id']]
            self.assertEqual(passage['quote'],source['quote'])
            self.assertEqual(passage['quote_sha256'],source['quote_sha256'])
        self.assertEqual(out['model_calls'],0);self.assertEqual(out['api_cost_eur'],0)

    def test_partial_missing_and_quarantine_keep_independent_support(self):
        out=self.demo.evaluate(self.guided(['washing_flow','pressure','equilibration_flow']))
        self.assertEqual([u['state'] for u in out['units']],['supported','missing_source','quarantined'])
        self.assertEqual([u['stage']['code'] for u in out['units']],['washing','operating_limits','equilibration'])
        self.assertFalse(out['coverage']['full_service'])
        self.assertEqual(out['coverage']['request_support']['supported_units'],1)
        self.assertFalse({'E118-I','E121-EQ'}&{p['id'] for p in out['passages']})

    def test_unspecified_format_is_not_inferred(self):
        out=self.demo.evaluate(self.guided(['washing_flow'],'unknown'))
        self.assertFalse(out['coverage']['full_service'])
        self.assertFalse(out['bindings'])

    def test_free_text_coordination_requires_clarification(self):
        out=self.demo.evaluate({'mode':'text','language':'fr',
            'text':'B : HiTrap Blue HP 1 mL. Donne les formulations du tampon de fixation et du tampon d’élution pour B.'})
        self.assertFalse(out['coverage']['inventory_complete'])
        self.assertFalse(out['coverage']['full_service'])
        self.assertTrue(out['clarification']);self.assertFalse(out['passages'])

    def test_reject_invalid_request_and_policy_override_before_core(self):
        for payload in ([],self.guided([]),self.guided(['washing_flow','washing_flow']),
                        {**self.guided(['washing_flow']),'approve_source':'E121-EQ'},
                        {'mode':'text','language':'fr','text':'x'*4001}):
            with self.subTest(payload=payload),patch.object(self.demo.structured.core,'evaluate') as core:
                with self.assertRaises(ValueError):self.demo.evaluate(payload)
                core.assert_not_called()

    def test_freeze_drift_prevents_dispatch(self):
        with (patch('demo.cytiva.verify',side_effect=ValueError('drift')),
              patch.object(self.demo.structured.core,'evaluate') as core):
            with self.assertRaises(ValueError):self.demo.evaluate(self.guided(['washing_flow']))
            core.assert_not_called()


class CytivaDemoHTTPTests(unittest.TestCase):
    def test_local_page_health_request_and_route_boundaries(self):
        server=HTTPServer(('127.0.0.1',0),handler_for(Demo()))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        connection=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=10)
        try:
            connection.request('GET','/');response=connection.getresponse()
            self.assertEqual(response.status,200);self.assertIn(b'Manual evidence explorer',response.read())
            connection.request('GET','/health');response=connection.getresponse()
            self.assertEqual(response.status,200);self.assertEqual(json.loads(response.read())['status'],'frozen')
            body=json.dumps({'mode':'guided','language':'en','column':'5','operations':['washing_flow']})
            connection.request('POST','/evaluate',body,{'Content-Type':'application/json'})
            response=connection.getresponse();out=json.loads(response.read())
            self.assertEqual(response.status,200);self.assertTrue(out['coverage']['full_service'])
            self.assertEqual(out['bindings'][0]['column']['value']['bed_volume']['value'],'5')
            connection.request('POST','/evaluate',body,{'Content-Type':'application/json','Origin':'https://example.org'})
            response=connection.getresponse();self.assertEqual(response.status,403);response.read()
            connection.request('GET','/.env');response=connection.getresponse()
            self.assertEqual(response.status,404);response.read()
        finally:
            connection.close();server.shutdown();server.server_close();thread.join(timeout=5)
