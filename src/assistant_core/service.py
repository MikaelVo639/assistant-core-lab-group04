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
        if intent is Intent.HELP:
            return self._help()
        if intent is Intent.GREETING:
            return Response(answer="Hello! I can help with offices, fees and rules.", intent=intent)
        if intent is Intent.FEE:
            return self._fee(text)
        if intent is Intent.OFFICE:
            return self._office(text)
        if intent is Intent.RULE:
            return self._rule(text)
        return self._unknown()

    def _help(self) -> Response:
        """Describe real configured capabilities without searching or calling a provider."""
        example_credits = min(12, self.settings.max_credits)
        names = sorted(self.offices.names)
        office_example = f"try 'where is {names[0]}'" if names else "no offices are loaded"
        return Response(
            answer=(
                "I can help you with:\n"
                f"- Office locations and opening hours: {office_example}.\n"
                f"- Tuition estimates: try 'tuition for {example_credits} credits'; "
                f"the rate is {self.settings.credit_rate_vnd:,} VND per credit "
                f"and the normal-credit limit is {self.settings.max_credits}. Retakes are supported.\n"
                "- Handbook rules: try 'exam absence' or 'thesis registration credits'.\n"
                "- Greetings: say 'hello'.\n"
                "Ask 'help' or 'what can you do?' to see this list again."
            ),
            intent=Intent.HELP,
        )

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
        return Response(
            answer=answer,
            intent=Intent.RULE,
            sources=[Source(id=rule.id, title=rule.title)],
            degraded=degraded,
        )

    @staticmethod
    def _unknown() -> Response:
        return Response(answer="Sorry, I don't know that yet.", intent=Intent.UNKNOWN)
