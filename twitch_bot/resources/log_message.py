import logging

from flask import request

from twitch_bot.resources.app import app

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
logging.basicConfig(level=logging.INFO)


@app.route("/log", methods=['POST'])
def log_message():
    if request.method != 'POST':
        return 'only POST method supported', 405

    if request.json is None:
        return 'no request data provided', 400

    message = request.json.get('message', None)
    if message is None:
        return f"'message' required in the json body", 400
    if not isinstance(message, str):
        return f'unexpected message type; expected str, got %s' % type(message), 422

    logger.info(message)

    return 'success', 200