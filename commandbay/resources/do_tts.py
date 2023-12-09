from html import unescape
from queue import Empty, Queue
import time
from typing import Dict, List, Optional, Annotated
from threading import Thread
import logging
import uuid

from fastapi import APIRouter, Body
from pydantic import BaseModel

from commandbay.core.tts import tts
from commandbay.models.twitch.reward import Reward
from commandbay.models.user import User
from commandbay.resources.utils import HtmlBaseModel


tts_router = APIRouter()

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

_tts_queue: Queue['ChatEventMessage'] = Queue()


class ChatEventMessage(HtmlBaseModel):
    user: str
    platform_user_id: str
    platform: str
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


class PostReward(HtmlBaseModel):
    rewardName:str
    rewardId:uuid.UUID
    rewardCost:int
    rewardMessage:str = ""  # This is the user's associated text-based message
    rewardDescription:str = ""
    rewardRedemptionId:str = ""


@tts_router.post(r"")
def post_tts_message(
    user:Annotated[str, Body(...)],
    user_id:uuid.UUID=Body(...),
    platform:str=Body(...),
    text:Optional[str]=Body(default=None),
    first_chat:Optional[bool]=Body(default=False),
    reward:Optional[PostReward]=Body(default=None),
):
    text = unescape(text) if text else text
    # reward.rewardName = unescape(reward.rewardName) if reward.rewardName else reward.rewardName
    # reward.rewardMessage = unescape(reward.rewardMessage) if reward.rewardMessage else reward.rewardMessage
    # reward.rewardDescription = unescape(reward.rewardDescription) if reward.rewardDescription else reward.rewardDescription
    rewardId = getattr(reward, 'rewardId', None)

    message = ChatEventMessage(
        user=user, platform_user_id=str(user_id), platform=platform,
        text=text,
        just_arrived=first_chat or False,
        rewardId=str(rewardId) if rewardId else None,
        rewardName=getattr(reward, 'rewardName', None),
    )
    _tts_queue.put(message)
    return {'success': True}


def initialize_tts():
    thread = Thread(target=handle_queue, daemon=True)
    thread.start()


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
        user: User = User.ensure_user_exists(name=msg.user, platform_user_id=msg.platform_user_id, platform=msg.platform)
        nickname = str(user.tts_nickname if user.tts_nickname is not None else user.name)
        if nickname not in user_msg_containers:
            if bool(user.tts_included):
                user_msg_containers[nickname] = MessagesContainer(user=nickname)
        message_container: Optional[MessagesContainer] = user_msg_containers.get(nickname, None)
        if message_container is None:
            continue

        # translate redemption names
        #TODO:database-backed translation with UI for editing nicknames. "streamelements says bob redeemed drink water asterisk asterisk asterisk"
        if msg.rewardId is not None and msg.rewardName is not None:
            reward: Reward = Reward.ensure_reward(msg.rewardId, msg.rewardName)
            reward_name = str(reward.tts_name if reward.tts_name is not None else reward.name)
            message_container.redemptions.append(reward_name)

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
