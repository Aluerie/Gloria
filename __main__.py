from __future__ import annotations

import asyncio
import logging
import sys
from typing import override

import discord
import steam
from discord.ext import commands, tasks

import config
from logs import setup_logging

if sys.platform == "win32":
    # wtf why it bugs out without it
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=discord.Intents.default(),
            description="A simple bot that can get steam user info",
        )
        self.steam = steam.Client()  # attach a steam.Client instance to the bot

    async def on_ready(self) -> None:
        await self.steam.wait_until_ready()
        print("Ready")

    @override
    async def setup_hook(self) -> None:
        self.check_rp.start()

    @override
    async def start(self, token: str, username: str, password: str) -> None:
        await asyncio.gather(
            super().start(token),
            self.steam.login(username, password),
        )  # start the client and bot concurrently

    @override
    async def close(self) -> None:
        await self.steam.close()  # make sure to close the client when we close the discord bot
        await super().close()

    @tasks.loop(minutes=10)
    async def check_rp(self) -> None:
        log.debug("Checking Rich Presence")
        user = self.steam.get_user(config.IRENE_ID64)
        if user:
            print(user.rich_presence)

        if self.check_rp.current_loop == 2:
            await self.tree.sync()

    @check_rp.before_loop
    async def check_rp_before_loop(self) -> None:
        await self.wait_until_ready()
        await self.steam.wait_until_ready()


class UserNotFound(commands.BadArgument):
    """For when a matching user cannot be found"""

    def __init__(self, argument: str) -> None:
        self.argument = argument
        super().__init__(f"User {argument!r} not found.")


bot = DiscordBot()


@bot.tree.command()
async def user(interaction: discord.Interaction[DiscordBot]) -> None:
    """Show some basic info on a steam user"""
    user = await interaction.client.steam.fetch_user(config.IRENE_ID64)
    embed = discord.Embed(description=user.name)
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="64 bit ID:", value=str(user.id64))
    embed.add_field(name="Currently playing:", value=f"{user.app or 'Nothing'}")
    embed.add_field(name="Friends:", value=len(await user.friends()))
    embed.add_field(name="Apps:", value=len(await user.apps()))
    await interaction.response.send_message(f"Info on {user.name}", embed=embed)


async def main() -> None:
    async with bot:
        await bot.start(config.DISCORD_TOKEN, config.STEAM_USERNAME, config.STEAM_PASSWORD)


with setup_logging():
    asyncio.run(main())
