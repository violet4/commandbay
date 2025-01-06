import sys
import time
from threading import Thread, Lock
from queue import Queue

from typing import Any
import logging

import pyttsx3
from pyttsx3.engine import Engine


logger = logging.getLogger(__name__)


class Message:
    user: str
    message: str


class TTS:
    _thread: Thread
    _queue: Queue[Message]
    _speaking_thread: Thread
    _lock: Lock

    def __init__(self):
        self.tts: Engine = pyttsx3.init(debug=True)
        self._lock = Lock()

        self.tts_disabled = False
        self.tts_enabled = True

        self.setProperty('volume', 0.2)
        # it seems 100 is 1x speed, 200 is 2x speed, etc.
        self.setProperty('rate', 135)
        # if this voice isn't installed then this command is simply ignored.
        # mbrola
        # self.setProperty('voice', 'mb-us1')
        self.setProperty('voice', 'mb-us3')

    def setProperty(self, propName: str, value: Any):
        if self.tts_disabled:
            return
        self.tts.setProperty(propName, value)

    def say(self, string:str):
        #TODO:instead of creating a new thread every time, put this whole thing inside a watcher thread
        if self.tts_disabled:
            return
        with self._lock:
            self.tts.say(string)
            thread = Thread(target=self.tts.runAndWait, daemon=True)
            thread.start()
            while True:
                if not self.tts.proxy._queue:
                    break
                try:
                    if self.tts.proxy._queue[0][0].__name__ == 'endLoop':
                        self.tts.proxy._queue[0][0]()
                        break
                except:
                    pass
                time.sleep(0.12)


tts: TTS = TTS()
