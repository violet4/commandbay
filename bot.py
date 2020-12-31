#!/usr/bin/env python

# https://dev.to/ninjabunny9000/let-s-make-a-twitch-bot-with-python-2nd8

# https://www.twitch.tv/violet_revenant

import re
import os
from twitchio.ext import commands
import datetime
import sqlite3
import importlib
import sys


env = dict()
this_dir = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(this_dir, 'env.txt')
with open(env_file, 'r') as fr:
    for line in fr:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            continue
        k, v = line.split('=', 1)
        env[k] = v


owner_username = env['OWNER_ID']
bot_nick = env['BOT_NICK']
channel = env['CHANNEL']
re_greet_minutes = int(env['re_greet_minutes'])

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

command_prefix = env['BOT_PREFIX']
bot = commands.Bot(
    # set up the bot
    irc_token=env['TMI_TOKEN'],
    client_id=env['CLIENT_ID'],
    nick=env['BOT_NICK'],
    prefix=command_prefix,
    initial_channels=[channel]
)

# import plugin commands
plugins_dir = os.path.join(this_dir, 'plugins')
sys.path.append(this_dir)
for module in os.listdir(plugins_dir):
    if not module.endswith('.py'):
        continue
    module = module.split('.', 1)[0]
    module = f'plugins.{module}'
    module = importlib.import_module(module)
    for name, fn in module.commands:
        fn = bot.command(name=name)(fn)

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

def now():
    return datetime.datetime.now()

# @bot.event
# async def event_message(ctx):
    # elif user.name == owner_username:
    #     print(ctx.content)
    #     await ctx.channel.send(ctx.content)

@bot.event
async def event_join(user):
    'Runs every time a message is sent in chat.'

    # make sure the bot ignores itself and the streamer
    if user.name.lower() in (bot_nick.lower(), channel.lower()):
        return

    # TODO see if twitch has an event for when users enter the stream, not just when they say something
    last_seen_dt = get_time_last_saw_user(user.name)

    minutes_since_last_saw_user = None
    if last_seen_dt:
        minutes_since_last_saw_user = datetime.datetime.now() - last_seen_dt
        minutes_since_last_saw_user = (
            minutes_since_last_saw_user.total_seconds() / 60
        )

    # TODO: A table of parameterized greetings, so it's a bit random.
    if not last_seen_dt:
        message = f'Welcome, {user.name}!'
        print(message, now())
        await user.channel.send(message)
    elif last_seen_dt and minutes_since_last_saw_user >= re_greet_minutes:
        message = f'Welcome back, {user.name}!'
        print(message, now())
        await user.channel.send(message)
    update_last_saw_user(user.name)

    # await bot.handle_commands(ctx)

@bot.event
async def event_part(user):
    print(f'user {user.name} has left channel {user.channel} at {now()}')

def print_startup_message_file():
    startup_file_path = os.path.join(this_dir, 'startup_message.txt')
    if os.path.exists(startup_file_path):
        with open(startup_file_path, 'r') as fr:
            for line in fr:
                print(line)

if __name__ == '__main__':
    print_startup_message_file()
    bot.run()
