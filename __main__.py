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
log.setLevel(logging.INFO)


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
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
        self.steam = steam.Client()  # attach a steam.Client instance to the bot

    async def on_ready(self) -> None:
        await self.steam.wait_until_ready()
        print("Ready")

    @override
    async def setup_hook(self) -> None:
        print("hi")
        self.check_rp.start()
        print("wtf")

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
        log.info("Checking Rich Presence")
        user = self.steam.get_user(config.IRENE_ID64)

        if not user:
            log.info("No user in cache")
        elif rp := user.rich_presence:
            log.info("Irene's RP status = %s", rp.get("status"))
        else:
            log.info("Irene's RP is None")

    @check_rp.before_loop
    async def check_rp_before_loop(self) -> None:
        # await self.wait_until_ready()
        # await self.steam.wait_until_ready() # bugged - NEVER HAPPENS
        pass


class UserNotFound(commands.BadArgument):
    """For when a matching user cannot be found"""

    def __init__(self, argument: str) -> None:
        self.argument = argument
        super().__init__(f"User {argument!r} not found.")


bot = DiscordBot()


@bot.hybrid_command()
async def user(ctx: commands.Context[DiscordBot]) -> None:
    """Show some basic info on a steam user"""
    user = ctx.bot.steam.get_user(config.IRENE_ID64)
    if user is None:
        await ctx.reply("Irene is None :c")
        return

    embed = discord.Embed(description=user.name)
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="64 bit ID:", value=str(user.id64))
    embed.add_field(name="Currently playing:", value=f"{user.app or 'Nothing'}")
    # embed.add_field(name="Friends:", value=len(await user.friends()))
    embed.add_field(name="Apps:", value=len(await user.apps()))
    await ctx.reply(f"Info on {user.name}", embed=embed)


@bot.command(aliases=["ping", "hello"])
async def hi(ctx: commands.Context[DiscordBot]) -> None:
    await ctx.send("Hello!")


@bot.command()
async def sync(ctx: commands.Context[DiscordBot]) -> None:
    await ctx.bot.tree.sync()
    await ctx.send("Sync is done.")


async def main() -> None:
    async with bot:
        await bot.start(config.DISCORD_TOKEN, config.STEAM_USERNAME, config.STEAM_PASSWORD)


with setup_logging():
    asyncio.run(main())
