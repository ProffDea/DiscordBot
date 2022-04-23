import os
import sys
import traceback
import discord
import logging
import datetime
from discord.ext import commands

from src import config, log
from src.postgres import database

if not os.path.exists("logs"):
    os.mkdir("logs")
log.create("discord")
log.create("bot")


def get_intents():
    intents = discord.Intents.all()
    return intents


def get_cogs():
    local_modules = []
    for local_file in os.listdir("cogs"):
        if local_file.endswith(".py"):
            local_modules.append(local_file[:-3])
    return local_modules


bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(config.get("DEFAULT_PREFIX")),
    description=config.get("BOT_DESCRIPTION"),
    case_insensitive=True,
    intents=get_intents()
)
bot.version = "2.3.1"
bot.owner_ids = config.get("BOT_OWNERS")
bot.start_time = datetime.datetime.utcnow()

modules = get_cogs()
for file in modules:
    try:
        bot.load_extension("cogs.%s" % file)
    except Exception as error:
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )


    @bot.event
    async def on_ready():
        await database.base_metadata()

        logger = logging.getLogger("bot")
        logger.info(
            "%s is now online in %s servers" % (
                bot.user.name, len(bot.guilds)
            )
        )
        activity_type = config.get_activity_type()
        activity_message = config.get("ACTIVITY_MESSAGE")
        if activity_type and activity_message:
            activity = discord.Activity(
                type=activity_type,
                name=activity_message
            )
            await bot.change_presence(activity=activity)

bot.run(config.get("BOT_TOKEN"))
