from __future__ import annotations

import re


TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")


def tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_RE.finditer(text)]


def chunk_text(text: str, max_words: int = 80, overlap: int = 15) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    step = max(1, max_words - overlap)
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + max_words]).strip()
        if chunk:
            chunks.append(chunk)
    return chunks
