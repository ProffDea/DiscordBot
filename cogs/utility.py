from discord.ext import commands

from src import config

class Utility(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Ping", help="Displays the bot latency")
    async def ping(self, ctx):
        lat = round(self.bot.latency * 1000)
        await ctx.send("%sms" % (lat))

    @commands.command(name="Dir")
    async def dire(self, ctx):
        owner_id = config.get("BOT_OWNER")
        nt = type(config.get("BOT_OWNER"))
        if ctx.message.author.id == owner_id:
            y = True
        else:
            y = False
        await ctx.send("%s %s %s" % (owner_id, nt, y))

def setup(bot):
    bot.add_cog(Utility(bot))