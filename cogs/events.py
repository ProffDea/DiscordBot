from discord.ext import commands

from src.postgres import database
from src.modules import snipe, voice_roles


class Events(commands.Cog, name="Events"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        async with database.async_session() as session:
            await voice_roles.check(session, member, before, after)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        async with database.async_session() as session:
            await snipe.store(session, message, False)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        async with database.async_session() as session:
            await snipe.store(session, before, True)


def setup(bot):
    bot.add_cog(Events(bot))
