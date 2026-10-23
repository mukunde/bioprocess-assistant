"""Deterministic lexical passage retrieval and atomic source-context assembly.

No model, network, database, question reference or answer policy is used here.
"""
from collections import Counter
import hashlib
import json
import math
import re
import unicodedata

STOP = set('a an the of and or to in on for with at is are be it that this what which can should do does my as from after before then de du des le la les un une et ou en au aux pour avec sur dans est sont que quel quelle quelles quels ce ces il elle je mon ma mes donne'.split())
# Small declared vocabulary bridge, not a translation model or question-ID lookup.
ALIASES = {
    'contre': 'backpressure', 'pression': 'backpressure', 'contrepression': 'backpressure',
    'augmente': 'increase', 'augmentation': 'increase', 'increases': 'increase', 'increased': 'increase', 'rose': 'increase',
    'nettoyage': 'clean', 'nettoyer': 'clean', 'cleaning': 'clean', 'cleaned': 'clean',
    'proteines': 'protein', 'proteins': 'protein', 'proteine': 'protein',
    'precipitees': 'precipitated', 'denaturees': 'denatured',
    'hydrophobes': 'hydrophobic', 'fortement': 'strongly', 'liees': 'bound',
    'lipides': 'lipid', 'lipids': 'lipid', 'lipoproteines': 'lipoprotein', 'lipoproteins': 'lipoprotein',
    'detergent': 'detergent', 'ethanol': 'ethanol', 'tampon': 'buffer',
    'lavage': 'wash', 'laver': 'wash', 'washing': 'wash',
    'debit': 'flow', 'reduit': 'lower', 'reduced': 'lower', 'faible': 'lower',
    'seuil': 'threshold', 'colonne': 'column', 'colonnes': 'column',
    'milieux': 'media', 'milieu': 'media', 'substances': 'substance',
    'alternatives': 'alternative', 'alcalin': 'alkali', 'alcaline': 'alkali',
    'heures': 'h', 'heure': 'h', 'hour': 'h', 'hours': 'h',
    'maintien': 'stand', 'hold': 'stand', 'solvant': 'solvent',
    'regeneration': 'regeneration', 'capacite': 'capacity', 'initiale': 'original',
    'cause': 'cause', 'unique': 'sole',
}


def terms(text, bilingual=True):
    text = ''.join(c for c in unicodedata.normalize('NFKD', text.lower()) if not unicodedata.combining(c))
    tokens = re.findall(r'[a-z0-9]+', text)
    return [ALIASES.get(t, t) if bilingual else t for t in tokens if t not in STOP]


def closure(passages, seed):
    """Order dependencies before their child; reject absent/cyclic scope links."""
    ordered, active, seen = [], set(), set()
    def visit(pid):
        if pid not in passages:
            raise ValueError('Missing context dependency: ' + pid)
        if pid in active:
            raise ValueError('Cyclic context dependency')
        if pid in seen:
            return
        active.add(pid)
        for parent in passages[pid]['requires']:
            visit(parent)
        active.remove(pid)
        seen.add(pid)
        ordered.append(pid)
    visit(seed)
    return ordered


def eligible(passages, pid):
    return all(not passages[p]['quarantined'] for p in closure(passages, pid))


class BM25:
    def __init__(self, passages, bilingual=True, k1=1.2, b=0.75, index_context=False):
        if not math.isfinite(k1) or k1 <= 0 or not math.isfinite(b) or not 0 <= b <= 1:
            raise ValueError('Invalid BM25 parameters')
        self.passages = {p['id']: p for p in passages}
        if len(self.passages) != len(passages):
            raise ValueError('Duplicate passage IDs')
        self.bilingual, self.k1, self.b = bilingual, k1, b
        self.docs = {}
        for pid, p in self.passages.items():
            if eligible(self.passages, pid) and p.get('searchable', True):
                ids = closure(self.passages, pid) if index_context else [pid]
                text = '\n'.join(self.passages[item]['quote'] for item in ids)
                self.docs[pid] = Counter(terms(text, bilingual))
        self.lengths = {pid: sum(tf.values()) for pid, tf in self.docs.items()}
        self.average = sum(self.lengths.values()) / max(1, len(self.docs))
        self.df = Counter(t for tf in self.docs.values() for t in tf)

    def search(self, question, top_k=5):
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 0:
            raise ValueError('top_k must be a nonnegative integer')
        scores = []
        for pid, tf in self.docs.items():
            value = 0.0
            for t in set(terms(question, self.bilingual)):
                frequency = tf[t]
                if frequency:
                    idf = math.log(1 + (len(self.docs) - self.df[t] + 0.5) / (self.df[t] + 0.5))
                    norm = frequency + self.k1 * (1 - self.b + self.b * self.lengths[pid] / (self.average or 1))
                    value += idf * frequency * (self.k1 + 1) / norm
            if value > 0:
                scores.append({'passage_id': pid, 'score': value})
        return sorted(scores, key=lambda x: (-x['score'], x['passage_id']))[:top_k]


def serialize(passages, ids):
    """All serialized source metadata, labels and exact quotes count toward budget."""
    return json.dumps({'source_passages': [{k: passages[pid][k] for k in (
        'id', 'pdf_page_1based', 'pdf_page_index_0based', 'scope', 'quote',
        'quote_sha256', 'page_text_start', 'page_text_end')} for pid in ids]},
        ensure_ascii=False, separators=(',', ':'))


def assemble(passages, hits, count_tokens, max_tokens=2048):
    if isinstance(max_tokens, bool) or not isinstance(max_tokens, int) or max_tokens < 1:
        raise ValueError('max_tokens must be a positive integer')
    selected, excluded, accepted = [], [], []
    if count_tokens(serialize(passages, [])) > max_tokens:
        return {'ids': [], 'accepted_seeds': [], 'excluded': [{'reason': 'empty_wrapper_over_budget'}],
                'context': '', 'tokens': 0, 'budget_complete': False}
    for hit in hits:
        seed = hit['passage_id']
        unit = closure(passages, seed)
        if not eligible(passages, seed):
            excluded.append({'seed': seed, 'reason': 'quarantine_in_bundle'})
            continue
        candidate = selected + [pid for pid in unit if pid not in selected]
        size = count_tokens(serialize(passages, candidate))
        if size > max_tokens:
            excluded.append({'seed': seed, 'reason': 'whole_bundle_over_budget', 'candidate_tokens': size})
            continue
        selected = candidate
        accepted.append(seed)
    text = serialize(passages, selected)
    return {'ids': selected, 'accepted_seeds': accepted, 'excluded': excluded, 'context': text,
            'tokens': count_tokens(text), 'budget_complete': not excluded,
            'context_sha256': hashlib.sha256(text.encode()).hexdigest()}
