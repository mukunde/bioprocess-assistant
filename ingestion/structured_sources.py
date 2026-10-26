"""Offline, design-approved catalog/source adapter for the structured control.

Historical experiment modules/data are read, never modified or rerun. No model,
database, telemetry exporter or HTTP client is used by this module.
"""
from collections import Counter
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_EVEN
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import re
import unicodedata

from ingestion.local_passage_retrieval import BM25, closure, terms


ROOT = Path(__file__).resolve().parents[1]
TECHNICAL = Path('docs/technical')
DECISION = Path('docs/decisions/2026-10-25-task-request-technical-review.json')
SOURCE_FIELDS = ('id', 'pdf_page_1based', 'pdf_page_index_0based', 'scope', 'quote',
                 'quote_sha256', 'page_text_start', 'page_text_end')


class IntegrityError(ValueError):
    """Unavailable/corrupt approved local inputs; never a missing-source answer."""


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def compact(value, *, sort_keys=False):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'),
                      sort_keys=sort_keys, allow_nan=False)


def normalize_label(label):
    return ' '.join(unicodedata.normalize('NFKC', label).casefold().split())


class Catalog:
    """Exact typed-label resolution; no scan of questions or exclusions."""

    def __init__(self, config):
        self.config = deepcopy(config)
        self.products, self.methods, inventory = {}, {}, set()
        self.entities = {e['id']: e for family in ('products', 'methods')
                         for e in self.config[family]}
        for family, table in (('products', self.products), ('methods', self.methods)):
            for entity in self.config[family]:
                for row in entity['labels']:
                    row = row if isinstance(row, dict) else {'text': row}
                    label = normalize_label(row['text'])
                    if label in inventory:
                        raise IntegrityError('Catalog label collision: ' + row['text'])
                    inventory.add(label)
                    table[label] = (entity['id'], row.get('match_kind', 'reviewed_alias'),
                                    row.get('explicit_bed_volume'))
        self.ambiguous, self.out_of_scope = set(), set()
        for field, target in (('ambiguous_labels', self.ambiguous),
                              ('known_out_of_scope_labels', self.out_of_scope)):
            for label in self.config[field]:
                key = normalize_label(label)
                if key in inventory:
                    raise IntegrityError('Catalog label collision: ' + label)
                inventory.add(key)
                target.add(key)

    def resolve(self, label, kind='product'):
        key = normalize_label(label)
        table = self.products if kind == 'product' else self.methods
        if key in table:
            ref, match, volume = table[key]
            return {'status': match, 'refs': [ref], 'volume': deepcopy(volume)}
        status = ('ambiguous' if kind == 'product' and key in self.ambiguous else
                  'out_of_scope' if kind == 'product' and key in self.out_of_scope else
                  'unresolved')
        return {'status': status, 'refs': [], 'volume': None}


class SourceAdapter:
    def __init__(self, root=ROOT):
        self.root = Path(root).resolve()
        try:
            self._load()
        except IntegrityError:
            raise
        except (OSError, KeyError, TypeError, ValueError) as exc:
            raise IntegrityError('Invalid local structured-control inputs: ' + str(exc)) from exc

    def path(self, relative):
        path = (self.root / relative).resolve()
        if not path.is_relative_to(self.root):
            raise IntegrityError('Input path outside project')
        return path

    def _load(self):
        decision = read(self.path(DECISION))
        if decision['decision'] != 'technical_design_approved_with_TC01_TC04_clarifications':
            raise IntegrityError('Technical design approval missing')
        for name in ('task-request-v01.schema.json', 'task-request-catalog-v01.json',
                     'task-request-source-adapter-v01.json'):
            relative = (TECHNICAL / name).as_posix()
            if digest(self.path(relative)) != decision['current_artifact_sha256_lf'][relative]:
                raise IntegrityError('Approved artifact hash mismatch: ' + relative)
        self.schema = read(self.path(TECHNICAL / 'task-request-v01.schema.json'))
        self.config = read(self.path(TECHNICAL / 'task-request-source-adapter-v01.json'))
        self.catalog = Catalog(read(self.path(TECHNICAL / 'task-request-catalog-v01.json')))
        self.versions = {key: digest(self.path(TECHNICAL / name)) for key, name in (
            ('schema_sha256_lf', 'task-request-v01.schema.json'),
            ('catalog_sha256_lf', 'task-request-catalog-v01.json'),
            ('adapter_sha256_lf', 'task-request-source-adapter-v01.json'))}
        basis = self.config['basis']
        for path_key, hash_key in (
            ('registry_file', 'registry_sha256_lf'), ('policy_file', 'policy_file_sha256_lf'),
            ('source_review_manifest', 'source_review_manifest_sha256_lf')):
            if digest(self.path(basis[path_key])) != basis[hash_key]:
                raise IntegrityError('Pinned input hash mismatch: ' + basis[path_key])
        self.versions['corpus_manifest_sha256_lf'] = basis['source_review_manifest_sha256_lf']
        lexical = self.config['ranking_policy']['lexical_primitive']
        if digest(self.path(lexical['reference_file'])) != lexical['reference_sha256_lf']:
            raise IntegrityError('Pinned lexical primitive changed')
        registry = read(self.path(basis['registry_file']))
        policy = read(self.path(basis['policy_file']))['source_runtime_policy']
        manifest = read(self.path(basis['source_review_manifest']))
        self.eligible = set(basis['eligible_source_ids'])
        self.excluded = set(basis['excluded_source_ids'])
        if (self.eligible & self.excluded or len(self.eligible) != 25 or
                self.excluded != {'E118-I', 'E121-EQ'} or
                self.excluded != set(policy['quarantined_ids']) or
                self.excluded != set(manifest['not_individually_reviewed_source_ids']) or
                registry['source'] != basis['pdf_identity'] or
                manifest['source_pdf_sha256'] != basis['pdf_identity']['sha256']):
            raise IntegrityError('Corpus eligibility/provenance mismatch')
        self.passages = {}
        for source in registry['passages']:
            sid = source['id']
            if sid in self.passages:
                raise IntegrityError('Duplicate source identity')
            fp = self.config['source_fingerprints'][sid]
            if (any(source[k] != v for k, v in fp.items()) or
                    hashlib.sha256(source['quote'].encode('utf-8')).hexdigest() != fp['quote_sha256']):
                raise IntegrityError('Source fingerprint mismatch: ' + sid)
            self.passages[sid] = {**{k: source[k] for k in SOURCE_FIELDS},
                                  'requires': policy['requires'][sid],
                                  'quarantined': sid in self.excluded,
                                  'searchable': sid in policy['searchable_ids']}
        if set(self.passages) != self.eligible | self.excluded:
            raise IntegrityError('Source inventory mismatch')
        for sid in self.passages:
            closure(self.passages, sid)
        for role in self.config['roles']:
            for candidate in role['candidates']:
                bundle = self.bundle(candidate)
                if not set(candidate['direct_support_source_ids']) <= set(bundle):
                    raise IntegrityError('Direct support outside atomic bundle')
        ranking = self.config['ranking_policy']
        self.index = BM25(list(self.passages.values()), bilingual=False,
                          k1=ranking['bm25_k1'], b=ranking['bm25_b'], index_context=True)
        self.policy = policy

    def bundle(self, candidate):
        ordered = []
        for sid in candidate['root_source_ids'] + candidate['required_guard_source_ids']:
            for member in closure(self.passages, sid):
                if member not in self.eligible:
                    raise IntegrityError('Ineligible candidate bundle member: ' + member)
                if member not in ordered:
                    ordered.append(member)
        return ordered

    def rank(self, candidates, query_parts):
        """Input: (candidate, covered units) pairs after all semantic gates."""
        query = sorted(set(terms(' '.join(query_parts), bilingual=False)))
        ranked = []
        for candidate, units in candidates:
            scores = []
            for sid in candidate['root_source_ids']:
                tf = self.index.docs.get(sid, Counter())
                score = 0.0
                for token in query:
                    frequency = tf[token]
                    if frequency:
                        idf = math.log(1 + (len(self.index.docs) - self.index.df[token] + .5) /
                                       (self.index.df[token] + .5))
                        norm = frequency + self.index.k1 * (
                            1 - self.index.b + self.index.b * self.index.lengths[sid] /
                            (self.index.average or 1))
                        score += idf * frequency * (self.index.k1 + 1) / norm
                scores.append(score)
            raw = sum(scores) / len(scores)
            rounded = Decimal(str(raw)).quantize(Decimal('0.000000000001'), rounding=ROUND_HALF_EVEN)
            scope = candidate['scope_specificity']
            components = {'new_units': len(units), 'product_grade': scope['product_grade'],
                          'column_grade': scope['column_grade'], 'bm25_raw': raw,
                          'bm25_rounded': str(rounded), 'query_tokens': query}
            key = (-len(units), -scope['product_grade'], -scope['column_grade'],
                   -rounded, tuple(sorted(candidate['root_source_ids'])))
            ranked.append((key, candidate, units, components))
        return sorted(ranked, key=lambda row: row[0])

    def syringe_reference_flow(self, column):
        """Read the two literal reference pairs; no inferred drop conversion."""
        role = next(r for r in self.config['roles'] if r['id'] == 'role:blue.syringe_note')
        source = role['candidates'][0]['direct_support_source_ids'][0]
        pattern = (r'(\d+(?:\.\d+)?) mL/min corresponds to approximately\s+(\d+) '
                   r'drops/min when using a (?:syringe with a )?(\d+) mL HiTrap column')
        pairs = re.findall(pattern, self.passages[source]['quote'])
        if len(pairs) != 2:
            raise IntegrityError('Pinned syringe note cannot be read deterministically')
        return next((Decimal(flow) for flow, _, size in pairs if Decimal(size) == column), None)


def local_token_counter(root, policy):
    """Construct cl100k_base solely from a verified local file, never an URL.

    Pattern/special IDs are those of pinned tiktoken 0.12.0 cl100k_base.
    Deliberately bypass get_encoding(), whose cache miss can initiate a download.
    """
    import tiktoken
    from tiktoken.load import load_tiktoken_bpe

    if importlib.metadata.version('tiktoken') != policy['tiktoken_version']:
        raise IntegrityError('Pinned tokenizer version unavailable')
    filename = hashlib.sha1(
        b'https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken').hexdigest()
    asset = Path(root) / '.local-tools/tiktoken-cache' / filename
    if not asset.is_file() or hashlib.sha256(asset.read_bytes()).hexdigest() != policy['asset_sha256']:
        raise IntegrityError('Missing/invalid local tokenizer asset; downloads forbidden')
    encoding = tiktoken.Encoding(
        name='cl100k_base',
        pat_str=r"'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}++|\p{N}{1,3}+| ?[^\s\p{L}\p{N}]++[\r\n]*+|\s++$|\s*[\r\n]|\s+(?!\S)|\s",
        mergeable_ranks=load_tiktoken_bpe(str(asset.resolve()), expected_hash=policy['asset_sha256']),
        special_tokens={'<|endoftext|>': 100257, '<|fim_prefix|>': 100258,
                        '<|fim_middle|>': 100259, '<|fim_suffix|>': 100260,
                        '<|endofprompt|>': 100276})
    return lambda text: len(encoding.encode(text, disallowed_special=()))
