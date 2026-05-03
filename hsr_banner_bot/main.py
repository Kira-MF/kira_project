# -*- coding: utf-8 -*-
import asyncio
import logging
from bot import dp, bot
from db import init_db
from scheduler import scheduler_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

async def main():
    await init_db()
    await asyncio.gather(
        dp.start_polling(bot),
        scheduler_loop(bot),
    )

if __name__ == "__main__":
    asyncio.run(main())
