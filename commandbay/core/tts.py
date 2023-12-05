from threading import Thread
from queue import Queue

from typing import Any
import logging

logger = logging.getLogger(__name__)


class Message:
    user: str
    message: str
"""
{
"user":"$user",
"first_chat": true,
"message":"$encodeForHtml[$chatMessage]",
"rewardCost": "$encodeForHtml[$rewardCost]",
"bitsCheered": $bitsCheered[$user],
"rewardDescription": "$encodeForHtml[$rewardDescription]",
"rewardImageUrl": "$encodeForHtml[$rewardImageUrl]",
"streamTitle": "$encodeForHtml[$streamTitle]",
"time": "$encodeForHtml[$time]",
"rawUserRoles": "$rawUserRoles[$user, all]",
"userRolesTwitch": $userRoles[$user, twitch],
"userRolesTeam": $userRoles[$user, team],
"userRolesFirebot": $userRoles[$user, firebot],
"userRolesCustom": $userRoles[$user, custom]
}

twitch ['Subscriber', 'Tier 1 Sub', 'Moderator']
firebot ['Active Chat User']
custom []
team []

a = {
    'user': 'kornmess',
    'first_chat': False,
    'message': 'lol',
    'rawUserRoles': 'Subscriber,Tier 1 Sub,Moderator,Active Chat User,,',
    'rewardCost': '',
    'bitsCheered': '545',
    'rewardDescription': '',
    'rewardImageUrl': '',
    'streamTitle': 'I has factory &#x27;n frens| LGBTQIA+ | !discord | !charity | !exo | !route',
    'time': '3:26 pm',
    # twitch firebot custom team
    'userRoles': [['Subscriber', 'Tier 1 Sub', 'Moderator'], ['Active Chat User'], [], []]
}
"""

class TTS:
    _thread: Thread
    _queue: Queue[Message]
    @classmethod
    def _class_init(cls):
        if cls._thread is not None:
            return
        cls._queue: Queue[Message] = Queue()
        cls._thread = Thread(target=cls.process_queue_thread, daemon=True)

    @classmethod
    def process_queue_thread(cls):
        l = list()
        while True:
            # make sure we exhaust the queue before we go to the next step
            # so we can process the current queue set as a single step
            while cls._queue:
                msg: Message = cls._queue.get()


    def __init__(self):
        try:
            import pyttsx3
            from pyttsx3.engine import Engine
            self.tts: Engine = pyttsx3.init()

            self.tts_disabled = False
            self.tts_enabled = True

            self.setProperty('volume', 0.1)
            self.setProperty('rate', 120)
            # if this voice isn't installed then this command is simply ignored.
            # mbrola
            self.setProperty('voice', 'mb-us1')

        except (ImportError, OSError):
            pyttsx3 = None
            self.tts_disabled = True
            self.tts_enabled = False
            logger.info("failed to import pyttsx3; text-to-speech is disabled")

    def setProperty(self, propName: str, value: Any):
        if self.tts_disabled:
            return
        self.tts.setProperty(propName, value)

    def say(self, string:str):
        if self.tts_disabled:
            return
        self.tts.say(string)

    def runAndWait(self):
        if self.tts_disabled:
            return
        self.tts.runAndWait()

    def dostuff(self):
        if tts.tts_disabled:
            return
        # if author_name not in (self.owner_username, MISSING_AUTHOR_NAME):
        #     if author_name.lower() in self.name_translation:
        #         author_name = str(self.name_translation.get(author_name.lower()))
        #         author_name = f'friend {author_name}'
        #     tts.say(author_name)
        #     tts.say('says')
        #     tts_message = message_content
        #     # put spacing between each sentence instead of sounding like a
        #     # run-on sentence

        #     tts_message = url_re.sub('URL', tts_message)
        #     parts = re.split(r'[?.;,!]+', tts_message)
        #     for part in parts:
        #         if not part.strip():
        #             continue
        #         tts.say(part)
        #     tts.runAndWait()
        # elif author_name == MISSING_AUTHOR_NAME:
        #     msg_start = message_content.split(',')[0]
        #     if msg_start in greet_starts:
        #         name = message_content.split(',')[1].split('!')[0].lstrip()
        #         tts.say(f"new arrival to chat: {name}")
        #         tts.runAndWait()



tts: TTS = TTS()
