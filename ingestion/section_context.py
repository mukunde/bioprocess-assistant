"""Opt-in product-section context policy; independent of evaluation references."""
import re
import unicodedata
from ingestion.local_passage_retrieval import assemble, closure, eligible, serialize, terms


def folded(text):
    text = ''.join(c for c in unicodedata.normalize('NFKD', text.lower()) if not unicodedata.combining(c))
    return ' '.join(re.findall(r'[a-z0-9]+', text))


def section_plan(question, hits, config):
    """No IDs/labels from the question set are accepted or consulted."""
    if not hits and config['require_positive_retrieval_hit']:
        return {'triggered': False, 'reason': 'no_retrieval_evidence', 'overview_ids': [], 'families': []}
    query_terms = set(terms(question))
    if 'pressure' in query_terms:
        query_terms.add('backpressure')
    matched_terms = sorted(query_terms & set(config['trigger_terms']))
    if not matched_terms:
        return {'triggered': False, 'reason': 'no_section_trigger', 'overview_ids': [], 'families': []}
    text = folded(question)
    # Match aliases as whole phrases, not arbitrary substrings of a product name.
    mentioned = [f for f in config['families'] if any(' ' + folded(alias) + ' ' in ' ' + text + ' '
                  for alias in f['query_aliases'])]
    chosen = mentioned or config['families']
    return {'triggered': True, 'reason': 'pressure_flow_or_threshold', 'trigger_terms': matched_terms,
            'product_resolution': 'explicit_family' if mentioned else 'unresolved_product',
            'families': [f['id'] for f in chosen],
            'overview_ids': list(dict.fromkeys(pid for f in chosen for pid in f['overview_ids']))}


def assemble_sections(passages, hits, question, count_tokens, config, max_tokens=2048):
    plan = section_plan(question, hits, config)
    if not plan['triggered']:
        return {**assemble(passages, hits, count_tokens, max_tokens), 'section_plan': plan,
                'section_status': 'not_requested'}
    overview = list(dict.fromkeys(pid for anchor in plan['overview_ids'] for pid in closure(passages, anchor)))
    blocked = any(not eligible(passages, anchor) for anchor in plan['overview_ids'])
    if blocked or count_tokens(serialize(passages, overview)) > max_tokens:
        result = assemble(passages, hits, count_tokens, max_tokens)
        result['excluded'].insert(0, {'reason': 'section_quarantine' if blocked else 'whole_section_overview_over_budget'})
        result['budget_complete'] = False
        return {**result, 'section_plan': plan, 'section_status': 'unavailable'}
    # Preflight guarantees the entire overview fits, so assembly cannot keep a partial overview.
    priority = [{'passage_id': pid} for pid in plan['overview_ids']]
    result = assemble(passages, priority + hits, count_tokens, max_tokens)
    if not set(overview) <= set(result['ids']):
        raise ValueError('Atomic overview unexpectedly split')
    return {**result, 'section_plan': plan, 'section_status': 'included'}
