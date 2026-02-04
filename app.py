from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, Optional


APP_NAME = "app"


@dataclass(frozen=True)
class Config:
    input_text: Optional[str]
    input_file: Optional[str]
    output_file: Optional[str]
    uppercase: bool
    json_output: bool
    log_level: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="A reliable CLI template with clear UX and guardrails.",
        epilog=(
            "Examples:\n"
            "  app --text \"hello world\"\n"
            "  app --file input.txt --output out.txt\n"
            "  app --text \"hello\" --json\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--text",
        dest="input_text",
        help="Inline text to process.",
    )
    input_group.add_argument(
        "--file",
        dest="input_file",
        help="Path to a text file to process.",
    )
    parser.add_argument(
        "--output",
        dest="output_file",
        help="Write output to a file instead of stdout.",
    )
    parser.add_argument(
        "--uppercase",
        action="store_true",
        help="Transform text to uppercase.",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Emit a JSON object with metadata.",
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("APP_LOG_LEVEL", "INFO"),
        help="Logging level (default: INFO).",
    )
    return parser


def parse_args(argv: Iterable[str]) -> Config:
    parser = build_parser()
    args = parser.parse_args(argv)
    return Config(
        input_text=args.input_text,
        input_file=args.input_file,
        output_file=args.output_file,
        uppercase=args.uppercase,
        json_output=args.json_output,
        log_level=args.log_level.upper(),
    )


def configure_logging(level: str) -> None:
    numeric = getattr(logging, level, None)
    if not isinstance(numeric, int):
        raise ValueError(f"Invalid log level: {level}")
    logging.basicConfig(
        level=numeric,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def read_input(config: Config) -> str:
    if config.input_text is not None:
        return config.input_text
    if config.input_file is None:
        raise ValueError("Either --text or --file must be provided.")
    if not os.path.exists(config.input_file):
        raise FileNotFoundError(f"Input file not found: {config.input_file}")
    with open(config.input_file, "r", encoding="utf-8") as handle:
        return handle.read()


def transform(text: str, uppercase: bool) -> str:
    output = text.strip()
    if uppercase:
        output = output.upper()
    return output


def render_output(text: str, json_output: bool) -> str:
    if not json_output:
        return text
    payload = {
        "app": APP_NAME,
        "length": len(text),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "output": text,
    }
    return json.dumps(payload, ensure_ascii=True)


def write_output(result: str, output_file: Optional[str]) -> None:
    if output_file:
        with open(output_file, "w", encoding="utf-8") as handle:
            handle.write(result)
        logging.info("Wrote output to %s", output_file)
    else:
        print(result)


def run(argv: Iterable[str]) -> int:
    try:
        config = parse_args(argv)
        configure_logging(config.log_level)
        logging.info("Starting %s", APP_NAME)

        raw_text = read_input(config)
        processed = transform(raw_text, config.uppercase)
        result = render_output(processed, config.json_output)
        write_output(result, config.output_file)

        logging.info("Completed successfully")
        return 0
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        logging.exception("Unexpected error")
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


def main() -> None:
    raise SystemExit(run(sys.argv[1:]))


if __name__ == "__main__":
    main()
