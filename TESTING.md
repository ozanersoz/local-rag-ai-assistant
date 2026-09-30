# Testing and Evaluation

The project includes an automated test suite using Python's built-in `unittest` module. No extra packages are required.

## Run Tests

```bash
./run_tests.sh
```

Or:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

## What The Tests Cover

- Tokenization and document chunking
- Local embedding vector normalization
- Failure behavior when Foundry embeddings are required but unavailable
- SQLite indexing
- Vector retrieval
- Answer generation using retrieved evidence

## Manual Evaluation Questions

Use these questions after reindexing:

```bash
python3 app.py --reindex
python3 app.py --ask "Which countries in South America are landlocked?"
python3 app.py --ask "What is the capital of Brazil?"
python3 app.py --ask "Which country includes the Galapagos Islands?"
python3 app.py --ask "What is the Pantanal?"
python3 app.py --ask "Which countries are associated with the lithium triangle?"
python3 app.py --ask "What is Mercosur?"
python3 app.py --ask "Why is the Amazon rainforest important?"
```

Expected behavior: the assistant should retrieve relevant local evidence from `data/`, answer from that evidence, and list source chunks. If Foundry Local is configured, the generated answer should still stay grounded in the retrieved context.

