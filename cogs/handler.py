from discord.ext import commands
import sys
import traceback

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, "on_error"):
            return
        _ignored = (commands.CommandNotFound)
        error = getattr(error, "original", error)
        if isinstance(error, _ignored):
            return
        else:
            print("Ignoring exception in command %s:" % (ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))