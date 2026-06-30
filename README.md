# MuiKira Projects

Сборник моих Python-проектов: Telegram/Discord боты, парсеры и небольшие API-интеграции.

> Сейчас проекты лежат в одном репозитории как общий портфель. Для удобства просмотра каждый проект можно вынести в отдельный репозиторий без изменений логики.

## Проекты

| Проект | Что делает | Стек |
|---|---|---|
| [currency_bot](./currency_bot) | Telegram-бот курсов валют и крипты | aiogram, requests |
| [shop_bot](./shop_bot) | Telegram-магазин с балансом, каталогом и админкой | aiogram |
| [similar_parser](./similar_parser) | Парсер похожих Telegram-каналов | Telethon, Playwright |
| [Jojo_DS_BOT](./Jojo_DS_BOT) | Discord RPG-бот по JoJo | discord.py |
| [lolz_notifier](./lolz_notifier) | Уведомления покупателям Lolz Market | aiogram, aiohttp |
| [hsr_banner_bot](./hsr_banner_bot) | Трекер баннеров Honkai: Star Rail | aiogram, aiohttp, aiosqlite |

## Общий запуск

```powershell
cd project_folder
py -m pip install -r requirements.txt
copy .env.example .env
py main.py
```

У некоторых проектов точка входа называется не `main.py`, а по имени проекта. Это указано в README внутри папки.

## Что не хранится в репозитории

- токены и ключи;
- `.env`;
- базы данных;
- Telegram session-файлы;
- `__pycache__` и `.pyc`.

Для настройки есть `.env.example` и `config.example.json`.
