# Add custom help command
# Add error handling
# Add Lavalink features

import os
import sys
import traceback
import discord
from discord.ext import commands

import src.config as config
import src.log as log

log.start()

def get_intents():
    intents = discord.Intents.all()
    return intents

bot = commands.Bot(command_prefix=config.get("DEFAULT_PREFIX"),
                   descritpion=config.get("BOT_DESCRIPTION"),
                   case_insensitive=True,
                   intents=get_intents())
bot.version = "1.0.0"

modules = "cogs"
for file in os.listdir(modules):
    if file.endswith(".py"):
        try:
            bot.load_extension("%s.%s" % (modules, file[:-3]))
        except Exception as error:
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

bot.run(config.get("BOT_TOKEN"))