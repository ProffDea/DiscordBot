import discord
import datetime
from discord.ext import commands
from discord.commands import slash_command, Option
from sqlalchemy.future import select

from src import webhooks, utils
from src.postgres import database
from src.modules import snipe


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        guild_ids=[648977487744991233],
        name="say",
        description="Repeats the message you want the bot to say."
    )
    async def slash_say(
            self,
            ctx: discord.ApplicationContext,
            message: Option(
                str,
                description="The contents the bot will repeat."
            )
    ):
        await ctx.respond("Success", ephemeral=True)
        await ctx.send(message)

    # Does not support files yet
    @slash_command(
        guild_ids=[648977487744991233],
        name="snipe",
        description="Show the most recent deleted/edited message in the current channel."
    )
    async def snipe(self, ctx: discord.ApplicationContext):
        async with database.async_session() as session:
            snipe_exist = await database.snipe_exists(session, ctx.channel.id)
            if not snipe_exist:
                return await ctx.respond("There is nothing to snipe yet!", ephemeral=True)
            stmt = (
                select(
                    database.Users.user_id,
                    database.Snipe.created_at,
                    database.Snipe.deleted_at,
                    database.Snipe.message,
                    database.Snipe.is_edit,
                    database.Snipe.file_urls
                )
                .select_from(database.Users)
                .join(database.TextChannels, database.TextChannels.channel_id == ctx.channel.id)
                .join(database.Snipe, database.Snipe.channel == database.TextChannels.id)
                .where(database.Users.id == database.Snipe.user)
                .order_by(database.Snipe.deleted_at.desc())
            )
            results = await session.execute(stmt)
            results = results.all()
            user_id, created_at, deleted_at, message, is_edit, file_urls = results[0]
            member = ctx.guild.get_member(user_id)
            webhook = await webhooks.from_channel(session, self.bot, ctx.channel)
            created_time = utils.hrf_time_diff(
                datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc),
                created_at.replace(tzinfo=datetime.timezone.utc)
            )
            deleted_time = utils.hrf_time_diff(
                datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc),
                deleted_at.replace(tzinfo=datetime.timezone.utc)
            )
            event_edit = "edited" if is_edit else "deleted"
            if file_urls:
                for url in file_urls:
                    message += "\n%s" % url
            await ctx.delete()
            await webhook.send(
                content=message,
                username=member.display_name,
                avatar_url=member.display_avatar,
                view=snipe.Info(member, created_time, deleted_time, event_edit)
            )
            #await ctx.respond("Message was created %s ago" % created_time, ephemeral=True)


def setup(bot):
    bot.add_cog(Fun(bot))
