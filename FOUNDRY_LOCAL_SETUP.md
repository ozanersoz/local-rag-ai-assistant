# Foundry Local Setup Notes

This app is designed to work with a local OpenAI-compatible Foundry Local endpoint.

Foundry Local is not bundled into this project. Install Foundry Local separately, then run the commands below in PowerShell or Command Prompt.

## Start Foundry Local

Default models:

```powershell
foundry server start
foundry model load phi-3.5-mini
foundry model load qwen3-embedding-0.6b
```

Use the endpoint printed by `foundry server start`. Do not assume a fixed port; Foundry Local may choose a different port.

If your machine has a different chat model, replace `phi-3.5-mini` with that model name. If your machine has a different embedding model, replace `qwen3-embedding-0.6b` with that embedding model name.

If you are unsure of the exact cached model name, run:

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

## Configure Environment Variables

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

## Run The App With Foundry Generation

First diagnose both Foundry endpoints:

```powershell
python diagnose_foundry.py
```

If that says `Embedding OK` and `Chat OK`, run:

```powershell
python app.py --reindex
python app.py --ask "Which countries in South America are landlocked?"
```

Foundry embeddings and Foundry answer generation are required by default. The app fails instead of using fallback behavior unless `--allow-fallback` is explicitly provided.

## Foundry Embeddings Are Required

The worksheet explicitly asks for the Foundry Local embedding model for both document embeddings and question embeddings. This project therefore uses Foundry embeddings by default. Reindexing fails if the Foundry embedding endpoint is not working.

Development-only embedding and output fallback:

```powershell
python app.py --reindex --allow-fallback
python app.py --ask "Which countries in South America are landlocked?" --allow-fallback
```

Do not use `--allow-fallback` for the worksheet demo.

## Expected Endpoints

- `POST /v1/chat/completions`
- `POST /v1/embeddings`

The project includes a development-only fallback, but the worksheet-compliant path requires the Foundry embedding endpoint and Foundry chat endpoint.
