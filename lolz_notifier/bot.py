# -*- coding: utf-8 -*-
import asyncio
import json
import os
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
ADMIN_ID     = int(os.getenv("ADMIN_TG_ID", "0"))
CONFIG_FILE  = "config.json"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TG_BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

class TemplateState(StatesGroup):
    waiting_template = State()
    waiting_interval = State()

# HELPERS
def load_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить шаблон", callback_data="edit_template")],
        [InlineKeyboardButton(text="⏱ Интервал проверки", callback_data="edit_interval")],
        [InlineKeyboardButton(text="📋 Текущий шаблон",   callback_data="show_template")],
        [InlineKeyboardButton(text="📊 Статистика",        callback_data="show_stats")],
        [InlineKeyboardButton(text="👥 Список покупателей", callback_data="show_buyers")],
        [InlineKeyboardButton(text="🗑 Очистить список",    callback_data="clear_buyers")],
    ])

# COMMANDS
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Нет доступа.")
        return
    await state.clear()
    await message.answer(
        "👋 Привет! Я помогаю управлять авто-уведомлениями покупателей на лолзе.\n\n"
        "Выбери действие:",
        reply_markup=main_kb()
    )

@dp.callback_query(F.data == "show_template")
async def show_template(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    config = load_config()
    template = config.get("message_template", "Не задан")
    await callback.message.edit_text(
        f"📋 Текущий шаблон сообщения:\n\n{template}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
        ])
    )

@dp.callback_query(F.data == "show_stats")
async def show_stats(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    config = load_config()
    sent_count = len(config.get("sent_to", []))
    interval   = config.get("check_interval", 60)
    await callback.message.edit_text(
        f"📊 Статистика:\n\n"
        f"📨 Отправлено уведомлений: **{sent_count}**\n"
        f"⏱ Интервал проверки: **{interval} сек**",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
        ])
    )

@dp.callback_query(F.data == "show_buyers")
async def show_buyers(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    config = load_config()
    sent_to = config.get("sent_to", [])
    if not sent_to:
        text = "👥 Список покупателей пуст."
    else:
        ids = "\n".join([f"• {uid}" for uid in sent_to])
        text = f"👥 Покупатели которым уже отправлено ({len(sent_to)}):\n\n{ids}"
    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
        ])
    )

@dp.callback_query(F.data == "clear_buyers")
async def clear_buyers_confirm(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    await callback.message.edit_text(
        "⚠️ Ты уверен что хочешь очистить список?\n\n"
        "После очистки бот снова напишет всем покупателям из истории продаж!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, очистить", callback_data="clear_buyers_yes")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")],
        ])
    )

@dp.callback_query(F.data == "clear_buyers_yes")
async def clear_buyers_yes(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    config = load_config()
    config["sent_to"] = []
    save_config(config)
    await callback.message.edit_text(
        "✅ Список очищен! Бот снова напишет покупателям при следующей проверке.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
        ])
    )

@dp.callback_query(F.data == "edit_template")
async def edit_template(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(TemplateState.waiting_template)
    config   = load_config()
    template = config.get("message_template", "")
    await callback.message.edit_text(
        f"✏️ Введи новый шаблон сообщения.\n\n"
        f"Текущий:\n{template}"
    )

@dp.message(TemplateState.waiting_template)
async def save_template(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    config = load_config()
    config["message_template"] = message.text
    save_config(config)
    await state.clear()
    await message.answer(
        "✅ Шаблон обновлён!\n\n"
        f"Новый шаблон:\n{message.text}",
        reply_markup=main_kb()
    )

@dp.callback_query(F.data == "edit_interval")
async def edit_interval(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(TemplateState.waiting_interval)
    config   = load_config()
    interval = config.get("check_interval", 60)
    await callback.message.edit_text(
        f"⏱ Введи интервал проверки продаж в секундах.\n\n"
        f"Текущий: {interval} сек\n"
        f"Минимум: 30 сек (лимит API лолза)"
    )

@dp.message(TemplateState.waiting_interval)
async def save_interval(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    try:
        interval = int(message.text)
        if interval < 30:
            await message.answer("❌ Минимум 30 секунд (лимит API лолза)!")
            return
    except ValueError:
        await message.answer("❌ Введи число!")
        return

    config = load_config()
    config["check_interval"] = interval
    save_config(config)
    await state.clear()
    await message.answer(
        f"✅ Интервал обновлён: {interval} сек",
        reply_markup=main_kb()
    )

@dp.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Выбери действие:",
        reply_markup=main_kb()
    )

# RUN
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
