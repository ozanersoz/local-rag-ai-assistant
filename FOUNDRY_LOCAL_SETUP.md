# Foundry Local Setup Notes

This app is designed to work with a local OpenAI-compatible Foundry Local endpoint.

Foundry Local is not bundled into this project. Install Foundry Local separately on the Lenovo, then run the commands below in PowerShell or Command Prompt.

## Start Foundry Local

Default model:

```powershell
foundry server start --port 39839 --idle-timeout 0
foundry model load qwen3-0.6b
```

If your Lenovo has a different model, replace `qwen3-0.6b` with that model name.

## Configure Environment Variables

PowerShell:

```powershell
$env:FOUNDRY_LOCAL_ENDPOINT = "http://127.0.0.1:39839"
$env:FOUNDRY_LOCAL_MODEL = "qwen3-0.6b"
```

Command Prompt:

```bat
set FOUNDRY_LOCAL_ENDPOINT=http://127.0.0.1:39839
set FOUNDRY_LOCAL_MODEL=qwen3-0.6b
```

## Run The App With Foundry Generation

```powershell
python app.py --reindex
python app.py --ask "Which countries in South America are landlocked?"
```

## Optional Foundry Embeddings

If you have a Foundry embedding model available, set it before reindexing.

PowerShell:

```powershell
$env:FOUNDRY_LOCAL_EMBEDDING_MODEL = "your-embedding-model"
python app.py --reindex --require-foundry-embeddings
python app.py --ask "What is Mercosur?" --require-foundry-embeddings
```

Command Prompt:

```bat
set FOUNDRY_LOCAL_EMBEDDING_MODEL=your-embedding-model
python app.py --reindex --require-foundry-embeddings
python app.py --ask "What is Mercosur?" --require-foundry-embeddings
```

Use strict mode when the worksheet requires the embedding step to come from Foundry Local rather than the fallback local-hash embedding method.

## Expected Endpoints

- `POST /v1/chat/completions`
- `POST /v1/embeddings`

The project keeps a built-in fallback so it can be graded or demonstrated even when Foundry Local has not been installed on the machine.

