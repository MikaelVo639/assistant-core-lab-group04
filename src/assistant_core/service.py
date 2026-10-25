import logging

from assistant_core.config import Settings, load_settings
from assistant_core.errors import InvalidRequest, ProviderError
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.models import Intent, Message, Response
from assistant_core.responder import Responder, make_responder
from assistant_core.router import route
from assistant_core.tools import parse_credits, tuition

log = logging.getLogger(__name__)

GREETING = "Hello! I can help with offices, fees and rules."
UNKNOWN = "Sorry I dont know"


class AssistantService:
    def __init__(self, settings: Settings, offices: OfficeDirectory, handbook: Handbook, responder: Responder) -> None:
        self._settings = settings
        self._offices = offices
        self._handbook = handbook
        self._responder = responder

    def handle(self, msg: Message) -> Response:
        intent = route(msg.text, self._offices.names)
        if intent is Intent.GREETING:
            resp = Response(answer=GREETING, intent=intent)
        elif intent is Intent.FEE:
            resp = self._fee(msg.text)
        elif intent is Intent.OFFICE:
            office = self._offices.find(msg.text)
            resp = Response(answer=office.format_response(), intent=intent) if office else self._rule(msg.text)
        else:
            resp = self._rule(msg.text)
        log.info("handled", extra={"intent": resp.intent.value, "degraded": resp.degraded, "chars": len(msg.text)})
        return resp

    def _fee(self, text: str) -> Response:
        s = self._settings
        try:
            credits, retake = parse_credits(text)
            total = tuition(credits, retake, s.credit_rate_vnd, s.retake_multiplier, s.max_credits)
        except InvalidRequest as e:
            return Response(answer=str(e), intent=Intent.FEE)
        return Response(answer=f"Your tuition is {total} VND", intent=Intent.FEE)

    def _rule(self, text: str) -> Response:
        rule = self._handbook.search(text)
        if rule is None:
            return Response(answer=UNKNOWN, intent=Intent.UNKNOWN)
        try:
            answer, degraded = self._responder.explain(text, rule), False
        except ProviderError:
            log.warning("provider failed; using template fallback")
            answer, degraded = rule.format_fallback_response(), True
        return Response(answer=answer, intent=Intent.RULE, sources=[rule.source], degraded=degraded)


def build_service(settings: Settings | None = None) -> AssistantService:
    settings = settings or load_settings()
    return AssistantService(
        settings,
        OfficeDirectory(settings.data_dir),
        Handbook(settings.data_dir),
        make_responder(settings),
    )
