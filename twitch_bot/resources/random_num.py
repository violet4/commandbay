from twitch_bot.resources.app import app


from flask import request


import random


def random_num():
    max_val = request.args.get('max', None)
    if max_val is None:
        return 'max is required', 400
    try:
        max_val = int(max_val)
    except:
        return 'max must be an integer value', 422
    return str(random.randint(1, max_val)), 200
