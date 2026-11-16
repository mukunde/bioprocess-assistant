"""Opt-in guided Chainlit adapter over existing approved local authority.

No preview, model, authority mutation or free-text interpretation. Callbacks own
only per-session controls and opaque action tokens; source clicks recheck authority.
"""
import asyncio
import atexit
import html
import json
import os
from pathlib import Path
import re
import uuid

import chainlit as cl
from chainlit.input_widget import Select, Switch

from serving.local_registry import Registry
from demo import registry_tracing

PRODUCTS = {
    "Not specified": "unknown", "MabSelect — exact unsuffixed product": "mabselect",
    "MabSelect SuRe": "sure", "MabSelect SuRe LX": "sure_lx",
    "MabSelect family — variant unknown": "family_unknown",
    "Other product": "other", "Conflicting labels": "contradictory",
}
CONTEXTS = {
    "Unknown — help me clarify": "unknown",
    "Precipitated or denatured substances": "precipitated_substances",
    "Hydrophobic proteins, lipoproteins or lipids": "hydrophobic_deposits",
    "Mixed / uncertain / other": "mixed_other",
}
DEFAULTS = {"product": next(iter(PRODUCTS)), "context": next(iter(CONTEXTS)),
            "cleaning": True, "pressure": False}
ITEM_LABELS = {'cleaning_options': 'Documented cleaning options',
               'pressure_limit': 'Numerical maximum pressure'}
STATUS_LABELS = {'supported': 'Documented support', 'partial': 'Partial answer',
                 'needs_clarification': 'Clarification needed',
                 'abstained': 'No supported answer to this requested item',
                 'quarantined': 'Evidence held', 'unavailable': 'Registry unavailable',
                 'excluded': 'Excluded from this request'}
KEY = "mabselect_documentary"
UNAVAILABLE = "Registry unavailable. No quotation or procedure supplied; no preview fallback. Retry manually."
STALE = "These controls or this result are no longer current. Use the latest controls and submit again."
NOTICE = ("Documentary support only: no diagnosis or operational authorization. "
          "Messages are snapshots, not live approvals. Open a source to check current authority; "
          "previously displayed text cannot be recalled after a withdrawal.")
_tracing = None


def text(value):
    """Literal source content must not create HTML, Markdown links or images."""
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~-])", r"\\\1", html.escape(str(value), quote=False))


def request(settings):
    if not isinstance(settings, dict) or set(settings) != set(DEFAULTS):
        raise ValueError("Invalid controls")
    if (type(settings['product']) is not str or type(settings['context']) is not str
            or settings['product'] not in PRODUCTS or settings['context'] not in CONTEXTS):
        raise ValueError("Invalid selection")
    if any(type(settings[k]) is not bool for k in ('cleaning', 'pressure')):
        raise ValueError("Invalid switch")
    items = [v for k, v in (('cleaning', 'cleaning_options'), ('pressure', 'pressure_limit'))
             if settings[k]]
    if not items:
        raise ValueError("Select at least one question")
    return {'kind': 'reviewed_serving_request/v1', 'request_id': 'chainlit-guided-request',
            'language': 'en', 'tasks': [{'task_id': 'A', 'product': PRODUCTS[settings['product']],
            'deposit_context': CONTEXTS[settings['context']], 'requested_items': items,
            'excluded_items': []}]}


def service():
    """Root/tracing are operator-only configuration; constructing Registry is read-only."""
    global _tracing
    root = os.environ.get('MABSELECT_REGISTRY_ROOT', '').strip()
    if os.environ.get('BIOPROCESS_MODE') != 'mabselect' or not root:
        raise ValueError('Explicit documentary mode and authority required')
    if _tracing is None:
        _tracing = registry_tracing.configure(
            trace_file=os.environ.get('MABSELECT_TRACE_FILE') or None,
            protected_root=Path(root).resolve())
        atexit.register(_tracing.close)
    return registry_tracing.ObservedRegistry(Registry(Path(root).resolve()), _tracing)


def source_message(passage):
    quote = "\n".join("> " + text(line) for line in passage['quote'].splitlines())
    return (
        f"### {text(passage['source_id'])} · PDF page {passage['pdf_page_1based']}\n\n"
        f"**Cytiva handbook** · {text(passage['document_reference'])}"
        f" · Printed page {text(passage['printed_page_label'])}\n\n"
        f"{text(passage['scope'])}\n\n**Original passage**\n\n{quote}"
    )


def provenance_file(source_id, view):
    return cl.File(
        name=source_id + '-provenance.json',
        content=json.dumps(view, ensure_ascii=False, indent=2).encode('utf-8'),
        mime='application/json',
    )


async def send_controls(
    state, revision, content, citations=(), *, can_submit=True,
    session_key=KEY, action_name='mabselect_submit', label='Find documented guidance',
):
    # Serialize button replacement with delivery so an older send cannot
    # leave a button behind after a newer settings update.
    async with state['button_lock']:
        if not current(state, revision, session_key):
            return
        previous = state.pop('submit_action', None)
        if previous is not None:
            await previous.remove()
        if not current(state, revision, session_key):
            return
        actions = list(citations)
        if can_submit:
            state['submit_token'] = uuid.uuid4().hex
            action = cl.Action(name=action_name, label=label, icon='search',
                               payload={'token': state['submit_token']})
            state['submit_action'] = action
            actions.append(action)
        await cl.Message(content=content, actions=actions).send()


async def start():
    state = {'settings': dict(DEFAULTS), 'revision': 0, 'sources': {}, 'busy': False,
             'submit_token': None, 'button_lock': asyncio.Lock()}
    cl.user_session.set(KEY, state)
    # Controls and an explicit retry remain available during an authority outage.
    # Showing controls grants no authority and performs no lookup or activation.
    await cl.ChatSettings([
        Select(id='product', label='Exact product', values=list(PRODUCTS), initial_index=0),
        Select(id='context', label='Context to explore (not a diagnosis)', values=list(CONTEXTS), initial_index=0),
        Switch(id='cleaning', label='Documented cleaning options', initial=True),
        Switch(id='pressure', label='Numerical maximum pressure', initial=False),
    ]).send()
    try:
        await asyncio.wait_for(asyncio.to_thread(_check), timeout=15)
    except Exception:
        await send_controls(state, 0, UNAVAILABLE)
        return
    await send_controls(
        state, 0,
        '### MabSelect documentary guidance\n\n'
        '1. Choose the product and context in **Settings**.\n'
        '2. Confirm your selections and choose **Find documented guidance**.\n'
        '3. Open a citation to read the original passage.\n\n' + NOTICE,
    )


def _check():
    registry = service()
    with registry.lock:
        registry._snapshot()


async def settings_update(settings):
    state = cl.user_session.get(KEY)
    if not state:
        await cl.Message(content=UNAVAILABLE).send()
        return
    state['revision'] += 1
    state['sources'] = {}
    state['submit_token'] = None
    try:
        request(settings)
    except (ValueError, TypeError):
        await send_controls(
            state, state['revision'],
            'Choose valid controls and select at least one question in Settings.',
            can_submit=False,
        )
        return
    state['settings'] = dict(settings)
    await send_controls(state, state['revision'],
                        'Controls updated. Select Find documented guidance to continue.')


async def free_text():
    await cl.Message(content='This mode uses guided controls only. Open Settings, choose the product '
                     'and context, then press Find documented guidance. No free-text lookup or model call was made.').send()


def render(out, submitted):
    """Keep alternatives, conditions, original warnings and reservations separate."""
    lines = ['### Request outcome: ' + text(STATUS_LABELS[out['status']]),
             '**Submitted product**: ' + text(submitted['product']),
             '**Context explored**: ' + text(submitted['context']),
             '**Questions**: ' + ', '.join(ITEM_LABELS[v] for v in request(submitted)['tasks'][0]['requested_items']),
             NOTICE]
    if out['status'] == 'unavailable':
        return UNAVAILABLE
    targets = []
    for item in out['items']:
        lines.append('**' + text(ITEM_LABELS[item['requested_item']]) + ': '
                     + text(STATUS_LABELS[item['state']]) + '**')
        if item['state'] == 'needs_clarification':
            targets.extend(t for t in item['clarification_targets'] if t not in targets)
        if item['state'] == 'abstained':
            lines.append('No procedure or numerical substitute is inferred. '
                         + ('This product is outside this documentary release; this does not establish incompatibility.'
                            if item['reason'] == 'outside_release_scope' else
                            'Absence is limited to the selected reviewed excerpts, not the whole manual.'))
        if item['state'] in ('quarantined', 'unavailable'):
            lines.append('Required support is held or unavailable for this scope. No incomplete procedure supplied.')
    if targets:
        labels = {'product': 'the exact product label', 'deposit_context': 'one context to explore',
                  'context': 'one context to explore'}
        lines.append('Please specify: ' + ', '.join(labels[t] for t in targets)
                     + '. Edit these fields in Settings; retain supplied fields. A confirmed diagnosis is not required.')
    displayed_conditions = set()
    for bundle in out['context']['bundles']:
        if bundle['options'] and all(o['role'] == 'clarification_context' for o in bundle['options']):
            lines.append('**Clarification context — not a selected procedure**')
        condition = bundle['condition_explanation']
        if condition not in displayed_conditions:
            lines += ['**Scope and conditions**', text(condition)]
            displayed_conditions.add(condition)
        for option in bundle['options']:
            lines.append('#### ' + text(option['wording']))
            for step in option['steps']:
                lines.append(text(step['wording']) + '\nSources: ' + ', '.join(text(s) for s in step['source_ids']))
            for warning in option['warnings']:
                lines.append('**Original precaution**: ' + text(warning['wording'])
                             + '\nSources: ' + ', '.join(text(s) for s in warning['source_ids']))
        lines += ['**Required sources**: ' + ', '.join(text(s) for s in bundle['required_source_ids']),
                  '**Review reservations**']
        lines.extend(text(s) for s in bundle['visible_reservations'])
    return '\n\n'.join(lines)


def current(state, revision, session_key=KEY):
    return cl.user_session.get(session_key) is state and state['revision'] == revision


async def submit(action):
    state = cl.user_session.get(KEY)
    if not state or not state.get('submit_token') or action.payload != {'token': state['submit_token']}:
        await cl.Message(content=STALE).send()
        return
    if state['busy']:
        await cl.Message(content='A request is already being checked. Please wait.').send()
        return
    revision = state['revision']
    state['busy'] = True
    state['sources'] = {}
    state['submit_token'] = None
    try:
        submitted = dict(state['settings'])
        value = request(submitted)
        out = await asyncio.wait_for(asyncio.to_thread(lambda: service().evaluate(value)), timeout=15)
        if not current(state, revision):
            await cl.Message(content=STALE).send()
            return
        body = render(out, submitted)
        actions = []
        if out['status'] != 'unavailable':
            passages = {p['source_id']: p for p in out['context']['passages']}
            for ref in out['citation_refs']:
                token = uuid.uuid4().hex
                state['sources'][token] = (ref['release_id'], ref['source_id'])
                page = passages[ref['source_id']]['pdf_page_1based']
                actions.append(cl.Action(name='mabselect_source', payload={'token': token},
                                         label=ref['source_id'] + ' · PDF page ' + str(page), icon='file-text'))
        if actions:
            body += '\n\n**Open a source to read the original passage**'
        await send_controls(state, revision, body, actions)
    except Exception:
        if current(state, revision):
            state['sources'] = {}
            await send_controls(state, revision, UNAVAILABLE)
    finally:
        state['busy'] = False


async def source(action):
    state = cl.user_session.get(KEY)
    token = action.payload.get('token') if isinstance(action.payload, dict) else None
    ref = state['sources'].get(token) if state and isinstance(token, str) else None
    if not ref:
        await cl.Message(content=STALE).send()
        return
    revision = state['revision']
    try:
        view = await asyncio.wait_for(asyncio.to_thread(lambda: service().source(*ref)), timeout=15)
        if not current(state, revision) or state['sources'].get(token) != ref:
            await cl.Message(content=STALE).send()
            return
        if view.get('status') != 'available' or view.get('passage') is None:
            await cl.Message(content='**Source held.** No quotation supplied under current authority. '
                             'Resubmit the request; earlier messages remain historical snapshots.').send()
            return
        p = view['passage']
        body = source_message(p) + '\n\n' + NOTICE
        await cl.Message(content=body, elements=[provenance_file(p['source_id'], view)]).send()
    except Exception:
        await cl.Message(content=UNAVAILABLE if current(state, revision)
                         and state['sources'].get(token) == ref else STALE).send()
