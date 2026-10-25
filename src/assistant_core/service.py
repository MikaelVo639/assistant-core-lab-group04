"""Coordinate assistant capabilities through a single object-oriented boundary."""

from __future__ import annotations

import logging
from time import perf_counter
from typing import TYPE_CHECKING

from assistant_core.errors import InvalidRequest, ProviderError
from assistant_core.models import Intent, Message, Response, Source
from assistant_core.responder import TemplateResponder
from assistant_core.router import route
from assistant_core.tools import parse_credits, tuition

if TYPE_CHECKING:
    from assistant_core.config import Settings
    from assistant_core.knowledge import Handbook, OfficeDirectory
    from assistant_core.responder import Responder

log = logging.getLogger("assistant_core")


class AssistantService:
    """Orchestrate injected collaborators without owning their domain logic or I/O."""

    def __init__(self, settings: Settings, offices: OfficeDirectory, handbook: Handbook, responder: Responder):
        self.settings = settings
        self.offices = offices
        self.handbook = handbook
        self.responder = responder
        self.fallback = TemplateResponder()

    def handle(self, msg: Message) -> Response:
        """Return an answer and safe metadata; provider outages use a template."""
        started = perf_counter()
        response = self._answer(msg.text)
        log.info(
            "handled",
            extra={
                "intent": response.intent.value,
                "latency_ms": round((perf_counter() - started) * 1000, 3),
                "session": msg.session_id,
                "degraded": response.degraded,
            },
        )
        return response

    def _answer(self, text: str) -> Response:
        intent = route(text, self.offices.names)
        if intent is Intent.GREETING:
            return Response(answer="Hello! I can help with offices, fees and rules.", intent=intent)
        if intent is Intent.FEE:
            return self._fee(text)
        if intent is Intent.OFFICE:
            return self._office(text)
        if intent is Intent.RULE:
            return self._rule(text)
        return self._unknown()

    def _fee(self, text: str) -> Response:
        try:
            credits, retake = parse_credits(text)
            total = tuition(
                credits,
                retake,
                self.settings.credit_rate_vnd,
                self.settings.retake_multiplier,
                self.settings.max_credits,
            )
        except InvalidRequest as exc:
            return Response(answer=str(exc), intent=Intent.FEE)
        return Response(answer=f"Your tuition is {total:,} VND.", intent=Intent.FEE)

    def _office(self, text: str) -> Response:
        office = self.offices.find(text)
        if office is None:
            return self._unknown()
        return Response(
            answer=f"{office.name}: room {office.room}, open {office.hours}.",
            intent=Intent.OFFICE,
        )

    def _rule(self, text: str) -> Response:
        rule = self.handbook.search(text)
        if rule is None:
            return self._unknown()
        degraded = False
        try:
            answer = self.responder.explain(text, rule)
        except ProviderError:
            log.warning("provider failed; using template fallback")
            answer = self.fallback.explain(text, rule)
            degraded = True
        answer = f"{answer} (source: {rule.id})"
        return Response(
            answer=answer,
            intent=Intent.RULE,
            sources=[Source(id=rule.id, title=rule.title)],
            degraded=degraded,
        )

    @staticmethod
    def _unknown() -> Response:
        return Response(answer="Sorry, I don't know that yet.", intent=Intent.UNKNOWN)


def build_service(settings: Settings | None = None) -> AssistantService:
    """Compose validated collaborators without configuring the caller's logging."""
    from assistant_core.config import load_settings
    from assistant_core.knowledge import Handbook, OfficeDirectory
    from assistant_core.responder import make_responder

    resolved = settings if settings is not None else load_settings()
    return AssistantService(
        resolved,
        OfficeDirectory.from_csv(resolved.data_dir / "offices.csv"),
        Handbook.from_json(resolved.data_dir / "handbook.json"),
        make_responder(resolved),
    )
