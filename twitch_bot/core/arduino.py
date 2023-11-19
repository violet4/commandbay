from enum import Enum
import time
import glob
from typing import Optional

import serial


class ArduinoStateEnum(str, Enum):
    on = 'on'
    off = 'off'
    unknown = 'unknown'


class Arduino(serial.Serial):
    def __init__(self, path:Optional[str]=None):
        self.setup_time = 0
        path = self.find_arduino()
        if path is None:
            return
        super().__init__(path, 9600)
        self.setup_time = time.time()

    def ensure_ready(self) -> bool:
        if self.setup_time == 0:
            return False
        time_since_startup = time.time() - self.setup_time
        if time_since_startup < 2:
            remaining = 2 - time_since_startup
            time.sleep(remaining)

        exception = self._test_write()
        if exception is not None:
            self.close()
            self.port = self.find_arduino()
            self.open()
            time.sleep(2)
            exception = self._test_write()
            if isinstance(exception, Exception):
                raise exception

        return True

    def _test_write(self):
        try:
            self.write('-\n'.encode())
        except Exception as e:
            return e

    OFF = '0\n'.encode()
    ON = '1\n'.encode()

    GET_STATE = '2\n'.encode()

    def get_state(self) -> ArduinoStateEnum:
        self.ensure_ready()
        self.write(self.GET_STATE)
        result = self.readline().decode().strip()
        if result == '1':
            return ArduinoStateEnum.on
        elif result == '0':
            return ArduinoStateEnum.off

        return ArduinoStateEnum.unknown

    def is_on(self):
        return self.get_state()==ArduinoStateEnum.on

    def is_off(self):
        return self.get_state()==ArduinoStateEnum.off

    def change_setting(self, value:bytes):
        self.ensure_ready()
        self.write(value)

    def off(self):
        self.change_setting(self.OFF)

    def on(self):
        self.change_setting(self.ON)

    def reset(self):
        self.off()
        time.sleep(1)
        self.on()

    @classmethod
    def find_arduino(cls):
        results = glob.glob('/dev/ttyACM*')
        if len(results)==1:
            return results[0]
