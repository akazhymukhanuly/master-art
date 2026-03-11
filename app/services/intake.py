import json
import re

from openai import AsyncOpenAI

from app.config import get_settings
from app.schemas import DeliveryType, IntakeParseRequest, ParsedBrief


def _extract_size(text: str) -> tuple[int, int]:
    match = re.search(r"(\d{2,4})\s*[xх]\s*(\d{2,4})", text.lower())
    if match:
        return int(match.group(1)), int(match.group(2))
    return 200, 100


def _extract_qty(text: str) -> int:
    match = re.search(r"(тираж|qty|quantity|дана|штук)\D{0,10}(\d{1,4})", text.lower())
    if match:
        return int(match.group(2))
    return 1


def _extract_urgency(text: str) -> int:
    match = re.search(r"(срок|день|күн|days?)\D{0,10}(\d{1,2})", text.lower())
    if match:
        return max(1, int(match.group(2)))
    return 3


def _fallback_parse(payload: IntakeParseRequest) -> ParsedBrief:
    text = payload.message
    width, height = _extract_size(text)
    quantity = _extract_qty(text)
    urgency = _extract_urgency(text)
    delivery = DeliveryType.DELIVERY if "достав" in text.lower() else DeliveryType.PICKUP
    return ParsedBrief(
        summary=text[:200],
        service_type="banner",
        material="banner_frontlit",
        width_cm=width,
        height_cm=height,
        quantity=quantity,
        urgency_days=urgency,
        has_design=True,
        delivery_type=delivery,
        delivery_address="",
        audience="local businesses",
        style_hint="bold and modern",
    )


async def parse_client_intake(payload: IntakeParseRequest) -> ParsedBrief:
    settings = get_settings()
    if not settings.openai_api_key or settings.openai_api_key == "replace_me":
        return _fallback_parse(payload)

    client = AsyncOpenAI(api_key=settings.openai_api_key, timeout=settings.openai_timeout_seconds)
    lang = "Russian" if payload.language.value == "ru" else "Kazakh"
    prompt = (
        f"Extract a production brief from this user request in {lang}. "
        "Return strict JSON fields: "
        "summary, service_type, material, width_cm, height_cm, quantity, urgency_days, "
        "has_design, delivery_type, delivery_address, audience, style_hint.\n"
        f"Message: {payload.message}"
    )
    response = await client.responses.create(
        model=settings.openai_model,
        input=[{"role": "user", "content": prompt}],
        max_output_tokens=500,
    )
    text = response.output_text.strip()
    if not text:
        return _fallback_parse(payload)
    try:
        data = json.loads(text)
        return ParsedBrief.model_validate(data)
    except Exception:
        return _fallback_parse(payload)

