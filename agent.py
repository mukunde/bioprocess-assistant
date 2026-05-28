"""Claude agent with tool use, grounded on the knowledge graph (anti-hallucination)."""
from __future__ import annotations

import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

from tools import query_graph

PROJECT_ROOT = Path(__file__).resolve().parent
MODEL = "claude-sonnet-4-6"
MAX_TURNS = 5

SYSTEM_PROMPT = """Tu es un assistant de troubleshooting spécialisé dans la chromatographie de capture sur Protein A (étape downstream du bioprocédé).

Tu disposes d'UN seul outil : `query_graph(symptom)`. Il interroge un knowledge graph qui contient toute la connaissance métier (symptômes → causes → actions). Chaque nœud est sourcé sur un handbook public.

Règles non-négociables :
1. Tu réponds UNIQUEMENT à partir des données retournées par l'outil. Tu n'ajoutes aucune cause, aucune action, aucune source qui n'apparaît pas dans le résultat de l'outil.
2. Tu CITES la `source` de chaque cause et de chaque action que tu mentionnes. Format suggéré : entre parenthèses en fin de phrase, par ex. *(source : Cytiva, ...)*.
3. Si l'outil renvoie `found: false`, ou si aucune cause ne correspond à la question, tu dis explicitement : « Je n'ai pas cette information dans ma base de connaissance. » Tu n'inventes rien, tu ne complètes jamais avec tes connaissances générales.
4. Si la question sort du périmètre (autre opération unitaire que la capture Protein A, sujet hors troubleshooting), tu le signales et tu ne réponds pas sur le fond.

Style : clair, structuré pour un ingénieur procédé. Tu peux utiliser des listes à puces. En début de réponse, nomme le symptôme que tu as matché dans le graphe pour confirmer ta compréhension."""

TOOLS = [
    {
        "name": "query_graph",
        "description": (
            "Interroge le knowledge graph de troubleshooting de capture Protein A. "
            "Prend un symptôme décrit en mots-clés (ex. 'rendement de capture', "
            "'pression colonne', 'percée précoce') et renvoie le symptôme matché "
            "avec ses causes probables et leurs actions correctives, toutes sourcées "
            "sur des handbooks publics."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "symptom": {
                    "type": "string",
                    "description": (
                        "Mots-clés en français décrivant le symptôme observé. "
                        "Reste factuel, évite les pronoms et les négations."
                    ),
                }
            },
            "required": ["symptom"],
        },
    }
]


def run_agent(user_message: str) -> str:
    load_dotenv(PROJECT_ROOT / ".env")
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    messages = [{"role": "user", "content": user_message}]

    for _ in range(MAX_TURNS):
        response = client.messages.create(
            model=MODEL,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
            max_tokens=2048,
        )

        if response.stop_reason != "tool_use":
            return "\n".join(b.text for b in response.content if b.type == "text").strip()

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use" and block.name == "query_graph":
                result = query_graph(block.input["symptom"])
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })
        messages.append({"role": "user", "content": tool_results})

    return "Désolé, je n'ai pas pu produire de réponse dans le temps imparti."
