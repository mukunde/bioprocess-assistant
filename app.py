"""Chainlit UI for the Protein A troubleshooting agent."""
import asyncio

import chainlit as cl
from chainlit.input_widget import Slider

from agent import run_agent
from tools import DEFAULT_MIN_MATCH_SCORE


@cl.on_chat_start
async def start():
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
    cl.user_session.set("min_score", float(settings.get("min_score", DEFAULT_MIN_MATCH_SCORE)))


@cl.on_message
async def on_message(message: cl.Message):
    min_score = cl.user_session.get("min_score") or DEFAULT_MIN_MATCH_SCORE
    reply, match_score, threshold = await asyncio.to_thread(
        run_agent, message.content, min_score
    )

    # Footer with match score and current threshold for transparency.
    if match_score is None:
        footer = f"\n\n---\n*Aucun candidat dans le graphe · seuil actuel : {threshold:.2f}*"
    else:
        verdict = "✓ accepté" if match_score >= threshold else "✗ sous seuil"
        footer = (
            f"\n\n---\n*Score du match : {match_score:.2f}  ·  "
            f"seuil actuel : {threshold:.2f}  ·  {verdict}*"
        )

    await cl.Message(content=reply + footer).send()
