import datetime
import discord
from discord.ext import commands
from discord.commands import slash_command, Option, SlashCommandGroup
from sqlalchemy.future import select
from sqlalchemy import text

from discord.ext import pages

from src.postgres import database
from src import utils


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    assign = SlashCommandGroup(
        "assign",
        "Assign different settings to the server."
    )
    unassign = SlashCommandGroup(
        "unassign",
        "Unassign settings that are currently in effect."
    )

    list = SlashCommandGroup(
        "list",
        "Commands to list data in pages."
    )

    voice = list.create_subgroup(
        "voice",
        "Commands related to listing voice data."
    )

    @voice.command(
        guild_ids=[648977487744991233],
        name="roles",
        description="List both global and local voice roles that have been set in the server."
    )
    async def list_voice_roles(self, ctx: discord.ApplicationContext, page: int = 1):
        page = page - 1
        async with database.async_session() as session:
            embeds = [discord.Embed(title="Currently Assigned Voice Roles")]
            global_role_id = await database.get_voice_global_role(session, ctx.guild.id)
            if global_role_id is not None:
                global_role = ctx.guild.get_role(global_role_id)
                embeds[0].add_field(name="The Server Global Role", value=global_role.mention, inline=False)
            stmt = (
                select(database.Roles.role_id, database.VoiceChannels.channel_id)
                .select_from(database.Roles)
                .join(database.Guilds, database.Guilds.guild_id == ctx.guild.id)
                .join(database.VoiceLocalRoles, database.VoiceLocalRoles.role == database.Roles.id)
                .join(database.VoiceChannels, database.VoiceChannels.id == database.VoiceLocalRoles.channel)
                .where(database.Roles.id == database.VoiceLocalRoles.role)
            )
            results = await session.execute(stmt)
            results = results.all()
            for local_voice in results:
                if len(embeds[len(embeds) - 1].fields) >= 4:
                    embeds.append(discord.Embed(title="Currently Assigned Voice Roles"))
                role = ctx.guild.get_role(local_voice[0])
                channel = ctx.guild.get_channel(local_voice[1])
                embeds[len(embeds) - 1].add_field(name=channel.name, value=role.mention, inline=False)
            paginator = pages.Paginator(pages=embeds)
            if page > paginator.page_count:
                page = paginator.page_count
            elif page < 0:
                page = 0
            await paginator.respond(ctx.interaction)
            # Not efficient
            if page != 0:
                await paginator.goto_page(page_number=page)

    @unassign.command(
        guild_ids=[648977487744991233],
        name="global",
        description="Removes set global role from being assigned to users."
    )
    @commands.has_permissions(manage_roles=True)
    async def unassign_voice_global_role(self, ctx: discord.ApplicationContext):
        async with database.async_session() as session:
            voice_global_role_exist = await database.voice_global_role_exists(session, ctx.guild.id)
            if not voice_global_role_exist:
                return await ctx.respond(
                    "There is currently no global role assigned to this server.",
                    ephemeral=True
                )
            stmt = text(
                """
                DELETE FROM voice_global_roles
                USING guilds
                WHERE voice_global_roles.guild = guilds.id
                AND guilds.guild_id = :guild_id
                """
            )
            await session.execute(stmt, {"guild_id": ctx.guild.id})
            await session.commit()
            await ctx.respond("Success. Global role has been unassigned from this server.")

    @unassign.command(
        guild_ids=[648977487744991233],
        name="local",
        description="Removes set local role from voice channel from being assigned to users."
    )
    @commands.has_permissions(manage_roles=True)
    async def unassign_voice_local_role(
            self,
            ctx: discord.ApplicationContext,
            channel: Option(
                discord.VoiceChannel,
                description="Channel to remove the local role from."
            )
    ):
        async with database.async_session() as session:
            voice_local_role_exist = await database.voice_local_role_exists(session, channel.id)
            if not voice_local_role_exist:
                return await ctx.respond(
                    "There is currently no local role assigned to %s." % channel.mention,
                    ephemeral=True
                )
            stmt = text(
                """
                DELETE FROM voice_local_roles
                USING voice_channels
                WHERE voice_local_roles.channel = voice_channels.id
                AND voice_channels.channel_id = :channel_id
                """
            )
            await session.execute(stmt, {"channel_id": channel.id})
            await session.commit()
        await ctx.respond("Success. Local role has been unassigned from %s." % channel.mention)

    @assign.command(
        guild_ids=[648977487744991233],
        name="global",
        description="One role per server. Users joining voice channels with no local role are given this role."
    )
    @commands.has_permissions(manage_roles=True)
    async def assign_voice_global_role(
            self,
            ctx: discord.ApplicationContext,
            role: Option(
                discord.Role,
                description="The role to assign as the global voice role to the whole server."
            )
    ):
        async with database.async_session() as session:
            global_role_id = await database.get_voice_global_role(session, ctx.guild.id)
            if global_role_id == role.id:
                return await ctx.respond(
                    "%s is already assigned as the global voice role." % role.mention,
                    ephemeral=True
                )
            await database.init_guild(session, ctx.guild)
            await database.init_role(session, role)
            guild_key = await database.get_guild_key(session, ctx.guild.id)
            role_key = await database.get_role_key(session, role.id)
            voice_global_role_exist = await database.voice_global_role_exists(
                session, ctx.guild.id
            )
            note = ""
            if not voice_global_role_exist:
                session.add(
                    database.VoiceGlobalRoles(
                        guild=guild_key,
                        role=role_key
                    )
                )
            elif voice_global_role_exist:
                stmt = (
                    select(database.VoiceGlobalRoles)
                    .where(database.VoiceGlobalRoles.guild == guild_key)
                )
                results = await session.execute(stmt)
                voice_global_roles = results.scalars().first()
                voice_global_roles.role = role_key
                note = "\nNote: Previous global role has been unassigned with newly assigned role."
            await session.commit()
        await ctx.respond(
            "Success. %s has been assigned as the global role.%s" % (role.mention, note)
        )

    @assign.command(
        guild_ids=[648977487744991233],
        name="local",
        description="One role per channel. Users joining specified voice channel are given this role."
    )
    @commands.has_permissions(manage_roles=True)
    async def assign_voice_local_role(
            self,
            ctx: discord.ApplicationContext,
            channel: Option(
                discord.VoiceChannel,
                description="The channel to assign the local voice role to."
            ),
            role: Option(
                discord.Role,
                description="The role to assign as the local voice role to the channel."
            )
    ):
        async with database.async_session() as session:
            local_role_id = await database.get_voice_local_role(session, channel.id)
            if local_role_id == role.id:
                return await ctx.respond(
                    "%s is already assigned as the local voice role for %s." % (
                        role.mention,
                        channel.mention
                    ),
                    ephemeral=True
                )
            await database.init_voice_channel(session, channel)
            await database.init_role(session, role)
            voice_channel_key = await database.get_voice_channel_key(
                session, channel.id
            )
            role_key = await database.get_role_key(session, role.id)
            voice_local_role_exist = await database.voice_local_role_exists(
                session, ctx.guild.id
            )
            note = ""
            if not voice_local_role_exist:
                session.add(
                    database.VoiceLocalRoles(
                        channel=voice_channel_key,
                        role=role_key
                    )
                )
            elif voice_local_role_exist:
                stmt = (
                    select(database.VoiceLocalRoles)
                    .where(database.VoiceLocalRoles.channel == voice_channel_key)
                )
                results = await session.execute(stmt)
                voice_local_roles = results.scalars().first()
                voice_local_roles.role = role_key
                note = "\nNote: Previous local role has been unassigned with newly assigned role."
            await session.commit()
        await ctx.respond(
            "Success. %s has been assigned to %s as the local role.%s" % (
                role.mention, channel.mention, note
            )
        )

    @slash_command(
        guild_ids=[648977487744991233],
        name="ping",
        description="Displays the bot latency."
    )
    async def slash_ping(self, ctx: discord.ApplicationContext):
        lat = round(self.bot.latency * 1000)
        await ctx.respond("%sms" % lat)

    # Doesn't take into account of plurals or "and"
    @slash_command(
        guild_ids=[648977487744991233],
        name="uptime",
        description="Check how long the bot has been online for."
    )
    async def slash_uptime(self, ctx: discord.ApplicationContext):
        eta_str = utils.hrf_time_diff(datetime.datetime.utcnow(), self.bot.start_time)
        await ctx.respond(eta_str)


def setup(bot):
    bot.add_cog(Utility(bot))
