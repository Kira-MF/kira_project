# Similar Parser

Парсер похожих Telegram каналов. Две версии на выбор.

## Версии

### similar_parser.py — через Telethon API
- Нужны `api_id` и `api_hash` от my.telegram.org
- Работает без Telegram Premium
- Быстрее и стабильнее

### similar_parser_web.py — через web.telegram.org + Playwright
- Нужен Telegram Premium
- Не нужны api_id/api_hash
- Работает через браузер

## Установка

```
py -m pip install -r requirements.txt
py -m playwright install chromium
```

## Настройка

**similar_parser.py:**
```python
API_ID   = 12345678       # с my.telegram.org
API_HASH = "твой_хэш"
```

**similar_parser_web.py:**
Авторизуйся в web.telegram.org через браузер Chromium перед запуском.

## Запуск

```
py similar_parser.py
```
или
```
py similar_parser_web.py
```

## Результат

Сохраняет список похожих каналов в `similar_channels.txt`.
