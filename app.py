"""Chainlit UI for the Protein A troubleshooting agent."""
import asyncio
import logging
import os

import chainlit as cl
from chainlit.input_widget import Slider

from tools import DEFAULT_MIN_MATCH_SCORE, resolve_min_score

logger = logging.getLogger(__name__)
SERVICE_ERROR_MESSAGE = (
    "Le service est momentanément indisponible. "
    "Je ne peux pas fournir de réponse pour le moment. Vous pouvez réessayer plus tard."
)


def run_agent(*args, **kwargs):
    # Documentary sessions never import or initialize the model client.
    from agent import run_agent as graph_agent
    return graph_agent(*args, **kwargs)


def documentary_mode():
    # This is server configuration, never a browser-controlled route selector.
    # Unknown configurations fail closed instead of falling back to the agent.
    return os.environ.get("BIOPROCESS_MODE", "graph") != "graph"


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    """Gate the public demo behind a single shared credential.
    Credentials live in env vars (never in code); requires CHAINLIT_AUTH_SECRET
    to be set so Chainlit can sign the session JWT."""
    expected_user = os.environ.get("DEMO_USERNAME")
    expected_pass = os.environ.get("DEMO_PASSWORD")
    if expected_user and expected_pass and username == expected_user and password == expected_pass:
        return cl.User(identifier=username, metadata={"role": "demo"})
    return None


@cl.on_chat_start
async def start():
    if os.environ.get('BIOPROCESS_MODE') == 'sepharose_candidate':
        from demo import chainlit_sepharose
        await chainlit_sepharose.start()
        return
    if documentary_mode():
        from demo import chainlit_mabselect
        await chainlit_mabselect.start()
        return
    await cl.ChatSettings(
        [
            Slider(
                id="min_score",
                label="Seuil de match minimum (score BM25 Lucene)",
                initial=DEFAULT_MIN_MATCH_SCORE,
                min=0.0,
                max=6.0,
                step=0.25,
                description=(
                    "En dessous de ce seuil, le tool refuse le match et l'agent "
                    "applique la règle anti-hallucination « je n'ai pas cette "
                    "information dans ma base de connaissance ». 2.5 = équilibré "
                    "sur ce graphe (filtre les matches faibles type endotoxines→HCP "
                    "sans rejeter les questions in-scope reformulées librement)."
                ),
            )
        ]
    ).send()
    cl.user_session.set("min_score", DEFAULT_MIN_MATCH_SCORE)
    await cl.Message(
        content=(
            "**Bioprocess Troubleshooting Assistant** - capture Protein A.\n\n"
            "Décris un symptôme observé sur ton étape de capture (par ex. "
            "*« mon rendement de capture a chuté »*) et je te propose les causes "
            "probables et les actions correctives, chacune sourcée sur un handbook.\n\n"
            "*Le seuil de match du knowledge graph est ajustable via l'icône ⚙️ "
            "Settings dans la boîte de saisie.*"
        )
    ).send()


@cl.on_settings_update
async def on_settings_update(settings):
    if os.environ.get('BIOPROCESS_MODE') == 'sepharose_candidate':
        from demo import chainlit_sepharose
        await chainlit_sepharose.settings_update(settings)
        return
    if documentary_mode():
        from demo import chainlit_mabselect
        await chainlit_mabselect.settings_update(settings)
        return
    cl.user_session.set("min_score", resolve_min_score(settings.get("min_score")))


@cl.on_message
async def on_message(message: cl.Message):
    if os.environ.get('BIOPROCESS_MODE') == 'sepharose_candidate':
        from demo import chainlit_sepharose
        await chainlit_sepharose.free_text()
        return
    if documentary_mode():
        from demo import chainlit_mabselect
        await chainlit_mabselect.free_text()
        return
    metadata: dict = {}
    try:
        min_score = resolve_min_score(cl.user_session.get("min_score"))
        reply, match_score, threshold = await asyncio.to_thread(
            run_agent, message.content, min_score, answer_metadata=metadata
        )
    except Exception:
        # Keep operational failures distinct from a legitimate knowledge refusal.
        # Details belong in server logs, never in a user-visible Chainlit step.
        logger.exception("Troubleshooting request failed")
        await cl.Message(content=SERVICE_ERROR_MESSAGE).send()
        return

    # Footer with match score and current threshold for transparency.
    if metadata.get("status") == "error":
        footer = "\n\n---\n*La réponse n'a pas pu être validée. Vous pouvez réessayer.*"
    elif match_score is None:
        footer = f"\n\n---\n*Aucun score de recherche disponible · seuil actuel : {threshold:.2f}*"
    else:
        verdict = "au-dessus du seuil lexical" if match_score >= threshold else "sous le seuil lexical"
        outcome = "réponse sourcée" if metadata.get("status") == "answer" else "réponse refusée"
        footer = (
            f"\n\n---\n*Meilleur score retrouvé : {match_score:.2f}  ·  "
            f"seuil actuel : {threshold:.2f}  ·  {verdict}  ·  {outcome}*"
        )

    await cl.Message(content=reply + footer).send()


@cl.action_callback("mabselect_submit")
async def mabselect_submit(action):
    if documentary_mode() and os.environ.get('BIOPROCESS_MODE') != 'sepharose_candidate':
        from demo import chainlit_mabselect
        await chainlit_mabselect.submit(action)


@cl.action_callback("mabselect_source")
async def mabselect_source(action):
    if documentary_mode() and os.environ.get('BIOPROCESS_MODE') != 'sepharose_candidate':
        from demo import chainlit_mabselect
        await chainlit_mabselect.source(action)


@cl.action_callback('sepharose_submit')
async def sepharose_submit(action):
    if os.environ.get('BIOPROCESS_MODE') == 'sepharose_candidate':
        from demo import chainlit_sepharose
        await chainlit_sepharose.submit(action)


@cl.action_callback('sepharose_source')
async def sepharose_source(action):
    if os.environ.get('BIOPROCESS_MODE') == 'sepharose_candidate':
        from demo import chainlit_sepharose
        await chainlit_sepharose.source(action)
