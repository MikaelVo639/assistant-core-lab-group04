"""Compose assistant objects and expose their service through a small CLI."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from typing import TYPE_CHECKING, NoReturn

from pydantic import ValidationError

if TYPE_CHECKING:
    from assistant_core.service import AssistantService


class _ArgumentParser(argparse.ArgumentParser):
    """Explain invalid usage without echoing potentially sensitive argument values."""

    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        self.exit(2, "Invalid command-line arguments. Use --help for usage.\n")


def build_service() -> AssistantService:
    """Construct the object graph using the public contracts of the lab modules."""
    from assistant_core.config import load_settings
    from assistant_core.logging_setup import setup_logging
    from assistant_core.service import build_service as compose_service

    settings = load_settings()
    setup_logging(settings.log_level)
    return compose_service(settings)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _ArgumentParser(description="Ask about offices, tuition fees, and handbook rules.")
    parser.add_argument("--session-id", default="local", help="Session identifier for request metadata")
    parser.add_argument("text", nargs="+", help="Question to send to the assistant")
    args = parser.parse_args(argv)
    try:
        from assistant_core.errors import ConfigError, DataError
        from assistant_core.models import Message

        message = Message(text=" ".join(args.text), session_id=args.session_id)
        service = build_service()
    except ModuleNotFoundError as exc:
        return _missing_component(exc)
    except (ConfigError, DataError):
        print("Cannot start assistant. Check the environment and knowledge files.", file=sys.stderr)
        return 2
    except ValidationError:
        print("Invalid message or configuration. Check the input and environment values.", file=sys.stderr)
        return 2
    response = service.handle(message)
    print(response.answer)
    return 0


def _missing_component(exc: ModuleNotFoundError) -> int:
    components = {
        "config",
        "errors",
        "models",
        "knowledge",
        "logging_setup",
        "responder",
        "router",
        "tools",
        "service",
    }
    if exc.name not in {f"assistant_core.{name}" for name in components}:
        raise exc
    print("Cannot start assistant. Complete the remaining Lab 03 package modules.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
