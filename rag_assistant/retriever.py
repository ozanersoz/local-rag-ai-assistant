from __future__ import annotations

import math
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

from .embeddings import cosine_similarity, deserialize, embed
from .text import tokenize


def retrieve_keyword(db_path: Path, question: str, limit: int = 4) -> list[dict[str, object]]:
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


def retrieve_vector(db_path: Path, question: str, limit: int = 4) -> list[dict[str, object]]:
    question_vector = embed(question)
    question_terms = set(tokenize(question))
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        """
        SELECT c.id, c.source, c.chunk_index, c.content, v.embedding
        FROM chunks c
        JOIN vectors v ON v.chunk_id = c.id
        """
    ).fetchall()
    conn.close()

    scored = []
    for chunk_id, source, chunk_index, content, raw_vector in rows:
        vector_score = cosine_similarity(question_vector, deserialize(raw_vector))
        content_terms = set(tokenize(content))
        overlap_score = len(question_terms & content_terms) / max(1, len(question_terms))
        score = (0.7 * vector_score) + (0.3 * overlap_score)
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


def retrieve(db_path: Path, question: str, limit: int = 4, mode: str = "vector") -> list[dict[str, object]]:
    if mode == "keyword":
        results = retrieve_keyword(db_path, question, limit)
        for item in results:
            item["retrieval"] = "keyword"
        return results
    return retrieve_vector(db_path, question, limit)
