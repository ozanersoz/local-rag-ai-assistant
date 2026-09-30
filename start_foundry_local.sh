#!/usr/bin/env bash
set -euo pipefail

MODEL="${FOUNDRY_LOCAL_MODEL:-qwen3-0.6b}"
PORT="${FOUNDRY_LOCAL_PORT:-39839}"
ENDPOINT="http://127.0.0.1:${PORT}"

if ! command -v foundry >/dev/null 2>&1; then
  cat <<MSG
Foundry Local CLI was not found.

Install Foundry Local first, then run this script again.
Docs: https://learn.microsoft.com/en-us/azure/foundry-local/
MSG
  exit 1
fi

echo "Starting Foundry Local server on ${ENDPOINT}..."
if ! foundry server start --port "${PORT}" --idle-timeout 0; then
  echo "Server start returned a non-zero status. Trying restart..."
  foundry server restart --port "${PORT}" --idle-timeout 0
fi

echo "Loading model ${MODEL}..."
foundry model load "${MODEL}"

cat > .foundry.env <<ENV
export FOUNDRY_LOCAL_ENDPOINT="${ENDPOINT}"
export FOUNDRY_LOCAL_MODEL="${MODEL}"
ENV

cat <<MSG

Foundry Local is ready for this project.

Run:
  source .foundry.env
  python3 app.py --reindex
  python3 app.py --ask "Which countries in South America are landlocked?"

To use a different model:
  FOUNDRY_LOCAL_MODEL=your-model-name ./start_foundry_local.sh

MSG

