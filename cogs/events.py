import discord
from discord.ext import commands

from src import config

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(Events(bot))