# Lolz Notifier

Telegram-бот для авто-уведомлений покупателей на Lolz Market.

## Что умеет

- мониторит последние продажи через Lolz Market API;
- получает покупателя по item id;
- отправляет сообщение покупателю через Lolz Forum API;
- даёт админ-меню в Telegram;
- хранит шаблон сообщения, интервал проверки и статистику.

## Установка

```powershell
py -m pip install -r requirements.txt
```

## Настройка

Создай `.env`:

```env
TG_BOT_TOKEN=токен_telegram_бота
ADMIN_TG_ID=твой_telegram_id
LOLZ_TOKEN=токен_lolz
LOLZ_USER_ID=твой_lolz_user_id
```

Создай рабочий конфиг из примера:

```powershell
copy config.example.json config.json
```

## Запуск

```powershell
py main.py
```
