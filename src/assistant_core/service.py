"""Coordinate configuration, knowledge, tools, and responders for one request."""

from __future__ import annotations

import logging
from time import perf_counter

from assistant_core.config import Settings, load_settings
from assistant_core.errors import InvalidRequest, ProviderError
from assistant_core.knowledge import Handbook, OfficeDirectory, Rule
from assistant_core.models import Intent, Message, Response
from assistant_core.responder import Responder, make_responder
from assistant_core.router import route
from assistant_core.tools import parse_credits, tuition

log = logging.getLogger("assistant_core")

GREETING = "Hello! I can help with offices, fees and rules."
UNKNOWN = "Sorry I dont know"


class AssistantService:
    """Orchestrate injected collaborators through one public entry point."""

    def __init__(
        self,
        settings: Settings,
        offices: OfficeDirectory,
        handbook: Handbook,
        responder: Responder,
    ) -> None:
        self._settings = settings
        self._offices = offices
        self._handbook = handbook
        self._responder = responder

    def handle(self, msg: Message) -> Response:
        """Answer a validated message and log safe request metadata."""
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
        intent = route(text, self._offices.names)
        if intent is Intent.GREETING:
            return Response(answer=GREETING, intent=intent)
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
                rate=self._settings.credit_rate_vnd,
                retake_multiplier=self._settings.retake_multiplier,
                max_credits=self._settings.max_credits,
            )
        except InvalidRequest as exc:
            return Response(answer=str(exc), intent=Intent.FEE)
        return Response(answer=f"Your tuition is {total} VND", intent=Intent.FEE)

    def _office(self, text: str) -> Response:
        office = self._offices.find(text)
        if office is None:
            return self._unknown()
        return Response(answer=office.format_response(), intent=Intent.OFFICE)

    def _rule(self, text: str) -> Response:
        rule: Rule | None = self._handbook.search(text)
        if rule is None:
            return self._unknown()

        degraded = False
        try:
            answer = f"{self._responder.explain(text, rule)} (source: {rule.id})"
        except ProviderError:
            log.warning("provider failed; using template fallback")
            answer = rule.format_fallback_response()
            degraded = True

        return Response(
            answer=answer,
            intent=Intent.RULE,
            sources=[rule.source],
            degraded=degraded,
        )

    @staticmethod
    def _unknown() -> Response:
        return Response(answer=UNKNOWN, intent=Intent.UNKNOWN)


def build_service(settings: Settings | None = None) -> AssistantService:
    """Compose a service from validated settings and the packaged data files."""
    resolved = settings or load_settings()
    offices = OfficeDirectory.from_csv(resolved.data_dir)
    handbook = Handbook.from_json(resolved.data_dir)
    return AssistantService(resolved, offices, handbook, make_responder(resolved))
