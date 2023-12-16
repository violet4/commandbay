import cProfile
import pstats
import io
from functools import wraps
import random
from typing import List, Callable
import datetime
import re
import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse

import requests


url_re = re.compile(r'https?://[^ ]+')

log_format = '%(levelname)s:%(module)s:%(asctime)s:%(pathname)s:%(lineno)d:%(message)s'
log_formatter = logging.Formatter(log_format)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


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


def generate_csrf_code(length=20):
    csrf_code = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=length))
    return csrf_code


def generate_user_auth_url(
    client_id, force=False, scopes:List[str]=[],
    redirect_url='http://localhost:3000',
):
    url = 'https://id.twitch.tv/oauth2/authorize'
    url += "?client_id={0}&response_type=code".format(client_id)
    url += '&redirect_uri='+redirect_url
    if scopes:
        url += "&scope=" + parse.quote(" ".join(scopes))
    if force:
        url += '&force_verify=true'
    csrf_code = generate_csrf_code()
    url += '&state=' + csrf_code
    return csrf_code, url.replace(' ', '%20')


def get_oauth_token(client_id:str, scopes:List[str], force=False):
    """
    https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/#get-the-user-to-authorize-your-app
    """
    csrf_code, url = generate_user_auth_url(client_id, scopes=scopes, force=force)
    print("Please open this URL in your browser to authenticate:")
    print(url)
    result = dict()
    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            # print(self.path)
            result['path'] = self.path
            self.wfile.write(b'<html><head></head><body>hello!</body></html>')
            self.wfile.flush()
    server = HTTPServer(('localhost', 3000), RequestHandler)
    server.handle_request()
    path = result['path']
    parsed:parse.ParseResult = parse.urlparse(path)
    qs = parse.parse_qs(parsed.query)
    assert qs['state'][0] == csrf_code, Exception("csrf code didn't match; mitm?")
    token = qs['code'][0]
    return token


def get_token_from_user_auth_code(client_id, client_secret, user_authorization_code):
    sess = requests.Session()
    get_token_url = 'https://id.twitch.tv/oauth2/token'
    resp = sess.post(get_token_url, data={
        'client_id': client_id,
        'client_secret': client_secret,
        'code': user_authorization_code,
        'grant_type':  'authorization_code',
        'redirect_uri': 'http://localhost:3000',
    })

    # {
    #     "access_token":"...",
    #     "expires_in":15393,
    #     "refresh_token":"...",
    #     "scope":["bits:read","channel:bot","channel:read:redemptions","channel:read:subscriptions","chat:edit","chat:read"],
    #     "token_type":"bearer",
    # }
    data = resp.json()
    return data


def profiled(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()

        result = fn(*args, **kwargs)

        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

        return result
    return wrapper
