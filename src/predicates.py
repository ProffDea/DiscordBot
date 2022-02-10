from src import config

def is_owners(ctx):
    owner_id = config.get("BOT_OWNERS")
    return ctx.message.author.id in owner_id