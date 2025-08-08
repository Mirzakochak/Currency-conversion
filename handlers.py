import sys
if sys.version_info >= (3, 0):
    try:
        import ssl
    except ImportError:
        raise ImportError("The ssl module is required but not available in this environment. Please ensure your Python installation includes SSL support.")

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services import get_fiat_rate, get_crypto_rate, get_crypto_to_fiat
import re

router = Router()

# ======== State Definitions ==========
class ConvertState(StatesGroup):
    menu = State()
    select_currency = State()
    input_amount = State()
    process_conversion = State()

# ======== Menus ==========
main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🛋‍♂️ تومان به ارز"), KeyboardButton(text="🛋‍♀️ ارز به تومان")],
    [KeyboardButton(text="💱 رمزارز ↔ ارز"), KeyboardButton(text="ℹ️ راهنما")]
], resize_keyboard=True)

back_button = [KeyboardButton(text="🔙 بازگشت")]

currency_buttons_toman_to = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="💵 دلار"), KeyboardButton(text="💶 یورو")],
    [KeyboardButton(text="💷 پوند"), KeyboardButton(text="🇹️‍🇷 لیر")],
    [KeyboardButton(text="🇦🇪 درهم"), KeyboardButton(text="🪙 تتر")],
    [KeyboardButton(text="🔺 ترون")],
    back_button
], resize_keyboard=True)

currency_buttons_to_toman = currency_buttons_toman_to

crypto_fiat_buttons = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="USD → TRX"), KeyboardButton(text="TRX → USD")],
    [KeyboardButton(text="TRX → USD"), KeyboardButton(text="TRX → EUR")],
    [KeyboardButton(text="USDT → USD"), KeyboardButton(text="USDT → GBP")],
    [KeyboardButton(text="USD → USDT"), KeyboardButton(text="EUR → TRX")],
    back_button
], resize_keyboard=True)

# ======== Handlers ==========
@router.message(F.text == "/start")
async def start(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("سلام! \nلطفاً یکی از گزینه‌ها را انتخاب کن:", reply_markup=main_menu)
    await state.set_state(ConvertState.menu)

@router.message(F.text == "/help")
async def help(msg: Message):
    await msg.answer(
        "ℹ️ راهنمای ربات:\n\n"
        "- تبدیل تومان ↔ دلار، یورو، پوند، درهم، لیر، تتر، ترون\n"
        "- تبدیل رمزارزها با ارزهای رسمی (دلار، یورو، پوند)\n\n"
        "مثال:\n"
        "1 میلیون تومان به دلار\n"
        "100 تتر به تومان\n"
        "50 یورو به ترون\n\n"
        "از منو یکی رو انتخاب کن یا دستور رو تایپ کن."
    )

@router.message(ConvertState.menu)
async def handle_menu(msg: Message, state: FSMContext):
    text = msg.text
    if "تومان به ارز" in text:
        await msg.answer("لطفاً ارزی که می‌خوای تومان بهش تبدیل بشه رو انتخاب کن:", reply_markup=currency_buttons_toman_to)
        await state.set_state(ConvertState.select_currency)
        await state.update_data(direction="toman_to")
    elif "ارز به تومان" in text:
        await msg.answer("کدوم ارز رو می‌خوای به تومان تبدیل کنی؟", reply_markup=currency_buttons_to_toman)
        await state.set_state(ConvertState.select_currency)
        await state.update_data(direction="to_toman")
    elif "رمزارز" in text:
        await msg.answer("یک گزینه تبدیل رمزارز ↔ ارز رو انتخاب کن:", reply_markup=crypto_fiat_buttons)
        await state.set_state(ConvertState.select_currency)
        await state.update_data(direction="crypto_fiat")
    elif "راهنما" in text:
        await help(msg)
    else:
        await msg.answer("لطفاً از منو یکی از گزینه‌ها رو انتخاب کن.")

@router.message(ConvertState.select_currency)
async def handle_currency_selection(msg: Message, state: FSMContext):
    text = msg.text.strip().lower()
    currency_map = {
        "دلار": "usd", "💵 دلار": "usd",
        "یورو": "eur", "💶 یورو": "eur",
        "پوند": "gbp", "💷 پوند": "gbp",
        "لیر": "try", "🇹️‍🇷 لیر": "try",
        "درهم": "aed", "🇦🇪 درهم": "aed",
        "تتر": "usdt", "🪙 تتر": "usdt",
        "ترون": "trx", "🔺 ترون": "trx"
    }
    if "بازگشت" in text:
        await start(msg, state)
        return

    normalized = text.replace("\u200c", "").strip()
    await state.update_data(selected=normalized)
    await msg.answer("عدد مبلغ رو وارد کن:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ConvertState.input_amount)

@router.message(ConvertState.input_amount)
async def handle_amount(msg: Message, state: FSMContext):
    user_data = await state.get_data()
    selected = user_data.get("selected")
    direction = user_data.get("direction")

    match = re.search(r"[0-9٠-٩۰-۹,.٫]+", msg.text)
    if not match:
        await msg.answer("لطفاً فقط مبلغ عددی وارد کن (بدون کلمه اضافی مثل تومان).")
        return

    clean_input = match.group(0).replace(",", "").replace("٫", ".")
    try:
        amount = float(clean_input)
    except:
        await msg.answer("مقدار واردشده نامعتبر است.")
        return

    currency_map = {
        "دلار": "usd", "💵 دلار": "usd",
        "یورو": "eur", "💶 یورو": "eur",
        "پوند": "gbp", "💷 پوند": "gbp",
        "لیر": "try", "🇹️‍🇷 لیر": "try",
        "درهم": "aed", "🇦🇪 درهم": "aed",
        "تتر": "usdt", "🪙 تتر": "usdt",
        "ترون": "trx", "🔺 ترون": "trx"
    }

    if direction == "toman_to":
        target = currency_map.get(selected)
        if not target:
            await msg.answer("ارز نامعتبر بود.")
            return
        rate = await (get_crypto_rate(target) if target in ["trx", "usdt"] else get_fiat_rate(target))
        if rate:
            result = amount / rate
            await msg.answer(f"{int(amount):,} تومان = {result:.4f} {target.upper()}")
    elif direction == "to_toman":
        source = currency_map.get(selected)
        if not source:
            await msg.answer("ارز نامعتبر بود.")
            return
        rate = await (get_crypto_rate(source) if source in ["trx", "usdt"] else get_fiat_rate(source))
        if rate:
            result = amount * rate
            await msg.answer(f"{amount} {source.upper()} = {int(result):,} تومان")
    elif direction == "crypto_fiat":
        map_pairs = {
            "usd → trx": ("usd", "trx"),
            "trx → usd": ("trx", "usd"),
            "trx → eur": ("trx", "eur"),
            "usdt → usd": ("usdt", "usd"),
            "usdt → gbp": ("usdt", "gbp"),
            "usd → usdt": ("usdt", "usd"),
            "eur → trx": ("trx", "eur")
        }
        pair = map_pairs.get(selected.lower())
        if not pair:
            await msg.answer("تبدیل انتخاب‌شده نامعتبر است.")
            return
        source, target = pair
        rate = await get_crypto_to_fiat(source, target)
        if not rate:
            # Try reversed direction
            reverse_rate = await get_crypto_to_fiat(target, source)
            if reverse_rate:
                rate = 1 / reverse_rate
            else:
                await msg.answer("نرخ تبدیل پیدا نشد.")
                return
        if source in ["trx", "usdt"]:
            result = amount * rate
            await msg.answer(f"{amount} {source.upper()} = {result:.4f} {target.upper()}")
        else:
            result = amount / rate
            await msg.answer(f"{amount} {source.upper()} = {result:.4f} {target.upper()}")
    else:
        await msg.answer("مسیر تبدیل مشخص نیست.")

    await state.clear()
    await msg.answer("می‌خوای چی‌کار دیگه‌ای انجام بدی؟", reply_markup=main_menu)
    await state.set_state(ConvertState.menu)
