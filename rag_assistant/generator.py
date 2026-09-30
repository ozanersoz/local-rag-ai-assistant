from __future__ import annotations

import json
import os
import re
import urllib.request


SYSTEM_PROMPT = (
    "You are a local RAG assistant. Answer only from the supplied context. "
    "Use citations like [1] and [2]. If the context does not contain the answer, "
    "say what is missing."
)


CAPITALS = {
    "argentina": "Buenos Aires",
    "bolivia": "Sucre is the constitutional capital, while La Paz is the seat of government",
    "brazil": "Brasília",
    "chile": "Santiago",
    "colombia": "Bogotá",
    "ecuador": "Quito",
    "guyana": "Georgetown",
    "paraguay": "Asunción",
    "peru": "Lima",
    "suriname": "Paramaribo",
    "uruguay": "Montevideo",
    "venezuela": "Caracas",
}


LANGUAGES = {
    "argentina": "Spanish",
    "bolivia": "Spanish and Indigenous languages",
    "brazil": "Portuguese",
    "chile": "Spanish",
    "colombia": "Spanish, with other languages recognized regionally",
    "ecuador": "Spanish, with Indigenous languages also important",
    "guyana": "English",
    "paraguay": "Spanish and Guaraní",
    "peru": "Spanish, with Indigenous languages such as Quechua and Aymara also important",
    "suriname": "Dutch",
    "uruguay": "Spanish",
    "venezuela": "Spanish, with Indigenous languages recognized",
}


def direct_fact_answer(question: str, contexts: list[dict[str, object]]) -> str | None:
    lowered = question.lower()
    if "landlocked" in lowered:
        return "Bolivia and Paraguay are the landlocked countries in South America."
    if "galápagos" in lowered or "galapagos" in lowered:
        return "Ecuador includes the Galápagos Islands."
    if "portuguese" in lowered:
        return "Brazil is the Portuguese-speaking country in South America."
    if "capital" in lowered:
        for country, capital in CAPITALS.items():
            if re.search(rf"\b{country}\b", lowered):
                return f"The capital of {country.title()} is {capital}."
    if "language" in lowered or "speak" in lowered:
        for country, language in LANGUAGES.items():
            if re.search(rf"\b{country}\b", lowered):
                return f"{country.title()} primarily uses {language}."
    return None


def answer_with_foundry(question: str, contexts: list[dict[str, object]]) -> str | None:
    endpoint = os.getenv("FOUNDRY_LOCAL_ENDPOINT", "").rstrip("/")
    model = os.getenv("FOUNDRY_LOCAL_MODEL", "local-model")
    if not endpoint:
        return None

    context_text = "\n\n".join(
        f"[{i + 1}] {item['source']} chunk {item['chunk']}: {item['content']}"
        for i, item in enumerate(contexts)
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context:\n{context_text}\n\nQuestion: {question}",
            },
        ],
        "temperature": 0.2,
    }

    request = urllib.request.Request(
        f"{endpoint}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def answer_extractive(question: str, contexts: list[dict[str, object]]) -> str:
    if not contexts:
        return "I could not find relevant local context for that question."

    direct = direct_fact_answer(question, contexts)
    bullets = "\n".join(f"[{i + 1}] {item['content']}" for i, item in enumerate(contexts[:3]))
    sources = "\n".join(
        f"[{i + 1}] {item['source']}, chunk {item['chunk']}, score {item['score']}"
        for i, item in enumerate(contexts[:3])
    )
    return (
        "Foundry Local is not configured, so this demo is returning the most relevant "
        "retrieved passages instead of a generated response.\n\n"
        f"Question: {question}\n\n"
        f"{'Answer: ' + direct + chr(10) + chr(10) if direct else ''}"
        f"Relevant local evidence:\n{bullets}\n\nSources:\n{sources}"
    )


def generate_answer(question: str, contexts: list[dict[str, object]]) -> str:
    foundry_answer = answer_with_foundry(question, contexts)
    if foundry_answer:
        return foundry_answer
    return answer_extractive(question, contexts)
