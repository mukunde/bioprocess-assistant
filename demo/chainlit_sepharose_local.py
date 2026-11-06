"""Separate, loopback-only guided Chainlit entry point for Sepharose serving."""
import asyncio
from hmac import compare_digest
import json
import os
from uuid import uuid4

import chainlit as cl
from chainlit.config import config
from chainlit.input_widget import Select, Switch

from demo.chainlit_sepharose import CONTEXTS, DEFAULTS, PRODUCTS, controls, render
from serving.sepharose_candidate import NOTICE as PREVIEW_NOTICE
from serving.sepharose_local import Authority, LocalSepharose, NOTICE

KEY = "sepharose_local"
UNAVAILABLE = "Sepharose documentary service is unavailable. No source or procedure supplied."
STALE = "This result is stale. Submit the request again for current evidence."


def service():
    if config.run.host != "127.0.0.1":
        raise ValueError("Sepharose serving requires a loopback listener")
    return LocalSepharose(Authority(os.environ["SEPHAROSE_LOCAL_AUTHORITY"],
                                    os.environ["SEPHAROSE_CANDIDATE_ROOT"]))


@cl.password_auth_callback
def authenticate(username, password):
    user = os.environ.get("DEMO_USERNAME")
    secret = os.environ.get("DEMO_PASSWORD")
    if user and secret and compare_digest(username.encode(), user.encode()) and compare_digest(password.encode(), secret.encode()):
        return cl.User(identifier=user)
    return None


def submit_button(state):
    state["submit"] = uuid4().hex
    return cl.Action(name="sepharose_local_submit", label="Find documentary guidance", payload={"token": state["submit"]})


def same_session(state, revision):
    return cl.user_session.get(KEY) is state and state["revision"] == revision


async def checked(call):
    return await asyncio.wait_for(asyncio.to_thread(call), timeout=15)


@cl.on_chat_start
async def start():
    state = {"settings": dict(DEFAULTS), "revision": 0, "sources": {}}
    cl.user_session.set(KEY, state)
    await cl.ChatSettings([
        Select(id="product", label="Exact product", values=list(PRODUCTS), initial_index=0),
        Select(id="context", label="Context to explore", values=list(CONTEXTS), initial_index=0),
        Switch(id="guidance", label="Cleaning indication and conditional options", initial=True),
        Switch(id="pressure", label="Numerical maximum pressure", initial=False),
    ]).send()
    await cl.Message(content="Select the exact product and context in Settings.",
                     actions=[submit_button(state)]).send()


@cl.on_settings_update
async def settings_update(settings):
    state = cl.user_session.get(KEY)
    if not state:
        return
    state.update(revision=state["revision"] + 1, sources={}, submit=None)
    try:
        controls(settings)
    except ValueError:
        await cl.Message(content="Choose valid controls and at least one question.").send()
        return
    state["settings"] = dict(settings)
    await cl.Message(content="Settings updated.", actions=[submit_button(state)]).send()


@cl.on_message
async def free_text(_):
    await cl.Message(content="Use the guided controls in Settings.").send()


@cl.action_callback("sepharose_local_submit")
async def submit(action):
    state = cl.user_session.get(KEY)
    if not state or not state["submit"] or action.payload != {"token": state["submit"]}:
        await cl.Message(content=STALE).send()
        return
    revision, submitted = state["revision"], dict(state["settings"])
    state.update(submit=None, sources={})
    try:
        local = service()
        result = await checked(lambda: local.evaluate(controls(submitted)))
        if result["status"] == "unavailable":
            raise ValueError("Authority unavailable")
        refs, actions = {}, []
        for ref in result["citations"]:
            token = uuid4().hex
            refs[token] = (ref["release_id"], ref["source_id"], ref["generation"])
            actions.append(cl.Action(name="sepharose_local_source", payload={"token": token},
                                     label=ref["source_id"] + " · PDF page " + str(ref["pdf_page_1based"])))
        content = render(result, submitted).replace(PREVIEW_NOTICE, NOTICE, 1).replace(
            "held in this withdrawal simulation", "held by the local withdrawal inventory")
        if not await checked(lambda: local.current(result["generation"])):
            raise ValueError("Authority changed")
        if same_session(state, revision):
            state["sources"] = refs
            await cl.Message(content=content, actions=actions + [submit_button(state)]).send()
    except Exception:
        if same_session(state, revision):
            await cl.Message(content=UNAVAILABLE, actions=[submit_button(state)]).send()


@cl.action_callback("sepharose_local_source")
async def source(action):
    state = cl.user_session.get(KEY)
    token = action.payload.get("token") if isinstance(action.payload, dict) else None
    ref = state["sources"].get(token) if state and type(token) is str else None
    if not ref:
        await cl.Message(content=STALE).send()
        return
    revision = state["revision"]
    try:
        local = service()
        view = await checked(lambda: local.source(*ref))
        if view["status"] != "available":
            raise ValueError("Source unavailable")
        # Inline provenance avoids a second, independently cached file endpoint.
        content = NOTICE + "\n\n**" + ref[1] + " · PDF page " + str(view["passage"]["pdf_page_1based"])
        content += "**\n\n" + view["passage"]["quote"] + "\n\n"
        content += "```json\n" + json.dumps(view, ensure_ascii=False, indent=2) + "\n```"
        if not await checked(lambda: local.current(ref[2])):
            raise ValueError("Authority changed")
        if same_session(state, revision) and state["sources"].get(token) == ref:
            await cl.Message(content=content).send()
    except Exception:
        if same_session(state, revision):
            await cl.Message(content=UNAVAILABLE).send()
