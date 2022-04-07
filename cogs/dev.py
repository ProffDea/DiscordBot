import discord
import logging
from discord.ext import commands
from discord import slash_command, Option

from bot import get_cogs


class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="load")
    @commands.is_owner()
    async def load(self, ctx, cog: str):
        self.bot.load_extension("cogs.%s" % cog)
        logger = logging.getLogger("bot.Developer")
        logger.info("%s cog has been loaded" % cog)
        await ctx.send("Success")

    @commands.command(name="unload")
    @commands.is_owner()
    async def unload(self, ctx, cog: str):
        self.bot.unload_extension("cogs.%s" % cog)
        logger = logging.getLogger("bot.Developer")
        logger.info("%s cog has been unloaded" % cog)
        await ctx.send("Success")

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx, cog: str):
        try:
            self.bot.unload_extension("cogs.%s" % cog)
        except discord.errors.ExtensionNotLoaded:
            pass
        self.bot.load_extension("cogs.%s" % cog)
        logger = logging.getLogger("bot.Developer")
        logger.info("%s cog has been reloaded" % cog)
        await ctx.send("Success")

    @slash_command(
        name="load",
        description="Load a module that the bot does not currently have loaded in yet."
    )
    @commands.is_owner()
    async def slash_load(
        self, ctx, cog: Option(
            str,
            name="module",
            description="The modules that involve all of the bot's features.",
            choices=get_cogs()
        )
    ):
        self.bot.load_extension("cogs.%s" % cog)
        logger = logging.getLogger("bot.Developer")
        logger.info("%s cog has been loaded" % cog)
        await ctx.respond("Success", ephemeral=True)

    @slash_command(
        name="unload",
        description="Unload a module that the bot has loaded in."
    )
    @commands.is_owner()
    async def slash_unload(
        self, ctx, cog: Option(
            str,
            name="module",
            description="The modules that involve all of the bot's features.",
            choices=get_cogs()
        )
    ):
        self.bot.unload_extension("cogs.%s" % cog)
        logger = logging.getLogger("bot.Developer")
        logger.info("%s cog has been unloaded" % cog)
        await ctx.respond("Success", ephemeral=True)

    @slash_command(
        name="reload",
        description="Reload a module to refresh it."
    )
    @commands.is_owner()
    async def slash_reload(
        self, ctx, cog: Option(
            str,
            name="module",
            description="The modules that involve all of the bot's features.",
            choices=get_cogs()
        )
    ):
        try:
            self.bot.unload_extension("cogs.%s" % cog)
        except discord.errors.ExtensionNotLoaded:
            pass
        self.bot.load_extension("cogs.%s" % cog)
        logger = logging.getLogger("bot.Developer")
        logger.info("%s cog has been reloaded" % cog)
        await ctx.respond("Success", ephemeral=True)


def setup(bot):
    bot.add_cog(Developer(bot))
