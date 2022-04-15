import discord
from discord.ext import commands
from discord.commands import slash_command, Option


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="say",
        description="Repeats the message you want the bot to say."
    )
    async def slash_say(
            self,
            ctx: discord.ApplicationContext,
            message: Option(
                str,
                description="The contents the bot will repeat."
            )
    ):
        await ctx.respond("Success", ephemeral=True)
        await ctx.send(message)


def setup(bot):
    bot.add_cog(Fun(bot))
