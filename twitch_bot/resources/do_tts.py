from html import unescape
from queue import Empty, Queue
import time
from typing import Dict, List, Optional
from threading import Thread

from fastapi import Body
from pydantic import BaseModel

from twitch_bot.core.tts import tts


_tts_queue: Queue['Message'] = Queue()


class Message(BaseModel):
    user: str
    just_arrived: bool = False
    text: Optional[str] = None


class MessagesContainer(BaseModel):
    user: str
    just_arrived: bool = False
    texts: List[str] = []


def do_tts(user:str=Body(...), text:Optional[str]=Body(default=None), first_chat:bool=Body(default=False)):
    if text:
        text = unescape(text)
    message = Message(user=user, text=text, just_arrived=first_chat)
    _tts_queue.put(message)
    return {'success': True}


def initialize_tts():
    thread = Thread(target=handle_queue, daemon=True)
    thread.start()


def process_queue(_tts_queue:Queue['Message'], current_items: Dict[str, MessagesContainer]):
    had_new_items = False
    while True:
        try:
            msg = _tts_queue.get_nowait()
            had_new_items = True
        except Empty:
            break
        if msg.user not in current_items:
            current_items[msg.user] = MessagesContainer(user=msg.user)
        message_container: MessagesContainer = current_items[msg.user]

        if msg.just_arrived:
            message_container.just_arrived = True
        if msg.text:
            message_container.texts.append(msg.text)

    return had_new_items


def handle_current_items(current_message_containers: Dict[str, MessagesContainer]):
    for username in list(current_message_containers.keys()):
        message_container: MessagesContainer = current_message_containers.pop(username)
        print("message_container:", message_container)

        tts.say(username)
        if message_container.just_arrived:
            tts.say("just arrived")
            if message_container.texts:
                tts.say("and says")
        else:
            tts.say('says')

        for message in message_container.texts:
            tts.say(message)

    tts.runAndWait()


def handle_queue():
    current_message_containers: Dict[str, MessagesContainer] = dict()
    while True:
        had_new_items = process_queue(_tts_queue, current_message_containers)

        if had_new_items:
            handle_current_items(current_message_containers)
        else:
            time.sleep(0.1)
