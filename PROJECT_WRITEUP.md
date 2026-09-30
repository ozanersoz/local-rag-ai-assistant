# Project Writeup: Local RAG AI Assistant with Microsoft Foundry Local

## Objective

The assignment asks for a local question-answering assistant that uses the RAG pattern and Microsoft Foundry Local. This project builds that system as a Python command-line application focused on South American country knowledge. It answers questions from a local collection of Wikipedia-derived country notes by retrieving relevant evidence before generating or returning an answer.

## System Overview

The assistant has four main stages:

1. **Ingestion:** The app reads `.txt` and `.md` files from the `data/` folder, including South American country profiles, regional geography notes, capitals/languages notes, and source links.
2. **Chunking:** Each document is split into overlapping passages so retrieval can return focused context.
3. **Indexing:** Chunks are stored in SQLite with keyword weights and vector embeddings.
4. **Answering:** The user question is embedded, relevant chunks are retrieved by cosine similarity, and the answer is produced with citations.

## Foundry Local Role

Foundry Local is used as the optional local AI runtime. When a local OpenAI-compatible endpoint is available, the app can send the retrieved context to `/v1/chat/completions` and use a local model to generate the final answer. It can also use `/v1/embeddings` for embeddings if an embedding model is configured. When Foundry Local is not running, the application still works by using a built-in local embedding fallback and extractive answer mode.

## Retrieval Design

The default retrieval mode is vector retrieval. The application converts both document chunks and user questions into normalized vectors, then ranks chunks by cosine similarity. The code also includes a keyword mode to show the difference between lexical matching and vector-style retrieval.

## Local-First Design

The project keeps the document collection, index, retrieval logic, and optional model calls on the user's machine. This matches the assignment goal of an offline/local assistant and allows the knowledge base to be inspected and changed without sending queries to a cloud service.

## User Workflow

The user runs `python3 app.py --reindex` to build the local SQLite index. Then the user can ask a single question with `--ask` or open an interactive session. The answer includes retrieved evidence and source references, which makes the assistant's reasoning easier to inspect.

## Limitations

This submission does not include the formal testing phase because testing was intentionally excluded from the requested scope. A future version could add a web UI, a larger document collection, and a formal answer-quality test set.
