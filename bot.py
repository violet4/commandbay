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
import logging
from typing import Any, Union, Callable, Optional, Type, TypeVar

from twitchio.ext import commands
from twitchio.message import Message
from twitchio.channel import Channel
from twitchio.chatter import Chatter, PartialChatter
from twitchio.ext.commands.core import Context


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

class TTS:
    def __init__(self):
        try:
            import pyttsx3
            from pyttsx3.engine import Engine
            self.tts: Engine = pyttsx3.init()
            self.tts_disabled = False
            self.tts_enabled = True
        except ImportError:
            pyttsx3 = None
            self.tts_disabled = True
            self.tts_enabled = False
            logger.info("failed to import pyttsx3; text-to-speech is disabled")

    def setProperty(self, propName: str, value: Any):
        if self.tts_disabled:
            return
        self.tts.setProperty(propName, value)

    def say(self, string:str):
        if self.tts_disabled:
            return
        self.tts.say(string)

    def runAndWait(self):
        if self.tts_disabled:
            return
        self.tts.runAndWait()


tts: TTS = TTS()
tts.setProperty('volume', 0.1)


# XXX: singleton?
env = dict()
this_dir = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(this_dir, 'env.txt')

url_re = re.compile(r'https?://[^ ]+')
NO_MESSAGE_CONTENT = 'no_message_content'


def load_env(env):
    with open(env_file, 'r') as fr:
        for line in fr:
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                continue
            k, v = line.split('=', 1)
            env[k] = v
    return env


env = load_env(env)
logger.debug('env: %s', env)

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

# TODO: timestamp to bigint and save epoch time

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

logger.info("channels: %s", channels)
command_prefix = env['BOT_PREFIX']
bot = commands.Bot(
    token=env['TMI_TOKEN'],
    # set up the bot
    irc_token=env['TMI_TOKEN'],
    client_id=env['CLIENT_ID'],
    nick=env['BOT_NICK'],
    prefix=command_prefix,
    initial_channels=channels,
)

# super().__init__(
#     token=getenv('TWITCH_TOKEN'),
#     prefix='!',
#     initial_channels=[getenv('TWITCH_CHANNEL')],
# )

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
    logger.info(f'loading plugin {module}')
    module = f'plugins.{module}'
    module = importlib.import_module(module)
    if not hasattr(module, 'commands'):
        logger.error(f"couldn't find 'commands' attribute in module {module}")
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
            # register the command with the twitch bot
            bot.command(name=name)(orig_fn)


@bot.event(name='event_ready')
async def event_ready():
    'Called once when the bot goes online.'
    logger.info(f"{bot_nick} is online!")
    # ws = bot._ws  # this is only needed to send messages within event_ready
    # await ws.send_privmsg(channel, f"/me has landed!")
    # await ws.send_privmsg(channel, f"👋")

def extract_datetime(dt_string, default=datetime.datetime.now):
    # dt_string = str(datetime.datetime.now())
    m = re.match(
        r'(\d{4})-(\d{2})-(\d{2}) (\d{1,2}):(\d{1,2}):(\d{1,2})',
        dt_string
    )
    if not m:
        if isinstance(default, Callable):
            return default()
        return default
    parts = [int(p) for p in m.groups()]
    if len(parts) == 6:
        y, mon, d, h, m, s = parts
        return datetime.datetime(y, mon, d, h, m, s)


def get_time_user_seen_last(user, channel):
    cursor = conn.execute(
        'SELECT last_seen from viewers where name=? and channel=?',
        (user.name,channel.name)
    )

    row = cursor.fetchone()
    cursor.close()
    if not row:
        return None

    return extract_datetime(row[0])


def strip(o):
    if isinstance(o, str):
        return o.strip()
    elif o is None:
        return None
    elif isinstance(o, (list, set)):
        return type(o)(strip(a) for a in o)
    return o


def update_user_seen_last(user:Chatter):
    if not isinstance(user, Chatter):
        return
    now_dt = now()
    channel_name = getattr(getattr(user, 'channel', None), 'name', None)
    columns = [
        strip(user.id),       # userid
        strip(channel_name),  # channel
        strip(user.name),     # name
        strip(now_dt),        # last_seen
        strip(now_dt),        # first_seen
        strip(now_dt),        # UPSERT last_seen
    ]
    INSERT_QUERY = f'''INSERT INTO
            viewers (userid,channel,name,last_seen,first_seen,last_exited)
            -- when counting number of args, don't forget last_seen=.. below
            values (?,?,?,?,?,null)
        ON CONFLICT(name,channel) DO UPDATE SET last_seen=?;
    '''
    try:
        conn.execute(INSERT_QUERY, columns)
    except sqlite3.IntegrityError as e:
        logger.debug("integrity error:\n%s\n%s", INSERT_QUERY, columns)
    conn.commit()


def ensure_event(event):
    cursor = conn.execute(
        '''SELECT eventid FROM events WHERE event=? LIMIT 1''',
        (strip(event),),
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
        (strip(event),),
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
        (strip(channel),),
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
        (strip(channel),),
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
        (strip(username),),
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
        (strip(username),),
    )
    conn.commit()
    cursor = conn.execute('''SELECT last_insert_rowid();''')
    row = cursor.fetchone()
    cursor.close()
    userid = row[0]
    return userid


def insert_history(user:Chatter, channel:Channel, event:str):
    if not isinstance(user, Chatter):
        return
    eventid = ensure_event(event)
    channelid = ensure_channel(channel.name)
    userid = ensure_user(user.name.strip())
    conn.execute(
        '''INSERT INTO history VALUES (?,?,?,?)''',
        (
            strip(userid),
            strip(now()),
            strip(channelid),
            strip(eventid),
        ),
    )
    conn.commit()


def update_user_exited_last(user, channel):
    now_str = str(datetime.datetime.now())
    conn.execute(
        f'''INSERT INTO viewers values (?,?,?,?,?,?)
        ON CONFLICT(userid,channel) DO UPDATE SET last_exited=?;
        ''',
        (
            strip(user.id),
            strip(channel.name),
            strip(user.name),
            strip(now_str),
            strip(now_str),
            strip(now_str),
            strip(now_str),
        ),
    )
    conn.commit()
    insert_history(user, channel, 'part_channel')


def now():
    return datetime.datetime.now()


@bot.command(name='song')
async def song(ctx:Context):
    logger.info("song command:\nctx: %s", ctx)


@bot.event(name='event_message')
async def event_message(msg:Message):
    """
    • TTS
    • handle nonexistent commands
    • Runs every time a message is sent in chat.
    """
    message_content = getattr(msg, 'content', NO_MESSAGE_CONTENT)
    author: Union["Chatter", "PartialChatter"] = msg.author
    if isinstance(author, Chatter):
        update_user_seen_last(author)
        author_name = author.name
    else:
        author_name = 'missing_author_name'

    channel: Optional[Channel] = msg.channel if isinstance(msg.channel, Channel) else None
    channel_name: str = getattr(channel, 'name', 'missing_channel_name')
    logger.debug(f'{now()} ({channel_name}) {author_name}: {msg.content}')

    if getattr(getattr(msg, 'author'), 'name', str(random.randbytes(20))) in ignore_users:
        return

    # handle commands, including bad/nonexistent commands
    if message_content.lstrip().startswith(command_prefix):
        #TODO:add the actual command
        if isinstance(author, Chatter) and isinstance(channel, Channel):
            insert_history(author, channel, 'command')
        #TODO:may need to handle parsing a bit more intelligently
        command = message_content.split()[0]
        command = command[1:]  # chop off the command prefix
        if command not in bot.commands and command!='song':
            logger.warning(
                f'%s:user %s tried to use nonexistent '
                f'command %s: %s',
                now(), author_name, command, message_content
            )
            return

        await bot.handle_commands(msg)
        return

    if isinstance(author, Chatter) and isinstance(channel, Channel):
        insert_history(author, channel, 'message')
    else:
        logger.debug("author %s isn't an author and channel %s isn't a channel", author, channel)

    # TTS
    # don't TTS yourself
    if tts.tts_enabled and author_name!=owner_username:
        tts.say(author_name)
        tts.say('says')
        tts_message = message_content
        # put spacing between each sentence instead of sounding like a
        # run-on sentence

        tts_message = url_re.sub('URL', tts_message)
        parts = re.split(r'[?.;,!]+', tts_message)
        for part in parts:
            if not part.strip():
                continue
            tts.say(part)
        tts.runAndWait()

greetings = [
    'Hello, {}!',
    'Welcome, {}!',
    'Hi, {}!',
    'Oh hai, {}!',
]
re_greetings = [
    'Hello again, {}!',
    'Welcome back, {}!',
    'Long time no see, {}!',
]


async def send(channel, message):
    if channel.name.lower() not in talk_channels:
        return
    print("WOULD HAVE SAID IN CHAT:", message)
    # await channel.send(message)


@bot.event(name='event_join')
async def event_join(channel, user):
    logger.debug("********** event_join\nuser: %s\nchannel: %s\n***********", user, channel)

    logger.info(f'event_join {channel.name} {user.name}')
    insert_history(user, channel, 'join')

    # make sure the bot ignores itself and the streamer
    if user.name.lower() in ignore_users:
        return

    # TODO see if twitch has an event for when users enter the stream, not just when they say something
    last_seen_dt = get_time_user_seen_last(user, channel)

    minutes_since_user_seen_last = None
    if last_seen_dt:
        minutes_since_user_seen_last = now() - last_seen_dt
        minutes_since_user_seen_last = (
            minutes_since_user_seen_last.total_seconds() / 60
        )

    greetlist = None
    # never seen before
    if not last_seen_dt:
        greetlist = greetings
    # seen, but it's been a while
    elif (
        last_seen_dt
        and (minutes_since_user_seen_last is not None)
        and (minutes_since_user_seen_last >= re_greet_minutes)
    ):
        greetlist = re_greetings

    if greetlist:
        greeting = random.choice(greetlist)
        message = greeting.format(user.name)
        # logger.debug(now(), message)
        logger.info(f'{now()} ({channel.name}): {user.name} joined')
        await send(channel, message)

    update_user_seen_last(user)


class NowStr:
    def __init__(self):
        pass
    def __str__(self):
        # INFO:__main__:2023-10-10 13:29:14.374787
        return str(now().strftime('%Y-%m-%d %H:%M:%S'))

nowstr = NowStr()

@bot.event(name='event_part')
async def event_part(chatter:Chatter, *args):
    args = list(args)
    channel: Optional[Channel] = None
    if args:
        channel = args[0]
        logging.debug('event_part got channel from args[0]')
    if channel is None:
        channel = getattr(chatter, 'channel', None)
        logging.debug('event_part got channel from chatter.channel')
    logger.info('%s:ch(%s): chatter has parted: %s', nowstr, channel, chatter)
    if channel is not None:
        update_user_exited_last(chatter, channel)


def print_startup_message_file():
    startup_file_path = os.path.join(this_dir, 'startup_message.txt')
    if os.path.exists(startup_file_path):
        with open(startup_file_path, 'r') as fr:
            for line in fr:
                logger.info(line)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print_startup_message_file()
    try:
        bot.run()
    except KeyboardInterrupt:
        sys.exit(0)
