# Add custom help command
# Add error handling
# Add Lavalink features
# Add help messages to functions
# Add profiles
# Add pool for database
# Add global cooldowns
# Add global checks

import os
import sys
import traceback
import discord
from discord.ext import commands

from src import config, log

if not os.path.exists("logs"):
    os.mkdir("logs")
log.start()

def get_intents():
    intents = discord.Intents.all()
    return intents

bot = commands.Bot(command_prefix=commands.when_mentioned_or(config.get("DEFAULT_PREFIX")),
                   descritpion=config.get("BOT_DESCRIPTION"),
                   case_insensitive=True,
                   intents=get_intents())
bot.version = "1.3.1"

modules = "cogs"
for file in os.listdir(modules):
    if file.endswith(".py"):
        try:
            bot.load_extension("%s.%s" % (modules, file[:-3]))
        except Exception as error:
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @bot.event
    async def on_ready():
        watching = discord.Activity(type=discord.ActivityType.watching,
                                name=config.get("BOT_PRESENCE"))
        await bot.change_presence(activity=watching)

bot.run(config.get("BOT_TOKEN"))