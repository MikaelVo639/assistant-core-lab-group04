"""Command-line entry point for the refactored assistant."""

from __future__ import annotations

import sys

from pydantic import ValidationError

from assistant_core.config import load_settings
from assistant_core.errors import AssistantError
from assistant_core.logging_setup import setup_logging
from assistant_core.models import Message
from assistant_core.service import AssistantService, build_service

USAGE = "usage: python -m assistant_core [question]"


def _ask(service: AssistantService, text: str) -> None:
    """Validate one message, print its answer, and keep errors on stderr."""
    try:
        message = Message(text=text)
    except ValidationError:
        print("Invalid message: must be 1-2000 characters.", file=sys.stderr)
        return
    print(service.handle(message).answer)


def main(argv: list[str] | None = None) -> int:
    """Run one question from argv or an interactive prompt."""
    args = sys.argv[1:] if argv is None else argv

    if args and args[0] in {"-h", "--help"}:
        print(USAGE)
        return 0

    try:
        settings = load_settings()
        setup_logging(settings.log_level)
        service = build_service(settings)
    except AssistantError as exc:
        print(f"startup failed: {exc}", file=sys.stderr)
        return 2

    if args:
        _ask(service, " ".join(args))
        return 0

    print("assistant ready")
    while True:
        try:
            question = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.strip().lower() == "quit":
            break
        _ask(service, question)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
