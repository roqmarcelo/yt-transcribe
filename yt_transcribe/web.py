"""Minimal FastAPI web UI for yt-transcribe.

Run with:  uvicorn yt_transcribe.web:app --reload
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from .core import TranscriptError, available_languages, fetch_transcript
from .formats import FORMATS, render

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="yt-transcribe", description="Lightweight YouTube transcript fetcher")


class TranscribeRequest(BaseModel):
    url: str
    lang: str = "en"
    format: str = "txt"
    timestamps: bool = False


@app.get("/")
def index() -> FileResponse:
    """Serve the single-page UI."""
    return FileResponse(_STATIC_DIR / "index.html")


@app.get("/api/languages")
def languages(url: str) -> JSONResponse:
    """List available caption tracks for a video."""
    try:
        tracks = available_languages(url)
    except TranscriptError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    return JSONResponse(content={"tracks": tracks})


@app.post("/api/transcribe")
def transcribe(req: TranscribeRequest) -> JSONResponse:
    """Fetch and render a transcript."""
    if req.format not in FORMATS:
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid format. Choose from: {', '.join(FORMATS)}"},
        )

    languages_pref = [c.strip() for c in req.lang.split(",") if c.strip()]
    try:
        transcript = fetch_transcript(req.url, languages=languages_pref)
        output = render(transcript, req.format, timestamps=req.timestamps)
    except TranscriptError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})

    return JSONResponse(
        content={
            "video_id": transcript.video_id,
            "language": transcript.language,
            "language_code": transcript.language_code,
            "is_generated": transcript.is_generated,
            "segment_count": len(transcript.segments),
            "format": req.format,
            "content": output,
        }
    )
