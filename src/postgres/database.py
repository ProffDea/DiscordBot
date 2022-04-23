import discord
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, BIGINT, ForeignKey, exists, DateTime, Text, Boolean, ARRAY
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


async def get_user_key(session: AsyncSession, user_id: int):
    stmt = (
        select(Users.id)
        .where(Users.user_id == user_id)
    )
    results = await session.execute(stmt)
    return results.scalars().first()


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


async def get_text_channel_key(session: AsyncSession, channel_id: int):
    stmt = (
        select(TextChannels.id)
        .where(TextChannels.channel_id == channel_id)
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


async def get_webhook(session: AsyncSession, channel_id: int):
    stmt = (
        select(Webhooks.webhook_id)
        .select_from(Webhooks)
        .join(TextChannels, TextChannels.channel_id == channel_id)
        .where(Webhooks.channel == TextChannels.id)
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


async def user_exists(session: AsyncSession, user_id: int):
    stmt = (
        select(Users)
        .where(Users.user_id == user_id)
    )
    stmt_exists = select(exists(stmt))
    results_exists = await session.execute(stmt_exists)
    if results_exists.scalars().first():
        return True
    return False


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


async def snipe_exists(session: AsyncSession, channel_id: int):
    stmt = (
        select(Snipe)
        .join(TextChannels, TextChannels.channel_id == channel_id)
        .where(Snipe.channel == TextChannels.id)
    )
    stmt_exists = select(exists(stmt))
    results_exists = await session.execute(stmt_exists)
    if results_exists.scalars().first():
        return True
    return False


async def webhook_exists(session: AsyncSession, webhook_id: int):
    stmt = (
        select(Webhooks)
        .where(Webhooks.webhook_id == webhook_id)
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


async def text_channel_exists(session: AsyncSession, channel_id: int):
    stmt = (
        select(TextChannels)
        .where(TextChannels.channel_id == channel_id)
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
        session.add(
            Roles(
                guild=guild_key,
                role_id=role.id
            )
        )


async def init_webhook(session: AsyncSession, webhook: discord.Webhook):
    webhook_exist = await webhook_exists(session, webhook.id)
    if not webhook_exist:
        await init_text_channel(session, webhook.channel)
        channel_key = await get_text_channel_key(session, webhook.channel.id)
        session.add(
            Webhooks(
                channel=channel_key,
                webhook_id=webhook.id
            )
        )


async def init_user(session: AsyncSession, user: discord.User):
    user_exist = await user_exists(session, user.id)
    if not user_exist:
        session.add(
            Users(user_id=user.id)
        )


async def init_guild(session: AsyncSession, guild: discord.Guild):
    guild_exist = await guild_exists(session, guild.id)
    if not guild_exist:
        session.add(
            Guilds(guild_id=guild.id)
        )


async def init_text_channel(session: AsyncSession, channel: discord.TextChannel):
    text_channel_exist = await text_channel_exists(session, channel.id)
    if not text_channel_exist:
        await init_guild(session, channel.guild)
        guild_key = await get_guild_key(session, channel.guild.id)
        session.add(
            TextChannels(
                guild=guild_key,
                channel_id=channel.id
            )
        )


async def init_voice_channel(session: AsyncSession, channel: discord.VoiceChannel):
    voice_channel_exist = await voice_channel_exists(session, channel.id)
    if not voice_channel_exist:
        await init_guild(session, channel.guild)
        guild_key = await get_guild_key(session, channel.guild.id)
        session.add(
            VoiceChannels(
                guild=guild_key,
                channel_id=channel.id
            )
        )


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


class TextChannels(Base):
    __tablename__ = "text_channels"
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


class Webhooks(Base):
    __tablename__ = "webhooks"
    id = Column(BIGINT, name="id", primary_key=True)
    channel = Column(
        ForeignKey(
            "text_channels.id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
    )
    webhook_id = Column(BIGINT, name="webhook_id", unique=True, nullable=False)


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


class Snipe(Base):
    __tablename__ = "snipe"
    id = Column(BIGINT, name="id", primary_key=True)
    user = Column(
        ForeignKey(
            "users.id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        name="user",
        nullable=False
    )
    channel = Column(
        ForeignKey(
            "text_channels.id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        name="channel",
        nullable=False
    )
    created_at = Column(DateTime, name="created_at", unique=True, nullable=False)
    deleted_at = Column(DateTime, name="deleted_at", unique=True, nullable=False)
    message = Column(Text, name="message", unique=False, nullable=True)
    is_edit = Column(Boolean, name="is_edit", unique=False, nullable=False)
    file_urls = Column(ARRAY(Text), name="file_urls", unique=False, nullable=True)


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
    role = Column(
        ForeignKey(
            "roles.id",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
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
