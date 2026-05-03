# -*- coding: utf-8 -*-
import asyncio
import logging
from datetime import datetime
from aiogram import Bot
from api import get_banners, parse_banners
from db import get_all_users, get_subscriptions

log = logging.getLogger(__name__)

CHECK_INTERVAL = 60 * 60 * 2  # каждые 2 часа
last_banner_ids = set()

def get_banner_id(banner: dict) -> str:
    """Уникальный ID баннера - версия + тип."""
    items = banner.get("items", [])
    five_stars = [i.get("name", "") for i in items if isinstance(i, dict) and i.get("rarity") == 5]
    return f"{banner.get('version', '')}_{banner.get('type', '')}_{','.join(sorted(five_stars))}"

def get_five_star_names(banner: dict) -> str:
    """Получить имена 5* персонажей из баннера."""
    items = banner.get("items", [])
    names = [i.get("name", "") for i in items if isinstance(i, dict) and i.get("rarity") == 5]
    return ", ".join(names) or "Неизвестно"

async def check_and_notify(bot: Bot):
    """Проверить баннеры и уведомить пользователей."""
    global last_banner_ids

    data = await get_banners()
    banners = parse_banners(data)

    if not banners:
        return

    current_ids = {get_banner_id(b) for b in banners}

    # Новые баннеры
    new_banners = [b for b in banners if get_banner_id(b) not in last_banner_ids]

    # Баннеры заканчивающиеся через 24 часа
    if last_banner_ids:
        ending_soon = []
        for b in banners:
            end_ts = b.get("end", 0)
            if end_ts:
                hours_left = (end_ts - datetime.now().timestamp()) / 3600
                if 0 < hours_left <= 24:
                    ending_soon.append(b)

        if ending_soon:
            users = await get_all_users()
            for user_id in users:
                try:
                    lines = ["⚠️ **Баннеры заканчиваются через 24 часа:**\n"]
                    for b in ending_soon:
                        lines.append(f"• {get_five_star_names(b)}")
                    await bot.send_message(user_id, "\n".join(lines), parse_mode="Markdown")
                except Exception as e:
                    log.warning(f"Не удалось отправить уведомление {user_id}: {e}")
                await asyncio.sleep(0.1)

    # Уведомляем о новых баннерах
    if new_banners and last_banner_ids:
        users = await get_all_users()
        for user_id in users:
            try:
                lines = ["🎉 **Новые баннеры запущены!**\n"]
                for b in new_banners:
                    if b["type"] == "character":
                        lines.append(f"👤 Версия {b.get('version', '')}: {get_five_star_names(b)}\n")

                await bot.send_message(user_id, "\n".join(lines), parse_mode="Markdown")

                # Проверяем подписки
                subs = await get_subscriptions(user_id)
                if subs:
                    for b in new_banners:
                        items = b.get("items", [])
                        chars_lower = [i.get("name", "").lower() for i in items if isinstance(i, dict)]
                        for sub in subs:
                            if sub.lower() in chars_lower:
                                await bot.send_message(
                                    user_id,
                                    f"🔔 **{sub.capitalize()}** появился на баннере!\nНе пропусти!",
                                    parse_mode="Markdown"
                                )
            except Exception as e:
                log.warning(f"Не удалось отправить уведомление {user_id}: {e}")
            await asyncio.sleep(0.1)

    last_banner_ids = current_ids

async def scheduler_loop(bot: Bot):
    """Основной цикл планировщика."""
    log.info("Планировщик уведомлений запущен!")
    while True:
        try:
            await check_and_notify(bot)
        except Exception as e:
            log.error(f"Ошибка в планировщике: {e}")
        await asyncio.sleep(CHECK_INTERVAL)
