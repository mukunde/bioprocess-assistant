"""Run a local, model-free Cytiva evidence demo: python -m demo.cytiva."""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
from time import perf_counter

from experiments.cytiva.free_text_v03_freeze import verify
from ingestion.free_text_bridge_v03 import FreeTextControlV03
from ingestion.structured_request_v03 import StructuredControlV03
from ingestion.free_text_contract import na, slot

OPERATIONS = {
    'loading_flow': ('operating_phase', 'sample_application', 'flow_rate', None),
    'washing_flow': ('operating_phase', 'washing', 'flow_rate', None),
    'washing_volume': ('operating_phase', 'washing', 'column_volumes', None),
    'washing_stop': ('operating_phase', 'washing', 'stopping_criteria', None),
    'elution_volume': ('operating_phase', 'elution', 'column_volumes', None),
    'binding_buffer': ('preparation', 'buffer_preparation', 'buffer_formulation', 'binding'),
    'elution_buffer': ('preparation', 'buffer_preparation', 'buffer_formulation', 'elution'),
    'pressure': ('general_topic', 'operating_limits', 'maximum_pressure', None),
    'equilibration_flow': ('operating_phase', 'equilibration', 'flow_rate', None),
}


def guided_submission(payload):
    if set(payload) != {'mode', 'language', 'column', 'operations'}:
        raise ValueError('Unexpected guided fields')
    if payload['language'] not in ('en', 'fr') or payload['column'] not in ('1', '5', 'unknown'):
        raise ValueError('Choose a language and column format')
    ops = payload['operations']
    if (not isinstance(ops, list) or not 1 <= len(ops) <= len(OPERATIONS)
            or any(not isinstance(x, str) or x not in OPERATIONS for x in ops)
            or len(set(ops)) != len(ops)):
        raise ValueError('Choose distinct supported request types')
    items = []
    for op in ops:
        kind, stage, information, use = OPERATIONS[op]
        items.append({'item_id': op, 'stage': {'kind': kind, 'code': stage},
                      'information': [information], 'answer_mode': 'single_context',
                      'techniques': na(), 'facets': {'buffer_use': slot(use) if use else na(),
                          'elution_mode': na(), 'syringe_query_mode': na()}})
    product = 'HiTrap Blue HP'+(' '+payload['column']+' mL' if payload['column'] != 'unknown' else '')
    return {'document_kind': 'structured_submission', 'contract_version': 'task-request-0.1-tech-proposed',
            'input_mode': 'structured', 'language': payload['language'], 'tasks': [{
                'task_id': 'B', 'sample_ref': None, 'intent': 'documentary_procedure_lookup',
                'product': slot(product), 'column': slot(), 'facts': [],
                'items': items, 'exclusions': []}]}


class Demo:
    def __init__(self):
        self.freeze = verify(environment=True)
        self.structured = StructuredControlV03()
        self.free_text = FreeTextControlV03()

    def evaluate(self, payload):
        if not isinstance(payload, dict):
            raise ValueError('Expected a request object')
        verify(environment=True)  # Refuse drift rather than silently use a new candidate.
        started = perf_counter()
        if payload.get('mode') == 'guided':
            submission = guided_submission(payload)
            outcome = self.structured.evaluate(submission)
            result = outcome['compatibility_result'] if not outcome['failure'] else None
            stages = {i['item_id']: i['stage'] for i in submission['tasks'][0]['items']}
            rows = [{**u, 'stage': stages[u['item_id']]} for u in result['plan']['units']] if result else []
            clarification = None
        elif payload.get('mode') == 'text' and set(payload) == {'mode', 'language', 'text'}:
            if payload['language'] not in ('en', 'fr') or not isinstance(payload['text'], str) or not 1 <= len(payload['text']) <= 4000:
                raise ValueError('Use EN/FR text of 1 to 4,000 characters')
            outcome = self.free_text.evaluate({k: payload[k] for k in ('language', 'text')})
            compatible = outcome['compatibility_outcome']
            result = compatible['core_result'] if not compatible['failure'] else None
            # Use original ledger occurrences, including preblocked requests.
            ledger = compatible['interpretation_ledger'] or {}
            known = {u['unit_id']: u for u in ledger.get('requested_units', [])}
            rows = [{'task_id': known[u['unit_id']]['owner'].get('task_id'),
                     'item_id': known[u['unit_id']]['item_id'],
                     'stage': known[u['unit_id']]['stage'],
                     'information': known[u['unit_id']]['information'],
                     'state': u['summary_state'], 'source_ids': u['source_ids']}
                    for u in compatible['unit_outcomes']]
            clarification = ('Use the guided request or specify the product, format and step explicitly.'
                             if not outcome['coverage_summary']['inventory_complete'] else None)
        else:
            raise ValueError('Choose guided or text mode')
        context = result['plan']['context'] if result else {'source_passages': [], 'bindings': []}
        # No generated prose or source filtering: retain the whole validated bundle,
        # including dependencies and warnings, plus per-unit bindings.
        return {'coverage': outcome['coverage_summary'], 'units': rows,
                'passages': context['source_passages'], 'bindings': context['bindings'],
                'clarification': clarification, 'freeze_id': self.freeze['id'],
                'request_id': result['plan']['request_id'] if result else None,
                'context_tokens': result['plan']['context_tokens'] if result else 0,
                'elapsed_ms': round((perf_counter()-started)*1000, 1),
                'model_calls': 0, 'api_cost_eur': 0,
                'corpus_scope': '25 reviewed excerpts; E118-I and E121-EQ remain excluded.'}


def handler_for(demo):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass  # Do not log request text.

        def reply(self, status, data, content_type='application/json; charset=utf-8'):
            body = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == '/':
                self.reply(200, (Path(__file__).parent/'static/cytiva.html').read_bytes(), 'text/html; charset=utf-8')
            elif self.path == '/health':
                try:
                    self.reply(200, verify(environment=True))
                except (ValueError, OSError, KeyError):
                    self.reply(503, {'error': 'Frozen baseline unavailable'})
            else:
                self.reply(404, {'error': 'Not found'})

        def do_POST(self):
            if self.path != '/evaluate':
                self.reply(404, {'error': 'Not found'}); return
            expected = 'http://'+self.headers.get('Host', '')
            if self.headers.get('Origin', expected) != expected:
                self.reply(403, {'error': 'Use the local demo page'}); return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 20000 or self.headers.get_content_type() != 'application/json':
                    self.reply(400, {'error': 'Send a small JSON request'}); return
                payload = json.loads(self.rfile.read(length).decode('utf-8'))
                self.reply(200, demo.evaluate(payload))
            except (ValueError, TypeError, KeyError, UnicodeError):
                self.reply(400, {'error': 'Request invalid or frozen baseline unavailable. Check the selected fields.'})
            except Exception:
                self.reply(503, {'error': 'Local evidence service unavailable. No answer was generated.'})
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8766)
    args = parser.parse_args()
    demo = Demo()
    server = HTTPServer(('127.0.0.1', args.port), handler_for(demo))
    print(f'Cytiva local demo: http://127.0.0.1:{server.server_port}/', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
