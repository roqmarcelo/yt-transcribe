# yt-transcribe

Lightweight, fast YouTube transcript fetcher. **Captions only — no AI, no audio download, no ffmpeg.**

It reads the subtitle tracks YouTube already exposes (manually uploaded or
auto-generated), so transcription is effectively instant and free.

## Features

- **CLI** and a **minimal web UI**
- Output as plain text, SRT, WebVTT, or JSON
- Optional inline timestamps for plain text
- Handles every common URL form: `watch?v=`, `youtu.be/`, `/shorts/`, `/embed/`, `/live/`, bare video IDs
- Language preference with automatic fallback to any available track

## Requirements

- Python 3.13 (see `.tool-versions`)

## Setup

```bash
git clone https://github.com/<your-username>/yt-transcribe.git
cd yt-transcribe
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## CLI usage

```bash
# Plain text to stdout
python -m yt_transcribe.cli "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# SRT subtitles saved to a file
python -m yt_transcribe.cli "dQw4w9WgXcQ" -f srt -o subtitles.srt

# Plain text with timestamps, preferring Spanish then English
python -m yt_transcribe.cli "<url>" -l es,en -t

# List the caption tracks a video offers
python -m yt_transcribe.cli "<url>" --list-langs
```

| Flag | Description |
|------|-------------|
| `-l, --lang` | Preferred language code(s), comma-separated (default: `en`) |
| `-f, --format` | `txt` (default), `srt`, `vtt`, `json` |
| `-t, --timestamps` | Include timestamps in `txt` output |
| `-o, --output` | Write to a file instead of stdout |
| `--list-langs` | List available caption tracks and exit |

## Web UI

```bash
./run.sh
# or: uvicorn yt_transcribe.web:app --reload
```

Open <http://127.0.0.1:8000>, paste a URL, pick a format, and get the transcript
with copy / download buttons.

### HTTP API

- `GET /api/languages?url=<url>` — list available caption tracks
- `POST /api/transcribe` — body `{ "url", "lang", "format", "timestamps" }`

## How it works

`youtube-transcript-api` requests the caption data YouTube serves to its own
player. There is no model inference and no media download, which keeps the tool
small and quick. The trade-off: a video with **no captions at all** cannot be
transcribed — that would require downloading audio and running speech-to-text.

## License

MIT
