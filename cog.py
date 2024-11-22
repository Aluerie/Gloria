from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord.ext import commands, tasks

import config

if TYPE_CHECKING:
    from bot import GloriaBot

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class UserNotFound(commands.BadArgument):
    """For when a matching user cannot be found."""

    def __init__(self, argument: str) -> None:
        self.argument = argument
        super().__init__(f"User {argument!r} not found.")


class TestSteamCog(commands.Cog):
    def __init__(self, bot: GloriaBot) -> None:
        self.bot = bot
        self.check_rp.start()

    @commands.hybrid_command()
    async def user(self, ctx: commands.Context[GloriaBot]) -> None:
        """Show some basic info on a steam user"""
        user = ctx.bot.dota.get_user(config.IRENE_ID64)
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

    @commands.command(aliases=["ping", "hello"])
    async def hi(self, ctx: commands.Context[GloriaBot]) -> None:
        await ctx.send("Hello!")

    @commands.command()
    async def sync(self, ctx: commands.Context[GloriaBot]) -> None:
        await ctx.bot.tree.sync()
        await ctx.send("Sync is done.")

    @tasks.loop(minutes=10)
    async def check_rp(self) -> None:
        log.info("Checking TopSourceGames")
        # random query
        query = "SELECT login FROM valve_devs"
        valve_devs: list[str] = [i for (i,) in await self.bot.pool.fetch(query)]

        live_matches = await self.bot.dota.top_live_matches()
        msg = f"Received {len(live_matches)} live matches and {len(valve_devs)} valve devs"
        log.info(msg)
        await self.bot.glory_channel.send(msg)

    @check_rp.before_loop
    async def check_rp_before_loop(self) -> None:
        await self.bot.wait_until_ready()
        await self.bot.dota.wait_until_ready()
        # print("Steam Client is ready")
        await self.bot.dota.wait_until_gc_ready()

    @check_rp.error
    async def send_error(self, exc: BaseException) -> None:
        log.error("Error in `send_error`: %s", exc, exc_info=exc)
        await self.bot.glory_channel.send(f"{config.ERROR_PING}\n```py\n{exc}```")


async def setup(bot: GloriaBot) -> None:
    await bot.add_cog(TestSteamCog(bot))
