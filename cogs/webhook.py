from discord.ext import commands
import os
import random

from src import config

# Add cooldowns/coroutines
# Add checks for dm messages
class Webhook(commands.Cog, name="Webhooks"):
    def __init__(self, bot):
        self.bot = bot

    # Checks current context for webhooks.
    # If no webhook matching config hook name, create new webhook.
    # Returns webhook object
    async def grab(ctx):
        webhooks = await ctx.channel.webhooks()
        imgs = os.listdir("src/images/webhook")
        if not imgs:
            img = "Default"
            av = None
        else:
            img = random.choice(imgs)
            with open("src/images/webhook/%s" % (img), "rb") as f:
                av = f.read()
        webhook = None
        if webhooks:
            for wh in webhooks:
                if wh.name == config.get("HOOK_NAME"):
                    webhook = wh
                    break
        if not webhooks or not webhook:
            webhook = await ctx.channel.create_webhook(name=config.get("HOOK_NAME"), avatar=av)
        return webhook

    @commands.command(name="Talk")
    async def talk(self, ctx):
        webhook = await Webhook.grab(ctx)
        await webhook.send("Hello")

def setup(bot):
    bot.add_cog(Webhook(bot))