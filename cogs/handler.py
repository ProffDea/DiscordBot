import logging
from discord.ext import commands
from discord.commands import errors


class CommandErrorHandler(commands.Cog, name="Command Error Handler"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print("on_command_error has been called")
        if hasattr(ctx.command, "on_error"):
            return
        _ignored = (commands.CommandNotFound,)
        error = getattr(error, "original", error)
        if isinstance(error, _ignored):
            return
        else:
            logger = logging.getLogger(
                "bot.%s" % (
                    ctx.command.cog_name if ctx.command.cog_name else "Handler"
                )
            )
            logger.exception(
                "Ignoring exception in %s cog command: %s" % (
                    ctx.command.cog_name, ctx.command
                ),
                exc_info=error
            )


def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
