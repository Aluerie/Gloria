from __future__ import annotations

import asyncio
import logging
import sys

from bot import GloriaBot
from database import create_pool
from logs import setup_logging

if sys.platform == "win32":
    # wtf why it bugs out without it
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


async def main() -> None:
    pool = await create_pool()
    async with pool as pool, GloriaBot(pool) as bot:
        await bot.start()


with setup_logging():
    asyncio.run(main())
