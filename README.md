# Local RAG AI Assistant with Foundry Local

A local Retrieval-Augmented Generation (RAG) assistant for answering questions about South American countries. The knowledge base is built from Wikipedia-derived country and regional notes, split into chunks, embedded with Foundry Local, stored in SQLite, retrieved with cosine similarity, and passed to a local chat model for the final answer.

The primary workflow uses Foundry Local for:

- Document embeddings
- Question embeddings
- Final answer generation

A development-only local embedding fallback is available, but the default and recommended path is Foundry Local.

## Features

- South America knowledge base in `data/`
- Wikipedia-derived country and regional source notes
- Python text chunking with overlap
- Foundry Local embedding support through `/v1/embeddings`
- SQLite storage for chunks, keyword weights, and vectors
- Vector retrieval with cosine similarity
- Optional keyword retrieval mode for comparison
- Foundry Local chat generation through `/v1/chat/completions`
- Source-cited answers
- CLI question mode and interactive mode
- Automated unit tests

## Project Structure

```text
app.py                         Command-line interface
data/                          Local knowledge-base documents
rag_assistant/text.py          Tokenizing and chunking
rag_assistant/embeddings.py    Foundry embeddings and explicit dev fallback
rag_assistant/indexer.py       SQLite index builder
rag_assistant/retriever.py     Vector and keyword retrieval
rag_assistant/generator.py     Foundry Local or extractive answer generation
PROJECT_WRITEUP.md             Project explanation
PRESENTATION_OUTLINE.md        Final presentation notes
SUBMISSION_SUMMARY.md          Short submitter summary
TESTING.md                     Test and evaluation instructions
EVALUATION_QUESTIONS.md        Demo questions and expected answers
run_tests.bat                  Windows test runner
```

## Requirements

- Python 3.10 or newer
- Foundry Local installed for the recommended workflow
- A Foundry Local chat model, such as `phi-3.5-mini`
- A Foundry Local embedding model, such as `qwen3-embedding-0.6b`

On Windows, use `python` in the commands below. On macOS or Linux, use `python3` if that is how Python is installed on your system.

## Option 1: Run with Foundry Local Embeddings

This is the recommended path and matches the full RAG workflow.

Start Foundry Local:

```powershell
foundry server start
```

Keep that terminal open. Foundry will print a local endpoint. Copy that endpoint; do not assume a fixed port.

In a second terminal, load the chat and embedding models:

```powershell
foundry model load phi-3.5-mini
foundry model load qwen3-embedding-0.6b
```

If you need to check installed or cached model names:

```powershell
foundry model list
```

Set the Foundry environment variables. Replace `PORT_FROM_FOUNDRY` with the port printed by `foundry server start`.

PowerShell:

```powershell
$env:FOUNDRY_LOCAL_ENDPOINT = "http://127.0.0.1:PORT_FROM_FOUNDRY"
$env:FOUNDRY_LOCAL_MODEL = "phi-3.5-mini"
$env:FOUNDRY_LOCAL_EMBEDDING_MODEL = "qwen3-embedding-0.6b"
```

Command Prompt:

```bat
set FOUNDRY_LOCAL_ENDPOINT=http://127.0.0.1:PORT_FROM_FOUNDRY
set FOUNDRY_LOCAL_MODEL=phi-3.5-mini
set FOUNDRY_LOCAL_EMBEDDING_MODEL=qwen3-embedding-0.6b
```

macOS/Linux:

```bash
export FOUNDRY_LOCAL_ENDPOINT="http://127.0.0.1:PORT_FROM_FOUNDRY"
export FOUNDRY_LOCAL_MODEL="phi-3.5-mini"
export FOUNDRY_LOCAL_EMBEDDING_MODEL="qwen3-embedding-0.6b"
```

Check the Foundry connection:

```powershell
python diagnose_foundry.py
```

Build the SQLite index with Foundry embeddings:

```powershell
python app.py --reindex
```

Ask a question with Foundry answer generation required:

```powershell
python app.py --ask "Which countries in South America are landlocked?" --require-foundry-generation
```

Start interactive question mode:

```powershell
python app.py --require-foundry-generation
```

Type `quit` to exit interactive mode.

## Option 2: Run Without Foundry (Fallback Mode)

This mode is for development or quick local checks only. It uses deterministic local hash embeddings instead of Foundry Local embeddings, so it should not be used when Foundry embeddings are required.

Build the index with the local embedding fallback:

```powershell
python app.py --reindex --allow-local-embeddings
```

Ask a question with the fallback index:

```powershell
python app.py --ask "What is the capital of Brazil?" --allow-local-embeddings
```

Run interactive mode with fallback embeddings:

```powershell
python app.py --allow-local-embeddings
```

## Retrieval Modes

Vector retrieval is the default:

```powershell
python app.py --ask "Which country includes the Galapagos Islands?" --require-foundry-generation
```

Keyword retrieval is available for comparison:

```powershell
python app.py --retrieval keyword --ask "Which country includes the Galapagos Islands?" --require-foundry-generation
```

The app retrieves 6 chunks by default. To send more or fewer chunks to the answer step, use `--top-k`:

```powershell
python app.py --ask "Which countries border Peru?" --top-k 8 --require-foundry-generation
```

## Demo Questions

```powershell
python app.py --ask "Which countries in South America are landlocked?" --require-foundry-generation
python app.py --ask "What is the capital of Brazil?" --require-foundry-generation
python app.py --ask "Which country includes the Galapagos Islands?" --require-foundry-generation
python app.py --ask "What language does Suriname use?" --require-foundry-generation
python app.py --ask "Which country is the only Portuguese-speaking country in South America?" --require-foundry-generation
python app.py --ask "Which countries border Peru?" --require-foundry-generation
python app.py --ask "What is the Pantanal?" --require-foundry-generation
python app.py --ask "Which countries are associated with the lithium triangle?" --require-foundry-generation
python app.py --ask "What is Mercosur?" --require-foundry-generation
```

## Testing

Run the automated tests:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

On Windows, you can also run:

```bat
run_tests.bat
```

See `TESTING.md` and `EVALUATION_QUESTIONS.md` for the testing and evaluation plan.

## When to Reindex

Rebuild the SQLite index whenever files in `data/` change:

```powershell
python app.py --reindex
```

The generated index is stored at `rag_index.sqlite` and is intentionally ignored by Git.

## Troubleshooting

If `python` is not found, install Python 3 or try `python3`.

If `foundry` is not found, install Foundry Local and reopen your terminal.

If `python diagnose_foundry.py` says `FOUNDRY_LOCAL_ENDPOINT is not set`, start Foundry Local and set the endpoint to the value printed by `foundry server start`.

If answer generation fails, check:

```powershell
$env:FOUNDRY_LOCAL_ENDPOINT
$env:FOUNDRY_LOCAL_MODEL
foundry model list
```

If reindexing fails with a Foundry embedding error, check:

```powershell
$env:FOUNDRY_LOCAL_EMBEDDING_MODEL
foundry model list
python diagnose_foundry.py
```

Then rebuild the index:

```powershell
python app.py --reindex
```

## Clone and Run

```powershell
git clone git@github.com:ozanersoz/local-rag-ai-assistant.git
cd local-rag-ai-assistant
foundry server start
```

In another terminal, set the Foundry environment variables, then run:

```powershell
python diagnose_foundry.py
python app.py --reindex
python app.py --ask "Which countries in South America are landlocked?" --require-foundry-generation
```

Generated files such as `rag_index.sqlite`, `.env`, and `__pycache__/` are ignored by Git.
