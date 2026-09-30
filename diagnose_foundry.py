from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def post_json(url: str, payload: dict[str, object]) -> dict[str, object]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    endpoint = os.getenv("FOUNDRY_LOCAL_ENDPOINT", "http://127.0.0.1:39839").rstrip("/")
    chat_model = os.getenv("FOUNDRY_LOCAL_MODEL", "phi-3.5-mini")
    embedding_model = os.getenv("FOUNDRY_LOCAL_EMBEDDING_MODEL", "qwen3-embedding-0.6b")

    print(f"FOUNDRY_LOCAL_ENDPOINT={endpoint}")
    print(f"FOUNDRY_LOCAL_MODEL={chat_model}")
    print(f"FOUNDRY_LOCAL_EMBEDDING_MODEL={embedding_model}")

    try:
        data = post_json(
            f"{endpoint}/v1/embeddings",
            {"model": embedding_model, "input": "Brazil is in South America."},
        )
        vector = data["data"][0]["embedding"]
        print(f"Embedding OK: received vector with {len(vector)} dimensions")
    except urllib.error.HTTPError as exc:
        print(f"Embedding HTTP error {exc.code}: {exc.read().decode('utf-8', errors='replace')}")
        return 1
    except Exception as exc:
        print(f"Embedding request failed: {type(exc).__name__}: {exc}")
        return 1

    try:
        data = post_json(
            f"{endpoint}/v1/chat/completions",
            {
                "model": chat_model,
                "messages": [{"role": "user", "content": "Answer in one word: ready?"}],
                "temperature": 0.0,
            },
        )
        content = data["choices"][0]["message"]["content"]
        print(f"Chat OK: {content}")
    except urllib.error.HTTPError as exc:
        print(f"Chat HTTP error {exc.code}: {exc.read().decode('utf-8', errors='replace')}")
        return 1
    except Exception as exc:
        print(f"Chat request failed: {type(exc).__name__}: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

