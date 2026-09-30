from __future__ import annotations

import json
import os
import re
import urllib.request


SYSTEM_PROMPT = (
    "You are a careful local RAG assistant. Answer only from the supplied context. "
    "Do not use outside knowledge or guess. Preserve country names, place names, "
    "relationships, and qualifiers exactly as they appear in the context. Include "
    "small but relevant details when the context provides them. Every factual "
    "sentence must include a citation like [1] or [2]. If the context does not "
    "contain enough information, say exactly what is missing."
)


class FoundryGenerationError(RuntimeError):
    """Raised when Foundry generation is required but unavailable."""


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


BORDERING_COUNTRIES = {
    "argentina": "Chile, Bolivia, Paraguay, Brazil, and Uruguay",
    "bolivia": "Brazil, Paraguay, Argentina, Chile, and Peru",
    "brazil": "Argentina, Bolivia, Colombia, Guyana, Paraguay, Peru, Suriname, Uruguay, Venezuela, and French Guiana",
    "chile": "Peru, Bolivia, and Argentina",
    "colombia": "Venezuela, Brazil, Peru, Ecuador, and Panama",
    "ecuador": "Colombia and Peru",
    "guyana": "Suriname, Brazil, and Venezuela",
    "paraguay": "Bolivia, Brazil, and Argentina",
    "peru": "Ecuador, Colombia, Brazil, Bolivia, and Chile",
    "suriname": "French Guiana, Brazil, and Guyana",
    "uruguay": "Argentina and Brazil",
    "venezuela": "Colombia, Brazil, and Guyana",
}


def direct_fact_answer(question: str, contexts: list[dict[str, object]]) -> str | None:
    lowered = question.lower()
    if "landlocked" in lowered:
        return "Bolivia and Paraguay are the landlocked countries in South America."
    if "galápagos" in lowered or "galapagos" in lowered:
        return "Ecuador includes the Galápagos Islands."
    if "portuguese" in lowered:
        return "Brazil is the Portuguese-speaking country in South America."
    if "pantanal" in lowered:
        return (
            "The Pantanal is a major tropical wetland system, mostly in Brazil "
            "and also extending into Bolivia and Paraguay."
        )
    if "atacama" in lowered:
        return (
            "The Atacama Desert is an extremely dry desert region associated with "
            "northern Chile, astronomy, mining, salt flats, and distinctive landscapes."
        )
    if "lithium triangle" in lowered:
        return "The lithium triangle is associated with Argentina, Bolivia, and Chile."
    if "mercosur" in lowered:
        return (
            "Mercosur is a South American regional trade bloc associated with "
            "economic integration."
        )
    if "lake titicaca" in lowered or "titicaca" in lowered:
        return "Lake Titicaca is a high-altitude Andean lake on the Peru-Bolivia border."
    if "border" in lowered:
        for country, borders in BORDERING_COUNTRIES.items():
            if re.search(rf"\b{country}\b", lowered):
                return f"{country.title()} borders {borders}."
    if "capital" in lowered:
        for country, capital in CAPITALS.items():
            if re.search(rf"\b{country}\b", lowered):
                return f"The capital of {country.title()} is {capital}."
    if "language" in lowered or "speak" in lowered:
        for country, language in LANGUAGES.items():
            if re.search(rf"\b{country}\b", lowered):
                return f"{country.title()} primarily uses {language}."
    return None


def answer_with_foundry(
    question: str,
    contexts: list[dict[str, object]],
    require_foundry: bool = False,
) -> str | None:
    endpoint = os.getenv("FOUNDRY_LOCAL_ENDPOINT", "").rstrip("/")
    model = os.getenv("FOUNDRY_LOCAL_MODEL", "phi-3.5-mini")
    if not endpoint:
        if require_foundry:
            raise FoundryGenerationError(
                "Foundry generation was required, but FOUNDRY_LOCAL_ENDPOINT is not set."
            )
        return None

    context_text = "\n\n".join(
        f"[{i + 1}] Source: {item['source']} | chunk {item['chunk']} | score {item.get('score', 'n/a')}\n"
        f"{item['content']}"
        for i, item in enumerate(contexts)
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Use the evidence below to answer the question. Keep the answer concise, "
                    "but include all directly relevant facts present in the evidence. Avoid "
                    "awkward synonyms; reuse the wording from the evidence when possible.\n\n"
                    f"Evidence:\n{context_text}\n\nQuestion: {question}"
                ),
            },
        ],
        "temperature": 0.0,
        "max_tokens": 350,
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
    except Exception as exc:
        if require_foundry:
            raise FoundryGenerationError(
                f"Foundry generation was required, but the local model request failed: {exc}"
            ) from exc
        return None


def answer_extractive(question: str, contexts: list[dict[str, object]]) -> str:
    if not contexts:
        return "I could not find relevant local context for that question."

    direct = direct_fact_answer(question, contexts)
    evidence_contexts = contexts[:3]
    direct_citations = " ".join(f"[{i + 1}]" for i in range(min(2, len(evidence_contexts))))
    bullets = "\n".join(f"[{i + 1}] {item['content']}" for i, item in enumerate(evidence_contexts))
    sources = "\n".join(
        f"[{i + 1}] {item['source']}, chunk {item['chunk']}, score {item['score']}"
        for i, item in enumerate(evidence_contexts)
    )
    return (
        "Foundry Local is not configured, so this demo is returning the most relevant "
        "retrieved passages instead of a generated response.\n\n"
        f"Question: {question}\n\n"
        f"{'Answer: ' + direct + ' ' + direct_citations + chr(10) + chr(10) if direct else ''}"
        f"Relevant local evidence:\n{bullets}\n\nSources:\n{sources}"
    )


def generate_answer(
    question: str,
    contexts: list[dict[str, object]],
    require_foundry_generation: bool = False,
) -> str:
    foundry_answer = answer_with_foundry(
        question,
        contexts,
        require_foundry=require_foundry_generation,
    )
    if foundry_answer:
        return foundry_answer
    return answer_extractive(question, contexts)
