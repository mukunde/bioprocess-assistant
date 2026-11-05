"""Explicit, non-activated Chainlit workbench for the separate Sepharose candidate."""
import asyncio
from functools import lru_cache
import json
import os
from pathlib import Path
import uuid

import chainlit as cl
from chainlit.input_widget import Select, Switch

from demo.chainlit_mabselect import text, STATUS_LABELS
from serving.sepharose_candidate import Candidate, NOTICE, request

KEY = 'sepharose_candidate_ui'
PRODUCTS = {'Not specified': 'unknown', 'Protein A Sepharose': 'protein_a',
            'Protein G Sepharose': 'protein_g', 'MabSelect — outside this candidate': 'mabselect'}
CONTEXTS = {'Unknown — help me clarify': 'unknown',
            'Precipitated or denatured proteins': 'precipitated_proteins',
            'Hydrophobic proteins, lipoproteins or lipids': 'hydrophobic_deposits'}
DEFAULTS = {'product': next(iter(PRODUCTS)), 'context': next(iter(CONTEXTS)), 'guidance': True, 'pressure': False}
UNAVAILABLE = NOTICE + '\n\nCandidate unavailable. No quotation or procedure supplied. Retry manually; nothing was activated.'
STALE = 'Previous controls or result are stale. Use the latest candidate controls and submit again.'


def controls(value):
    if (not isinstance(value, dict) or set(value) != set(DEFAULTS)
            or type(value['product']) is not str or value['product'] not in PRODUCTS
            or type(value['context']) is not str or value['context'] not in CONTEXTS):
        raise ValueError('Invalid controls')
    return request({'product': PRODUCTS[value['product']], 'deposit_context': CONTEXTS[value['context']],
                    'guidance': value['guidance'], 'pressure': value['pressure']})


@lru_cache(maxsize=8)
def _candidate(root):
    return Candidate(root, preview=True)


def service():
    root = os.environ.get('SEPHAROSE_CANDIDATE_ROOT', '').strip()
    if os.environ.get('BIOPROCESS_MODE') != 'sepharose_candidate' or not root:
        raise ValueError('Explicit candidate configuration required')
    return _candidate(str(Path(root).resolve()))


def button(state):
    state['submit_token'] = uuid.uuid4().hex
    return cl.Action(name='sepharose_submit', label='Inspect candidate guidance', payload={'token': state['submit_token']})


def current(state, revision):
    return cl.user_session.get(KEY) is state and state['revision'] == revision


async def start():
    state = {'settings': dict(DEFAULTS), 'revision': 0, 'submit_token': None, 'sources': {}, 'busy': False}
    cl.user_session.set(KEY, state)
    await cl.ChatSettings([
        Select(id='product', label='Exact product', values=list(PRODUCTS), initial_index=0),
        Select(id='context', label='Context to explore — not a diagnosis', values=list(CONTEXTS), initial_index=0),
        Switch(id='guidance', label='Cleaning indication and conditional options', initial=True),
        Switch(id='pressure', label='Numerical maximum pressure', initial=False),
    ]).send()
    try:
        await asyncio.wait_for(asyncio.to_thread(lambda: service()._snapshot()), timeout=15)
    except Exception:
        await cl.Message(content=UNAVAILABLE, actions=[button(state)]).send()
        return
    await cl.Message(content=NOTICE+'\n\n**Rising backpressure · Protein A/G Sepharose**\n\n'
                     'Choose product and context in Settings, then inspect the staged candidate. '
                     'No cause is diagnosed. No live serving authority or approval is created. '
                     'Messages are snapshots; source clicks recheck this candidate. Free text is not interpreted.',
                     actions=[button(state)]).send()


async def settings_update(settings):
    state = cl.user_session.get(KEY)
    if not state:
        await cl.Message(content=UNAVAILABLE).send()
        return
    state['revision'] += 1
    state['sources'] = {}
    state['submit_token'] = None
    try:
        controls(settings)
    except (TypeError, ValueError):
        await cl.Message(content='Choose valid candidate controls and at least one question.').send()
        return
    state['settings'] = dict(settings)
    await cl.Message(content=NOTICE+'\n\nControls updated; earlier messages remain snapshots.', actions=[button(state)]).send()


async def free_text():
    await cl.Message(content=NOTICE+'\n\nUse Settings and Inspect candidate guidance. No free-text lookup or model call was made.').send()


def render(out, submitted):
    if out['status'] in ('unavailable', 'invalid_request'):
        return UNAVAILABLE
    lines = [NOTICE, '**Submitted product**: '+text(submitted['product']),
             '**Context explored**: '+text(submitted['context']),
             '**Request outcome**: '+text(STATUS_LABELS[out['status']])]
    for item in out['items']:
        label = 'Cleaning indication and conditional options' if item['question'] == 'guidance' else 'Numerical maximum pressure'
        lines.append('**'+label+': '+text(STATUS_LABELS[item['state']])+'**')
        if item['state'] == 'needs_clarification':
            targets = []
            if PRODUCTS[submitted['product']] == 'unknown':
                targets.append('the exact product')
            if CONTEXTS[submitted['context']] == 'unknown':
                targets.append('an available context to explore')
            lines.append('Please specify '+', '.join(targets)+' in Settings. '
                         'Retain supplied fields; a confirmed diagnosis is not required. No recipe has been selected.')
        if item.get('held_review_scopes') or item['state'] in ('quarantined', 'partial'):
            lines.append('Required support is held in this withdrawal simulation. No incomplete option is supplied; independent support may remain.')
            if item.get('held_review_scopes'):
                lines.append('Held review scopes: '+', '.join(text(s) for s in item['held_review_scopes']))
        if item['state'] == 'abstained':
            lines.append('This product is outside the Protein A/G Sepharose candidate. No cleaning procedure or substitute '
                         'is supplied; no incompatibility is inferred.' if item['question'] == 'guidance' else
                         'No numerical pressure limit is supplied by this candidate. Absence is limited to the reviewed excerpts, '
                         'not the whole manual. No recipe is transferred to a different product.')
    for bundle in out['bundles']:
        lines += ['**'+text(bundle['role'])+' · '+text(bundle['scope'])+'**', text(bundle['wording'])]
        passages = {p['source_id']: p for p in bundle['passages']}
        for pid in bundle['quote_ids']:
            lines.append(text(passages[pid]['quote'])+'\nSource: '+text(pid))
        lines.append('**Required sources**: '+', '.join(text(x) for x in bundle['required_source_ids']))
        lines += [text(x) for x in bundle['review']['reservations']]
    lines += [text(x) for x in out['limits']]
    return '\n\n'.join(lines)


async def submit(action):
    state = cl.user_session.get(KEY)
    if not state or not state['submit_token'] or action.payload != {'token': state['submit_token']}:
        await cl.Message(content=STALE).send()
        return
    if state['busy']:
        await cl.Message(content='A candidate request is already being checked.').send()
        return
    revision = state['revision']
    state.update(busy=True, sources={}, submit_token=None)
    try:
        submitted = dict(state['settings'])
        value = controls(submitted)
        out = await asyncio.wait_for(asyncio.to_thread(lambda: service().evaluate(value)), timeout=15)
        if not current(state, revision):
            await cl.Message(content=STALE).send()
            return
        actions = []
        for ref in out['citations']:
            token = uuid.uuid4().hex
            state['sources'][token] = (ref['release_id'], ref['source_id'])
            actions.append(cl.Action(name='sepharose_source', payload={'token': token},
                                     label=ref['source_id']+' · PDF page '+str(ref['pdf_page_1based'])))
        await cl.Message(content=render(out, submitted), actions=actions+[button(state)]).send()
    except Exception:
        state['sources'] = {}
        if current(state, revision):
            await cl.Message(content=UNAVAILABLE, actions=[button(state)]).send()
    finally:
        state['busy'] = False


async def source(action):
    state = cl.user_session.get(KEY)
    token = action.payload.get('token') if isinstance(action.payload, dict) else None
    ref = state['sources'].get(token) if state and type(token) is str else None
    if not ref:
        await cl.Message(content=STALE).send()
        return
    revision = state['revision']
    try:
        view = await asyncio.wait_for(asyncio.to_thread(lambda: service().source(*ref)), timeout=15)
        if not current(state, revision) or state['sources'].get(token) != ref:
            await cl.Message(content=STALE).send()
            return
        if view['status'] != 'available':
            await cl.Message(content=NOTICE+'\n\nSource held or candidate unavailable; no new quotation supplied.').send()
            return
        p = view['passage']
        await cl.Message(content=NOTICE+'\n\n**'+text(p['source_id'])+' · PDF page '+str(p['pdf_page_1based'])
                         +'**\n\n'+text(p['scope'])+'\n\n'+text(p['quote']),
                         elements=[cl.Text(name='Candidate source and scoped reviews',
                                           content=json.dumps(view, ensure_ascii=False, indent=2), language='json', display='inline')]).send()
    except Exception:
        await cl.Message(content=UNAVAILABLE if current(state, revision) and state['sources'].get(token) == ref else STALE).send()
