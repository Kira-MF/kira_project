# -*- coding: utf-8 -*-
import logging
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

# ─── CONFIG ───────────────────────────────────────────────────────
BOT_TOKEN = "ТВОЙ_ТОКЕН_СЮДА"
EXCHANGE_API_KEY = "ТВОЙ_КЛЮЧ_С_EXCHANGERATE-API.COM"

# ─── LOGGING ──────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ─── STATES ───────────────────────────────────────────────────────
class ConvertState(StatesGroup):
    waiting_amount = State()

# ─── DATA ─────────────────────────────────────────────────────────
FIAT_CURRENCIES = ["USD", "EUR", "RUB", "KZT", "BYN", "UAH", "TRY", "AED", "GBP", "PLN"]
CRYPTO_LIST = ["USDT", "TON", "BTC", "ETH", "SOL", "XRP", "LTC", "DOGE", "USDC"]
CONVERT_FROM = ["RUB", "USD", "EUR", "USDT", "BTC", "TON"]

CRYPTO_IDS = {
    "BTC": "bitcoin", "ETH": "ethereum", "USDT": "tether",
    "SOL": "solana", "XRP": "ripple", "LTC": "litecoin",
    "DOGE": "dogecoin", "USDC": "usd-coin", "TON": "the-open-network"
}

# ─── API FUNCTIONS ────────────────────────────────────────────────
def get_fiat_rate(base: str, target: str = "RUB") -> float | None:
    try:
        url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/{base}"
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("result") == "success":
            return data["conversion_rates"].get(target)
    except:
        pass
    return None

def get_fiat_rates_all(base: str) -> dict | None:
    try:
        url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/latest/{base}"
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("result") == "success":
            return data["conversion_rates"]
    except:
        pass
    return None

def get_crypto_price(symbol: str) -> float | None:
    coin_id = CRYPTO_IDS.get(symbol)
    if not coin_id:
        return None
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd,rub"
        r = requests.get(url, timeout=10)
        data = r.json()
        return data.get(coin_id, {}).get("usd")
    except:
        pass
    return None

def get_all_crypto_prices() -> dict:
    ids = ",".join(CRYPTO_IDS.values())
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd,rub"
        r = requests.get(url, timeout=10)
        return r.json()
    except:
        return {}

# ─── KEYBOARDS ────────────────────────────────────────────────────
def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💱 Курс валюты", callback_data="menu_fiat"),
         InlineKeyboardButton(text="🪙 Курс крипты", callback_data="menu_crypto")],
        [InlineKeyboardButton(text="🔄 Конвертер", callback_data="menu_convert")],
        [InlineKeyboardButton(text="ℹ️ О боте", callback_data="menu_about")],
    ])

def fiat_kb():
    buttons = []
    row = []
    for i, cur in enumerate(FIAT_CURRENCIES):
        row.append(InlineKeyboardButton(text=cur, callback_data=f"fiat_{cur}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def crypto_kb():
    buttons = []
    row = []
    for i, cur in enumerate(CRYPTO_LIST):
        row.append(InlineKeyboardButton(text=cur, callback_data=f"crypto_{cur}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def convert_kb():
    buttons = []
    row = []
    for i, cur in enumerate(CONVERT_FROM):
        row.append(InlineKeyboardButton(text=cur, callback_data=f"convert_{cur}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def back_kb(target="back_main"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data=target)]
    ])

def back_refresh_kb(refresh_data: str, back_data: str = "back_main"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Обновить", callback_data=refresh_data)],
        [InlineKeyboardButton(text="🔙 В меню", callback_data=back_data)],
    ])

# ─── HANDLERS ─────────────────────────────────────────────────────
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для курсов валют и криптовалют.\n"
        "Выбери нужный раздел:",
        reply_markup=main_menu_kb()
    )

@dp.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Выбери нужный раздел:",
        reply_markup=main_menu_kb()
    )

# ─── FIAT ─────────────────────────────────────────────────────────
@dp.callback_query(F.data == "menu_fiat")
async def menu_fiat(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "💱 Выбери валюту:",
        reply_markup=fiat_kb()
    )

@dp.callback_query(F.data.startswith("fiat_"))
async def show_fiat(callback: types.CallbackQuery):
    currency = callback.data.split("_")[1]
    await callback.message.edit_text("⏳ Получаю данные...")

    rates = get_fiat_rates_all(currency)
    if not rates:
        await callback.message.edit_text(
            "❌ Не удалось получить данные. Попробуй позже.",
            reply_markup=back_kb("menu_fiat")
        )
        return

    def r(c): return f"{rates[c]:.4f}" if c in rates else "—"

    text = (
        f"💱 **{currency}** — курс к основным валютам:\n\n"
        f"🇺🇸 USD: `{r('USD')}`\n"
        f"🇪🇺 EUR: `{r('EUR')}`\n"
        f"🇷🇺 RUB: `{r('RUB')}`\n"
        f"🇰🇿 KZT: `{r('KZT')}`\n"
        f"🇧🇾 BYN: `{r('BYN')}`\n"
        f"🇺🇦 UAH: `{r('UAH')}`\n"
        f"🇹🇷 TRY: `{r('TRY')}`\n"
        f"🇦🇪 AED: `{r('AED')}`\n"
        f"🇬🇧 GBP: `{r('GBP')}`\n"
        f"🇵🇱 PLN: `{r('PLN')}`\n"
    )

    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=back_refresh_kb(f"fiat_{currency}", "menu_fiat")
    )

# ─── CRYPTO ───────────────────────────────────────────────────────
@dp.callback_query(F.data == "menu_crypto")
async def menu_crypto(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🪙 Выбери криптовалюту:",
        reply_markup=crypto_kb()
    )

@dp.callback_query(F.data.startswith("crypto_"))
async def show_crypto(callback: types.CallbackQuery):
    symbol = callback.data.split("_")[1]
    coin_id = CRYPTO_IDS.get(symbol)
    if not coin_id:
        await callback.answer("Неизвестная монета")
        return

    await callback.message.edit_text("⏳ Получаю данные...")

    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd,rub,eur"
        r = requests.get(url, timeout=10)
        data = r.json().get(coin_id, {})

        usd = data.get("usd", "—")
        rub = data.get("rub", "—")
        eur = data.get("eur", "—")

        def fmt(v):
            if isinstance(v, float):
                return f"{v:,.2f}" if v > 1 else f"{v:.8f}"
            return str(v)

        text = (
            f"🪙 **{symbol}** — текущий курс:\n\n"
            f"🇺🇸 USD: `{fmt(usd)}`\n"
            f"🇷🇺 RUB: `{fmt(rub)}`\n"
            f"🇪🇺 EUR: `{fmt(eur)}`\n"
        )

        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=back_refresh_kb(f"crypto_{symbol}", "menu_crypto")
        )

    except Exception as e:
        await callback.message.edit_text(
            "❌ Ошибка при получении данных. Попробуй позже.",
            reply_markup=back_kb("menu_crypto")
        )

# ─── CONVERTER ────────────────────────────────────────────────────
@dp.callback_query(F.data == "menu_convert")
async def menu_convert(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🔄 Выбери валюту для конвертации:",
        reply_markup=convert_kb()
    )

@dp.callback_query(F.data.startswith("convert_"))
async def convert_choose(callback: types.CallbackQuery, state: FSMContext):
    currency = callback.data.split("_")[1]
    await state.update_data(convert_from=currency, convert_msg_id=callback.message.message_id)
    await state.set_state(ConvertState.waiting_amount)
    await callback.message.edit_text(
        f"🔄 Конвертация из **{currency}**\n\nВведи сумму:",
        parse_mode="Markdown"
    )

@dp.message(ConvertState.waiting_amount)
async def convert_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Введи число, например: `500`", parse_mode="Markdown")
        return

    data = await state.get_data()
    base = data.get("convert_from", "USD")
    await state.clear()

    await message.answer("⏳ Конвертирую...")

    try:
        # get fiat rates
        fiat_rates = get_fiat_rates_all("USD") or {}

        # get crypto prices
        crypto_data = get_all_crypto_prices()

        def get_usd_value(currency: str, amt: float) -> float | None:
            if currency in ["USD", "EUR", "RUB", "USDT"]:
                if currency == "USD":
                    return amt
                elif currency == "EUR":
                    eur_rate = fiat_rates.get("EUR")
                    return amt / eur_rate if eur_rate else None
                elif currency == "RUB":
                    rub_rate = fiat_rates.get("RUB")
                    return amt / rub_rate if rub_rate else None
                elif currency == "USDT":
                    return amt
            elif currency == "BTC":
                price = crypto_data.get("bitcoin", {}).get("usd")
                return amt * price if price else None
            elif currency == "TON":
                price = crypto_data.get("the-open-network", {}).get("usd")
                return amt * price if price else None
            return None

        usd_value = get_usd_value(base, amount)
        if not usd_value:
            await message.answer("❌ Не удалось получить данные.", reply_markup=back_kb("menu_convert"))
            return

        rub_rate = fiat_rates.get("RUB", 0)
        eur_rate = fiat_rates.get("EUR", 0)
        btc_price = crypto_data.get("bitcoin", {}).get("usd", 0)
        ton_price = crypto_data.get("the-open-network", {}).get("usd", 0)

        def fmt(v):
            if isinstance(v, float):
                return f"{v:,.2f}" if v > 0.01 else f"{v:.8f}"
            return "—"

        results = {
            "RUB": fmt(usd_value * rub_rate) if rub_rate else "—",
            "USD": fmt(usd_value),
            "EUR": fmt(usd_value * eur_rate) if eur_rate else "—",
            "USDT": fmt(usd_value),
            "BTC": fmt(usd_value / btc_price) if btc_price else "—",
            "TON": fmt(usd_value / ton_price) if ton_price else "—",
        }

        lines = "\n".join(
            f"`{amount} {base}` = **{v} {k}**"
            for k, v in results.items()
            if k != base
        )

        await message.answer(
            f"🔄 Результат конвертации:\n\n{lines}",
            parse_mode="Markdown",
            reply_markup=back_kb("menu_convert")
        )

    except Exception as e:
        await message.answer("❌ Ошибка при конвертации.", reply_markup=back_kb("menu_convert"))

# ─── ABOUT ────────────────────────────────────────────────────────
@dp.callback_query(F.data == "menu_about")
async def menu_about(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ **О боте**\n\n"
        "Этот бот показывает курсы валют и криптовалют, "
        "а также конвертирует суммы между ними.\n\n"
        "📊 Данные: ExchangeRate-API + CoinGecko",
        parse_mode="Markdown",
        reply_markup=back_kb("back_main")
    )

# ─── RUN ──────────────────────────────────────────────────────────
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
