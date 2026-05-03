# -*- coding: utf-8 -*-
import asyncio
import logging
from monitor import monitor_loop
from bot import dp, bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

async def main():
    """Запуск монитора и Telegram бота одновременно."""
    await asyncio.gather(
        monitor_loop(),
        dp.start_polling(bot),
    )

if __name__ == "__main__":
    asyncio.run(main())
