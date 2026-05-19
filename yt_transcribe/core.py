"""Core logic: parse YouTube URLs and fetch caption transcripts.

Captions-only. No audio download, no ffmpeg, no AI. Uses youtube-transcript-api,
which reads the subtitle tracks YouTube already exposes (manual or auto-generated).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

# An 11-char video id: letters, digits, dash, underscore.
_VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


class TranscriptError(Exception):
    """Raised for any user-facing failure while fetching a transcript."""


@dataclass
class Segment:
    """One timed line of a transcript."""

    text: str
    start: float
    duration: float

    @property
    def end(self) -> float:
        return self.start + self.duration


@dataclass
class Transcript:
    """A full transcript plus metadata about the track it came from."""

    video_id: str
    language: str
    language_code: str
    is_generated: bool
    segments: list[Segment]


def extract_video_id(url_or_id: str) -> str:
    """Pull the 11-char video id out of any common YouTube URL form, or accept a bare id."""
    value = url_or_id.strip()

    if _VIDEO_ID_RE.match(value):
        return value

    parsed = urlparse(value)
    host = parsed.netloc.lower().removeprefix("www.")

    # youtu.be/<id>
    if host == "youtu.be":
        candidate = parsed.path.lstrip("/").split("/")[0]
        if _VIDEO_ID_RE.match(candidate):
            return candidate

    if host in ("youtube.com", "m.youtube.com", "music.youtube.com"):
        # youtube.com/watch?v=<id>
        query_id = parse_qs(parsed.query).get("v", [None])[0]
        if query_id and _VIDEO_ID_RE.match(query_id):
            return query_id

        # /shorts/<id>, /embed/<id>, /live/<id>, /v/<id>
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) >= 2 and parts[0] in ("shorts", "embed", "live", "v"):
            if _VIDEO_ID_RE.match(parts[1]):
                return parts[1]

    raise TranscriptError(f"Could not find a YouTube video ID in: {url_or_id!r}")


def fetch_transcript(
    url_or_id: str,
    languages: list[str] | None = None,
) -> Transcript:
    """Fetch the best available caption transcript for a video.

    `languages` is an ordered preference list (e.g. ["en", "es"]). If omitted,
    English is preferred, then whatever the video offers first.
    """
    video_id = extract_video_id(url_or_id)
    preferences = languages or ["en"]

    api = YouTubeTranscriptApi()

    try:
        fetched = _fetch_with_fallback(api, video_id, preferences)
    except (TranscriptsDisabled, NoTranscriptFound):
        raise TranscriptError(
            f"No captions available for video {video_id}. "
            "The uploader may have disabled subtitles."
        )
    except VideoUnavailable:
        raise TranscriptError(
            f"Video {video_id} is unavailable (private, deleted, or region-locked)."
        )
    except CouldNotRetrieveTranscript as exc:
        raise TranscriptError(f"Could not retrieve transcript: {exc}")

    segments = [
        Segment(text=s.text, start=s.start, duration=s.duration)
        for s in fetched.snippets
    ]
    return Transcript(
        video_id=fetched.video_id,
        language=fetched.language,
        language_code=fetched.language_code,
        is_generated=fetched.is_generated,
        segments=segments,
    )


def _fetch_with_fallback(api, video_id: str, preferences: list[str]):
    """Try the preferred languages; if none match, fall back to any available track."""
    try:
        return api.fetch(video_id, languages=preferences)
    except NoTranscriptFound:
        # No preferred language matched — take whatever the video has.
        transcript_list = api.list(video_id)
        for transcript in transcript_list:
            return transcript.fetch()
        raise


def available_languages(url_or_id: str) -> list[dict]:
    """List every caption track a video offers, without fetching the text."""
    video_id = extract_video_id(url_or_id)
    api = YouTubeTranscriptApi()
    try:
        transcript_list = api.list(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        raise TranscriptError(f"No captions available for video {video_id}.")
    except VideoUnavailable:
        raise TranscriptError(f"Video {video_id} is unavailable.")

    return [
        {
            "language": t.language,
            "language_code": t.language_code,
            "is_generated": t.is_generated,
        }
        for t in transcript_list
    ]
