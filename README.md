# Local RAG AI Assistant with Foundry Local

This project implements a local document Q&A assistant focused on **South American country knowledge**. It follows the Retrieval-Augmented Generation workflow: ingest Wikipedia-derived country notes, chunk them, create local embeddings, store them in SQLite, retrieve the most relevant chunks, and use the retrieved evidence to answer the user's question.

The app runs without cloud services. If Microsoft Foundry Local is available, it can call a local OpenAI-compatible endpoint for chat generation and embeddings. If Foundry Local is not running, it still demonstrates the complete local RAG retrieval pipeline with a dependency-free local embedding fallback.

## Features

- Local document ingestion from `.txt` and `.md` files in `data/`
- South America knowledge base built from Wikipedia country pages
- Expanded sources covering countries, regions, ecosystems, history, languages, trade, and landmarks
- Overlapping document chunking
- SQLite storage for chunks, keyword weights, and vector embeddings
- Vector retrieval by cosine similarity
- Optional keyword retrieval mode for comparison
- Optional Foundry Local `/v1/chat/completions` generation
- Optional Foundry Local `/v1/embeddings` embeddings
- Required Foundry embedding mode with `--require-foundry-embeddings`
- Source citations in answers
- Automated tests and evaluation questions
- Command-line interactive mode and one-question demo mode

## Project Structure

```text
app.py                         Command-line interface
data/                          Local knowledge-base documents
rag_assistant/text.py          Tokenizing and chunking
rag_assistant/embeddings.py    Local and optional Foundry embeddings
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

## How To Run

Open a terminal and go to the project folder.

macOS example:

```bash
cd /Users/Student/Desktop/local-rag
```

Windows/Lenovo example after cloning:

```powershell
cd local-rag-ai-assistant
```

### Option 1: Run Without Foundry Local

This mode works immediately with Python. It still performs local document ingestion, chunking, indexing, vector retrieval, and source-cited answers. It does not use LLM generation.

Build or refresh the local SQLite index:

```bash
python3 app.py --reindex
```

On Windows, use `python` if `python3` is not available:

```powershell
python app.py --reindex
```

Ask a question:

```powershell
python3 app.py --ask "Which countries in South America are landlocked?"
python3 app.py --ask "What is the capital of Brazil?"
```

Use interactive mode:

```powershell
python3 app.py
```

Then type questions one at a time. Type `quit` to exit.

### Option 2: Run With Foundry Local

This mode uses Foundry Local for generated answers after retrieval. Foundry Local must already be installed so the `foundry` command is available.

Start Foundry Local and load the default model:

```powershell
foundry server start --port 39839 --idle-timeout 0
foundry model load qwen3-0.6b
```

Set environment variables in PowerShell:

```powershell
$env:FOUNDRY_LOCAL_ENDPOINT = "http://127.0.0.1:39839"
$env:FOUNDRY_LOCAL_MODEL = "qwen3-0.6b"
```

If you use Command Prompt instead:

```bat
set FOUNDRY_LOCAL_ENDPOINT=http://127.0.0.1:39839
set FOUNDRY_LOCAL_MODEL=qwen3-0.6b
```

Rebuild the index and ask a question:

```powershell
python app.py --reindex
python app.py --ask "Which countries in South America are landlocked?"
```

Use a different Foundry model:

```powershell
foundry model load your-model-name
$env:FOUNDRY_LOCAL_MODEL = "your-model-name"
python app.py --ask "What is the capital of Chile?"
```

Require Foundry Local embeddings instead of the fallback embedding method:

```powershell
$env:FOUNDRY_LOCAL_EMBEDDING_MODEL = "your-embedding-model"
python app.py --reindex --require-foundry-embeddings
python app.py --ask "What is Mercosur?" --require-foundry-embeddings
```

### Option 3: Compare Retrieval Modes

Default vector retrieval:

```powershell
python3 app.py --ask "Which country includes the Galápagos Islands?"
```

Keyword retrieval:

```powershell
python3 app.py --retrieval keyword --ask "Which country includes the Galápagos Islands?"
```

## Demo Questions

```powershell
python3 app.py --ask "Which countries in South America are landlocked?"
python3 app.py --ask "What is the capital of Brazil?"
python3 app.py --ask "Which country includes the Galapagos Islands?"
python3 app.py --ask "What language does Suriname use?"
python3 app.py --ask "Which country is the only Portuguese-speaking country in South America?"
python3 app.py --ask "Which countries border Peru?"
python3 app.py --ask "What is the Pantanal?"
python3 app.py --ask "Which countries are associated with the lithium triangle?"
python3 app.py --ask "What is Mercosur?"
```

## Testing

Run the automated tests:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Or run the Windows helper:

```bat
run_tests.bat
```

See `TESTING.md` and `EVALUATION_QUESTIONS.md` for the testing/evaluation plan.

## When To Reindex

Run this whenever you change files in `data/`:

```powershell
python3 app.py --reindex
```

The app stores the rebuilt index in `rag_index.sqlite`.

## Foundry Local Details

The start script runs:

```bash
foundry server start --port 39839 --idle-timeout 0
foundry model load qwen3-0.6b
```

The Python app reads:

```powershell
FOUNDRY_LOCAL_ENDPOINT
FOUNDRY_LOCAL_MODEL
FOUNDRY_LOCAL_EMBEDDING_MODEL
```

PowerShell Foundry environment setup:

```powershell
$env:FOUNDRY_LOCAL_ENDPOINT = "http://127.0.0.1:39839"
$env:FOUNDRY_LOCAL_MODEL = "qwen3-0.6b"
$env:FOUNDRY_LOCAL_EMBEDDING_MODEL = "your-embedding-model"
python app.py --reindex
python app.py --ask "Which country has Brasília as its capital?"
```

If the embedding model is not configured, the app uses its built-in local hashed embedding method so the project remains runnable on any Python 3 installation.

If the worksheet/demo requires real Foundry embeddings, use `--require-foundry-embeddings`. In that mode, the app fails fast unless the local Foundry embedding endpoint is working.

## Troubleshooting

If `python3` is not found, install Python 3 or try `python app.py` depending on your system.

If `foundry` was not found, install Foundry Local first and reopen PowerShell.

If Foundry Local starts but the app still uses fallback mode, run:

```powershell
$env:FOUNDRY_LOCAL_ENDPOINT = "http://127.0.0.1:39839"
$env:FOUNDRY_LOCAL_MODEL = "qwen3-0.6b"
python app.py --ask "What is the capital of Brazil?"
```

If you changed the knowledge base but answers still look old, run:

```powershell
python3 app.py --reindex
```

## Move This Project Through GitHub

On this Mac, from the project folder:

```bash
cd /Users/Student/Desktop/local-rag
git init
git add .
git commit -m "Initial local RAG assistant"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git push -u origin main
```

On the Lenovo laptop with Foundry Local:

```powershell
git clone git@github.com:ozanersoz/local-rag-ai-assistant.git
cd local-rag-ai-assistant
foundry server start --port 39839 --idle-timeout 0
foundry model load qwen3-0.6b
$env:FOUNDRY_LOCAL_ENDPOINT = "http://127.0.0.1:39839"
$env:FOUNDRY_LOCAL_MODEL = "qwen3-0.6b"
python app.py --reindex
python app.py --ask "Which countries in South America are landlocked?"
```

Generated files such as `rag_index.sqlite`, `.env`, and `__pycache__/` are intentionally ignored by Git. Rebuild the SQLite index on each machine with:

```powershell
python3 app.py --reindex
```
