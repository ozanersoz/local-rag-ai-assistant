from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import app


class AppCliTests(unittest.TestCase):
    def test_reindex_exits_without_interactive_prompt(self) -> None:
        with patch("sys.argv", ["app.py", "--reindex"]), patch(
            "app.build_index",
            return_value={"documents": 1, "chunks": 2, "embedding_provider": "foundry"},
        ) as build_index, patch("app.retrieve") as retrieve, patch("app.generate_answer") as generate_answer, patch(
            "builtins.input", side_effect=AssertionError("input should not be called")
        ):
            with redirect_stdout(io.StringIO()) as stdout:
                app.main()

        build_index.assert_called_once()
        retrieve.assert_not_called()
        generate_answer.assert_not_called()
        self.assertIn("Reindex complete", stdout.getvalue())

    def test_ask_passes_top_k_to_retriever(self) -> None:
        with patch("sys.argv", ["app.py", "--ask", "What is Mercosur?", "--top-k", "8"]), patch(
            "pathlib.Path.exists", return_value=True
        ), patch("app.retrieve", return_value=[]) as retrieve, patch("app.generate_answer", return_value="answer"):
            with redirect_stdout(io.StringIO()):
                app.main()

        retrieve.assert_called_once_with(
            app.DB_PATH,
            "What is Mercosur?",
            limit=8,
            mode="vector",
            allow_local_embeddings=False,
        )

    def test_allow_fallback_opt_in_controls_embeddings_and_output(self) -> None:
        with patch(
            "sys.argv",
            ["app.py", "--ask", "What is Mercosur?", "--allow-fallback"],
        ), patch("pathlib.Path.exists", return_value=True), patch(
            "app.retrieve", return_value=[]
        ) as retrieve, patch("app.generate_answer", return_value="answer") as generate_answer:
            with redirect_stdout(io.StringIO()):
                app.main()

        retrieve.assert_called_once_with(
            app.DB_PATH,
            "What is Mercosur?",
            limit=6,
            mode="vector",
            allow_local_embeddings=True,
        )
        generate_answer.assert_called_once_with(
            "What is Mercosur?",
            [],
            allow_fallback_generation=True,
        )


if __name__ == "__main__":
    unittest.main()
