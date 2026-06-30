# MuiKira Projects

Навигация по моим Python-проектам: Telegram/Discord боты, парсеры и небольшие API-интеграции.

Основные проекты вынесены в отдельные репозитории, чтобы их было проще смотреть по одному.

## Проекты

| Проект | Что делает | Стек |
|---|---|---|
| [currency-bot](https://github.com/Kira-MF/currency-bot) | Telegram-бот курсов валют и крипты | aiogram, requests |
| [shop-bot](https://github.com/Kira-MF/shop-bot) | Telegram-магазин с балансом, каталогом и админкой | aiogram |
| [similar-parser](https://github.com/Kira-MF/similar-parser) | Парсер похожих Telegram-каналов | Telethon, Playwright |
| [jojo-discord-bot](https://github.com/Kira-MF/jojo-discord-bot) | Discord RPG-бот по JoJo | discord.py |
| [lolz-notifier](https://github.com/Kira-MF/lolz-notifier) | Уведомления покупателям Lolz Market | aiogram, aiohttp |
| [hsr-banner-bot](https://github.com/Kira-MF/hsr-banner-bot) | Трекер баннеров Honkai: Star Rail | aiogram, aiohttp, aiosqlite |

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
