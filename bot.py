#!/usr/bin/env python

# https://dev.to/ninjabunny9000/let-s-make-a-twitch-bot-with-python-2nd8

# https://www.twitch.tv/violet_nocturnus

import os # for importing env vars for the bot to use
from twitchio.ext import commands
from envbash import load_envbash
load_envbash('env.txt')
this_dir = os.path.dirname(os.path.abspath(__file__))

owner_username = os.environ['OWNER_ID']
bot_nick = os.environ['BOT_NICK']
channel = os.environ['CHANNEL']

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

@bot.event
async def event_message(ctx):
    'Runs every time a message is sent in chat.'

    # make sure the bot ignores itself and the streamer
    if ctx.author.name.lower() == bot_nick.lower():
        return
    elif ctx.author.name == owner_username:
        print(ctx.content)
        await ctx.channel.send(ctx.content)

def print_startup_message_file():
    startup_file_path = os.path.join(this_dir, 'startup_message.txt')
    if os.path.exists(startup_file_path):
        with open(startup_file_path, 'r') as fr:
            for line in fr:
                print(line)

if __name__ == '__main__':
    print_startup_message_file()
    bot.run()
