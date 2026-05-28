"""Chainlit UI for the Protein A troubleshooting agent."""
import asyncio

import chainlit as cl

from agent import run_agent


@cl.on_chat_start
async def start():
    await cl.Message(
        content=(
            "**Bioprocess Troubleshooting Assistant** — capture Protein A.\n\n"
            "Décris un symptôme observé sur ton étape de capture (par ex. "
            "*« mon rendement de capture a chuté »*) et je te propose les causes "
            "probables et les actions correctives, chacune sourcée sur un handbook."
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    reply = await asyncio.to_thread(run_agent, message.content)
    await cl.Message(content=reply).send()
