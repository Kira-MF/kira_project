# -*- coding: utf-8 -*-
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from api import get_banners, parse_banners, format_banner_message, format_lightcone_message, get_banner_image
from db import add_user, toggle_notifications, get_subscriptions, subscribe_character, unsubscribe_character

load_dotenv()

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")

log = logging.getLogger(__name__)
bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚡ Баннеры персонажей", callback_data="now")],
        [InlineKeyboardButton(text="✨ Световой d1h", callback_data="lightcones")],
        [InlineKeyboardButton(text="📡 Уведомления", callback_data="notifications")],
        [InlineKeyboardButton(text="📋 Подписки", callback_data="my_subs")],
    ])

def back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
    ])

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await add_user(message.from_user.id)
    await message.answer(
        "🚂 **Astral Express**\n"
        "══════════════════\n"
        "Добро пожаловать, Первопроходец!\n\n"
        "Выбери направление:",
        reply_markup=main_kb(),
        parse_mode="Markdown"
    )

@dp.message(Command("now"))
async def cmd_now(message: types.Message):
    await add_user(message.from_user.id)
    msg = await message.answer("⏳ Загружаю данные...")
    data = await get_banners()
    banners = parse_banners(data)
    text = format_banner_message(banners)
    image = get_banner_image(banners, "character")
    await msg.delete()
    if image:
        await message.answer_photo(
            photo=image,
            caption=text,
            parse_mode="Markdown",
            reply_markup=back_kb()
        )
    else:
        await message.answer(text, parse_mode="Markdown", reply_markup=back_kb())

@dp.message(Command("subscribe"))
async def cmd_subscribe(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Использование: /subscribe <имя персонажа>\nПример: /subscribe Acheron")
        return
    character = args[1].strip()
    await subscribe_character(message.from_user.id, character)
    await message.answer(f"✅ Подписался на **{character}**!", parse_mode="Markdown")

@dp.message(Command("unsubscribe"))
async def cmd_unsubscribe(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Использование: /unsubscribe <имя персонажа>")
        return
    character = args[1].strip()
    await unsubscribe_character(message.from_user.id, character)
    await message.answer(f"✅ Отписался от **{character}**!", parse_mode="Markdown")

@dp.callback_query(F.data == "now")
async def cb_now(callback: types.CallbackQuery):
    await callback.message.edit_text("⏳ Загружаю данные...")
    data = await get_banners()
    banners = parse_banners(data)
    text = format_banner_message(banners)
    image = get_banner_image(banners, "character")
    await callback.message.delete()
    if image:
        await callback.message.answer_photo(
            photo=image,
            caption=text,
            parse_mode="Markdown",
            reply_markup=back_kb()
        )
    else:
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=back_kb())

@dp.callback_query(F.data == "lightcones")
async def cb_lightcones(callback: types.CallbackQuery):
    await callback.message.edit_text("⏳ Загружаю данные...")
    data = await get_banners()
    banners = parse_banners(data)
    text = format_lightcone_message(banners)
    image = get_banner_image(banners, "lightcone")
    await callback.message.delete()
    if image:
        await callback.message.answer_photo(
            photo=image,
            caption=text,
            parse_mode="Markdown",
            reply_markup=back_kb()
        )
    else:
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=back_kb())

@dp.callback_query(F.data == "notifications")
async def cb_notifications(callback: types.CallbackQuery):
    new_state = await toggle_notifications(callback.from_user.id)
    status = "включены 🔔" if new_state else "выключены 🔕"
    await callback.answer(f"Уведомления {status}", show_alert=True)

@dp.callback_query(F.data == "my_subs")
async def cb_my_subs(callback: types.CallbackQuery):
    subs = await get_subscriptions(callback.from_user.id)
    if not subs:
        text = "⭐ У тебя нет подписок.\n\nИспользуй /subscribe <имя> чтобы подписаться на персонажа."
    else:
        text = "⭐ **Твои подписки:**\n\n" + "\n".join([f"• {s.capitalize()}" for s in subs])
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=back_kb())

@dp.callback_query(F.data == "back_main")
async def cb_back_main(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "🚂 **Astral Express**\n══════════════════\nДобро пожаловать, Первопроходец!\n\nВыбери направление:",
        reply_markup=main_kb(),
        parse_mode="Markdown"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
