#!/usr/bin/env python

# https://dev.to/ninjabunny9000/let-s-make-a-twitch-bot-with-python-2nd8

# https://www.twitch.tv/violet_nocturnus

import re
import os # for importing env vars for the bot to use
from twitchio.ext import commands
from envbash import load_envbash
import datetime
import sqlite3
load_envbash('env.txt')
this_dir = os.path.dirname(os.path.abspath(__file__))

owner_username = os.environ['OWNER_ID']
bot_nick = os.environ['BOT_NICK']
channel = os.environ['CHANNEL']
re_greet_minutes = int(os.environ['re_greet_minutes'])

conn = sqlite3.connect('twitch_bot.db')
try:
    conn.execute('''
    create table viewers (
        name text
        , last_seen text
        , first_seen text
        , channel text
    )
    ''')
    conn.execute('''
    CREATE unique index
        viewers_unique_name_channel_index
        on viewers(name,channel);
    ''')
    conn.commit()
except sqlite3.OperationalError:
    conn.rollback()
    pass

bot = commands.Bot(
    # set up the bot
    irc_token=os.environ['TMI_TOKEN'],
    client_id=os.environ['CLIENT_ID'],
    nick=os.environ['BOT_NICK'],
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=[channel]
)

@bot.event
async def event_ready():
    'Called once when the bot goes online.'
    print(f"{bot_nick} is online!")
    ws = bot._ws  # this is only needed to send messages within event_ready
    # await ws.send_privmsg(channel, f"/me has landed!")
    # await ws.send_privmsg(channel, f"👋")


def extract_datetime(dt_string):
    # dt_string = str(datetime.datetime.now())
    m = re.match(
        r'(\d{4})-(\d{2})-(\d{2}) (\d{1,2}):(\d{1,2}):(\d{1,2})',
        dt_string
    )
    parts = [int(p) for p in m.groups()]
    return datetime.datetime(*parts)

def get_time_last_saw_user(name):
    cursor = conn.execute(
        'SELECT last_seen from viewers where name=? and channel=?',
        (name,channel)
    )

    row = cursor.fetchone()
    if not row:
        return None

    return extract_datetime(row[0])

def update_last_saw_user(username):
    now = str(datetime.datetime.now())
    conn.execute(
        f'''INSERT INTO viewers values (?,?,?,?)
            ON CONFLICT(name,channel) DO UPDATE SET last_seen=?;
        ''',
        (username, now, now, channel, now)
    )
    conn.commit()

@bot.event
async def event_message(ctx):
    'Runs every time a message is sent in chat.'

    # make sure the bot ignores itself and the streamer
    if ctx.author.name.lower() == bot_nick.lower():
        return
    # elif ctx.author.name == owner_username:
    #     print(ctx.content)
    #     await ctx.channel.send(ctx.content)

    # TODO see if twitch has an event for when users enter the stream, not just when they say something
    last_seen_dt = get_time_last_saw_user(ctx.author.name)

    minutes_since_last_saw_user = None
    if last_seen_dt:
        minutes_since_last_saw_user = datetime.datetime.now() - last_seen_dt
        minutes_since_last_saw_user = (
            minutes_since_last_saw_user.total_seconds() / 60
        )

    # TODO: A table of parameterized greetings, so it's a bit random.
    if not last_seen_dt:
        await ctx.channel.send(f'Welcome, {ctx.author.name}!')
    elif last_seen_dt and minutes_since_last_saw_user >= re_greet_minutes:
        await ctx.channel.send(f'Welcome back, {ctx.author.name}!')
    update_last_saw_user(ctx.author.name)


def print_startup_message_file():
    startup_file_path = os.path.join(this_dir, 'startup_message.txt')
    if os.path.exists(startup_file_path):
        with open(startup_file_path, 'r') as fr:
            for line in fr:
                print(line)

if __name__ == '__main__':
    print_startup_message_file()
    bot.run()
