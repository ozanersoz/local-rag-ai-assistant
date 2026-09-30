from __future__ import annotations

import math
import sqlite3
from collections import Counter
from pathlib import Path

from .embeddings import embed, serialize
from .text import chunk_text, tokenize


def connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS terms (
            chunk_id INTEGER NOT NULL,
            term TEXT NOT NULL,
            weight REAL NOT NULL,
            PRIMARY KEY (chunk_id, term),
            FOREIGN KEY (chunk_id) REFERENCES chunks(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS vectors (
            chunk_id INTEGER PRIMARY KEY,
            embedding TEXT NOT NULL,
            FOREIGN KEY (chunk_id) REFERENCES chunks(id)
        )
        """
    )
    return conn


def document_paths(data_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in data_dir.iterdir()
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}
    )


def build_index(data_dir: Path, db_path: Path) -> dict[str, int]:
    conn = connect(db_path)
    conn.execute("DELETE FROM vectors")
    conn.execute("DELETE FROM terms")
    conn.execute("DELETE FROM chunks")

    documents: list[tuple[str, int, str, Counter[str]]] = []
    for path in document_paths(data_dir):
        text = path.read_text(encoding="utf-8")
        for i, chunk in enumerate(chunk_text(text)):
            terms = Counter(tokenize(chunk))
            if terms:
                documents.append((path.name, i, chunk, terms))

    if not documents:
        raise SystemExit(f"No .txt or .md files found in {data_dir}")

    document_frequency: Counter[str] = Counter()
    for _, _, _, terms in documents:
        document_frequency.update(terms.keys())

    total_docs = len(documents)
    for source, chunk_index, content, terms in documents:
        cur = conn.execute(
            "INSERT INTO chunks (source, chunk_index, content) VALUES (?, ?, ?)",
            (source, chunk_index, content),
        )
        chunk_id = cur.lastrowid
        conn.execute(
            "INSERT INTO vectors (chunk_id, embedding) VALUES (?, ?)",
            (chunk_id, serialize(embed(content))),
        )
        max_tf = max(terms.values())
        for term, count in terms.items():
            tf = count / max_tf
            idf = math.log((1 + total_docs) / (1 + document_frequency[term])) + 1
            conn.execute(
                "INSERT INTO terms (chunk_id, term, weight) VALUES (?, ?, ?)",
                (chunk_id, term, tf * idf),
            )

    conn.commit()
    conn.close()
    return {"documents": len(document_paths(data_dir)), "chunks": total_docs}
