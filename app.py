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
        "--allow-local-embeddings",
        action="store_true",
        help="development fallback only; use local hash embeddings if Foundry embeddings are unavailable",
    )
    parser.add_argument(
        "--require-foundry-generation",
        action="store_true",
        help="fail unless Foundry Local generates the final answer",
    )
    args = parser.parse_args()

    try:
        if args.reindex or not DB_PATH.exists():
            stats = build_index(
                DATA_DIR,
                DB_PATH,
                allow_local_embeddings=args.allow_local_embeddings,
            )
            print(
                f"Indexed {stats['documents']} documents and {stats['chunks']} chunks "
                f"into {DB_PATH.name} using {stats['embedding_provider']} embeddings."
            )
            if args.reindex and not args.ask:
                return

        if args.ask:
            contexts = retrieve(
                DB_PATH,
                args.ask,
                mode=args.retrieval,
                allow_local_embeddings=args.allow_local_embeddings,
            )
            print(
                generate_answer(
                    args.ask,
                    contexts,
                    require_foundry_generation=args.require_foundry_generation,
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
                mode=args.retrieval,
                allow_local_embeddings=args.allow_local_embeddings,
            )
            print(
                "\n"
                + generate_answer(
                    question,
                    contexts,
                    require_foundry_generation=args.require_foundry_generation,
                )
            )
    except (FoundryEmbeddingError, FoundryGenerationError) as exc:
        print(f"Foundry configuration error: {exc}", file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
