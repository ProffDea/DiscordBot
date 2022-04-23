import discord
import datetime
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession

from src.postgres import database


async def store(session: AsyncSession, message: discord.Message, is_edit: bool):
    if message.author.bot:
        return
    await database.init_user(session, message.author)
    await database.init_text_channel(session, message.channel)
    user_key = await database.get_user_key(session, message.author.id)
    channel_key = await database.get_text_channel_key(session, message.channel.id)
    file_urls = None
    if message.attachments:
        file_urls = []
        for attachment in message.attachments:
            file_urls.append(attachment.url)
    session.add(
        database.Snipe(
            user=user_key,
            channel=channel_key,
            created_at=message.created_at.replace(tzinfo=None),
            deleted_at=datetime.datetime.utcnow().replace(tzinfo=None),
            message=message.content,
            is_edit=is_edit,
            file_urls=file_urls
        )
    )
    await session.commit()
