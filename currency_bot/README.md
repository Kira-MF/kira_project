# Currency Bot

Telegram бот для отслеживания курсов валют и криптовалют с конвертером.

## Возможности

- Курсы фиатных валют (USD, EUR, RUB, KZT, BYN, UAH, TRY, AED, GBP, PLN)
- Курсы крипты (BTC, ETH, USDT, SOL, XRP, LTC, DOGE, USDC, TON)
- Конвертер между валютами и криптой
- Кнопка обновить курс
- Inline кнопки

## Установка

```
py -m pip install -r requirements.txt
```

## Настройка

Открой `currency_bot.py` и вставь:
```python
BOT_TOKEN = "твой токен от @BotFather"
EXCHANGE_API_KEY = "ключ с exchangerate-api.com (бесплатный)"
```

## Запуск

```
py currency_bot.py
```

## API

- [ExchangeRate-API](https://exchangerate-api.com) — фиат (бесплатный план)
- [CoinGecko](https://coingecko.com) — крипта (бесплатно без ключа)
