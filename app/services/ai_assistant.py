from openai import AsyncOpenAI

from app.config import get_settings
from app.schemas import LeadCreate


SYSTEM_PROMPT = (
    "You are a senior sales assistant for MasterArt advertising agency in Kyzylorda. "
    "Write a concise Russian summary with: requirement, budget risk, and next manager action."
)


async def build_lead_summary(payload: LeadCreate) -> str:
    settings = get_settings()
    if not settings.openai_api_key or settings.openai_api_key == "replace_me":
        return "AI summary unavailable: OPENAI_API_KEY is not configured."

    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout_seconds,
    )
    user_text = (
        f"Client: {payload.customer_name}\n"
        f"Phone: {payload.customer_phone}\n"
        f"Language: {payload.language.value}\n"
        f"Service: {payload.service_type}\n"
        f"Material: {payload.material}\n"
        f"Size: {payload.width_cm}x{payload.height_cm} cm\n"
        f"Quantity: {payload.quantity}\n"
        f"Urgency days: {payload.urgency_days}\n"
        f"Has design: {payload.has_design}\n"
        f"Delivery: {payload.delivery_type.value}\n"
        f"Delivery address: {payload.delivery_address}\n"
        f"Notes: {payload.notes}"
    )
    response = await client.responses.create(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        max_output_tokens=220,
    )
    return response.output_text.strip()

