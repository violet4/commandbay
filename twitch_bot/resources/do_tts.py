from html import unescape
from queue import Empty, Queue
import time
from typing import Dict, List, Optional
from threading import Thread
import logging

from fastapi import Body
from pydantic import BaseModel

from twitch_bot.core.tts import tts


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

_tts_queue: Queue['ChatEventMessage'] = Queue()


class HtmlBaseModel(BaseModel):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, str):
                kwargs[k] = unescape(v)
        super().__init__(*args, **kwargs)


class ChatEventMessage(HtmlBaseModel):
    user: str
    just_arrived: bool = False
    text: Optional[str] = None
    rewardId: Optional[str] = None
    rewardName: Optional[str] = None


class MessagesContainer(BaseModel):
    """
    When we're handling a given queue batch, we shove all the events of
    a given user into one of these message containers so we can group
    events and messages by user.
    """
    user: str
    just_arrived: bool = False
    texts: List[str] = []
    redemptions: List[str] = []


class Reward(HtmlBaseModel):
    rewardName:str
    rewardId:str
    rewardCost:int
    rewardMessage:str = ""  # This is the user's associated text-based message
    rewardDescription:str = ""
    rewardRedemptionId:str = ""


def post_tts_message(
    user:str=Body(...),
    text:Optional[str]=Body(default=None),
    first_chat:bool=Body(default=False),
    reward:Optional[Reward]=Body(default=None),
):
    print("Reward:", reward)

    text = unescape(text) if text else text
    # reward.rewardName = unescape(reward.rewardName) if reward.rewardName else reward.rewardName
    # reward.rewardMessage = unescape(reward.rewardMessage) if reward.rewardMessage else reward.rewardMessage
    # reward.rewardDescription = unescape(reward.rewardDescription) if reward.rewardDescription else reward.rewardDescription
    message = ChatEventMessage(
        user=user, text=text,
        just_arrived=first_chat,
        rewardId=getattr(reward, 'rewardId', None),
        rewardName=getattr(reward, 'rewardName', None),
    )
    _tts_queue.put(message)
    return {'success': True}


def initialize_tts():
    thread = Thread(target=handle_queue, daemon=True)
    thread.start()


# to database+UI
known_redemptions = {
    '588c13b9-cebf-4655-8d0a-9d51d9d38e4b': 'FIRST',
    'c0eca28e-4026-4d31-8361-dbf221f04383': 'Fun Fact',
    'c4f1d1b9-91e4-4801-a7c2-67994036a0a0': 'Stretch',
    'a73bcf34-3904-4bdc-95b4-82f25dcb9309': 'Ask me anything',
    'ee4df394-b0a6-418b-8c8c-7997cf585e44': 'Drink water',  # sound
    '7746a20a-7850-4fe0-9caf-53f6940b2539': 'Hello Darkness',  # sound
    '3bf2811c-06f3-4ccf-9f1a-66deb884fcb1': 'Name a Pawn',  # Rimworld
}


sound_alert_prefix = 'Sound Alert: '
def chop_sound_alert_text(redemption_text:str):
    # "Sound Alert: Drink *** Water"
    if redemption_text.startswith(sound_alert_prefix):
        redemption_text = redemption_text[len(sound_alert_prefix):]
    return redemption_text


def process_current_queue_items(
    _tts_queue:Queue['ChatEventMessage'],
    user_msg_containers: Dict[str, MessagesContainer],
):
    had_new_items = False
    while True:
        try:
            msg: ChatEventMessage = _tts_queue.get_nowait()
            had_new_items = True
        except Empty:
            break
        if msg.user not in user_msg_containers:
            user_msg_containers[msg.user] = MessagesContainer(user=msg.user)
        message_container: MessagesContainer = user_msg_containers[msg.user]

        if msg.rewardId is not None and msg.rewardName is not None:
            print("msg.rewardId:", msg.rewardId)
            if msg.rewardId in known_redemptions:
                redemption_text = known_redemptions[msg.rewardId]
            else:
                logger.warn("redemption unknown: %s %s", msg.rewardId, msg.rewardName)
                redemption_text = msg.rewardName
                redemption_text = chop_sound_alert_text(redemption_text)
            message_container.redemptions.append(redemption_text)

        if msg.just_arrived:
            message_container.just_arrived = True

        if msg.text:
            message_container.texts.append(msg.text)

    return had_new_items


def handle_current_items(current_message_containers: Dict[str, MessagesContainer]):
    for username in list(current_message_containers.keys()):
        message_container: MessagesContainer = current_message_containers.pop(username)

        tts.say(username)
        already = False
        if message_container.just_arrived:
            tts.say("just arrived")
            already = True

        if message_container.redemptions:
            tts.say('{}redeemed'.format('and ' if already else ''))
            tts.say(' and '.join(message_container.redemptions))
            already = True

        if message_container.texts:
            tts.say('{}says'.format('and ' if already else ''))
            for message in message_container.texts:
                tts.say(message)
            already = True
 
    tts.runAndWait()


def handle_queue():
    current_message_containers: Dict[str, MessagesContainer] = dict()
    while True:
        had_new_items = process_current_queue_items(_tts_queue, current_message_containers)

        if had_new_items:
            handle_current_items(current_message_containers)
        else:
            time.sleep(0.1)
