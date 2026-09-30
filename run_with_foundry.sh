#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .foundry.env ]; then
  ./start_foundry_local.sh
fi

source .foundry.env
python3 app.py --reindex
python3 app.py --ask "Which countries in South America are landlocked?"
