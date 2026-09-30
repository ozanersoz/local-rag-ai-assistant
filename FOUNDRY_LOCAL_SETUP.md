# Foundry Local Setup Notes

This app is designed to work with a local OpenAI-compatible Foundry Local endpoint.

Foundry Local was not bundled into this project folder. Install Foundry Local separately, then use the scripts in this project to start the local server and point the app at it.

## Quick Start Script

```bash
./start_foundry_local.sh
source .foundry.env
python3 app.py --reindex
python3 app.py --ask "Which countries in South America are landlocked?"
```

The script uses the current Foundry Local CLI flow:

```bash
foundry server start --port 39839 --idle-timeout 0
foundry model load qwen3-0.6b
```

You can use a different model:

```bash
FOUNDRY_LOCAL_MODEL=your-model-name ./start_foundry_local.sh
```

## Environment Variables

```bash
export FOUNDRY_LOCAL_ENDPOINT="http://localhost:PORT"
export FOUNDRY_LOCAL_MODEL="your-chat-model"
```

Optional embedding model:

```bash
export FOUNDRY_LOCAL_EMBEDDING_MODEL="your-embedding-model"
python3 app.py --reindex
```

Strict Foundry embedding mode:

```bash
export FOUNDRY_LOCAL_EMBEDDING_MODEL="your-embedding-model"
python3 app.py --reindex --require-foundry-embeddings
python3 app.py --ask "What is Mercosur?" --require-foundry-embeddings
```

Use strict mode when the worksheet requires the embedding step to come from Foundry Local rather than the fallback local-hash embedding method.

## Expected Endpoints

- `POST /v1/chat/completions`
- `POST /v1/embeddings`

The project keeps a built-in fallback so it can be graded or demonstrated even when Foundry Local has not been installed on the machine.

## Files

- `start_foundry_local.sh` starts the Foundry Local daemon on a fixed port and loads a model.
- `run_with_foundry.sh` starts Foundry Local if needed, sources `.foundry.env`, reindexes, and runs a demo question.
- `.env.example` shows the variables the Python app reads.
