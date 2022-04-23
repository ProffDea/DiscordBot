import discord
import datetime
from discord.ext import commands
from sqlalchemy.ext.asyncio import AsyncSession

from src.postgres import database


class Info(discord.ui.View):
    def __init__(self, member: discord.Member, created_time: str, deleted_time: str, event_edit: str):
        super().__init__()
        self.member = member
        self.created_time = created_time
        self.deleted_time = deleted_time
        self.event_edit = event_edit

    @discord.ui.button(emoji="⚙", style=discord.ButtonStyle.blurple)
    async def details(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = discord.Embed(
            title="%s message" % self.event_edit.title(),
            description="Message Author: %s\nAuthor ID: %s\nCreated %s ago\n%s %s ago\n" % (
                self.member.mention, self.member.id, self.created_time, self.event_edit.title(), self.deleted_time
            )
        )
        embed.set_thumbnail(url=self.member.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)


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
