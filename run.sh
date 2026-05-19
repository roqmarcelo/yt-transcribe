#!/usr/bin/env bash
# Convenience launcher for the yt-transcribe web UI.
set -euo pipefail
cd "$(dirname "$0")"

PORT="${PORT:-8000}"

# Prefer the project virtualenv if present, so dependencies are always found.
if [[ -x ".venv/bin/uvicorn" ]]; then
  UVICORN=".venv/bin/uvicorn"
elif command -v uvicorn >/dev/null 2>&1; then
  UVICORN="uvicorn"
else
  echo "Error: uvicorn not found." >&2
  echo "Create the environment first:" >&2
  echo "  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi

echo "Starting yt-transcribe web UI on http://127.0.0.1:${PORT}"
exec "$UVICORN" yt_transcribe.web:app --host 127.0.0.1 --port "${PORT}" "$@"
