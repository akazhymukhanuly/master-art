from openai import AsyncOpenAI

from app.config import get_settings
from app.schemas import CreativeCopyRequest, CreativeCopyResponse


async def generate_creative_copy(payload: CreativeCopyRequest) -> CreativeCopyResponse:
    settings = get_settings()
    if not settings.openai_api_key or settings.openai_api_key == "replace_me":
        return CreativeCopyResponse(
            headlines=[
                f"{payload.service_type.title()} that gets attention in Kyzylorda",
                f"Your brand seen better with MasterArt {payload.service_type}",
                f"Fast, bold, and professional {payload.service_type}",
            ],
            call_to_action="Send your size and quantity to get a quote in 1 minute.",
        )

    client = AsyncOpenAI(api_key=settings.openai_api_key, timeout=settings.openai_timeout_seconds)
    lang = "Russian" if payload.language.value == "ru" else "Kazakh"
    prompt = (
        f"Write 3 short ad headlines and 1 CTA in {lang} for MasterArt.\n"
        f"Service: {payload.service_type}\nAudience: {payload.audience}\n"
        "Return JSON with keys: headlines (array of 3 strings), call_to_action (string)."
    )
    response = await client.responses.create(
        model=settings.openai_model,
        input=[{"role": "user", "content": prompt}],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "creative_copy",
                "schema": {
                    "type": "object",
                    "properties": {
                        "headlines": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 3,
                            "maxItems": 3,
                        },
                        "call_to_action": {"type": "string"},
                    },
                    "required": ["headlines", "call_to_action"],
                    "additionalProperties": False,
                },
            },
        },
    )
    text = response.output_text
    # Safe fallback if provider shape changes
    if not text:
        return CreativeCopyResponse(
            headlines=[
                "MasterArt: your brand, larger and brighter",
                "Advertising designs that convert to sales",
                "Outdoor and indoor visuals built to be noticed",
            ],
            call_to_action="Message us now for a personalized estimate.",
        )
    # Light parse without extra dependency
    import json

    parsed = json.loads(text)
    return CreativeCopyResponse(
        headlines=list(parsed.get("headlines", []))[:3],
        call_to_action=str(parsed.get("call_to_action", "")),
    )

