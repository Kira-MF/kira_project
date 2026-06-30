# Similar Parser

Парсер похожих Telegram каналов. Две версии на выбор.

## Версии

### similar_parser.py - через Telethon API
- Нужны `api_id` и `api_hash` от my.telegram.org
- Работает без Telegram Premium
- Быстрее и стабильнее

### similar_parser_web.py - через web.telegram.org + Playwright
- Нужен Telegram Premium
- Не нужны api_id/api_hash
- Работает через браузер

## Установка

```powershell
py -m pip install -r requirements.txt
py -m playwright install chromium
```

## Настройка

**similar_parser.py:**
Создай `.env`:

```env
API_ID=12345678
API_HASH=твой_хэш_с_my.telegram.org
```

**similar_parser_web.py:**
Авторизуйся в web.telegram.org через браузер Chromium перед запуском.

## Запуск

```powershell
py similar_parser.py
```
или
```powershell
py similar_parser_web.py
```

## Результат

Сохраняет список похожих каналов в `similar_channels.txt`.
