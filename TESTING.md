# Testing and Evaluation

The project includes an automated test suite using Python's built-in `unittest` module. No extra packages are required.

## Run Tests

PowerShell or Command Prompt:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Or double-click/run:

```bat
run_tests.bat
```

On macOS/Linux you can also use `python3` instead of `python`.

## What The Tests Cover

- Tokenization and document chunking
- Foundry embedding failure behavior when the endpoint is unavailable
- Mocked Foundry embedding indexing and retrieval
- SQLite indexing
- Vector retrieval
- Answer generation using retrieved evidence

## Manual Evaluation Questions

Use these questions after reindexing:

```powershell
python app.py --reindex
python app.py --ask "Which countries in South America are landlocked?"
python app.py --ask "What is the capital of Brazil?"
python app.py --ask "Which country includes the Galapagos Islands?"
python app.py --ask "What is the Pantanal?"
python app.py --ask "Which countries are associated with the lithium triangle?"
python app.py --ask "What is Mercosur?"
python app.py --ask "Why is the Amazon rainforest important?"
```

Expected behavior: the assistant should retrieve relevant local evidence from `data/`, answer from that evidence, and list source chunks. If Foundry Local is configured, the generated answer should still stay grounded in the retrieved context.
