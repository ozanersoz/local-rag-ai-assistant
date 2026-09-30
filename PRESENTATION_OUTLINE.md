# Presentation Outline

## Slide 1: Project Title

Local RAG AI Assistant for South American Countries with Microsoft Foundry Local.

## Slide 2: Problem

Students and users often need reliable answers about countries, capitals, borders, languages, and regions. A normal chatbot may hallucinate or fail to show where the answer came from.

## Slide 3: Solution

This assistant uses Retrieval-Augmented Generation. It searches local documents first, then answers from the retrieved evidence.

## Slide 4: Architecture

Wikipedia-derived country notes go into the `data/` folder. The app chunks them, embeds each chunk, stores everything in SQLite, retrieves the closest chunks for a question, then sends the context to Foundry Local or returns the cited evidence directly.

## Slide 5: Foundry Local

Foundry Local provides the optional on-device model runtime. The project can call local OpenAI-compatible chat and embedding endpoints, keeping data on the machine.

## Slide 6: Demo

Run:

```bash
python3 app.py --reindex
python3 app.py --ask "Which countries in South America are landlocked?"
```

Show that the answer includes local evidence and source references.

## Slide 7: What Was Built

The project includes ingestion, chunking, local indexing, vector retrieval, optional Foundry Local generation, citations, documentation, and a command-line interface.

## Slide 8: Future Work

Add a web interface, connect a specific Foundry Local model, expand the document collection, and add formal evaluation after the testing phase is in scope.
