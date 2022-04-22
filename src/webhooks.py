import discord
from sqlalchemy.ext.asyncio import AsyncSession

from src.postgres import database
from src import config


async def from_channel(session: AsyncSession, bot: discord.Bot, channel: discord.TextChannel):
    webhook_id = await database.get_webhook(session, channel.id)
    if not webhook_id:
        webhook = await channel.create_webhook(name=config.get("HOOK_NAME"))
        await database.init_webhook(session, webhook)
        await session.commit()
    else:
        webhook = await bot.fetch_webhook(webhook_id)
    return webhook
