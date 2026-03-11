from openai import AsyncOpenAI

from app.config import get_settings
from app.schemas import AssistantChatRequest, LeadCreate


SYSTEM_PROMPT = (
    "You are a senior sales assistant for MasterArt advertising agency in Kyzylorda. "
    "Write a concise Russian summary with: requirement, budget risk, and next manager action."
)

CHAT_SYSTEM_PROMPT = (
    "You are Zhibek, a polite personal consultant for MasterArt advertising agency in Kyzylorda. "
    "Answer in the same language as user (Russian or Kazakh). "
    "Be practical and concise: 2-5 short sentences. "
    "Use only business-safe facts: services, materials, rough lead time, addresses, WhatsApp +7 776 677 95 95. "
    "If exact price is unknown, suggest sending size/material/quantity for estimate."
)


def _faq_fallback(payload: AssistantChatRequest) -> str:
    text = payload.message.lower()

    if any(word in text for word in ["привет", "салем", "здравствуйте", "здра", "hello"]):
        return (
            "Здравствуйте! Я ИИ-консультант Жибек. "
            "Помогу с выбором услуги, материалов, сроков и предварительным расчетом. "
            "Что хотите изготовить: баннер, вывеску, стенд, билборд или лазерную/фрезерную работу?"
        )

    if any(word in text for word in ["услуг", "делаете", "что умеете", "не істейсің", "не жасайсыз"]):
        return (
            "Мы делаем фрезерную и лазерную резку, баннерную печать, дизайн в Corel, "
            "наружную и внутреннюю рекламу, стенды и билборды. "
            "Напишите задачу и примерные размеры, и я подскажу лучший формат."
        )

    if any(word in text for word in ["адрес", "где", "офис", "цех", "мекен", "қайда"]):
        return (
            "Наши точки: офис Н. Назарбаева 20 (SMALL сауда үйі), "
            "офис Қорқыт ата 28а (Қызылорда супермаркеті), цех Мичурина 24/1. "
            "Можно написать в WhatsApp: +7 776 677 95 95."
        )

    if any(word in text for word in ["цена", "стоимость", "сколько", "баға", "канша"]):
        return (
            "Точную цену считаем по параметрам: услуга, материал, размер, тираж и срок. "
            "Напишите эти данные, и я сразу дам ориентир по стоимости и срокам."
        )

    if any(word in text for word in ["срок", "когда", "срочно", "мерзім"]):
        return (
            "Срок зависит от сложности и загрузки, обычно от 1-3 дней для простых задач. "
            "Для срочного заказа напишите формат и размеры, проверю ближайшую дату запуска."
        )

    return (
        "Я ИИ-консультант Жибек и помогу по заказу в MasterArt. "
        "Опишите, что нужно изготовить, размеры, материал и срок. "
        "Я подскажу оптимальный вариант и дальнейшие шаги."
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


async def assistant_reply(payload: AssistantChatRequest) -> str:
    settings = get_settings()
    if not settings.openai_api_key or settings.openai_api_key == "replace_me":
        return _faq_fallback(payload)

    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout_seconds,
    )
    response = await client.responses.create(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": CHAT_SYSTEM_PROMPT},
            {"role": "user", "content": payload.message},
        ],
        max_output_tokens=260,
    )
    text = (response.output_text or "").strip()
    if not text:
        return _faq_fallback(payload)
    return text
