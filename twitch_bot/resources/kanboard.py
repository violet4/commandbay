from flask import request

from twitch_bot.resources.app import app
from twitch_bot.core.kanboard import Kanboard

kb = Kanboard()


def kanboard():
    if kb is None:
        return 'kanboard connection is not established', 503
    if request.method != 'POST':
        return 'only POST method supported', 405

    if request.json is None:
        return 'no request data provided', 400

    print(request.json)
    remind_title = request.json.get('title', None)
    if remind_title is None:
        return "reminder title must be provided in the 'title' value of your json data", 400
    if not isinstance(remind_title, str):
        return 'unexpected title type; expected str, got %s' % type(remind_title), 422

    title_prefix = '!remind '
    if remind_title.startswith(title_prefix):
        remind_title = remind_title[len(title_prefix):]

    kb.add_task(remind_title)
    return 'success', 200