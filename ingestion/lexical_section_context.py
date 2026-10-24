"""Experimental lexical views and atomic section overviews; source quotes stay exact."""
import re
import unicodedata

from ingestion.local_passage_retrieval import BM25, assemble, closure, eligible, serialize


def folded(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text.lower())
                   if not unicodedata.combining(c))


def phrase_pattern(text):
    return r'(?<!\w)' + r'[\W_]+'.join(re.escape(w) for w in re.findall(r'\w+', folded(text))) + r'(?!\w)'


def contains(text, alias):
    return re.search(phrase_pattern(alias), folded(text)) is not None


def lexical_view(text, vocabulary):
    text = folded(text)
    aliases = [(alias, token) for token, values in vocabulary['phrases'].items() for alias in values]
    # Longest phrases first; whole words prevent abbreviation/product prefix matches.
    for alias, token in sorted(aliases, key=lambda p: (-len(p[0]), p[0])):
        text = re.sub(phrase_pattern(alias), token, text)
    return re.sub(r'\w+', lambda m: vocabulary['words'].get(m.group(), m.group()), text)


class VocabularyIndex:
    def __init__(self, corpus, retrieval, vocabulary=None):
        self.passages = {p['id']: p for p in corpus}
        self.vocabulary = vocabulary
        projected = [{'id': p['id'], 'requires': p['requires'], 'quarantined': p['quarantined'],
                      'searchable': p.get('searchable', True),
                      'quote': lexical_view(p['quote'], vocabulary) if vocabulary and not p['quarantined'] else p['quote']}
                     for p in corpus]
        self.index = BM25(projected, retrieval['bilingual_aliases'], retrieval['k1'],
                          retrieval['b'], retrieval['index_context'])
        self.docs = self.index.docs

    def search(self, text, top_k=6):
        query = lexical_view(text, self.vocabulary) if self.vocabulary else text
        return self.index.search(query, top_k)


def overview_plan(passages, hits, question, config):
    if not hits:
        return {'triggered': False, 'reason': 'no_positive_source_hit', 'sections': [], 'anchor_ids': []}
    sections = [s for s in config['sections'] if all(any(contains(question, alias) for alias in group)
                for group in s['query_alias_groups'])]
    named_sections = {s['id'] for s in sections}
    reason = 'explicit_source_sections'
    if not sections:
        reason = 'highest_ranked_source_section'
        for hit in hits:
            ancestry = closure(passages, hit['passage_id'])
            sections = [s for s in config['sections'] if s['root_id'] in ancestry]
            if sections:
                break
    unresolved = config['unresolved_contaminant']
    methods = [name for name, aliases in unresolved['methods'].items()
               if any(contains(question, alias) for alias in aliases)]
    unknown = any(contains(question, alias) for alias in unresolved['unknown_markers'])
    general = unknown and len(methods) >= unresolved['min_distinct_methods']
    anchors = [pid for s in sections for pid in s['overview_ids']]
    if general:
        anchors += unresolved['overview_ids']
        for s in sections:
            if s['id'] in named_sections:
                anchors += unresolved['named_section_additions'].get(s['id'], [])
    return {'triggered': bool(anchors), 'reason': reason, 'sections': [s['id'] for s in sections],
            'general_unknown_context': general, 'matched_methods': methods,
            'anchor_ids': list(dict.fromkeys(anchors))}


def assemble_overviews(passages, hits, question, count_tokens, config, max_tokens=2048):
    plan = overview_plan(passages, hits, question, config)
    if not plan['triggered']:
        return {**assemble(passages, hits, count_tokens, max_tokens),
                'overview_plan': plan, 'overview_status': 'not_requested'}
    mandatory = list(dict.fromkeys(pid for seed in plan['anchor_ids'] for pid in closure(passages, seed)))
    blocked = any(not eligible(passages, seed) for seed in plan['anchor_ids'])
    if blocked or count_tokens(serialize(passages, mandatory)) > max_tokens:
        result = assemble(passages, hits, count_tokens, max_tokens)
        result['excluded'].insert(0, {'reason': 'overview_quarantine' if blocked else 'whole_overview_over_budget'})
        result['budget_complete'] = False
        return {**result, 'overview_plan': plan, 'overview_status': 'unavailable'}
    result = assemble(passages, [{'passage_id': p} for p in plan['anchor_ids']] + hits, count_tokens, max_tokens)
    if not set(mandatory) <= set(result['ids']):
        raise ValueError('Mandatory section overview unexpectedly split')
    return {**result, 'overview_plan': plan, 'overview_status': 'included'}
