from __future__ import annotations

import json
import os
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from rag_assistant.embeddings import FoundryEmbeddingError, embed, local_embedding
from rag_assistant.generator import FoundryGenerationError, generate_answer
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
                embed("Brazil")
        finally:
            if old_endpoint is not None:
                os.environ["FOUNDRY_LOCAL_ENDPOINT"] = old_endpoint
            if old_model is not None:
                os.environ["FOUNDRY_LOCAL_EMBEDDING_MODEL"] = old_model


class FakeEmbeddingResponse:
    def __enter__(self) -> "FakeEmbeddingResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return b'{"data":[{"embedding":[1.0,0.0,0.0,0.0]}]}'


class FakeChatResponse:
    def __enter__(self) -> "FakeChatResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return b'{"choices":[{"message":{"content":"Suriname uses Dutch as the official language [1]."}}]}'


class RagPipelineTests(unittest.TestCase):
    @patch("urllib.request.urlopen", return_value=FakeEmbeddingResponse())
    def test_index_retrieve_and_answer_with_foundry_embeddings(self, _urlopen) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(
                os.environ,
                {
                    "FOUNDRY_LOCAL_ENDPOINT": "http://foundry.test",
                    "FOUNDRY_LOCAL_EMBEDDING_MODEL": "qwen3-embedding-0.6b",
                },
            ):
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
                self.assertEqual(stats["embedding_provider"], "foundry")

                results = retrieve(db_path, "What is the capital of Brazil?")
                self.assertTrue(results)
                self.assertIn("Brazil", results[0]["content"])

                answer = generate_answer("What is the capital of Brazil?", results)
                self.assertIn("Brasília", answer)

    @patch("urllib.request.urlopen", return_value=FakeChatResponse())
    def test_foundry_generation_prompt_requires_grounded_citations(self, urlopen) -> None:
        with patch.dict(
            os.environ,
            {
                "FOUNDRY_LOCAL_ENDPOINT": "http://foundry.test",
                "FOUNDRY_LOCAL_MODEL": "phi-3.5-mini",
            },
        ):
            answer = generate_answer(
                "What language does Suriname use?",
                [
                    {
                        "source": "languages_capitals_quick_reference.md",
                        "chunk": 0,
                        "score": 0.98,
                        "content": "Suriname: capital Paramaribo; Dutch is the official language.",
                    }
                ],
                require_foundry_generation=True,
            )

        self.assertIn("Dutch", answer)
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["temperature"], 0.0)
        self.assertEqual(payload["model"], "phi-3.5-mini")
        combined_prompt = "\n".join(message["content"] for message in payload["messages"])
        self.assertIn("Every factual sentence must include a citation", combined_prompt)
        self.assertIn("Dutch is the official language", combined_prompt)
        self.assertIn("Source: languages_capitals_quick_reference.md", combined_prompt)

    def test_local_embedding_fallback_is_explicit_opt_in(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "countries.md").write_text("Brazil has Brasília as its capital.", encoding="utf-8")
            db_path = root / "rag.sqlite"

            stats = build_index(data_dir, db_path, allow_local_embeddings=True)
            self.assertEqual(stats["embedding_provider"], "local-hash")

    def test_border_question_prefers_exact_country_profile_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "data"
            data_dir.mkdir()
            (data_dir / "history.md").write_text(
                "Modern countries of South America emerged after independence. "
                "Later nation-building involved border conflicts near present-day Peru.",
                encoding="utf-8",
            )
            (data_dir / "profiles.md").write_text(
                "Peru is a country in western South America. Peru borders Ecuador, "
                "Colombia, Brazil, Bolivia, Chile, and the Pacific Ocean.",
                encoding="utf-8",
            )
            db_path = root / "rag.sqlite"

            build_index(data_dir, db_path, allow_local_embeddings=True)
            results = retrieve(
                db_path,
                "Which countries border Peru?",
                allow_local_embeddings=True,
            )

            self.assertTrue(results)
            self.assertEqual(results[0]["source"], "profiles.md")
            self.assertIn("Peru borders Ecuador", results[0]["content"])

    def test_requires_foundry_generation_when_requested(self) -> None:
        old_endpoint = os.environ.pop("FOUNDRY_LOCAL_ENDPOINT", None)
        try:
            with self.assertRaises(FoundryGenerationError):
                generate_answer(
                    "What is the capital of Brazil?",
                    [{"source": "test.md", "chunk": 0, "score": 1.0, "content": "Brazil has Brasília as its capital."}],
                    require_foundry_generation=True,
                )
        finally:
            if old_endpoint is not None:
                os.environ["FOUNDRY_LOCAL_ENDPOINT"] = old_endpoint


if __name__ == "__main__":
    unittest.main()
