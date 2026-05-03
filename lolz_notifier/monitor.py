# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import json
import os
import logging
from dotenv import load_dotenv

load_dotenv()

LOLZ_TOKEN   = os.getenv("LOLZ_TOKEN")
LOLZ_USER_ID = os.getenv("LOLZ_USER_ID")
CONFIG_FILE  = "config.json"

MARKET_API = "https://prod-api.lzt.market"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

HEADERS = {
    "Authorization": f"Bearer {LOLZ_TOKEN}",
    "Content-Type": "application/json",
}

def load_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

async def get_recent_sales(session: aiohttp.ClientSession) -> list:
    """Получить список последних продаж (1 страница)."""
    try:
        url = f"{MARKET_API}/user/{LOLZ_USER_ID}/items"
        params = {"show": "paid", "order_by": "pdate_to_down"}
        async with session.get(url, headers=HEADERS, params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("items", [])
            else:
                text = await resp.text()
                log.warning(f"Ошибка при получении продаж: {resp.status} - {text[:200]}")
                return []
    except Exception as e:
        log.error(f"Ошибка запроса продаж: {e}")
        return []

async def get_buyer(session: aiohttp.ClientSession, item_id: int) -> tuple:
    """Получить ID и username покупателя по item_id."""
    try:
        url = f"{MARKET_API}/{item_id}"
        async with session.get(url, headers=HEADERS) as resp:
            if resp.status == 200:
                data = await resp.json(content_type=None)
                item = data.get("item", {})
                buyer = item.get("buyer", {})
                buyer_id = buyer.get("user_id") if buyer else None
                username = buyer.get("username") if buyer else None
                return buyer_id, username
            else:
                return None, None
    except Exception as e:
        log.error(f"Ошибка запроса покупателя: {e}")
        return None, None

async def send_message(session: aiohttp.ClientSession, user_id: int, message: str) -> bool:
    """Отправить личное сообщение покупателю."""
    try:
        url = "https://prod-api.lolz.live/conversations"
        headers = {
            "Authorization": f"Bearer {LOLZ_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "recipient_id": user_id,
            "message_body": message,
            "is_group": False,
        }
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status in [200, 201]:
                log.info(f"Сообщение отправлено пользователю {user_id}")
                return True
            else:
                text = await resp.text()
                log.warning(f"Ошибка отправки: {resp.status} - {text[:200]}")
                return False
    except Exception as e:
        log.error(f"Ошибка отправки сообщения: {e}")
        return False

async def notify_buyer(session: aiohttp.ClientSession, item_id: int):
    """Уведомить покупателя - один раз навсегда."""
    config = load_config()
    sent_to = config.get("sent_to", [])

    buyer_id, username = await get_buyer(session, item_id)
    if not buyer_id:
        log.warning(f"Не удалось получить покупателя для item {item_id}")
        return

    if buyer_id in sent_to:
        return

    template = config.get("message_template", "Спасибо за покупку!")
    message = f"https://lzt.market/{item_id}\n\n{template}"
    success = await send_message(session, buyer_id, message)

    if success:
        log.info(f"Item {item_id} - отправлено @{username} (ID: {buyer_id})")
    else:
        log.warning(f"Item {item_id} - не удалось отправить @{username}")

    # Сохраняем в любом случае чтобы не спамить
    sent_to.append(buyer_id)
    config["sent_to"] = sent_to
    save_config(config)

    await asyncio.sleep(5)

async def monitor_loop():
    """Основной цикл мониторинга продаж."""
    log.info("Монитор продаж запущен!")

    async with aiohttp.ClientSession() as session:
        while True:
            config = load_config()
            interval = config.get("check_interval", 60)

            log.info("Проверяю новые продажи...")
            sales = await get_recent_sales(session)

            for item in sales:
                item_id = item.get("item_id")
                if item_id:
                    await notify_buyer(session, item_id)

            log.info(f"Следующая проверка через {interval} сек...")
            await asyncio.sleep(interval)

if __name__ == "__main__":
    asyncio.run(monitor_loop())
