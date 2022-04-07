import datetime
import discord
from discord.ext import commands
from discord.commands import slash_command, Option, SlashCommandGroup
from sqlalchemy.future import select
from sqlalchemy import text

from src.postgres import database


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

    @unassign.command(
        name="global",
        description="Removes set global role from being assigned to users."
    )
    @commands.has_permissions(manage_roles=True)
    async def unassign_voice_global_role(self, ctx):
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
        name="local",
        description="Removes set local role from voice channel from being assigned to users."
    )
    @commands.has_permissions(manage_roles=True)
    async def unassign_voice_local_role(
            self,
            ctx,
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
        name="global",
        description="One role per server. Users joining voice channels with no local role are given this role."
    )
    @commands.has_permissions(manage_roles=True)
    async def assign_voice_global_role(
            self,
            ctx,
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
                        guild=guild_key, role=role_key
                    )
                )
            elif voice_global_role_exist:
                stmt = select(
                    database.VoiceGlobalRoles
                ).where(
                    database.VoiceGlobalRoles.guild == guild_key
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
        name="local",
        description="One role per channel. Users joining specified voice channel are given this role."
    )
    @commands.has_permissions(manage_roles=True)
    async def assign_voice_local_role(
            self,
            ctx,
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
                        channel=voice_channel_key, role=role_key
                    )
                )
            elif voice_local_role_exist:
                stmt = select(
                    database.VoiceLocalRoles
                ).where(
                    database.VoiceLocalRoles.channel == voice_channel_key
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
        name="ping",
        description="Displays the bot latency."
    )
    async def slash_ping(self, ctx):
        lat = round(self.bot.latency * 1000)
        await ctx.respond("%sms" % lat)

    # Doesn't take into account of plurals or "and"
    @slash_command(
        name="uptime",
        description="Check how long the bot has been online for."
    )
    async def slash_uptime(self, ctx):
        uptime = datetime.datetime.utcnow() - self.bot.start_time
        days, rem = divmod(uptime.seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)
        if seconds < 1:
            seconds = 1
        locals_ = locals()
        magnitudes_str = ("%s %s" % (int(locals_[magnitude]), magnitude)
                          for magnitude in ("days", "hours", "minutes", "seconds") if locals_[magnitude])
        eta_str = ", ".join(magnitudes_str)
        await ctx.respond(eta_str)


def setup(bot):
    bot.add_cog(Utility(bot))
