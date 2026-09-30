#!/usr/bin/env bash
set -e

python3 app.py --reindex
python3 app.py --ask "Which countries in South America are landlocked?"
