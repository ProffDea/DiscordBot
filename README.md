# DiscordBot
A discord bot scripted using Python and utilizing the [Pycord](https://github.com/Pycord-Development/pycord) 
API wrapper library. The database this bot will be utilizing is [PostgreSQL](https://www.postgresql.org/). \
\
The bot will mainly function for utility purposes. The reasoning is to implement features within discord 
servers that discord does not provide or other bots may not feature.
# Features
**Voice Roles**
- A global role is a role from the server that is assigned as the default role for all the voice channels 
in the server.
- A local role is when a role from the server is assigned to a specific voice channel in the server.
- When a member joins one of the server's voice channels, the bot will give the assigned global role to the 
member **ONLY** if there is no local role assigned to that channel. If there is a local role, that role is 
given instead. When the member leaves the channel, the role is taken away.
# Prerequisites
- Python 3
- PostgreSQL 11 or higher
# Optional
- [Lavalink](https://github.com/freyacodes/Lavalink) (Plans to implement this in the future)
# Documentation
[Diagram](https://drawsql.app/proffdea-s-homelabs/diagrams/discordbot) of how the bot's database is 
structured
- Pycord [documentation](https://docs.pycord.dev/en/master/index.html)
- PostgreSQL [documentation](https://www.postgresqltutorial.com/)
- SQLAlchemy [documentation](https://docs.sqlalchemy.org/en/14/)

**Installation**\
Clone the repository
```
git clone https://github.com/ProffDea/DiscordBot.git
```
Create virtual environment
```
python3 -m venv name
```
Activate virtual environment on **Linux**
```
source name/bin/activate
```
Activate virtual environment on **Windows**
```
name\Scripts\activate
```
Install requirements.txt
```
python3 -m pip install -r requirements.txt
```
Create a copy of **example_config.yaml** and rename it to **config.yaml**. Fill out the copy.\
Go to the [Discord Developer Portal](https://discord.com/developers/applications) to grab your bot's token.
Make sure to have the applications.commands scope for OAuth2 to allow slash commands.