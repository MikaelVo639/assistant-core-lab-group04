import sys

from pydantic import ValidationError

from assistant_core.config import load_settings
from assistant_core.errors import AssistantError
from assistant_core.logging_setup import setup_logging
from assistant_core.models import Message
from assistant_core.service import AssistantService, build_service


def _ask(service: AssistantService, text: str) -> None:
    try:
        print(service.handle(Message(text=text)).answer)
    except ValidationError:
        print("Invalid message: must be 1-2000 characters.")


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    try:
        settings = load_settings()
        setup_logging(settings.log_level)
        service = build_service(settings)
    except AssistantError as e:
        print(f"startup failed: {e}", file=sys.stderr)
        return 2

    if args:
        _ask(service, " ".join(args))
        return 0

    print("assistant ready")
    while True:
        try:
            q = input("> ")
        except EOFError:
            break
        if q.strip() == "quit":
            break
        _ask(service, q)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
