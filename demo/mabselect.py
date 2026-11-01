"""Reviewed, model-free MabSelect documentary selector, separate from frozen v03."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from time import perf_counter

from experiments.cytiva.verify_mabselect_design import verify as verify_design
from experiments.cytiva.verify_cleaning_retrieval_package import verify as verify_q
from experiments.cytiva.verify_section_questions_package import verify as verify_n

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = {
    'unknown': 'Product not specified',
    'family_unknown': 'MabSelect family — variant unknown',
    'mabselect': 'MabSelect — exact unsuffixed product',
    'sure': 'MabSelect SuRe',
    'sure_lx': 'MabSelect SuRe LX',
    'other': 'Other product / variant not listed',
    'contradictory': 'Conflicting product labels',
}
CONTEXTS = {
    'unknown': 'Unknown / help me clarify',
    'precipitated_substances': 'Precipitated or denatured substances',
    'hydrophobic_deposits': 'Strongly bound hydrophobic proteins, lipoproteins or lipids',
    'mixed_other': 'Mixed, uncertain or other context',
}
REQUIRED = {
    'Q05': ['E167-H', 'E167-PH', 'E167-P'],
    'Q06': ['E167-H', 'E167-PH', 'E167-SH', 'E167-S'],
    'Q09': ['E166-H', 'E166-T', 'E166-PH', 'E166-LH', 'E167-H', 'E167-PH', 'E167-SH', 'E167-LH'],
    'N06': ['E167-H', 'E167-LH', 'E167-D'],
    'N07': ['E167-H', 'E167-LH', 'E167-E', 'E167-W'],
}
LIMITS = [
    'Exploring a deposit category does not establish a cause or operational suitability.',
    'The page-166 indication to clean on increased backpressure belongs to Protein A/G Sepharose; it is not attributed to MabSelect.',
    'The stronger-alkali sequence is restricted to SuRe/SuRe LX in the precipitated/denatured context. This is not a general sodium-hydroxide prohibition for plain MabSelect.',
    'pH 7.0–8.0 applies to the following binding-buffer wash, not an inferred cleaning-solution pH or an automatic adjustment.',
    'No missing flow, pressure, gradient, solvent duration, CV-to-mL conversion, dosage or reuse guarantee is inferred. Absence is limited to the selected blocks.',
]


def _read_bound(path, expected):
    raw = path.read_bytes()
    if hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest() != expected:
        raise ValueError('Reviewed source changed during evaluation')
    return json.loads(raw)


def _load():
    verify_design(root=ROOT)
    qdir = ROOT/'experiments/cytiva/reviewed-cleaning-retrieval'
    ndir = ROOT/'experiments/cytiva/reviewed-section-questions'
    qm = json.loads((qdir/'manifest.json').read_bytes())
    nm = json.loads((ndir/'manifest.json').read_bytes())
    verify_q(root=ROOT, package=qdir)
    verify_n(root=ROOT, package=ndir)
    name = 'experiments/cytiva/retrieval-pilot-v01/evidence.json'
    expected = qm['supporting_files'][name]
    if nm['dependencies'][name] != expected:
        raise ValueError('Inconsistent reviewed evidence bindings')
    evidence = _read_bound(ROOT/name, expected)
    q = _read_bound(qdir/'review.json', qm['files']['review.json'])
    n = _read_bound(ndir/'review.json', nm['files']['review.json'])
    return evidence, {d['question_id']: d for r in (q, n) for d in r['decisions']}


def _alternatives(passage):
    # Split this verified, edition-bound quotation, never synthesize a chemical.
    quote = passage['quote']
    texts = quote.split('2 column volumes of ', 1)[1].split('. Contact time:', 1)[0].split(', or ')
    if len(texts) != 4:
        raise ValueError('Expected four documented alternatives')
    rows = []
    for text in texts:
        if quote.count(text) != 1:
            raise ValueError('Ambiguous alternative source span')
        start = passage['page_text_start'] + quote.index(text)
        rows.append({'text': text, 'source_id': passage['id'], 'page_text_start': start,
                     'page_text_end': start + len(text),
                     'quote_sha256': hashlib.sha256(text.encode('utf-8')).hexdigest()})
    return rows


def evaluate(payload):
    if not isinstance(payload, dict) or set(payload) != {'mode', 'product', 'deposit_context'}:
        raise ValueError('Choose the exact product and context; no source or policy overrides')
    product, context = payload['product'], payload['deposit_context']
    if (payload['mode'] != 'mabselect' or not isinstance(product, str)
            or not isinstance(context, str) or product not in PRODUCTS or context not in CONTEXTS):
        raise ValueError('Unsupported MabSelect selection')
    started = perf_counter()
    evidence, decisions = _load()
    passages = {p['id']: p for p in evidence['passages']}
    options, options_intro = [], None
    target = None
    if product in ('unknown', 'family_unknown', 'contradictory', 'other'):
        state = 'outside_scope' if product == 'other' else 'needs_clarification'
        scopes, target = ['Q09'], 'product'
        message = ('This product/variant is outside the edition-bound selector. No incompatibility is inferred.'
                   if product == 'other' else 'Please confirm the exact product label; the family name or conflicting labels do not select a recipe.')
    elif context in ('unknown', 'mixed_other'):
        state, scopes, target = 'needs_clarification', ['Q09'], 'context'
        message = 'The exact product is retained. Explore one available deposit category at a time; no confirmed diagnosis is required and no combined procedure is selected.'
    elif context == 'precipitated_substances':
        state, scopes = 'documented_options', ['Q05']
        message = 'The manual documents four separate general formulations for this context. No formulation has been selected as suitable.'
        options.append({'title': 'General block — four separate alternatives', 'source_ids': REQUIRED['Q05'],
                        'quote_ids': ['E167-P'], 'alternatives': _alternatives(passages['E167-P']),
                        'notes': ['Each alternative: 2 column volumes; contact at least 10 min; immediately the documented follow-up wash. The complete source below retains all conditions.']})
        if product in ('sure', 'sure_lx'):
            scopes.append('Q06')
            options_intro = 'General alternatives and an additional product-restricted sequence are separate blocks, not consecutive treatments or a suitability ranking.'
            options.append({'title': 'Additional sequence — SuRe / SuRe LX only',
                            'source_ids': REQUIRED['Q06'], 'quote_ids': ['E167-SH', 'E167-S'],
                            'notes': ['Precipitated/denatured substances context only. Not a fifth general formulation, a mandatory next step or a concentration-selection algorithm.']})
    else:
        state, scopes = 'documented_options', ['N06', 'N07']
        message = 'Explore the documented hydrophobic-context alternatives; no detergent or solvent is selected for your process.'
        options_intro = 'Detergent and organic solvents are alternative routes. Within the solvent route, ethanol OR 2-propanol remains a choice, not a mixture or succession.'
        options = [
            {'title': 'Nonionic detergent — 0.1% is an example', 'source_ids': REQUIRED['N06'],
             'quote_ids': ['E167-D'], 'notes': ['pH applies to the following binding buffer. No named detergent, temperature, duration or numerical flow is specified in this block.']},
            {'title': 'Organic-solvent alternative — ethanol OR 2-propanol', 'source_ids': REQUIRED['N07'],
             'quote_ids': ['E167-E', 'E167-W'],
             'notes': ['Increasing gradients address air bubbles; lower flow addresses increased backpressure. No numerical gradient, flow or pressure limit, or solvent contact time is specified in this block. No page-166 12-hour hold is transferred.']},
        ]
    ids = list(dict.fromkeys(pid for scope in scopes for pid in REQUIRED[scope]))
    approvals = []
    for scope in scopes:
        decision = decisions[scope]
        if (decision['decision'] not in ('validated', 'validated_with_reservation')
                or set(decision['evidence_sha256']) != set(REQUIRED[scope])
                or not decision['reservations']):
            raise ValueError('Required scoped documentary review unavailable')
        approvals.append({'question_id': scope, 'decision': decision['decision'],
                          'reservations': deepcopy(decision['reservations'])})
    fields = ('id', 'pdf_page_1based', 'pdf_page_index_0based', 'scope', 'quote',
              'quote_sha256', 'page_text_start', 'page_text_end')
    return {'journey': 'mabselect-cleaning-v01', 'state': state, 'product': PRODUCTS[product],
            'deposit_context': context, 'context_label': CONTEXTS[context],
            'observation': 'MabSelect cleaning guidance', 'message': message,
            'clarification_target': target, 'options_intro': options_intro,
            'diagnosis_established': False, 'operational_authorization': False,
            'options': options, 'limits': LIMITS.copy(), 'review_scopes': approvals,
            'source_pdf_sha256': evidence['source']['sha256'],
            'passages': [{k: passages[pid][k] for k in fields} for pid in ids], 'bindings': [],
            'elapsed_ms': round((perf_counter()-started)*1000, 1), 'model_calls': 0, 'api_cost_eur': 0,
            'corpus_scope': 'Edition-bound MabSelect cleaning on PDF page 167; clarification may show separately scoped page-166 headings. Independent of frozen v03.'}
