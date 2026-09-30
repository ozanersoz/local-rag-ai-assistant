from __future__ import annotations

import hashlib
import json
import math
import os
import urllib.error
import urllib.request

from .text import tokenize


EMBEDDING_DIMENSIONS = 256
DEFAULT_FOUNDRY_EMBEDDING_MODEL = "qwen3-embedding-0.6b"


class FoundryEmbeddingError(RuntimeError):
    """Raised when Foundry embeddings are required but unavailable."""


LAST_FOUNDRY_EMBEDDING_ERROR = ""


def normalize(vector: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude == 0:
        return vector
    return [value / magnitude for value in vector]


def local_embedding(text: str, dimensions: int = EMBEDDING_DIMENSIONS) -> list[float]:
    """Create a dependency-free hashed bag-of-words embedding for local demos."""
    vector = [0.0] * dimensions
    for token in tokenize(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign
    return normalize(vector)


def foundry_embedding(text: str) -> list[float] | None:
    global LAST_FOUNDRY_EMBEDDING_ERROR
    LAST_FOUNDRY_EMBEDDING_ERROR = ""
    endpoint = os.getenv("FOUNDRY_LOCAL_ENDPOINT", "").rstrip("/")
    model = os.getenv("FOUNDRY_LOCAL_EMBEDDING_MODEL", DEFAULT_FOUNDRY_EMBEDDING_MODEL)
    if not endpoint or not model:
        LAST_FOUNDRY_EMBEDDING_ERROR = (
            "FOUNDRY_LOCAL_ENDPOINT or FOUNDRY_LOCAL_EMBEDDING_MODEL is not set."
        )
        return None

    payload = {"model": model, "input": text}
    request = urllib.request.Request(
        f"{endpoint}/v1/embeddings",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
        return normalize([float(value) for value in data["data"][0]["embedding"]])
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        LAST_FOUNDRY_EMBEDDING_ERROR = (
            f"HTTP {exc.code} from {endpoint}/v1/embeddings using model {model}: {body}"
        )
        return None
    except Exception as exc:
        LAST_FOUNDRY_EMBEDDING_ERROR = (
            f"{type(exc).__name__} from {endpoint}/v1/embeddings using model {model}: {exc}"
        )
        return None


def embed_with_provider(text: str, allow_local_fallback: bool = False) -> tuple[list[float], str]:
    foundry_vector = foundry_embedding(text)
    if foundry_vector is not None:
        return foundry_vector, "foundry"
    if allow_local_fallback:
        return local_embedding(text), "local-hash"
    raise FoundryEmbeddingError(
        "Foundry embeddings are required by the worksheet, but the local "
        "Foundry embedding endpoint did not return an embedding. Check "
        "FOUNDRY_LOCAL_ENDPOINT and FOUNDRY_LOCAL_EMBEDDING_MODEL. "
        f"Last Foundry error: {LAST_FOUNDRY_EMBEDDING_ERROR or 'unknown error'}"
    )


def embed(text: str, allow_local_fallback: bool = False) -> list[float]:
    vector, _ = embed_with_provider(text, allow_local_fallback=allow_local_fallback)
    return vector


def serialize(vector: list[float]) -> str:
    return json.dumps(vector, separators=(",", ":"))


def deserialize(raw: str) -> list[float]:
    return [float(value) for value in json.loads(raw)]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))
