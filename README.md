# Local RAG AI Assistant with Foundry Local

This project implements a local document Q&A assistant focused on **South American country knowledge**. It follows the Retrieval-Augmented Generation workflow: ingest Wikipedia-derived country notes, chunk them, create local embeddings, store them in SQLite, retrieve the most relevant chunks, and use the retrieved evidence to answer the user's question.

The app runs without cloud services. If Microsoft Foundry Local is available, it can call a local OpenAI-compatible endpoint for chat generation and embeddings. If Foundry Local is not running, it still demonstrates the complete local RAG retrieval pipeline with a dependency-free local embedding fallback.

## Features

- Local document ingestion from `.txt` and `.md` files in `data/`
- South America knowledge base built from Wikipedia country pages
- Overlapping document chunking
- SQLite storage for chunks, keyword weights, and vector embeddings
- Vector retrieval by cosine similarity
- Optional keyword retrieval mode for comparison
- Optional Foundry Local `/v1/chat/completions` generation
- Optional Foundry Local `/v1/embeddings` embeddings
- Source citations in answers
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
```

## How To Run

Open Terminal and go to the project folder:

```bash
cd /Users/Student/Desktop/local-rag
```

If you cloned this from GitHub onto a different computer, go to that cloned folder instead:

```bash
cd local-rag
```

### Option 1: Run Without Foundry Local

This mode works immediately with Python. It still performs local document ingestion, chunking, indexing, vector retrieval, and source-cited answers. It does not use LLM generation.

Build or refresh the local SQLite index:

```bash
python3 app.py --reindex
```

Ask a question:

```bash
python3 app.py --ask "Which countries in South America are landlocked?"
python3 app.py --ask "What is the capital of Brazil?"
```

Use interactive mode:

```bash
python3 app.py
```

Then type questions one at a time. Type `quit` to exit.

### Option 2: Run With Foundry Local

This mode uses Foundry Local for generated answers after retrieval. Foundry Local must already be installed so the `foundry` command is available.

Start Foundry Local, load the default model, and create `.foundry.env`:

```bash
./start_foundry_local.sh
```

Load the environment variables into the current terminal:

```bash
source .foundry.env
```

Rebuild the index and ask a question:

```bash
python3 app.py --reindex
python3 app.py --ask "Which countries in South America are landlocked?"
```

Or run the combined Foundry demo script:

```bash
./run_with_foundry.sh
```

Use a different Foundry model:

```bash
FOUNDRY_LOCAL_MODEL="your-model-name" ./start_foundry_local.sh
source .foundry.env
python3 app.py --ask "What is the capital of Chile?"
```

### Option 3: Compare Retrieval Modes

Default vector retrieval:

```bash
python3 app.py --ask "Which country includes the Galápagos Islands?"
```

Keyword retrieval:

```bash
python3 app.py --retrieval keyword --ask "Which country includes the Galápagos Islands?"
```

## Demo Questions

```bash
python3 app.py --ask "Which countries in South America are landlocked?"
python3 app.py --ask "What is the capital of Brazil?"
python3 app.py --ask "Which country includes the Galapagos Islands?"
python3 app.py --ask "What language does Suriname use?"
python3 app.py --ask "Which country is the only Portuguese-speaking country in South America?"
python3 app.py --ask "Which countries border Peru?"
```

## When To Reindex

Run this whenever you change files in `data/`:

```bash
python3 app.py --reindex
```

The app stores the rebuilt index in `rag_index.sqlite`.

## Foundry Local Details

The start script runs:

```bash
foundry server start --port 39839 --idle-timeout 0
foundry model load qwen3-0.6b
```

It writes:

```bash
.foundry.env
```

The Python app reads:

```bash
FOUNDRY_LOCAL_ENDPOINT
FOUNDRY_LOCAL_MODEL
FOUNDRY_LOCAL_EMBEDDING_MODEL
```

Manual Foundry environment setup:

```bash
export FOUNDRY_LOCAL_ENDPOINT="http://127.0.0.1:39839"
export FOUNDRY_LOCAL_MODEL="qwen3-0.6b"
export FOUNDRY_LOCAL_EMBEDDING_MODEL="your-embedding-model"
python3 app.py --reindex
python3 app.py --ask "Which country has Brasília as its capital?"
```

If the embedding model is not configured, the app uses its built-in local hashed embedding method so the project remains runnable on any Python 3 installation.

## Troubleshooting

If `python3` is not found, install Python 3 or try `python app.py` depending on your system.

If `./start_foundry_local.sh` says `foundry` was not found, install Foundry Local first and reopen Terminal.

If Foundry Local starts but the app still uses fallback mode, run:

```bash
source .foundry.env
python3 app.py --ask "What is the capital of Brazil?"
```

If you changed the knowledge base but answers still look old, run:

```bash
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

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
python3 app.py --reindex
./start_foundry_local.sh
source .foundry.env
python3 app.py --ask "Which countries in South America are landlocked?"
```

If `./start_foundry_local.sh` is not executable after cloning, run:

```bash
chmod +x start_foundry_local.sh run_with_foundry.sh run_demo.sh
```

Generated files such as `rag_index.sqlite`, `.foundry.env`, and `__pycache__/` are intentionally ignored by Git. Rebuild the SQLite index on each machine with:

```bash
python3 app.py --reindex
```
