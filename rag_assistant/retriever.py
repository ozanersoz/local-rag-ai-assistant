from __future__ import annotations

import math
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

from .embeddings import FoundryEmbeddingError, cosine_similarity, deserialize, embed_with_provider
from .text import tokenize


DEFAULT_TOP_K = 6

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "does",
    "in",
    "is",
    "of",
    "the",
    "to",
    "what",
    "which",
    "who",
    "with",
}

COUNTRY_NAMES = {
    "argentina",
    "bolivia",
    "brazil",
    "chile",
    "colombia",
    "ecuador",
    "guyana",
    "paraguay",
    "peru",
    "suriname",
    "uruguay",
    "venezuela",
}


def normalize_term(term: str) -> str:
    if len(term) > 4 and term.endswith("ies"):
        return term[:-3] + "y"
    if len(term) > 3 and term.endswith("s"):
        return term[:-1]
    return term


def normalized_terms(text: str) -> set[str]:
    return {normalize_term(token) for token in tokenize(text) if token not in STOPWORDS}


def relation_boost(question_terms: set[str], content: str, content_terms: set[str]) -> float:
    boost = 0.0
    mentioned_countries = question_terms & COUNTRY_NAMES
    if mentioned_countries and "border" in question_terms and "border" in content_terms:
        boost += 0.2
        lowered_content = content.lower()
        for country in mentioned_countries:
            if f"{country} borders" in lowered_content or f"borders {country}" in lowered_content:
                boost += 0.5
                break
    return min(boost, 0.7)


def retrieve_keyword(db_path: Path, question: str, limit: int = DEFAULT_TOP_K) -> list[dict[str, object]]:
    query_terms = Counter(tokenize(question))
    if not query_terms:
        return []

    conn = sqlite3.connect(db_path)
    placeholders = ",".join("?" for _ in query_terms)
    rows = conn.execute(
        f"""
        SELECT t.chunk_id, t.term, t.weight, c.source, c.chunk_index, c.content
        FROM terms t
        JOIN chunks c ON c.id = t.chunk_id
        WHERE t.term IN ({placeholders})
        """,
        tuple(query_terms.keys()),
    ).fetchall()
    conn.close()

    scores: dict[int, float] = defaultdict(float)
    metadata: dict[int, tuple[str, int, str]] = {}
    query_norm = math.sqrt(sum(v * v for v in query_terms.values())) or 1

    for chunk_id, term, weight, source, chunk_index, content in rows:
        scores[chunk_id] += (query_terms[term] / query_norm) * weight
        metadata[chunk_id] = (source, chunk_index, content)

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:limit]
    return [
        {
            "score": round(score, 4),
            "source": metadata[chunk_id][0],
            "chunk": metadata[chunk_id][1],
            "content": metadata[chunk_id][2],
        }
        for chunk_id, score in ranked
    ]


def retrieve_vector(
    db_path: Path,
    question: str,
    limit: int = DEFAULT_TOP_K,
    allow_local_embeddings: bool = False,
) -> list[dict[str, object]]:
    question_vector, query_provider = embed_with_provider(
        question,
        allow_local_fallback=allow_local_embeddings,
    )
    question_terms = normalized_terms(question)
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        """
        SELECT c.id, c.source, c.chunk_index, c.content, v.embedding, v.provider
        FROM chunks c
        JOIN vectors v ON v.chunk_id = c.id
        """
    ).fetchall()
    conn.close()

    scored = []
    stored_providers = {row[5] for row in rows}
    if stored_providers and stored_providers != {query_provider}:
        expected = ", ".join(sorted(stored_providers))
        raise FoundryEmbeddingError(
            f"Question embedding provider is {query_provider}, but the index contains "
            f"{expected} embeddings. Rebuild the index with `python app.py --reindex` "
            "or use `--allow-fallback` consistently for development-only fallback mode."
        )

    for chunk_id, source, chunk_index, content, raw_vector, _provider in rows:
        vector_score = cosine_similarity(question_vector, deserialize(raw_vector))
        content_terms = normalized_terms(content)
        overlap_score = len(question_terms & content_terms) / max(1, len(question_terms))
        phrase_score = 1.0 if question.lower() in content.lower() else 0.0
        important_terms = {term for term in question_terms if len(term) >= 5 or term in COUNTRY_NAMES}
        rare_term_hits = sum(1 for term in important_terms if term in content_terms)
        rare_term_score = rare_term_hits / max(1, len(important_terms))
        score = (
            (0.45 * vector_score)
            + (0.25 * overlap_score)
            + (0.2 * max(phrase_score, rare_term_score))
            + relation_boost(question_terms, content, content_terms)
        )
        scored.append(
            {
                "id": chunk_id,
                "score": round(score, 4),
                "vector_score": round(vector_score, 4),
                "overlap_score": round(overlap_score, 4),
                "source": source,
                "chunk": chunk_index,
                "content": content,
                "retrieval": "vector",
            }
        )
    return sorted(scored, key=lambda item: item["score"], reverse=True)[:limit]


def retrieve(
    db_path: Path,
    question: str,
    limit: int = DEFAULT_TOP_K,
    mode: str = "vector",
    allow_local_embeddings: bool = False,
) -> list[dict[str, object]]:
    if mode == "keyword":
        results = retrieve_keyword(db_path, question, limit)
        for item in results:
            item["retrieval"] = "keyword"
        return results
    return retrieve_vector(
        db_path,
        question,
        limit,
        allow_local_embeddings=allow_local_embeddings,
    )
