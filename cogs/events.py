import discord
from discord.ext import commands

from src.postgres import database


async def get_voice_role(voice_channel: discord.VoiceChannel):
    async with database.async_session() as session:
        voice_local_role_exist = await database.voice_local_role_exists(
            session,
            voice_channel.id
        )
        if voice_local_role_exist:
            role_id = await database.get_voice_local_role(
                session,
                voice_channel.id
            )
            role = voice_channel.guild.get_role(role_id)
            return role
        elif not voice_local_role_exist:
            voice_global_role_exist = await database.voice_global_role_exists(
                session,
                voice_channel.guild.id
            )
            if voice_global_role_exist:
                role_id = await database.get_voice_global_role(
                    session,
                    voice_channel.guild.id
                )
                role = voice_channel.guild.get_role(role_id)
                return role
        return None


async def voice_role_module(
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState
):
    if (
        before.channel and not after.channel or
        after.channel and member.guild.afk_channel and
        after.channel == member.guild.afk_channel
    ):  # Leaving channel or joining afk channel
        if (
            after.channel and member.guild.afk_channel and
            after.channel.id == member.guild.afk_channel.id
        ):
            before = after
        role = await get_voice_role(before.channel)
        if role and role in member.roles:
            await member.remove_roles(role)
    elif (
        not before.channel and after.channel or
        before.channel and after.channel and
        before.channel != after.channel
    ):  # Joining channel or moving between channels
        role_after = await get_voice_role(after.channel)
        if role_after and role_after not in member.roles:
            await member.add_roles(role_after)
        if before.channel and after.channel:
            role_before = await get_voice_role(before.channel)
            if (
                    role_before and role_before != role_after
                    and role_before in member.roles
            ):
                await member.remove_roles(role_before)


class Events(commands.Cog, name="Events"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        await voice_role_module(member, before, after)


def setup(bot):
    bot.add_cog(Events(bot))
