import argparse
import json
import logging
import sys
from dataclasses import dataclass
from typing import Any, Dict, Optional

# NOTE: These modules are placeholders for future integration.
# from classifier import classify_text
# from taxonomy import TAXONOMY
# from prompts import build_prompt


@dataclass
class AppConfig:
    log_level: str = "INFO"
    output_format: str = "json"


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Text classification CLI.")
    parser.add_argument("text", help="Text to classify.")
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (e.g., INFO, DEBUG).",
    )
    return parser.parse_args(argv)


def classify(text: str) -> Dict[str, Any]:
    """
    Placeholder classification logic.
    Replace with real classifier integration.
    """
    # TODO: Replace with actual classification:
    # result = classify_text(text, taxonomy=TAXONOMY, prompt=build_prompt(text))
    return {
        "label": "unknown",
        "confidence": 0.0,
        "input": text,
    }


def format_output(result: Dict[str, Any], fmt: str) -> str:
    if fmt == "text":
        return f"label={result['label']} confidence={result['confidence']}"
    return json.dumps(result, indent=2)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    config = AppConfig(log_level=args.log_level, output_format=args.format)

    setup_logging(config.log_level)
    logging.debug("Starting classification")

    try:
        result = classify(args.text)
        output = format_output(result, config.output_format)
        print(output)
        return 0
    except Exception as exc:
        logging.exception("Classification failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
