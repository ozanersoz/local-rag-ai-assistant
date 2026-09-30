# Project Writeup: Local RAG AI Assistant with Microsoft Foundry Local

## Objective

The assignment asks for a local question-answering assistant that uses the RAG pattern and Microsoft Foundry Local. This project builds that system as a Python command-line application focused on South American country knowledge. It answers questions from a local collection of Wikipedia-derived country notes by retrieving relevant evidence before generating or returning an answer.

## System Overview

The assistant has four main stages:

1. **Ingestion:** The app reads `.txt` and `.md` files from the `data/` folder, including South American country profiles, regional geography notes, capitals/languages notes, and source links.
2. **Chunking:** Each document is split into overlapping passages so retrieval can return focused context.
3. **Indexing:** Chunks are embedded with the Foundry Local embedding model and stored in SQLite with keyword weights and vector embeddings. The index records the embedding provider.
4. **Answering:** The user question is embedded, relevant chunks are retrieved by cosine similarity, and the answer is produced with citations.

## Foundry Local Role

Foundry Local is used for the required local AI steps. The app sends document chunks and user questions to `/v1/embeddings` using a Foundry Local embedding model, then sends retrieved context to `/v1/chat/completions` using the cached `phi-3.5-mini` chat model. A development-only local embedding fallback exists behind `--allow-local-embeddings`, but the worksheet-compliant workflow uses Foundry embeddings by default.

## Retrieval Design

The default retrieval mode is vector retrieval. The application converts both document chunks and user questions into normalized vectors, then ranks chunks by cosine similarity. The code also includes a keyword mode to show the difference between lexical matching and vector-style retrieval.

## Knowledge Base

The local knowledge base is expanded beyond basic country profiles. It includes countries, capitals, languages, geography, ecosystems, landmarks, history, trade, regional organizations, resources, and culture. Source pages are listed in `data/wikipedia_sources.md`.

## Local-First Design

The project keeps the document collection, index, retrieval logic, and optional model calls on the user's machine. This matches the assignment goal of an offline/local assistant and allows the knowledge base to be inspected and changed without sending queries to a cloud service.

## User Workflow

The user runs `python3 app.py --reindex` to build the local SQLite index. Then the user can ask a single question with `--ask` or open an interactive session. The answer includes retrieved evidence and source references, which makes the assistant's reasoning easier to inspect.

## Testing

The project includes an automated `unittest` suite that checks text processing, embeddings, indexing, retrieval, and answer generation. Manual evaluation questions are listed in `EVALUATION_QUESTIONS.md`.

## Limitations

Foundry Local must be installed separately on the machine that runs the Foundry demo. A future version could add a web UI and automated answer-quality scoring.
