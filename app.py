from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rag_assistant.embeddings import FoundryEmbeddingError
from rag_assistant.generator import FoundryGenerationError
from rag_assistant.generator import generate_answer
from rag_assistant.indexer import build_index
from rag_assistant.retriever import retrieve


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "rag_index.sqlite"


def main() -> None:
    parser = argparse.ArgumentParser(description="Local RAG Q&A assistant demo")
    parser.add_argument("--reindex", action="store_true", help="rebuild the local index")
    parser.add_argument("--ask", help="ask one question and exit")
    parser.add_argument(
        "--retrieval",
        choices=["vector", "keyword"],
        default="vector",
        help="retrieval strategy to use",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=6,
        help="number of retrieved chunks to send to the answer step",
    )
    parser.add_argument(
        "--allow-fallback",
        action="store_true",
        help="development only; allow local hash embeddings and extractive answers if Foundry is unavailable",
    )
    parser.add_argument(
        "--require-foundry-generation",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()

    try:
        if args.reindex:
            stats = build_index(
                DATA_DIR,
                DB_PATH,
                allow_local_embeddings=args.allow_fallback,
            )
            print(
                f"Indexed {stats['documents']} documents and {stats['chunks']} chunks "
                f"into {DB_PATH.name} using {stats['embedding_provider']} embeddings."
            )
            print("Reindex complete. Exiting because --reindex was provided.")
            return

        if not DB_PATH.exists():
            stats = build_index(
                DATA_DIR,
                DB_PATH,
                allow_local_embeddings=args.allow_fallback,
            )
            print(
                f"Indexed {stats['documents']} documents and {stats['chunks']} chunks "
                f"into {DB_PATH.name} using {stats['embedding_provider']} embeddings."
            )

        if args.ask:
            contexts = retrieve(
                DB_PATH,
                args.ask,
                limit=args.top_k,
                mode=args.retrieval,
                allow_local_embeddings=args.allow_fallback,
            )
            print(
                generate_answer(
                    args.ask,
                    contexts,
                    allow_fallback_generation=args.allow_fallback,
                )
            )
            return

        print(f"Local RAG assistant ({args.retrieval} retrieval). Type a question, or 'quit' to exit.")
        while True:
            question = input("\nQuestion> ").strip()
            if question.lower() in {"q", "quit", "exit"}:
                break
            contexts = retrieve(
                DB_PATH,
                question,
                limit=args.top_k,
                mode=args.retrieval,
                allow_local_embeddings=args.allow_fallback,
            )
            print(
                "\n"
                + generate_answer(
                    question,
                    contexts,
                    allow_fallback_generation=args.allow_fallback,
                )
            )
    except (FoundryEmbeddingError, FoundryGenerationError) as exc:
        print(f"Foundry configuration error: {exc}", file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
