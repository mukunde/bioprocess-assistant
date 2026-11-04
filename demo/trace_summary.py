"""Read-only, bounded summaries of the local registry-trace/v1 JSONL format."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import html
import json
import math
from pathlib import Path
import re

from .registry_tracing import RESOURCE, SOURCE_ROUTE, permitted

MAX_BYTES = 8 * 1024 * 1024
MAX_LINE = 16384
MAX_SPANS = 4096
FIELDS = {'schema', 'name', 'trace_id', 'span_id', 'parent_span_id', 'kind',
          'start_time_unix_nano', 'end_time_unix_nano', 'duration_ms', 'status',
          'resource', 'attributes'}
ROOT_NAMES = {method + ' ' + route for method in ('GET', 'POST')
              for route in ('/', '/api/reviewed/v1/evaluate', SOURCE_ROUTE, 'unmatched')}
NAMES = ROOT_NAMES | {'registry.evaluate', 'registry.source'}


class SummaryUnavailable(ValueError):
    """Controlled diagnostic: never attach a path or malformed input."""


def identifier(value, size):
    return (type(value) is str and re.fullmatch('[0-9a-f]{'+str(size)+'}', value)
            is not None and int(value, 16) != 0)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate key')
        result[key] = value
    return result


def clean_span(row):
    """Closed projection, independent of exporter input and exception messages."""
    if type(row) is not dict or set(row) != FIELDS:
        raise ValueError('Unknown record')
    if row['schema'] != 'registry-trace/v1' or row['resource'] != RESOURCE:
        raise ValueError('Unknown schema/resource')
    if row['name'] not in NAMES or row['status'] not in ('UNSET', 'OK', 'ERROR'):
        raise ValueError('Unknown operation/status')
    if not identifier(row['trace_id'], 32) or not identifier(row['span_id'], 16):
        raise ValueError('Invalid identity')
    parent = row['parent_span_id']
    if row['kind'] == 'SERVER':
        if parent is not None or row['name'].startswith('registry.'):
            raise ValueError('Invalid root')
    elif row['kind'] == 'INTERNAL':
        if not identifier(parent, 16) or not row['name'].startswith('registry.'):
            raise ValueError('Invalid child')
    else:
        raise ValueError('Invalid kind')
    start, end = row['start_time_unix_nano'], row['end_time_unix_nano']
    if (type(start) is not int or type(end) is not int
            or not 0 <= start <= end <= 2**63-1):
        raise ValueError('Invalid timestamp')
    duration = row['duration_ms']
    if (type(duration) not in (int, float) or not math.isfinite(duration)
            or duration < 0 or abs(duration - (end-start)/1e6) > .001):
        raise ValueError('Invalid duration')
    attributes = row['attributes']
    if type(attributes) is not dict or not all(permitted(k, v) for k, v in attributes.items()):
        raise ValueError('Unknown metadata')
    return dict(row, attributes=dict(attributes), resource=dict(RESOURCE))


def read_summary(filename):
    """Snapshot only; tolerate an exporter currently writing its last line."""
    try:
        with Path(filename).open('rb') as stream:
            data = stream.read(MAX_BYTES + 1)
    except OSError:
        raise SummaryUnavailable('Local trace file is unavailable; guidance is unaffected.') from None
    if len(data) > MAX_BYTES:
        raise SummaryUnavailable('Trace file exceeds the summary size limit; choose a smaller session file.')
    spans, ignored, pending, seen = [], 0, 0, set()
    for raw in data.splitlines(keepends=True):
        if not raw.endswith(b'\n'):
            pending += 1
            continue
        if len(raw) > MAX_LINE:
            ignored += 1
            continue
        try:
            row = clean_span(json.loads(raw, object_pairs_hook=unique_object))
            identity = (row['trace_id'], row['span_id'])
            if identity in seen:
                raise ValueError('Duplicate span')
        except (ValueError, TypeError, KeyError, OverflowError, RecursionError):
            ignored += 1
            continue
        seen.add(identity)
        spans.append(row)
        if len(spans) > MAX_SPANS:
            raise SummaryUnavailable('Trace file exceeds the span limit; choose a smaller session file.')
    groups = {}
    for span in spans:
        groups.setdefault(span['trace_id'], []).append(span)
    traces = []
    for trace_id, members in groups.items():
        roots = [s for s in members if s['kind'] == 'SERVER']
        root = roots[0] if len(roots) == 1 else None
        children = [s for s in members if s['kind'] == 'INTERNAL']
        complete = root is not None and all(s['parent_span_id'] == root['span_id'] for s in children)
        # Only dispatched evaluation/source operations have registry children.
        expected = ('registry.evaluate' if root and root['name'] == 'POST /api/reviewed/v1/evaluate' else
                    'registry.source' if root and root['name'] == 'GET '+SOURCE_ROUTE else None)
        if expected:
            complete = complete and len(children) == 1 and children[0]['name'] == expected
            status = root['attributes'].get('http.response.status_code')
            if not children and type(status) is int and status >= 400:
                # A rejected request may never enter Registry; a dropped child is
                # also possible. Do not infer dispatch or claim missing telemetry.
                complete = None
        traces.append({'trace_id': trace_id, 'root': root, 'children': children,
                       'complete': complete, 'started': min(s['start_time_unix_nano'] for s in members)})
    traces.sort(key=lambda t: t['started'], reverse=True)
    return {'spans': len(spans), 'http_requests': sum(s['kind'] == 'SERVER' for s in spans),
            'ignored_records': ignored, 'pending_records': pending,
            'outcomes': dict(Counter(s['attributes'].get('bioprocess.outcome', 'unknown')
                                     for s in spans if s['kind'] == 'SERVER')),
            'traces': traces}


def text_summary(summary):
    lines = ['LOCAL TRACE SUMMARY · metadata only · read-only',
             f"{summary['http_requests']} HTTP requests · {summary['spans']} spans · "
             f"{summary['ignored_records']} ignored records · {summary['pending_records']} pending lines",
             'Source views have separate trace IDs; proximity is not a parent link.',
             'Best effort: missing spans do not prove that no request occurred. No model/cost metrics.']
    for trace in summary['traces']:
        root = trace['root']
        state = ('root only / HTTP rejection; registry dispatch not established'
                 if trace['complete'] is None else
                 'complete' if trace['complete'] else 'partial / unlinked')
        lines.append(f"\nTrace {trace['trace_id']} · {state}")
        for span in ([root] if root else []) + trace['children']:
            attributes = span['attributes']
            when = datetime.fromtimestamp(span['start_time_unix_nano']/1e9, timezone.utc).isoformat(timespec='seconds')
            lines.append(f"  {when} · {span['name']} · {span['duration_ms']:.2f} ms · "
                         f"{attributes.get('bioprocess.outcome', 'unknown')} · HTTP "
                         f"{attributes.get('http.response.status_code', '-')} · {span['status']}")
            metadata = ', '.join(f'{k}={v}' for k, v in sorted(attributes.items())
                                 if k.startswith('bioprocess.') or k == 'error.type')
            if metadata:
                lines.append('    '+metadata)
    return '\n'.join(lines)


def html_summary(summary=None, *, unavailable=False):
    # No raw file path, line, exception, quotation or arbitrary HTML is rendered.
    message = ('Local trace summary unavailable. Guidance remains available. '
               'Check the local session file and refresh.' if unavailable else text_summary(summary))
    return ('''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Local trace summary</title><style>body{font:16px/1.6 system-ui;max-width:1100px;
margin:24px auto;padding:0 20px;color:#19343c}pre{white-space:pre-wrap;overflow-wrap:anywhere}
a{color:#08656d}</style><h1>Request → source → trace</h1>
<p><a href="/">Return to guidance</a> · <a href="/demo/traces">Refresh summary</a></p>
<p>Local session only. Exports are asynchronous; refresh after a moment.
This view does not flush queues, change authority or contact a backend.</p><pre>'''
            + html.escape(message) + '</pre></html>').encode('utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace_file', type=Path)
    args = parser.parse_args(argv)
    try:
        print(text_summary(read_summary(args.trace_file)))
    except SummaryUnavailable as error:
        print(str(error))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
