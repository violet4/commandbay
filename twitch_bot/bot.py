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
import re
import os
import importlib
import sys
import logging
from typing import Union, Optional, List
import random

from kanboard_integ import Kanboard

from twitchio.ext.commands import Bot as TwitchBot
from twitchio.ext.commands import command
from twitchio.message import Message
from twitchio.channel import Channel
from twitchio.chatter import Chatter, PartialChatter
from twitchio.ext.commands.core import Context
from twitchio.user import User

from twitch_bot.utils import load_env, now, nowstr, url_re
from twitch_bot.cli import parse_args
from twitch_bot.db import (
    get_time_user_seen_last, update_user_seen_last,
    insert_history, update_user_exited_last,
)
from twitch_bot.tts import tts
from twitch_bot.greetings import (
    re_greetings, greetings, greet_starts,
    robot_coffee_shop_name_generator, robot_greeting_generator,
)

MISSING_AUTHOR_NAME = 'missing_author_name'
NO_MESSAGE_CONTENT = 'no_message_content'

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class Bot(TwitchBot):
    def __init__(self):
        self.kb = Kanboard()
        env = dict()
        self.this_dir = os.path.dirname(os.path.abspath(__file__))
        env_file = os.path.join(os.path.dirname(self.this_dir), 'env.txt')
        env = load_env(env, env_file)
        logger.debug('env: %s', env)
        self.owner_username = env['OWNER_ID']
        self.bot_nick = env['BOT_NICK']
        channels = env.get('CHANNELS', '').split(',')
        logger.info("channels: %s", channels)
        self.talk_channels = set(env.get('TALK_CHANNELS', '').lower().split(','))
        self.re_greet_minutes = int(env['re_greet_minutes'])
        self.ignore_users = {
            # owner_username.lower(),
            self.bot_nick.lower(),
            # channel.lower()
        }
        for ignore_key in ('IGNORE_BOTS', 'IGNORE_USERS'):
            additional_ignores = list(filter(None, env[ignore_key].rstrip().split(',')))
            self.ignore_users.update(additional_ignores)
        self.command_prefix = env['BOT_PREFIX']

        self.command_env = {
            'tts': tts,
        }

        super().__init__(
            token=env['TMI_TOKEN'],
            # set up the bot
            irc_token=env['TMI_TOKEN'],
            client_id=env['CLIENT_ID'],
            nick=env['BOT_NICK'],
            prefix=self.command_prefix,
            initial_channels=channels,
        )

    def load_plugins(self):
        # import plugin commands
        plugins_dir = os.path.join(os.path.dirname(self.this_dir), 'plugins')
        sys.path.append(self.this_dir)
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
                    bot.command(name=name)(orig_fn)

    # @commands.event(name='event_ready')
    async def event_ready(self):
        'Called once when the bot goes online.'
        logger.info(f"{self.bot_nick} is online!")
        # ws = bot._ws  # this is only needed to send messages within event_ready
        # await ws.send_privmsg(channel, f"/me has landed!")
        # await ws.send_privmsg(channel, f"👋")

    @command(name='song')
    async def song(self, ctx:Context):
        logger.info("song command:\nctx: %s", ctx)

    @command(name='remind', aliases=['r', 'reminder'])
    async def remind(self, ctx:Context):
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
        if isinstance(author, Chatter):
            update_user_seen_last(author)
            author_name = author.name
        else:
            author_name = MISSING_AUTHOR_NAME

        channel: Optional[Channel] = msg.channel if isinstance(msg.channel, Channel) else None
        channel_name: str = getattr(channel, 'name', 'missing_channel_name')
        logger.debug(f'{now()} ({channel_name}) {author_name}: {msg.content}')

        user_name = getattr(getattr(msg, 'author'), 'name', str(random.randbytes(20)))
        if user_name in self.ignore_users:
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
        if tts.tts_enabled:
            if author_name not in (self.owner_username, MISSING_AUTHOR_NAME):
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
    #    print("WOULD HAVE SAID IN CHAT:", message)
        await channel.send(message)

    # @bot.event(name='event_join')
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

        if greetlist:
            greeting = random.choice(greetlist)
            message = greeting.format(user.name)
            message += (
                f" I'm a robot! "
                f"Welcome to {next(robot_coffee_shop_name_generator)}. "
                f"{next(robot_greeting_generator)}"
            )
            # logger.debug(now(), message)
            logger.info(f'{now()} ({channel.name}): {user.name} joined')
            await self.send(channel, message)

        update_user_seen_last(user)

    # @bot.event(name='event_part')
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
        startup_file_path = os.path.join(self.this_dir, 'startup_message.txt')
        if os.path.exists(startup_file_path):
            with open(startup_file_path, 'r') as fr:
                for line in fr:
                    logger.info(line)


if __name__ == '__main__':
    bot = Bot()
    args = parse_args(default_log_level='INFO')
    log_level = getattr(logging, args.log_level)
    logger.setLevel(level=log_level)
    logging.basicConfig(level=log_level)

    bot.print_startup_message_file()
    try:
        bot.run()
    except KeyboardInterrupt:
        sys.exit(0)
