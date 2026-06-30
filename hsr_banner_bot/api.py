import asyncio
# -*- coding: utf-8 -*-
import aiohttp
import logging
from datetime import datetime

log = logging.getLogger(__name__)

API_URL = "https://api.ennead.cc/mihoyo/starrail/calendar"

ELEMENTS = {
    "1": "Физика",
    "2": "Огонь",
    "4": "Лёд",
    "8": "Молния",
    "16": "Ветер",
    "32": "Квант",
    "64": "Мнимое",
}


CHAR_NAMES_RU = {
    "Silver Wolf LV.999": "Серебряный Волк ур.999",
    "Silver Wolf": "Серебряный Волк",
    "The Dahlia": "Далия",
    "Castorice": "Касторис",
    "Firefly": "Светлячок",
    "Evanescia": "Эванесция",
    "Tribbie": "Трибби",
    "Sunday": "Воскресенье",
    "Feixiao": "Фэйсяо",
    "Gallagher": "Галлахер",
    "Xueyi": "Сюэи",
    "Hook": "Крюк",
    "Guinaifen": "Гуйнайфэнь",
    "Lynx": "Рысь",
    "Sushang": "Сушан",
    "Acheron": "Ахерон",
    "Sparkle": "Искра",
    "Robin": "Робин",
    "Boothill": "Бутхилл",
    "Firefly": "Светлячок",
    "Jade": "Жадеит",
    "Yunli": "Юньли",
    "Feixiao": "Фэйсяо",
    "Lingsha": "Линша",
    "Rappa": "Раппа",
    "Fugue": "Фуга",
    "Aglaea": "Аглая",
    "The Herta": "Герта",
    "Hyacine": "Гиацин",
    "Mydei": "Мидеи",
    "Tribbie": "Трибби",
    "Cipher": "Шифр",
    "Castorice": "Касторис",
    "Anaxa": "Анакса",
    "Phainon": "Фэйнон",
    "Ashveil": "Эшвейл",
    "Mortenax Blade": "Клинок Мортенакс",
}

def translate_name(name: str) -> str:
    return CHAR_NAMES_RU.get(name, name)


async def get_banners() -> dict:
    """Получить текущие баннеры и события из API (3 попытки)."""
    for attempt in range(3):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json(content_type=None)
                        return data
                    else:
                        log.warning(f"API вернул статус {resp.status}")
        except Exception as e:
            log.warning(f"Попытка {attempt+1}/3 не удалась: {e}")
            await asyncio.sleep(3)
    log.error("Все попытки запроса к API исчерпаны")
    return {}

def parse_banners(data: dict) -> list:
    """Распарсить баннеры из ответа API."""
    banners = []

    for banner in data.get("banners", []):
        characters = banner.get("characters", [])
        light_cones = banner.get("light_cones", [])

        if characters:
            banner_type = "character"
            items = characters
        elif light_cones:
            banner_type = "lightcone"
            items = light_cones
        else:
            continue

        # Берем иконку первого 5* персонажа
        image = ""
        for item in items:
            if item.get("rarity") == 5:
                image = item.get("icon", "")
                break

        banners.append({
            "type": banner_type,
            "version": banner.get("version", ""),
            "items": items,
            "image": image,
            "start": banner.get("start_time"),
            "end": banner.get("end_time"),
        })

    return banners

def format_time(ts) -> str:
    """Форматировать timestamp в читаемую дату."""
    if not ts:
        return "Неизвестно"
    dt = datetime.fromtimestamp(ts)
    days_left = (dt - datetime.now()).days
    if days_left < 0:
        return f"{dt.strftime('%d.%m.%Y')} (завершен)"
    elif days_left == 0:
        return f"{dt.strftime('%d.%m.%Y')} (сегодня!)"
    return f"{dt.strftime('%d.%m.%Y')} ({days_left} дн.)"

def format_banner_message(banners: list) -> str:
    """Отформатировать сообщение о баннерах персонажей."""
    char_banners = [b for b in banners if b["type"] == "character"]

    if not char_banners:
        return "❌ Нет данных о текущих баннерах."

    lines = ["🌟 *Текущие баннеры Honkai: Star Rail*\n"]

    for i, banner in enumerate(char_banners, 1):
        items = banner["items"]
        five_stars = [x for x in items if x.get("rarity") == 5]
        four_stars = [x for x in items if x.get("rarity") == 4]
        end_str = format_time(banner.get("end"))

        lines.append("━━━━━━━━━━━━━━━━")
        lines.append(f"✦ *Фаза {i} - Версия {banner['version']}*")
        lines.append(f"🗓 До: {end_str}\n")

        if five_stars:
            lines.append("⭐ *5-звёздочные:*")
            for char in five_stars:
                lines.append(f"  • {char['name']}")

        if four_stars:
            lines.append("\n💫 *4-звёздочные:*")
            for char in four_stars:
                lines.append(f"  • {char['name']}")

        lines.append("")

    return "\n".join(lines)

def format_lightcone_message(banners: list) -> str:
    """Отформатировать сообщение о баннерах световых конусов."""
    lc_banners = [b for b in banners if b["type"] == "lightcone"]

    if not lc_banners:
        return "❌ Нет данных о баннерах световых конусов."

    lines = ["✨ *Баннеры световых конусов*\n"]

    for i, banner in enumerate(lc_banners, 1):
        items = banner["items"]
        five_stars = [x for x in items if x.get("rarity") == 5]
        four_stars = [x for x in items if x.get("rarity") == 4]
        end_str = format_time(banner.get("end"))

        lines.append("━━━━━━━━━━━━━━━━")
        lines.append(f"✦ *Фаза {i} - Версия {banner['version']}*")
        lines.append(f"🗓 До: {end_str}\n")

        if five_stars:
            lines.append("⭐ *5-звёздочные:*")
            for lc in five_stars:
                lines.append(f"  • {lc['name']}")

        if four_stars:
            lines.append("\n💫 *4-звёздочные:*")
            for lc in four_stars:
                lines.append(f"  • {lc['name']}")

        lines.append("")

    return "\n".join(lines)
def get_banner_image(banners: list, banner_type: str = "character") -> str:
    """Получить URL иконки первого 5* из баннера."""
    for banner in banners:
        if banner["type"] == banner_type and banner.get("image"):
            return banner["image"]
    return ""
