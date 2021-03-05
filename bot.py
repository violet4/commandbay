#!/usr/bin/env python
"""
view all events in order:
select history.timestamp,users.user,channels.channel,events.event from users inner join history using(userid) inner join events using(eventid) inner join channels using(channelid) order by timestamp;

view all events by user in order:
select users.user,history.timestamp,channels.channel,events.event from users inner join history using(userid) inner join events using(eventid) inner join channels using(channelid) order by user,timestamp;

view all events by channel in order:
select channels.channel,history.timestamp,users.user,events.event from users inner join history using(userid) inner join events using(eventid) inner join channels using(channelid) order by channel,timestamp;

"""
# https://dev.to/ninjabunny9000/let-s-make-a-twitch-bot-with-python-2nd8

# https://www.twitch.tv/violet_revenant

import random
import re
import os
import datetime
import sqlite3
import importlib
import sys
from collections.abc import Iterable

from twitchio.ext import commands
# pip install pyttsx3
import pyttsx3
tts = pyttsx3.init()
tts.setProperty('volume', 0.1)

# XXX: singleton?
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
channels = env.get('CHANNELS', '').split(',')
talk_channels = set(env.get('TALK_CHANNELS', '').lower().split(','))
re_greet_minutes = int(env['re_greet_minutes'])
ignore_users = {
    # owner_username.lower(),
    bot_nick.lower(),
    # channel.lower()
}

conn = sqlite3.connect('twitch_bot.db')
def execute(sql):
    try:
        conn.execute(sql)
        conn.commit()
    except sqlite3.OperationalError:
        conn.rollback()

execute(
'''CREATE TABLE viewers (
    userid bigint
    , channel text
    , name text
    , first_seen text
    , last_seen text
    , last_exited text
)
''')
execute(
'''CREATE unique index
    viewers_unique_userid_channel_index
    on viewers(userid,channel);
''')
execute(
'''CREATE TABLE history (
    userid BIGINT
    , timestamp TEXT
    , channelid BIGINT
    , eventid INT
)
''')
execute(
'''CREATE TABLE channels (
    channelid INTEGER PRIMARY KEY AUTOINCREMENT
    , channel TEXT
)
''')
execute(
'''CREATE unique index
    channels_unique_name_index
    on channels(channel);
''')

execute(
'''CREATE TABLE users (
    userid INTEGER PRIMARY KEY AUTOINCREMENT
    , user TEXT
)
''')
execute(
'''CREATE unique index
    users_unique_name_index
    on users(user);
''')
execute(
'''CREATE TABLE events (
    eventid INTEGER PRIMARY KEY AUTOINCREMENT
    , event text
);
''')
execute(
'''CREATE unique index
    events_unique_event_index
    on events(event);
''')

command_prefix = env['BOT_PREFIX']
bot = commands.Bot(
    # set up the bot
    irc_token=env['TMI_TOKEN'],
    client_id=env['CLIENT_ID'],
    nick=env['BOT_NICK'],
    prefix=command_prefix,
    initial_channels=channels,
)

command_env = {
    'tts': tts,
}

# import plugin commands
plugins_dir = os.path.join(this_dir, 'plugins')
sys.path.append(this_dir)
for module in os.listdir(plugins_dir):
    if not module.endswith('.py'):
        continue
    module = module.split('.', 1)[0]
    print(f'loading plugin {module}')
    module = f'plugins.{module}'
    module = importlib.import_module(module)
    if not hasattr(module, 'commands'):
        print(f"couldn't find 'commands' attribute in module {module}")
        continue
    for ele in module.commands:
        aliases = list()
        name = fn = None
        if isinstance(ele, tuple):
            name, fn = ele
        else:
            name = ele.get('name')
            fn = ele.get('fn')
            aliases = ele.get('aliases', [])
        # give plugins access to the tts object
        fn.env = command_env
        names = [name]
        names.extend(aliases)
        orig_fn = fn
        for name in names:
            fn = bot.command(
                name=name,
            )(orig_fn)

@bot.event
async def event_ready():
    'Called once when the bot goes online.'
    print(f"{bot_nick} is online!")
    # ws = bot._ws  # this is only needed to send messages within event_ready
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

def get_time_last_saw_user(user):
    cursor = conn.execute(
        'SELECT last_seen from viewers where userid=? and channel=?',
        (user.id,user.channel.name)
    )

    row = cursor.fetchone()
    cursor.close()
    if not row:
        return None

    return extract_datetime(row[0])

def strip(o):
    if hasattr(o, 'strip'):
        return o.strip()
    elif o is None:
        return None
    elif isinstance(o, Iterable):
        return type(o)(strip(a) for a in o)
    return o

def update_last_saw_user(user):
    now_dt = now()
    conn.execute(
        f'''INSERT INTO viewers values (?,?,?,?,?,?)
            ON CONFLICT(userid,channel) DO UPDATE SET last_seen=?;
        ''',
        strip((
            user.id,
            user.channel.name,
            user.name.strip(),
            now_dt,
            now_dt,
            None,

            now_dt
        ))
    )
    conn.commit()

def ensure_event(event):
    cursor = conn.execute(
        '''SELECT eventid FROM events WHERE event=? LIMIT 1''',
        strip((
            event,
        )),
    )
    row = cursor.fetchone()
    cursor.close()
    if row:
        eventid = row[0]
        return eventid

    conn.execute(
        '''INSERT INTO events (event)
        VALUES (?)
        ON CONFLICT (event)
        DO NOTHING;''',
        strip((
            event,
        )),
    )
    conn.commit()
    cursor = conn.execute('''SELECT last_insert_rowid();''')
    row = cursor.fetchone()
    cursor.close()
    eventid = row[0]
    return eventid

def ensure_channel(channel):
    cursor = conn.execute(
        '''SELECT channelid FROM channels WHERE channel=? LIMIT 1''',
        strip((channel,)),
    )
    row = cursor.fetchone()
    cursor.close()
    if row:
        channelid = row[0]
        return channelid

    conn.execute(
        '''INSERT INTO channels (channel)
        VALUES (?)
        ON CONFLICT (channel)
        DO NOTHING;''',
        strip((channel,)),
    )
    conn.commit()
    cursor = conn.execute('''SELECT last_insert_rowid();''')
    row = cursor.fetchone()
    cursor.close()
    channelid = row[0]
    return channelid

def ensure_user(username):
    cursor = conn.execute(
        '''SELECT userid FROM users WHERE user=? LIMIT 1''',
        strip((username,)),
    )
    row = cursor.fetchone()
    cursor.close()
    if row:
        userid = row[0]
        return userid

    conn.execute(
        '''INSERT INTO users (user)
        VALUES (?)
        ON CONFLICT (user)
        DO NOTHING;''',
        strip((username,)),
    )
    conn.commit()
    cursor = conn.execute('''SELECT last_insert_rowid();''')
    row = cursor.fetchone()
    cursor.close()
    userid = row[0]
    return userid

def insert_history(user, event):
    eventid = ensure_event(event)
    channelid = ensure_channel(user.channel.name)
    userid = ensure_user(user.name.strip())
    conn.execute(
        '''INSERT INTO history VALUES (?,?,?,?)''',
        strip((
            userid,
            now(),
            channelid,
            eventid,
        ))
    )
    conn.commit()

def update_user_last_exited(user, channel):
    now = str(datetime.datetime.now())
    conn.execute(
        f'''INSERT INTO viewers values (?,?,?,?,?,?)
            ON CONFLICT(userid,channel) DO UPDATE SET last_exited=?;
        ''',
        strip((
            user.id, channel.name, user.name, now, now, now,
            now
        ))
    )
    conn.commit()
    insert_history(user, 'part_channel')

def now():
    return datetime.datetime.now()

@bot.event
async def event_message(ctx):
    """
    • TTS
    • handle nonexistent commands
    """
    print(f'{now()} ({ctx.channel.name}) {ctx.author.name}: {ctx.content}')
    # useful someday: ctx.author.is_mod
    update_last_saw_user(ctx.author)
    if ctx.author.name.lower() in ignore_users:
        return

    # handle commands, including bad/nonexistent commands
    if ctx.content.lstrip().startswith(command_prefix):
        insert_history(ctx.author, 'command')
        command = ctx.content.split()[0]
        command = command[1:]
        if command not in bot.commands:
            print(
                now(),
                f'user {ctx.author.name} tried to use nonexistent '
                f'command {command}: {ctx.content}'
            )
            return

        await bot.handle_commands(ctx)
        return

    insert_history(ctx.author, 'message')

    # TTS
    tts.say(ctx.author.name)
    tts.say('says')
    message = ctx.content
    # put spacing between each sentence instead of sounding like a
    # run-on sentence
    message = re.sub(r'https?://[^ ]+', 'URL', message)
    parts = re.split(r'[?.;,!]+', message)
    for part in parts:
        if not part.strip():
            continue
        tts.say(part)
    tts.runAndWait()

greetings = [
    'Hello, {}!',
    'Welcome, {}!',
    'Hi, {}!',
]
re_greetings = [
    'Hello again, {}!',
    'Welcome back, {}!',
    'Long time no see, {}!',
]

async def send(channel, message):
    if channel.name.lower() not in talk_channels:
        return
    await channel.send(message)

@bot.event
async def event_join(user):
    'Runs every time a message is sent in chat.'
    print(f'event_join {user.channel.name} {user.name}')
    insert_history(user, 'join')

    # make sure the bot ignores itself and the streamer
    if user.name.lower() in ignore_users:
        return

    # TODO see if twitch has an event for when users enter the stream, not just when they say something
    last_seen_dt = get_time_last_saw_user(user)

    minutes_since_last_saw_user = None
    if last_seen_dt:
        minutes_since_last_saw_user = datetime.datetime.now() - last_seen_dt
        minutes_since_last_saw_user = (
            minutes_since_last_saw_user.total_seconds() / 60
        )

    greetlist = None
    # never seen before
    if not last_seen_dt:
        greetlist = greetings
    # seen, but it's been a while
    elif last_seen_dt and minutes_since_last_saw_user >= re_greet_minutes:
        greetlist = re_greetings

    if greetlist:
        greeting = random.choice(greetlist)
        message = greeting.format(user.name)
        # print(now(), message)
        print(f'{now()} ({user.channel.name}): {user.name} joined')
        await send(user.channel, message)
        # await user.channel.send(message)
    update_last_saw_user(user)


@bot.event
async def event_part(user):
    print(f'{now()} ({user.channel}): user {user.name} has parted')
    update_user_last_exited(user, user.channel)

def print_startup_message_file():
    startup_file_path = os.path.join(this_dir, 'startup_message.txt')
    if os.path.exists(startup_file_path):
        with open(startup_file_path, 'r') as fr:
            for line in fr:
                print(line)

if __name__ == '__main__':
    print_startup_message_file()
    bot.run()
