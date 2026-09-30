# Local RAG AI Assistant with Foundry Local

This project implements a local document Q&A assistant focused on **South American country knowledge**. It follows the Retrieval-Augmented Generation workflow: ingest Wikipedia-derived country notes, chunk them, create Foundry Local embeddings, store them in SQLite, retrieve the most relevant chunks, and use the retrieved evidence to answer the user's question.

The worksheet requires Foundry Local for document embeddings, question embeddings, and final answer generation. The normal project path therefore requires a running Foundry Local server, the cached `phi3.5` chat model, and a Foundry Local embedding model such as `qwen3-embedding-0.6b`.

## Features

- Local document ingestion from `.txt` and `.md` files in `data/`
- South America knowledge base built from Wikipedia country pages
- Expanded sources covering countries, regions, ecosystems, history, languages, trade, and landmarks
- Overlapping document chunking
- SQLite storage for chunks, keyword weights, and vector embeddings
- Vector retrieval by cosine similarity
- Optional keyword retrieval mode for comparison
- Optional Foundry Local `/v1/chat/completions` generation
- Required Foundry generation mode with `--require-foundry-generation`
- Required Foundry Local `/v1/embeddings` document and question embeddings
- Optional development-only local embedding fallback with `--allow-local-embeddings`
- Source citations in answers
- Automated tests and evaluation questions
- Command-line interactive mode and one-question demo mode

## Project Structure

```text
app.py                         Command-line interface
data/                          Local knowledge-base documents
rag_assistant/text.py          Tokenizing and chunking
rag_assistant/embeddings.py    Required Foundry embeddings plus explicit dev fallback
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

Start Foundry Local and load the cached `phi3.5` chat model plus the Foundry embedding model:

```powershell
foundry server start --port 39839 --idle-timeout 0
foundry model load phi3.5
foundry model load qwen3-embedding-0.6b
```

If `phi3.5` is not the exact cached model name on the Lenovo, list the local Foundry models and use the cached Phi 3.5 name shown there:

```powershell
foundry model list
```

For embedding model names, try:

```powershell
foundry model list --type embedding
```

If your Foundry CLI does not support `--type embedding`, use:

```powershell
foundry model list
```

Set environment variables in PowerShell:

```powershell
$env:FOUNDRY_LOCAL_ENDPOINT = "http://127.0.0.1:39839"
$env:FOUNDRY_LOCAL_MODEL = "phi3.5"
$env:FOUNDRY_LOCAL_EMBEDDING_MODEL = "qwen3-embedding-0.6b"
```

If you use Command Prompt instead:

```bat
set FOUNDRY_LOCAL_ENDPOINT=http://127.0.0.1:39839
set FOUNDRY_LOCAL_MODEL=phi3.5
set FOUNDRY_LOCAL_EMBEDDING_MODEL=qwen3-embedding-0.6b
```

Rebuild the index and ask a question:

```powershell
python app.py --reindex
python app.py --ask "Which countries in South America are landlocked?" --require-foundry-generation
```

Before running the full app, you can directly test both Foundry endpoints:

```powershell
python diagnose_foundry.py
```

Use a different Foundry model:

```powershell
foundry model load your-model-name
$env:FOUNDRY_LOCAL_MODEL = "your-model-name"
python app.py --ask "What is the capital of Chile?"
```

The app uses Foundry Local embeddings by default. If the embedding endpoint is not working, `python app.py --reindex` fails with a Foundry configuration error instead of silently using fallback embeddings.

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
foundry model load phi3.5
foundry model load qwen3-embedding-0.6b
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
$env:FOUNDRY_LOCAL_MODEL = "phi3.5"
$env:FOUNDRY_LOCAL_EMBEDDING_MODEL = "qwen3-embedding-0.6b"
python app.py --reindex
python app.py --ask "Which country has Brasília as its capital?" --require-foundry-generation
```

For development only, you can pass `--allow-local-embeddings` to use the local hash fallback. Do not use that flag for the worksheet demo because the worksheet explicitly asks for Foundry Local embeddings.

## Troubleshooting

If `python3` is not found, install Python 3 or try `python app.py` depending on your system.

If `foundry` was not found, install Foundry Local first and reopen PowerShell.

If Foundry Local starts but strict generation fails, run:

```powershell
$env:FOUNDRY_LOCAL_ENDPOINT = "http://127.0.0.1:39839"
$env:FOUNDRY_LOCAL_MODEL = "phi3.5"
python app.py --ask "What is the capital of Brazil?" --require-foundry-generation
```

If this prints `Foundry configuration error`, check that the Foundry server is still running, `FOUNDRY_LOCAL_ENDPOINT` is set to `http://127.0.0.1:39839`, and `FOUNDRY_LOCAL_MODEL` matches the exact cached Phi 3.5 model name.

If reindexing fails with a Foundry embedding error, run:

```powershell
foundry model list
foundry model load qwen3-embedding-0.6b
$env:FOUNDRY_LOCAL_EMBEDDING_MODEL = "qwen3-embedding-0.6b"
python diagnose_foundry.py
python app.py --reindex
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
foundry model load phi3.5
foundry model load qwen3-embedding-0.6b
$env:FOUNDRY_LOCAL_ENDPOINT = "http://127.0.0.1:39839"
$env:FOUNDRY_LOCAL_MODEL = "phi3.5"
$env:FOUNDRY_LOCAL_EMBEDDING_MODEL = "qwen3-embedding-0.6b"
python app.py --reindex
python app.py --ask "Which countries in South America are landlocked?" --require-foundry-generation
```

Generated files such as `rag_index.sqlite`, `.env`, and `__pycache__/` are intentionally ignored by Git. Rebuild the SQLite index on each machine with:

```powershell
python3 app.py --reindex
```
