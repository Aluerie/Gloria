from __future__ import annotations

import asyncio
import logging
import sys
from typing import TYPE_CHECKING, Any, override

import discord
from discord.ext import commands

# from steam import Client
from steam.ext.dota2 import Client

import config

if TYPE_CHECKING:
    import asyncpg

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class GloriaBot(commands.Bot):
    def __init__(self, pool: asyncpg.Pool[asyncpg.Record]) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=discord.Intents.default(),
            description="A simple bot that can get steam user info",
            activity=discord.Streaming(
                name="\N{YELLOW HEART} say hi @me",
                url="https://www.twitch.tv/irene_adler__",
            ),
            allowed_mentions=discord.AllowedMentions(roles=True, replied_user=False, everyone=False),
        )
        self.dota = Client()  # attach a steam.Client instance to the bot
        self.pool = pool

    @discord.utils.cached_property
    def glory_channel(self) -> discord.TextChannel:
        return self.get_channel(config.CHANNEL_ID)  # pyright: ignore[reportReturnType]  # known channel ID

    async def on_ready(self) -> None:
        await self.glory_channel.send("Hey, I'm reloaded.")

    @override
    async def setup_hook(self) -> None:
        await self.load_extension("cog")

    @override
    async def start(self) -> None:
        await asyncio.gather(
            super().start(config.DISCORD_TOKEN),
            self.dota.login(config.STEAM_USERNAME, config.STEAM_PASSWORD),
        )  # start the client and bot concurrently

    @override
    async def close(self) -> None:
        await self.dota.close()  # make sure to close the client when we close the discord bot
        await super().close()

    @override
    async def on_error(self: GloriaBot, event: str, *args: Any, **kwargs: Any) -> None:
        (_exception_type, exc, _traceback) = sys.exc_info()
        log.error("`bot.on_error`: %s", exc, exc_info=exc)
        await self.glory_channel.send(f"{config.ERROR_PING} `bot.on_error`\n```py\n{exc}```")

    @override
    async def on_command_error(self, ctx: commands.Context[GloriaBot], exc: commands.CommandError) -> None:
        log.error("`bot.on_error`: %s", exc, exc_info=exc)
        await ctx.send(f"{config.ERROR_PING} `bot.on_error`\n```py\n{exc}```")
