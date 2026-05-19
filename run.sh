#!/usr/bin/env bash
# Convenience launcher for the yt-transcribe web UI.
set -euo pipefail
cd "$(dirname "$0")"

PORT="${PORT:-8000}"
echo "Starting yt-transcribe web UI on http://127.0.0.1:${PORT}"
exec uvicorn yt_transcribe.web:app --host 127.0.0.1 --port "${PORT}" "$@"
