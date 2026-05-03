# MuiKira Projects

Мои проекты — боты и скрипты на Python.

## Проекты

| Проект | Описание | Стек |
|--------|----------|------|
| [currency_bot](./currency_bot) | Telegram бот курсов валют и крипты | aiogram, ExchangeRate-API, CoinGecko |
| [shop_bot](./shop_bot) | Telegram магазин бот с балансом и товарами | aiogram |
| [similar_parser](./similar_parser) | Парсер похожих Telegram каналов | Telethon, Playwright |
| [jojo_ds_bot](./Jojo_DS_BOT) | Discord JoJo бот со стендами и эволюциями | discord.py |
| [lolz_notifier](./lolz_notifier) | Авто-уведомления покупателей на Lolz Market | aiogram, aiohttp, Lolz API |
| [hsr_banner_bot](./hsr_banner_bot) | Telegram трекер баннеров Honkai: Star Rail | aiogram, aiohttp, aiosqlite |

## Стек

- Python 3.10+
- aiogram 3.x
- discord.py 2.x
- Telethon / Playwright
- aiohttp / aiosqlite
- REST API интеграции

## Запуск любого проекта

1. Перейди в папку проекта
2. Установи зависимости: `py -m pip install -r requirements.txt`
3. Вставь токен в `.env` файл
4. Запусти: `py main.py`
