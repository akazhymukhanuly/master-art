import asyncio
import re
from urllib.parse import urlparse

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    WebAppInfo,
)

from app.config import get_settings

PHONE_PATTERN = re.compile(r"^[+\d][\d()\-\s]{8,}$")


class LeadForm(StatesGroup):
    language = State()
    name = State()
    phone = State()
    service = State()
    material = State()
    size = State()
    qty = State()
    urgency = State()
    design = State()
    delivery = State()
    address = State()
    notes = State()


settings = get_settings()
bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher(storage=MemoryStorage())
studio_url = f"{settings.app_base_url}/app"

language_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Русский"), KeyboardButton(text="Қазақша")]],
    resize_keyboard=True,
)
service_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Баннер"), KeyboardButton(text="Фреза")],
        [KeyboardButton(text="Лазер"), KeyboardButton(text="Стенд")],
        [KeyboardButton(text="Билборд"), KeyboardButton(text="Дизайн")],
    ],
    resize_keyboard=True,
)
material_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="banner_frontlit"), KeyboardButton(text="banner_blockout")],
        [KeyboardButton(text="acrylic_3mm"), KeyboardButton(text="acrylic_5mm")],
        [KeyboardButton(text="composite_panel"), KeyboardButton(text="film_oracal")],
    ],
    resize_keyboard=True,
)
yes_no_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Да"), KeyboardButton(text="Нет")]],
    resize_keyboard=True,
)
delivery_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Самовывоз"), KeyboardButton(text="Доставка")]],
    resize_keyboard=True,
)

def _digits_count(value: str) -> int:
    return sum(ch.isdigit() for ch in value)


def _is_https_url(url: str) -> bool:
    try:
        return urlparse(url).scheme == "https"
    except Exception:
        return False


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    if _is_https_url(studio_url):
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Open MasterArt AI Studio", web_app=WebAppInfo(url=studio_url))],
            ],
            resize_keyboard=True,
        )
        await message.answer(
            "MasterArt AI Studio ready.\n"
            "Открой mini-app: идея -> концепты -> тюнинг сделки -> запуск.",
            reply_markup=kb,
        )
    else:
        await message.answer(
            "MasterArt AI Studio ready, but Telegram WebApp requires HTTPS URL.\n"
            f"Current URL: {studio_url}\n"
            "Set APP_BASE_URL to an HTTPS domain (ngrok/cloudflared), then use /studio."
        )
    await message.answer("Если нужен старый пошаговый режим, команда: /brief")


@dp.message(Command("brief"))
async def brief_mode(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Пошаговый режим включен.",
        reply_markup=language_keyboard,
    )
    await message.answer("Выберите язык / Тілді таңдаңыз:")
    await state.set_state(LeadForm.language)


@dp.message(Command("cancel"))
async def cancel_form(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Текущий сценарий отменен. Запустите заново: /start", reply_markup=ReplyKeyboardRemove())


@dp.message(Command("studio"))
async def studio(message: Message):
    if not _is_https_url(studio_url):
        await message.answer(
            "WebApp URL is not HTTPS.\n"
            f"Current: {studio_url}\n"
            "Use HTTPS tunnel and update APP_BASE_URL in .env, then restart bot."
        )
        return

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Open MasterArt AI Studio", web_app=WebAppInfo(url=studio_url))],
        ],
        resize_keyboard=True,
    )
    await message.answer(
        "Open AI Studio mini-app: it builds brief, concepts, and deal options live.",
        reply_markup=kb,
    )


@dp.message(Command("creative"))
async def creative_tip(message: Message):
    payload = {"service_type": "outdoor advertising", "audience": "local businesses", "language": "ru"}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(f"{settings.app_base_url}/api/creative-copy", json=payload)
            data = response.json()
    except Exception:
        await message.answer("Creative service temporary unavailable.")
        return

    headlines = data.get("headlines", [])
    cta = data.get("call_to_action", "")
    text = "AI creative ideas:\n"
    for i, line in enumerate(headlines, 1):
        text += f"{i}. {line}\n"
    text += f"CTA: {cta}"
    await message.answer(text)


@dp.message(LeadForm.language)
async def capture_language(message: Message, state: FSMContext):
    raw = (message.text or "").strip().lower()
    language = "kz" if "қазақ" in raw else "ru"
    await state.update_data(language=language)
    await message.answer("Как вас зовут?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(LeadForm.name)


@dp.message(LeadForm.name)
async def capture_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer("Введите корректное имя.")
        return
    await state.update_data(customer_name=name)
    await message.answer("Укажите номер телефона (например: +77771234567).")
    await state.set_state(LeadForm.phone)


@dp.message(LeadForm.phone)
async def capture_phone(message: Message, state: FSMContext):
    phone = (message.text or "").strip()
    if not PHONE_PATTERN.match(phone):
        await message.answer("Формат телефона неверный. Пример: +77771234567")
        return
    if _digits_count(phone) < 10:
        await message.answer("Номер слишком короткий. Нужны минимум 10 цифр.")
        return
    await state.update_data(customer_phone=phone)
    await message.answer("Выберите услугу:", reply_markup=service_keyboard)
    await state.set_state(LeadForm.service)


@dp.message(LeadForm.service)
async def capture_service(message: Message, state: FSMContext):
    await state.update_data(service_type=(message.text or "").strip())
    await message.answer("Выберите материал:", reply_markup=material_keyboard)
    await state.set_state(LeadForm.material)


@dp.message(LeadForm.material)
async def capture_material(message: Message, state: FSMContext):
    await state.update_data(material=(message.text or "").strip())
    await message.answer("Введите размер в см: ширинаxвысота (пример: 200x100)", reply_markup=ReplyKeyboardRemove())
    await state.set_state(LeadForm.size)


@dp.message(LeadForm.size)
async def capture_size(message: Message, state: FSMContext):
    raw = (message.text or "").strip().lower().replace(" ", "")
    if "x" not in raw:
        await message.answer("Неверный формат. Используйте: 200x100")
        return
    left, right = raw.split("x", 1)
    if not (left.isdigit() and right.isdigit()):
        await message.answer("Размер должен быть числовой: 200x100")
        return
    width_cm, height_cm = int(left), int(right)
    await state.update_data(width_cm=width_cm, height_cm=height_cm)
    await message.answer("Количество (шт):")
    await state.set_state(LeadForm.qty)


@dp.message(LeadForm.qty)
async def capture_qty(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text.isdigit() or int(text) <= 0:
        await message.answer("Введите целое число больше 0.")
        return
    await state.update_data(quantity=int(text))
    await message.answer("Срок в днях:")
    await state.set_state(LeadForm.urgency)


@dp.message(LeadForm.urgency)
async def capture_urgency(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text.isdigit() or int(text) <= 0:
        await message.answer("Введите целое число больше 0.")
        return
    await state.update_data(urgency_days=int(text))
    await message.answer("Нужен дизайн от MasterArt?", reply_markup=yes_no_keyboard)
    await state.set_state(LeadForm.design)


@dp.message(LeadForm.design)
async def capture_design(message: Message, state: FSMContext):
    raw = (message.text or "").strip().lower()
    has_design = raw in {"да", "yes", "иә"}
    await state.update_data(has_design=has_design)
    await message.answer("Формат получения: самовывоз или доставка?", reply_markup=delivery_keyboard)
    await state.set_state(LeadForm.delivery)


@dp.message(LeadForm.delivery)
async def capture_delivery(message: Message, state: FSMContext):
    raw = (message.text or "").strip().lower()
    if "достав" in raw:
        await state.update_data(delivery_type="delivery")
        await message.answer("Введите адрес доставки:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(LeadForm.address)
        return
    await state.update_data(delivery_type="pickup", delivery_address="")
    await message.answer("Дополнительные комментарии? Если нет, отправьте '-'")
    await state.set_state(LeadForm.notes)


@dp.message(LeadForm.address)
async def capture_address(message: Message, state: FSMContext):
    address = (message.text or "").strip()
    if len(address) < 4:
        await message.answer("Введите полный адрес доставки.")
        return
    await state.update_data(delivery_address=address)
    await message.answer("Дополнительные комментарии? Если нет, отправьте '-'")
    await state.set_state(LeadForm.notes)


@dp.message(LeadForm.notes)
async def capture_notes(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    notes = "" if text == "-" else text
    data = await state.get_data()
    payload = {
        "customer_name": data["customer_name"],
        "customer_phone": data["customer_phone"],
        "language": data["language"],
        "service_type": data["service_type"],
        "material": data["material"],
        "width_cm": data["width_cm"],
        "height_cm": data["height_cm"],
        "quantity": data["quantity"],
        "urgency_days": data["urgency_days"],
        "has_design": data["has_design"],
        "delivery_type": data["delivery_type"],
        "delivery_address": data.get("delivery_address", ""),
        "notes": notes,
    }

    headers = {"x-api-key": settings.internal_api_key}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{settings.app_base_url}/api/leads",
                json=payload,
                headers=headers,
            )
            proposal_resp = await client.post(
                f"{settings.app_base_url}/api/proposals",
                json=payload,
            )
    except Exception:
        await message.answer("Сервис временно недоступен. Попробуйте позже.")
        await state.clear()
        return

    if response.status_code >= 400:
        details = ""
        try:
            body = response.json()
            details = str(body.get("detail", body))
        except Exception:
            details = response.text[:300]
        await message.answer(f"Ошибка валидации заявки: {details}")
        await state.clear()
        return

    lead = response.json()
    await message.answer(
        f"Заявка принята. Номер: #{lead['id']}\n"
        f"Предварительная цена: {lead['estimated_price_kzt']} KZT\n"
        "Менеджер свяжется с вами в ближайшее время.",
        reply_markup=ReplyKeyboardRemove(),
    )
    if proposal_resp.status_code < 400:
        proposal = proposal_resp.json()
        lines = [f"Персональные пакеты ({proposal.get('lead_preview', '')}):"]
        for opt in proposal.get("options", []):
            benefits = ", ".join(opt.get("benefits", [])[:3])
            lines.append(
                f"- {opt['name']}: {opt['total_kzt']} KZT | {opt['eta_days']} days | {opt['material']} | {benefits}"
            )
        lines.append(f"Recommended: {proposal.get('recommended', 'Pro')}")
        await message.answer("\n".join(lines))

    if settings.telegram_notify_new_lead:
        try:
            manager_chat_id = int(settings.telegram_manager_chat_id)
            await bot.send_message(
                manager_chat_id,
                "New lead\n"
                f"#{lead['id']} | {lead['customer_name']} | {lead['customer_phone']}\n"
                f"Service: {lead['service_type']} | Material: {lead['material']}\n"
                f"Size: {lead['width_cm']}x{lead['height_cm']} cm | Qty: {lead['quantity']}\n"
                f"Urgency: {lead['urgency_days']} days | Delivery: {lead['delivery_type']}\n"
                f"Price: {lead['estimated_price_kzt']} KZT\n"
                f"AI: {lead['ai_summary']}",
            )
        except Exception:
            pass

    await state.clear()


@dp.message(F.text)
async def fallback(message: Message):
    await message.answer("Для нового заказа используйте /start. Для отмены текущего ввода: /cancel")


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
