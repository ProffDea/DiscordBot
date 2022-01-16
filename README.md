# DiscordBot
A discord bot scripted using Python and utilizing the [discord.py](https://github.com/Rapptz/discord.py#readme) API wrapper library. The database this bot will be utilizing is [PostgreSQL](https://www.postgresql.org/).

There are currently no features implemented as of yet, and only a very barebones foundation is built. Nevertheless, the bot is able to come online, run commands, and connect to the database.
# Prerequisites
- Python 3
- PostgreSQL 11 or higher
# Optional
- [Lavalink](https://github.com/freyacodes/Lavalink)
# Documentation
Work in Progress
- discord.py [documentation](https://discordpy.readthedocs.io/en/stable/)
- PostgreSQL [documentation](https://www.postgresqltutorial.com/)
- SQLAlchemy [documentation](https://docs.sqlalchemy.org/en/14/)

**Installation**\
Clone the repository
```
git clone https://github.com/ProffDea/DiscordBot.git
```
Create virtual environment, and activate environment
```
python3 -m venv name
source name/bin/activate
```
Install requirements.txt
```
python3 -m pip install -r requirements.txt
```
Go to the [Discord Developer Portal](https://discord.com/developers/applications) to grab your bot's token, and fill out a new **config.yaml** file using the **example_config.yaml** as reference.