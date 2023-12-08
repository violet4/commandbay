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
import re
import os
import importlib
import sys
import logging
from typing import Union, Optional, List, Callable, Dict
import random

import twitchio
from twitchio.ext.commands import Bot as TwitchBot
from twitchio.ext.commands import command
from twitchio.ext import pubsub
from twitchio.message import Message
from twitchio.channel import Channel
from twitchio.chatter import Chatter, PartialChatter
from twitchio.ext.commands.core import Context
from twitchio.user import User

from commandbay.core.utils import (
    load_env, load_environment, now, nowstr, url_re,
    get_token_from_user_auth_code,
    log_format, log_formatter, get_oauth_token,
)
from commandbay.cli import parse_args
from commandbay.core.db import (
    get_time_user_seen_last, update_user_seen_last,
    insert_history, update_user_exited_last,
)
from commandbay.core.tts import tts
from commandbay.core.greetings import (
    re_greetings, greetings, greet_starts,
    robot_coffee_shop_name_generator, robot_greeting_generator,
)
from commandbay.core.spotify import Spotify
from commandbay.core.kanboard import Kanboard

__all__ = (
    
)

MISSING_AUTHOR_NAME = 'missing_author_name'
NO_MESSAGE_CONTENT = 'no_message_content'

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class Environment:
    TMI_TOKEN:str
    OWNER_ID:str
    CLIENT_ID:str
    BOT_NICK:str
    BOT_PREFIX:str = '!'
    CHANNELS:str
    TALK_CHANNELS:str

    re_greet_minutes:int

    IGNORE_BOTS:str = ''
    IGNORE_USERS:str = ''
    NAME_TRANSLATIONS:str = 'somelongusername:nick;anotherlonguser:nickie'

    SPOTIPY_CLIENT_ID:str = ''
    SPOTIPY_CLIENT_SECRET:str = ''


class Bot(TwitchBot):
    def __init__(self, kb:Optional[Kanboard]=None, env:Union[Callable[[],Dict],Dict]=load_environment):
        self.kb = kb

        self.pubsub = pubsub.PubSubPool(self)

        if isinstance(env, Callable):
            env = env()
        if not isinstance(env, dict):
            raise Exception("environment must be of type Union[Callable[[],Dict],Dict]")

        self.env = env
        # logger.debug('env: %s', env)
        channels = env.get('CHANNELS', '').split(',')
        self.command_prefix = self.env['BOT_PREFIX']
        super().__init__(
            token=self.env['TMI_TOKEN'],
            client_id=self.env['CLIENT_ID'],
            client_secret=self.env['CLIENT_SECRET'],
            nick=self.env['BOT_NICK'],
            prefix=self.command_prefix,
            initial_channels=channels,
        )

        self.owner_username = self.env['OWNER_ID']
        self.bot_nick = self.env['BOT_NICK']
        self.name_translation = dict()
        if self.env.get('NAME_TRANSLATIONS', False):
            self.name_translation = {
                k.lower():v
                for k,v in
                map(lambda x: x.split(':'), self.env.get('NAME_TRANSLATIONS', '').split(';'))
            }
        logger.info("channels: %s", channels)
        self.talk_channels = set(self.env.get('TALK_CHANNELS', '').lower().split(','))
        self.re_greet_minutes = int(self.env['re_greet_minutes'])
        self.ignore_users = {
            # owner_username.lower(),
            self.bot_nick.lower(),
            # channel.lower()
        }
        for ignore_key in ('IGNORE_BOTS', 'IGNORE_USERS'):
            if ignore_key not in self.env:
                continue
            additional_ignores = list(filter(None, self.env[ignore_key].rstrip().lower().split(',')))
            self.ignore_users.update(additional_ignores)

        for spotify_key in ('SPOTIPY_CLIENT_ID', 'SPOTIPY_CLIENT_SECRET'):
            os.environ[spotify_key] = self.env.get(spotify_key, None)
        # https://developer.spotify.com/documentation/web-api/concepts/scopes
        self.spotify = Spotify()

        self.command_env = {
            'tts': tts,
        }

    async def do_subscribe(self, chan_name:str):
        """
        https://dev.twitch.tv/docs/pubsub/

        endpoint       | permissions required
        ---------------+--------------------------
        bits           | bits:read
        channel points | channel:read:redemptions
        """
        channels: List[twitchio.user.SearchUser] = await self.search_channels(chan_name)
        channel = [chan for chan in channels if chan.name.lower()==chan_name.lower()]
        if not channel:
            logger.info("couldn't get channel for channel name: %s", chan_name)
            return
        chan = channel[0]
        logger.info("attempting to pubsub subscribe to channel: %s", chan)

        self.event(name="event_pubsub_bits")(self.event_pubsub_bits)
        self.event(name="event_pubsub_channel_points")(self.event_pubsub_channel_points)
        topics = [
            pubsub.channel_points(self.env['TMI_TOKEN'])[chan.id],
            pubsub.bits(self.env['TMI_TOKEN'])[chan.id],
        ]
        await self.pubsub.subscribe_topics(topics)

    def load_plugins(self):
        # import plugin commands
        plugins_dir = os.path.join(os.path.dirname(THIS_DIR), 'plugins')
        sys.path.append(THIS_DIR)
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

            for ele in getattr(module, 'commands', []):
                aliases = list()
                name = fn = None
                if isinstance(ele, tuple):
                    name, fn = ele
                else:
                    name = ele.get('name')
                    fn = ele.get('fn')
                    aliases = ele.get('aliases', [])
                # give plugins access to the tts object
                fn.env = self.command_env
                names = [name]
                names.extend(aliases)
                orig_fn = fn
                for name in names:
                    # register the command with the twitch bot
                    self.command(name=name)(orig_fn)

    async def event_pubsub_bits(self, event: pubsub.PubSubBitsMessage):
        bits_used = event.bits_used
        content = event.message.content
        username = getattr(event.user, 'name')
        logger.info("%s used %s bits, content: %s", username, bits_used, content)

    async def event_pubsub_channel_points(self, event: pubsub.PubSubChannelPointsMessage):
        print(event.user.name, event.reward.title, event.reward.cost)

    async def event_ready(self):
        'Called once when the bot goes online.'
        logger.info(f"{self.bot_nick} is online!")
        # ws = bot._ws  # this is only needed to send messages within event_ready
        # await ws.send_privmsg(channel, f"/me has landed!")
        # await ws.send_privmsg(channel, f"👋")

    @command(name='remind', aliases=['r', 'reminder'])
    async def remind(self, ctx:Context):
        if self.kb is None:
            return
        #TODO:generalize command authentication
        author = (ctx.author.name or 'nonexistent_user').lower()
        if author not in {'terra_tera', 'violet_revenant'}:
            return
        remind_title = (str(ctx.message.content) or ' ').split(' ', 1)[1]
        self.kb.add_task(remind_title)
        # await self.send(ctx.channel, msg)

    # @bot.event(name='event_message')
    async def event_message(self, msg:Message):
        """
        • TTS
        • handle nonexistent commands
        • Runs every time a message is sent in chat.
        """
        message_content = getattr(msg, 'content', NO_MESSAGE_CONTENT)
        author: Union["Chatter", "PartialChatter"] = msg.author
        logger.info("chat message: %s %s", author, message_content)
        if isinstance(author, Chatter):
            update_user_seen_last(author)
            author_name = author.name
        else:
            author_name = MISSING_AUTHOR_NAME

        channel: Optional[Channel] = msg.channel if isinstance(msg.channel, Channel) else None
        channel_name: str = getattr(channel, 'name', 'missing_channel_name')
        logger.debug(f'{now()} ({channel_name}) {author_name}: {msg.content}')

        user_name = getattr(getattr(msg, 'author'), 'name', str(random.randbytes(20)))
        if user_name.lower() in self.ignore_users:
            logger.debug('ignoring entity and stopping processing: %s', user_name)
            return

        # handle commands, including bad/nonexistent commands
        if message_content.lstrip().startswith(self.command_prefix):
            #TODO:add the actual command
            if isinstance(author, Chatter) and isinstance(channel, Channel):
                insert_history(author, channel, 'command')
            #TODO:may need to handle parsing a bit more intelligently
            command = message_content.split()[0]
            command = command[1:]  # chop off the command prefix
            if command not in self.commands and command!='song':
                logger.warning(
                    f'%s:user %s tried to use nonexistent '
                    f'command %s: %s',
                    now(), author_name, command, message_content
                )
                return

            await self.handle_commands(msg)
            return

        if isinstance(author, Chatter) and isinstance(channel, Channel):
            insert_history(author, channel, 'message')
        else:
            logger.debug("author %s isn't an author and channel %s isn't a channel", author, channel)

        # TTS
        # don't TTS yourself
        if tts.tts_enabled:
            if author_name not in (self.owner_username, MISSING_AUTHOR_NAME):
                if author_name.lower() in self.name_translation:
                    author_name = str(self.name_translation.get(author_name.lower()))
                    author_name = f'friend {author_name}'
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
            elif author_name == MISSING_AUTHOR_NAME:
                msg_start = message_content.split(',')[0]
                if msg_start in greet_starts:
                    name = message_content.split(',')[1].split('!')[0].lstrip()
                    tts.say(f"new arrival to chat: {name}")
                    tts.runAndWait()

    async def send(self, channel:Channel, message:str):
        if channel.name.lower() not in self.talk_channels:
            return
        await channel.send(message)

    async def event_join(self, channel:Channel, user:User):
        super().event_join
        logger.debug("********** event_join\nuser: %s\nchannel: %s\n***********", user, channel)

        logger.info(f'event_join {channel.name} {user.name}')
        insert_history(user, channel, 'join')

        # make sure the bot ignores itself and the streamer
        if user.name.lower() in self.ignore_users:
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
            and (minutes_since_user_seen_last >= self.re_greet_minutes)
        ):
            greetlist = re_greetings

        #TODO:be smarter about when to do this and when not to
        if greetlist:
            greeting = random.choice(greetlist)
            message = greeting.format(user.name)
            if random.random() < 0.1:
                message += (
                    f" I'm a robot! "
                    f"Welcome to {next(robot_coffee_shop_name_generator)}. "
                    f"{next(robot_greeting_generator)}"
                )
            # logger.debug(now(), message)
            logger.info(f'{now()} ({channel.name}): {user.name} joined')
            await self.send(channel, message)

        update_user_seen_last(user)

    async def event_part(self, chatter:Chatter, *args):
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

    def print_startup_message_file(self):
        startup_file_path = os.path.join(THIS_DIR, 'startup_message.txt')
        if os.path.exists(startup_file_path):
            with open(startup_file_path, 'r') as fr:
                for line in fr:
                    logger.info(line)

    @command(name="song")
    async def song(self, ctx: Context):
        if self.spotify is None:
            return
        song_str = self.spotify.get_current_song_str()
        print("SONG STRING", song_str)
        if not song_str:
            await ctx.send("Failed to get info from Spotify API")
            return
        await ctx.send(song_str)


scopes = [
    'channel:read:redemptions',
    'channel:read:subscriptions',
    'bits:read',

    'channel:bot',
    'chat:read',
    'chat:edit',
]


async def main():
    args = parse_args(default_log_level='INFO')
    log_level = getattr(logging, args.log_level.upper(), args.log_level)
    logger.setLevel(level=log_level)
    logging.basicConfig(level=log_level, format=log_format)
    logging.getLogger().handlers[0].setFormatter(log_formatter)

    env = load_environment()

    user_authorization_code = get_oauth_token(env['CLIENT_ID'], scopes, force=True)
    auth_data = get_token_from_user_auth_code(env['CLIENT_ID'], env['CLIENT_SECRET'], user_authorization_code)
    env['TMI_TOKEN'] = auth_data['access_token']

    kb = Kanboard()
    bot = Bot(kb, env=env)
    await bot.do_subscribe('Terra_Tera')
    await bot.start()


if __name__ == '__main__':
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    import asyncio
    asyncio.get_event_loop().run_until_complete(main())
