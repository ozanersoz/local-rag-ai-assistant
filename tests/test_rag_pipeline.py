from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from rag_assistant.embeddings import FoundryEmbeddingError, embed, local_embedding
from rag_assistant.generator import generate_answer
from rag_assistant.indexer import build_index
from rag_assistant.retriever import retrieve
from rag_assistant.text import chunk_text, tokenize


class TextProcessingTests(unittest.TestCase):
    def test_tokenize_lowercases_words(self) -> None:
        self.assertEqual(tokenize("Brazil, Brasília, and Peru!"), ["brazil", "brasília", "and", "peru"])

    def test_chunk_text_overlaps(self) -> None:
        text = " ".join(f"word{i}" for i in range(20))
        chunks = chunk_text(text, max_words=10, overlap=2)
        self.assertEqual(len(chunks), 3)
        self.assertIn("word8", chunks[1])


class EmbeddingTests(unittest.TestCase):
    def test_local_embedding_is_normalized(self) -> None:
        vector = local_embedding("Brazil and Argentina")
        magnitude = sum(value * value for value in vector) ** 0.5
        self.assertAlmostEqual(magnitude, 1.0)

    def test_requires_foundry_when_requested(self) -> None:
        old_endpoint = os.environ.pop("FOUNDRY_LOCAL_ENDPOINT", None)
        old_model = os.environ.pop("FOUNDRY_LOCAL_EMBEDDING_MODEL", None)
        try:
            with self.assertRaises(FoundryEmbeddingError):
                embed("Brazil", require_foundry=True)
        finally:
            if old_endpoint is not None:
                os.environ["FOUNDRY_LOCAL_ENDPOINT"] = old_endpoint
            if old_model is not None:
                os.environ["FOUNDRY_LOCAL_EMBEDDING_MODEL"] = old_model


class RagPipelineTests(unittest.TestCase):
    def test_index_retrieve_and_answer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "countries.md").write_text(
                "Brazil has Brasília as its capital. Ecuador includes the Galápagos Islands. "
                "Bolivia and Paraguay are landlocked countries in South America.",
                encoding="utf-8",
            )
            db_path = root / "rag.sqlite"

            stats = build_index(data_dir, db_path)
            self.assertEqual(stats["documents"], 1)
            self.assertGreaterEqual(stats["chunks"], 1)
            self.assertEqual(stats["embedding_provider"], "local-hash")

            results = retrieve(db_path, "What is the capital of Brazil?")
            self.assertTrue(results)
            self.assertIn("Brazil", results[0]["content"])

            answer = generate_answer("What is the capital of Brazil?", results)
            self.assertIn("Brasília", answer)


if __name__ == "__main__":
    unittest.main()

