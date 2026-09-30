# Foundry Local Setup Notes

This app is designed to work with a local OpenAI-compatible Foundry Local endpoint.

Foundry Local is not bundled into this project. Install Foundry Local separately on the Lenovo, then run the commands below in PowerShell or Command Prompt.

## Start Foundry Local

Default models for the Lenovo:

```powershell
foundry server start --port 39839 --idle-timeout 0
foundry model load phi3.5
foundry model load qwen3-embedding-0.6b
```

If your Lenovo has a different chat model, replace `phi3.5` with that model name. If your Lenovo has a different embedding model, replace `qwen3-embedding-0.6b` with that embedding model name.

If you are unsure of the exact cached model name, run:

```powershell
foundry model list
```

## Configure Environment Variables

PowerShell:

```powershell
$env:FOUNDRY_LOCAL_ENDPOINT = "http://127.0.0.1:39839"
$env:FOUNDRY_LOCAL_MODEL = "phi3.5"
$env:FOUNDRY_LOCAL_EMBEDDING_MODEL = "qwen3-embedding-0.6b"
```

Command Prompt:

```bat
set FOUNDRY_LOCAL_ENDPOINT=http://127.0.0.1:39839
set FOUNDRY_LOCAL_MODEL=phi3.5
set FOUNDRY_LOCAL_EMBEDDING_MODEL=qwen3-embedding-0.6b
```

## Run The App With Foundry Generation

```powershell
python app.py --reindex
python app.py --ask "Which countries in South America are landlocked?" --require-foundry-generation
```

The `--require-foundry-generation` flag makes the app fail instead of using fallback answer generation. Use it for the Lenovo demo so you know `phi3.5` is actually answering.

## Foundry Embeddings Are Required

The worksheet explicitly asks for the Foundry Local embedding model for both document embeddings and question embeddings. This project therefore uses Foundry embeddings by default. Reindexing fails if the Foundry embedding endpoint is not working.

Development-only fallback:

```powershell
python app.py --reindex --allow-local-embeddings
```

Do not use `--allow-local-embeddings` for the worksheet demo.

## Expected Endpoints

- `POST /v1/chat/completions`
- `POST /v1/embeddings`

The project includes a development-only fallback, but the worksheet-compliant path requires the Foundry embedding endpoint.
