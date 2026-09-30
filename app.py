from __future__ import annotations

import argparse
from pathlib import Path

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
    args = parser.parse_args()

    if args.reindex or not DB_PATH.exists():
        stats = build_index(DATA_DIR, DB_PATH)
        print(
            f"Indexed {stats['documents']} documents and {stats['chunks']} chunks "
            f"into {DB_PATH.name}."
        )

    if args.ask:
        contexts = retrieve(DB_PATH, args.ask, mode=args.retrieval)
        print(generate_answer(args.ask, contexts))
        return

    print(f"Local RAG assistant ({args.retrieval} retrieval). Type a question, or 'quit' to exit.")
    while True:
        question = input("\nQuestion> ").strip()
        if question.lower() in {"q", "quit", "exit"}:
            break
        contexts = retrieve(DB_PATH, question, mode=args.retrieval)
        print("\n" + generate_answer(question, contexts))


if __name__ == "__main__":
    main()
