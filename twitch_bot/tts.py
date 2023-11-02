from typing import Any
import logging

logger = logging.getLogger(__name__)


class TTS:
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

        except ImportError:
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


tts: TTS = TTS()
