"""Render a Transcript into plain text, SRT, WebVTT, or JSON."""

from __future__ import annotations

import json

from .core import Transcript

FORMATS = ("txt", "srt", "vtt", "json")


def render(transcript: Transcript, fmt: str, timestamps: bool = False) -> str:
    """Render `transcript` in the requested format. `timestamps` only affects 'txt'."""
    if fmt == "txt":
        return _to_txt(transcript, timestamps)
    if fmt == "srt":
        return _to_srt(transcript)
    if fmt == "vtt":
        return _to_vtt(transcript)
    if fmt == "json":
        return _to_json(transcript)
    raise ValueError(f"Unknown format {fmt!r}. Choose from: {', '.join(FORMATS)}")


def _to_txt(transcript: Transcript, timestamps: bool) -> str:
    if timestamps:
        return "\n".join(
            f"[{_clock(s.start)}] {s.text}" for s in transcript.segments
        )
    # Join into flowing text; collapse caption line breaks into spaces.
    text = " ".join(s.text.replace("\n", " ").strip() for s in transcript.segments)
    return " ".join(text.split())


def _to_srt(transcript: Transcript) -> str:
    blocks = []
    for i, s in enumerate(transcript.segments, start=1):
        blocks.append(
            f"{i}\n"
            f"{_ts(s.start, ',')} --> {_ts(s.end, ',')}\n"
            f"{s.text}"
        )
    return "\n\n".join(blocks) + "\n"


def _to_vtt(transcript: Transcript) -> str:
    blocks = ["WEBVTT", ""]
    for s in transcript.segments:
        blocks.append(f"{_ts(s.start, '.')} --> {_ts(s.end, '.')}")
        blocks.append(s.text)
        blocks.append("")
    return "\n".join(blocks)


def _to_json(transcript: Transcript) -> str:
    payload = {
        "video_id": transcript.video_id,
        "language": transcript.language,
        "language_code": transcript.language_code,
        "is_generated": transcript.is_generated,
        "segments": [
            {"text": s.text, "start": round(s.start, 3), "duration": round(s.duration, 3)}
            for s in transcript.segments
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _ts(seconds: float, ms_sep: str) -> str:
    """Format seconds as HH:MM:SS<sep>mmm for SRT (',') or VTT ('.')."""
    if seconds < 0:
        seconds = 0.0
    millis = int(round(seconds * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{ms_sep}{millis:03d}"


def _clock(seconds: float) -> str:
    """Short MM:SS or HH:MM:SS label for inline txt timestamps."""
    total = int(seconds)
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"
