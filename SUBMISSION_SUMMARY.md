# Submission Summary

## Project

Local RAG AI Assistant for South American country knowledge with Microsoft Foundry Local support.

## Completed Deliverables

- Runnable Python assistant
- Local document ingestion
- Wikipedia-derived South American country knowledge base
- Expanded South America sources covering geography, ecosystems, landmarks, history, trade, languages, and organizations
- Chunking pipeline
- SQLite-backed local knowledge index
- Vector embeddings and cosine-similarity retrieval
- Optional keyword retrieval mode
- Optional Foundry Local chat-completions integration
- Optional Foundry Local embeddings integration
- Foundry Local startup script
- Foundry Local demo run script
- Required Foundry embedding mode with `--require-foundry-embeddings`
- Source-cited answers
- README with run instructions
- Project writeup
- Presentation outline
- Automated tests
- Evaluation question set

## Runtime Note

Foundry Local itself must be installed separately. This project includes `start_foundry_local.sh` and `run_with_foundry.sh` to start the local server, load a model, configure environment variables, and run the app once Foundry Local is installed.

## Quick Demo Command

```bash
python3 app.py --reindex
python3 app.py --ask "Which countries in South America are landlocked?"
```

## Demo Script

This project implements the local RAG pipeline from the task sheet using a South American country knowledge base. It loads Wikipedia-derived local documents, chunks them, stores them in SQLite, creates vector embeddings, retrieves relevant country context for a question, and answers using that local evidence. When Foundry Local is configured, the same retrieved evidence is sent to a local model endpoint for generation. Without Foundry Local, the app still runs fully locally and shows the retrieved evidence with citations.

## Test Command

```bash
./run_tests.sh
```
