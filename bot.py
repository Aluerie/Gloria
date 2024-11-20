from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, override

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
