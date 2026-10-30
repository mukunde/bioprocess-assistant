"""Bounded documentary backpressure journey; no inference model or v03 changes."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from time import perf_counter

from experiments.cytiva.verify_cleaning_retrieval_package import verify

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = {'protein_a': 'Protein A Sepharose', 'protein_g': 'Protein G Sepharose',
            'unknown': 'Product not specified', 'mabselect': 'MabSelect'}
CONTEXTS = {'unknown', 'precipitated_proteins', 'hydrophobic_deposits'}
LIMITS = [
    'The observed pressure increase does not establish a cause or a deposit type.',
    'No pressure threshold, numerical reduced flow rate or missing volume is inferred.',
    'Documentary review does not establish operational suitability, restored capacity or authorization to reuse the medium.',
]


def evaluate(payload):
    if not isinstance(payload, dict) or set(payload) != {'mode', 'product', 'deposit_context'}:
        raise ValueError('Choose the product and deposit context for this journey')
    product, context = payload['product'], payload['deposit_context']
    if (payload['mode'] != 'troubleshooting' or not isinstance(product, str)
            or not isinstance(context, str) or product not in PRODUCTS or context not in CONTEXTS):
        raise ValueError('Unsupported troubleshooting selection')
    started = perf_counter()
    # Validation reads the original review/reference files; none is indexed or
    # used as a generated answer. Displayed quotations come only from evidence.
    package = ROOT/'experiments/cytiva/reviewed-cleaning-retrieval'
    manifest = json.loads((package/'manifest.json').read_text(encoding='utf-8'))
    verify(root=ROOT, package=package)
    def read_bound(path, expected):
        raw = path.read_bytes()
        if hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest() != expected:
            raise ValueError('Reviewed source changed during evaluation')
        return json.loads(raw)
    evidence = read_bound(ROOT/'experiments/cytiva/retrieval-pilot-v01/evidence.json',
                          manifest['supporting_files']['experiments/cytiva/retrieval-pilot-v01/evidence.json'])
    review = read_bound(package/'review.json', manifest['files']['review.json'])
    passages = {p['id']: p for p in evidence['passages']}
    decisions = {d['question_id']: d for d in review['decisions']}
    options = []
    if product == 'unknown':
        state, question_ids = 'needs_clarification', ['Q09']
        ids = ['E166-H', 'E166-T', 'E166-PH', 'E166-LH', 'E167-H', 'E167-PH', 'E167-SH', 'E167-LH']
        message = 'Which exact product is involved? The manual distinguishes product-specific cleaning sections. No recipe has been selected.'
    elif product == 'mabselect':
        state, question_ids = 'outside_scope', ['Q09']
        ids = ['E166-H', 'E166-T', 'E166-PH', 'E166-LH', 'E167-H', 'E167-PH', 'E167-SH', 'E167-LH']
        message = 'This first journey covers Protein A/G Sepharose only. MabSelect requires its own product-specific route; no Sepharose recipe is transferred.'
    else:
        ids, question_ids = ['E166-H', 'E166-T'], ['Q01']
        message = 'For this product scope, the manual recommends cleaning when backpressure increases. It does not diagnose the cause.'
        if context == 'unknown':
            state = 'needs_clarification'
            question_ids += ['Q09']
            ids += ['E166-PH', 'E166-LH', 'E167-H', 'E167-PH', 'E167-SH', 'E167-LH']
            message += ' Which deposit context do you want to explore? An established diagnosis is not required, and none is assumed.'
        elif context == 'precipitated_proteins':
            state = 'documented_options'
            question_ids += ['Q02']
            ids += ['E166-PH', 'E166-P']
            options = [{'title': 'Sequence for precipitated or denatured proteins',
                        'source_ids': ['E166-H', 'E166-PH', 'E166-P'],
                        'quote_ids': ['E166-P']}]
        else:
            state = 'documented_options'
            question_ids += ['Q03', 'Q04']
            ids += ['E166-LH', 'E166-D', 'E166-E', 'E166-W']
            options = [
                {'title': 'Nonionic detergent: the manual gives an example',
                 'source_ids': ['E166-H', 'E166-LH', 'E166-D'], 'quote_ids': ['E166-D']},
                {'title': 'Alternative ethanol route, with its pressure precaution',
                 'source_ids': ['E166-H', 'E166-LH', 'E166-E', 'E166-W'],
                 'quote_ids': ['E166-E', 'E166-W']},
            ]
    # Preserve the actual reservations for every reused review scope. No recipe
    # quotation can be returned without its product/category and warning bundle.
    approvals = []
    for qid in question_ids:
        d = decisions[qid]
        if d['decision'] not in ('validated', 'validated_with_reservation'):
            raise ValueError('Required documentary review unavailable')
        if not set(d['evidence_sha256']) <= set(ids):
            raise ValueError('Required reviewed context missing')
        approvals.append({'question_id': qid, 'decision': d['decision'],
                          'reservations': deepcopy(d['reservations'])})
    fields = ('id', 'pdf_page_1based', 'pdf_page_index_0based', 'scope', 'quote',
              'quote_sha256', 'page_text_start', 'page_text_end')
    return {'journey': 'protein-ag-sepharose-backpressure-v01', 'state': state,
            'product': PRODUCTS[product], 'deposit_context': context,
            'observation': 'Increasing backpressure', 'message': message,
            'diagnosis_established': False, 'operational_authorization': False,
            'options': options, 'limits': LIMITS.copy(), 'review_scopes': approvals,
            'source_pdf_sha256': evidence['source']['sha256'],
            'passages': [{k: passages[pid][k] for k in fields} for pid in ids],
            'bindings': [], 'elapsed_ms': round((perf_counter()-started)*1000, 1),
            'model_calls': 0, 'api_cost_eur': 0,
            'corpus_scope': 'Reviewed cleaning excerpts, PDF pages 166–167. Documentary demo only; independent of frozen v03.'}
