"""Offline structural comparison of the saved subscription responses."""
import json
from collections import Counter
from pathlib import Path
from experiments.cytiva.v01.check_result import check
from experiments.cytiva.paths import V01 as HERE, candidate_path

schema = json.loads((HERE / 'schema.json').read_text(encoding='utf-8'))
corpus = json.loads((HERE / 'input.json').read_text(encoding='utf-8'))
summary = {}
for name in ('sonnet', 'sol'):
    data = json.loads(candidate_path(name).read_text(encoding='utf-8-sig'))
    report = check(data, schema, corpus)
    (HERE / f'verification-{name}.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    summary[name] = {
        'entities': len(data['entities']),
        'predicates': dict(Counter(c['predicate'] for c in data['claims'])),
        **{k: v for k, v in report.items() if k != 'resolved'},
    }
(HERE / 'comparaison-structurelle.json').write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(summary, ensure_ascii=False, indent=2))
