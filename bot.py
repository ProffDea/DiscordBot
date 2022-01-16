# Add custom help command
# Add error handling
# Add Lavalink features

import sys
import traceback
import discord
from discord.ext import commands

import bin.config as config

# Look into what intents.default enables
def get_intents():
    intents = discord.Intents.default()
    intents.members = True
    intents.presences = True
    return intents

bot = commands.Bot(command_prefix=config.get("DEFAULT_PREFIX"),
                   descritpion=config.get("BOT_DESCRIPTION"),
                   case_insensitive=True,
                   intents=get_intents())
bot.version = "1.0.0"

# Loop through cogs folder to add each extension instead
mods = (
    "cogs.utility",
)
for module in mods:
    try:
        bot.load_extension(module)
    except Exception as error:
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

bot.run(config.get("BOT_TOKEN"))