import random
import datetime
import re
from typing import Callable

url_re = re.compile(r'https?://[^ ]+')


def load_env(env, env_file:str):
    with open(env_file, 'r') as fr:
        for line in fr:
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                continue
            k, v = line.split('=', 1)
            env[k] = v
    return env

def extract_datetime(dt_string, default=datetime.datetime.now):
    # dt_string = str(datetime.datetime.now())
    m = re.match(
        r'(\d{4})-(\d{2})-(\d{2}) (\d{1,2}):(\d{1,2}):(\d{1,2})',
        dt_string
    )
    if not m:
        if isinstance(default, Callable):
            return default()
        return default
    parts = [int(p) for p in m.groups()]
    if len(parts) == 6:
        y, mon, d, h, m, s = parts
        return datetime.datetime(y, mon, d, h, m, s)


def now():
    return datetime.datetime.now()


class NowStr:
    def __init__(self):
        pass
    def __str__(self):
        # INFO:__main__:2023-10-10 13:29:14.374787
        return str(now().strftime('%Y-%m-%d %H:%M:%S'))


nowstr = NowStr()


def strip(o):
    if isinstance(o, str):
        return o.strip()
    elif o is None:
        return None
    elif isinstance(o, (list, set)):
        return type(o)(strip(a) for a in o)
    return o


def create_shuffle_generator(objects):
    objects = list(objects)
    while True:
        random.shuffle(objects)
        for ele in objects:
            yield ele
