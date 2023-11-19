from collections import defaultdict
from html import unescape
from queue import Empty, Queue
import time
from typing import Dict, List
from threading import Thread

from fastapi import Body
from pydantic import BaseModel

from twitch_bot.core.tts import tts


_tts_queue: Queue['Message'] = Queue()


class Message(BaseModel):
    user: str
    text: str


def do_tts(user:str=Body(...), text:str=Body(...)):
    message = unescape(text)
    _tts_queue.put(Message(user=user, text=message))
    return {'success': True}


def initialize_tts():
    thread = Thread(target=handle_queue, daemon=True)
    thread.start()


def structure_current_items(_tts_queue:Queue['Message'], current_items: Dict[str, List[str]]):
    had_new_items = False
    while True:
        try:
            msg = _tts_queue.get_nowait()
            had_new_items = True
        except Empty:
            break
        current_items[msg.user].append(msg.text)
    return had_new_items


def handle_current_items(current_items: Dict[str, List[str]]):
    for user in list(current_items.keys()):
        messages = current_items.pop(user)
        tts.say(user)
        tts.say('says')
        for message in messages:
            tts.say(message)
    tts.runAndWait()


def handle_queue():
    current_items: Dict[str, List[str]] = defaultdict(list)
    while True:
        had_new_items = structure_current_items(_tts_queue, current_items)

        if had_new_items:
            handle_current_items(current_items)
        else:
            time.sleep(0.1)
