import os
import random
import discord
from discord.ext import commands
from discord import slash_command

from src import config


# Add cooldowns/coroutines
# Add checks for dm messages
class Webhook(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Checks current context for webhooks.
    # If no webhook matching config hook name, create new webhook.
    # Returns webhook object
    @staticmethod
    async def grab(ctx: discord.ApplicationContext):
        webhooks = await ctx.channel.webhooks()
        imgs = os.listdir("src/images/webhook")
        if not imgs:
            img = "Default"
            av = None
        else:
            img = random.choice(imgs)
            with open("src/images/webhook/%s" % img, "rb") as f:
                av = f.read()
        webhook = None
        if webhooks:
            for wh in webhooks:
                if wh.name == config.get("HOOK_NAME"):
                    webhook = wh
                    break
        if not webhooks or not webhook:
            webhook = await ctx.channel.create_webhook(
                name=config.get("HOOK_NAME"),
                avatar=av
            )
        return webhook

    @commands.command(name="talk", enabled=False)
    async def talk(self, ctx: discord.ApplicationContext):
        webhook = await self.grab(ctx)
        await webhook.send("Hello")

    #@slash_command(name="talk")
    async def slash_talk(self, ctx: discord.ApplicationContext):
        webhook = await self.grab(ctx)
        await webhook.respond("Hello")


def setup(bot):
    bot.add_cog(Webhook(bot))
