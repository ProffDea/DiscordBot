from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Ping", help="Displays the bot latency")
    async def ping(self, ctx):
        lat = round(self.bot.latency * 1000)
        await ctx.send("%sms" % (lat))

def setup(bot):
    bot.add_cog(Utility(bot))