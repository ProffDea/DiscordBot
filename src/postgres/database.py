import discord
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BIGINT, ForeignKey, exists
from sqlalchemy.future import select

from src import config

engine = create_async_engine(
    "postgresql+asyncpg://%s:%s@%s:%s/%s" % (
        config.get("DB_USER"),
        config.get("DB_PASSWORD"),
        config.get("DB_IP"),
        config.get("DB_PORT"),
        config.get("DB_NAME")
    )
)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


async def get_guild_key(session: AsyncSession, guild_id: int):
    stmt = (
        select(Guilds.id)
            .where(Guilds.guild_id == guild_id)
    )
    results = await session.execute(stmt)
    return results.scalars().first()


async def get_role_key(session: AsyncSession, role_id: int):
    stmt = (
        select(Roles.id)
            .where(Roles.role_id == role_id)
    )
    results = await session.execute(stmt)
    return results.scalars().first()


async def get_voice_channel_key(session: AsyncSession, channel_id: int):
    stmt = (
        select(VoiceChannels.id)
            .where(VoiceChannels.channel_id == channel_id)
    )
    results = await session.execute(stmt)
    return results.scalars().first()


async def get_voice_global_role(session: AsyncSession, guild_id: int):
    stmt = (
        select(Roles.role_id)
            .select_from(VoiceGlobalRoles)
            .join(Guilds, Guilds.guild_id == guild_id)
            .join(Roles.id, Roles.id == VoiceGlobalRoles.role)
            .where(Guilds.id == VoiceGlobalRoles.guild)
    )
    results = await session.execute(stmt)
    return results.scalars().first()


async def get_voice_local_role(session: AsyncSession, channel_id: int):
    stmt = (
        select(Roles.role_id)
            .select_from(VoiceLocalRoles)
            .join(VoiceChannels, VoiceChannels.channel_id == channel_id)
            .join(Roles, Roles.id == VoiceLocalRoles.role)
            .where(VoiceChannels.id == VoiceLocalRoles.channel)
    )
    results = await session.execute(stmt)
    return results.scalars().first()


async def guild_exists(session: AsyncSession, guild_id: int):
    stmt = (
        select(Guilds)
            .where(Guilds.guild_id == guild_id)
    )
    stmt_exists = select(exists(stmt))
    results_exists = await session.execute(stmt_exists)
    if results_exists.scalars().first():
        return True
    return False


async def role_exists(session: AsyncSession, role_id: int):
    stmt = (
        select(Roles)
            .where(Roles.role_id == role_id)
    )
    stmt_exists = select(exists(stmt))
    results_exists = await session.execute(stmt_exists)
    if results_exists.scalars().first():
        return True
    return False


async def voice_channel_exists(session: AsyncSession, channel_id: int):
    stmt = (
        select(VoiceChannels)
            .where(VoiceChannels.channel_id == channel_id)
    )
    stmt_exists = select(exists(stmt))
    results_exists = await session.execute(stmt_exists)
    if results_exists.scalars().first():
        return True
    return False


async def voice_global_role_exists(session: AsyncSession, guild_id: int):
    stmt = (
        select(VoiceGlobalRoles)
            .join(Guilds, Guilds.guild_id == guild_id)
            .where(VoiceGlobalRoles.guild == Guilds.id)
    )
    stmt_exists = select(exists(stmt))
    results_exists = await session.execute(stmt_exists)
    if results_exists.scalars().first():
        return True
    return False


async def voice_local_role_exists(session: AsyncSession, channel_id: int):
    stmt = (
        select(VoiceLocalRoles)
            .join(VoiceChannels, VoiceChannels.channel_id == channel_id)
            .where(VoiceLocalRoles.channel == VoiceChannels.id)
    )
    stmt_exists = select(exists(stmt))
    results_exists = await session.execute(stmt_exists)
    if results_exists.scalars().first():
        return True
    return False


async def init_role(session: AsyncSession, role: discord.Role):
    role_exist = await role_exists(session, role.id)
    if not role_exist:
        await init_guild(session, role.guild)
        guild_key = await get_guild_key(session, role.guild.id)
        session.add(Roles(guild=guild_key, role_id=role.id))


async def init_guild(session: AsyncSession, guild: discord.Guild):
    guild_exist = await guild_exists(session, guild.id)
    if not guild_exist:
        session.add(Guilds(guild_id=guild.id))


async def init_voice_channel(session: AsyncSession, channel: discord.VoiceChannel):
    voice_channel_exist = await voice_channel_exists(session, channel.id)
    if not voice_channel_exist:
        await init_guild(session, channel.guild)
        guild_key = await get_guild_key(session, channel.guild.id)
        session.add(VoiceChannels(guild=guild_key, channel_id=channel.id))


async def base_metadata():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class Users(Base):
    __tablename__ = "users"
    id = Column(BIGINT, name="id", primary_key=True)
    user_id = Column(BIGINT, name="user_id", unique=True, nullable=False)


class Guilds(Base):
    __tablename__ = "guilds"
    id = Column(BIGINT, name="id", primary_key=True)
    guild_id = Column(BIGINT, name="guild_id", unique=True, nullable=False)


class VoiceChannels(Base):
    __tablename__ = "voice_channels"
    id = Column(BIGINT, name="id", primary_key=True)
    guild = Column(
        ForeignKey(
            "guilds.id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        name="guild",
        nullable=False
    )
    channel_id = Column(BIGINT, name="channel_id", unique=True, nullable=False)


class Roles(Base):
    __tablename__ = "roles"
    id = Column(BIGINT, name="id", primary_key=True)
    guild = Column(
        ForeignKey(
            "guilds.id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        name="guild",
        nullable=False
    )
    role_id = Column(BIGINT, name="role_id", unique=True, nullable=False)


class VoiceGlobalRoles(Base):
    __tablename__ = "voice_global_roles"
    id = Column(BIGINT, name="id", primary_key=True)
    guild = Column(
        ForeignKey(
            "guilds.id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        name="guild",
        nullable=False
    )
    role = Column(ForeignKey("roles.id", onupdate="CASCADE", ondelete="CASCADE"),
                  name="role",
                  nullable=False
                  )


class VoiceLocalRoles(Base):
    __tablename__ = "voice_local_roles"
    id = Column(BIGINT, name="id", primary_key=True)
    channel = Column(
        ForeignKey(
            "voice_channels.id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        name="channel",
        nullable=False
    )
    role = Column(
        ForeignKey(
            "roles.id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        name="role",
        nullable=False
    )
