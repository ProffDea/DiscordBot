import yaml
import discord

with open("config.yaml") as f:
    conf = yaml.safe_load(f)


def get_activity_type():
    activity = get("BOT_ACTIVITY")
    if activity.lower() == "playing":
        return discord.ActivityType.playing
    elif activity.lower() == "streaming":
        return discord.ActivityType.streaming
    elif activity.lower() == "listening":
        return discord.ActivityType.listening
    elif activity.lower() == "watching":
        return discord.ActivityType.watching
    else:
        return None


def get(var: str):
    return conf[var]


def refresh():
    pass
