from __future__ import annotations

import unittest
from unittest.mock import patch

import app


class AppCliTests(unittest.TestCase):
    def test_reindex_exits_without_interactive_prompt(self) -> None:
        with patch("sys.argv", ["app.py", "--reindex"]), patch(
            "app.build_index",
            return_value={"documents": 1, "chunks": 2, "embedding_provider": "foundry"},
        ) as build_index, patch("builtins.input", side_effect=AssertionError("input should not be called")):
            app.main()

        build_index.assert_called_once()


if __name__ == "__main__":
    unittest.main()
