# Currency Bot

Telegram бот для отслеживания курсов валют и криптовалют с конвертером.

## Возможности

- Курсы фиатных валют (USD, EUR, RUB, KZT, BYN, UAH, TRY, AED, GBP, PLN)
- Курсы крипты (BTC, ETH, USDT, SOL, XRP, LTC, DOGE, USDC, TON)
- Конвертер между валютами и криптой
- Кнопка обновить курс
- Inline кнопки

## Установка

```powershell
py -m pip install -r requirements.txt
```

## Настройка

Создай `.env` рядом с `currency_bot.py`:

```env
BOT_TOKEN=твой_токен_от_BotFather
EXCHANGE_API_KEY=ключ_с_exchangerate-api.com
```

## Запуск

```powershell
py currency_bot.py
```

## API

- [ExchangeRate-API](https://exchangerate-api.com) — фиат (бесплатный план)
- [CoinGecko](https://coingecko.com) — крипта (бесплатно без ключа)
