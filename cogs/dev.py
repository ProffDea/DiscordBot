from discord.ext import commands

from src import predicates

class Developer(commands.Cog, name="Developer"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="Load", aliases=["L"])
    @commands.check(predicates.is_owners)
    async def load(self, ctx, cog):
        self.bot.load_extension("cogs.%s" % (cog))
        await ctx.send("Done")

    @commands.command(name="Unload", aliases=["U"])
    @commands.check(predicates.is_owners)
    async def unload(self, ctx, cog):
        self.bot.unload_extension("cogs.%s" % (cog))
        await ctx.send("Done")

    @commands.command(name="Reload", aliases=["R"])
    @commands.check(predicates.is_owners)
    async def reload(self, ctx, cog):
        self.bot.unload_extension("cogs.%s" % (cog))
        self.bot.load_extension("cogs.%s" % (cog))
        await ctx.send("Done")

def setup(bot):
    bot.add_cog(Developer(bot))