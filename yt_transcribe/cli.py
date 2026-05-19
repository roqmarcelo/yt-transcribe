"""Command-line interface for yt-transcribe."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .core import TranscriptError, available_languages, fetch_transcript
from .formats import FORMATS, render


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="yt-transcribe",
        description="Fetch a YouTube video's captions. Fast, lightweight, no AI.",
    )
    parser.add_argument("url", help="YouTube URL or 11-character video ID")
    parser.add_argument(
        "-l",
        "--lang",
        default="en",
        help="Preferred language code(s), comma-separated (default: en). "
        "Falls back to any available track if none match.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=FORMATS,
        default="txt",
        help="Output format (default: txt)",
    )
    parser.add_argument(
        "-t",
        "--timestamps",
        action="store_true",
        help="Include timestamps in txt output",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="Write to FILE instead of stdout",
    )
    parser.add_argument(
        "--list-langs",
        action="store_true",
        help="List available caption tracks for the video and exit",
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        if args.list_langs:
            tracks = available_languages(args.url)
            for t in tracks:
                kind = "auto" if t["is_generated"] else "manual"
                print(f"  {t['language_code']:<8} {t['language']} ({kind})")
            return 0

        languages = [code.strip() for code in args.lang.split(",") if code.strip()]
        transcript = fetch_transcript(args.url, languages=languages)
        output = render(transcript, args.format, timestamps=args.timestamps)

    except TranscriptError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output if output.endswith("\n") else output + "\n")
        print(f"Saved transcript to {args.output}", file=sys.stderr)
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
