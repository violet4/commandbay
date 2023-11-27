import sqlite3
import logging
import datetime
from typing import Union

from sqlalchemy import create_engine, String, Integer, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import twitchio
from twitchio.channel import Channel
from twitchio.chatter import Chatter, PartialChatter
from twitchio.user import User

from .utils import extract_datetime, now, strip


logger = logging.getLogger(__name__)


conn = sqlite3.connect('bot_memory.db')

engine = create_engine('sqlite:///db.sqlite3')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


#TODO:for now we're using typing.cast(Column[int], value), but maybe we can make sqlalchemy TypeDecorator work someday?
# class StrColumn(TypeDecorator):
#     impl = String
#     def process_bind_param(self, value, _):
#         return value
#     def process_result_value(self, value, _):
#         return value
# class IntColumn(TypeDecorator):
#     impl = Integer
#     def process_bind_param(self, value, _):
#         return value
#     def process_result_value(self, value, _):
#         return value


def execute(sql):
    try:
        conn.execute(sql)
    except sqlite3.OperationalError:
        conn.rollback()


execute(
'''
CREATE TABLE viewers (
        name text
        , last_seen text
        , first_seen text
        , channel text
    , userid bigint, last_exited text);
''')
execute(
    '''CREATE UNIQUE INDEX viewers_unique_name_channel_index
        on viewers(name,channel);
''')

# TODO: timestamp to bigint and save epoch time

execute(
'''CREATE TABLE history (
    userid BIGINT
    , timestamp TEXT
    , channelid BIGINT
    , eventid INT
)
''')
execute(
'''CREATE TABLE channels (
    channelid INTEGER PRIMARY KEY AUTOINCREMENT
    , channel TEXT
)
''')
execute(
'''CREATE unique index
    channels_unique_name_index
    on channels(channel);
''')

execute(
'''CREATE TABLE users (
    userid INTEGER PRIMARY KEY AUTOINCREMENT
    , user TEXT
)
''')
execute(
'''CREATE unique index
    users_unique_name_index
    on users(user);
''')
execute(
'''CREATE TABLE events (
    eventid INTEGER PRIMARY KEY AUTOINCREMENT
    , event text
);
''')
execute(
'''CREATE unique index
    events_unique_event_index
    on events(event);
''')
execute(
'''CREATE UNIQUE INDEX
    viewers_unique_userid_channel_index
    on viewers(userid,channel);
''')

def get_time_user_seen_last(user, channel):
    cursor = conn.execute(
        'SELECT last_seen from viewers where name=? and channel=?',
        (user.name,channel.name)
    )

    row = cursor.fetchone()
    cursor.close()
    if not row:
        return None

    return extract_datetime(row[0])


def update_user_seen_last(user_or_chatter:Union[Chatter, PartialChatter,User]):
    now_dt = now()
    channel_name = getattr(getattr(user_or_chatter, 'channel', None), 'name', None)
    user_id = strip(getattr(user_or_chatter, 'id', None))
    if user_id is None:
        return
    columns = [
        strip(user_or_chatter.name),  # userid
        strip(channel_name),          # channel
        strip(now_dt),                # last_seen
        strip(now_dt),                # first_seen
        strip(now_dt),                # last_exited
        strip(now_dt),                # UPSERT last_seen
    ]
    INSERT_QUERY = f'''INSERT INTO
            viewers (name,channel,last_seen,first_seen,last_exited)
            -- when counting number of args, don't forget last_seen=.. below
            values (?,?,?,?,?)
        ON CONFLICT(name,channel) DO UPDATE SET last_seen=?;
    '''

    try:
        conn.execute(INSERT_QUERY, columns)
    except sqlite3.IntegrityError as e:
        logger.debug("integrity error:\n%s\n%s", INSERT_QUERY, columns)
    conn.commit()


def ensure_event(event):
    cursor = conn.execute(
        '''SELECT eventid FROM events WHERE event=? LIMIT 1''',
        (strip(event),),
    )
    row = cursor.fetchone()
    cursor.close()
    if row:
        eventid = row[0]
        return eventid

    conn.execute(
        '''INSERT INTO events (event)
        VALUES (?)
        ON CONFLICT (event)
        DO NOTHING;''',
        (strip(event),),
    )
    conn.commit()
    cursor = conn.execute('''SELECT last_insert_rowid();''')
    row = cursor.fetchone()
    cursor.close()
    eventid = row[0]
    return eventid


def ensure_channel(channel):
    cursor = conn.execute(
        '''SELECT channelid FROM channels WHERE channel=? LIMIT 1''',
        (strip(channel),),
    )
    row = cursor.fetchone()
    cursor.close()
    if row:
        channelid = row[0]
        return channelid

    conn.execute(
        '''INSERT INTO channels (channel)
        VALUES (?)
        ON CONFLICT (channel)
        DO NOTHING;''',
        (strip(channel),),
    )
    conn.commit()
    cursor = conn.execute('''SELECT last_insert_rowid();''')
    row = cursor.fetchone()
    cursor.close()
    channelid = row[0]
    return channelid


def ensure_user(username):
    cursor = conn.execute(
        '''SELECT userid FROM users WHERE user=? LIMIT 1''',
        (strip(username),),
    )
    row = cursor.fetchone()
    cursor.close()
    if row:
        userid = row[0]
        return userid

    conn.execute(
        '''INSERT INTO users (user)
        VALUES (?)
        ON CONFLICT (user)
        DO NOTHING;''',
        (strip(username),),
    )
    conn.commit()
    cursor = conn.execute('''SELECT last_insert_rowid();''')
    row = cursor.fetchone()
    cursor.close()
    userid = row[0]
    return userid


def insert_history(user_or_chatter:Union[Chatter, PartialChatter,User], channel:Channel, event:str):
    acceptable_types = (twitchio.user.User, PartialChatter, User)
    if not isinstance(user_or_chatter, acceptable_types):
        logger.error(
            "unexpected: user %s (type %s) is not of an acceptable type %s",
            user_or_chatter, type(user_or_chatter),
            acceptable_types,
        )
        return
    eventid = ensure_event(event)
    channelid = ensure_channel(channel.name)

    username = getattr(user_or_chatter, 'name', None)
    if username is None:
        logger.error("Failed to get name of user_or_chatter: %s (type %s)", user_or_chatter, type(user_or_chatter))
        return

    username = username.strip()
    userid = ensure_user(username)
    if userid is None:
        logger.error(
            "failed to ensure user_or_chatter.name in database; user_or_chatter.name: %s; "
            "user_or_chatter: %s, (type %s)",
            username,
            user_or_chatter,
            type(user_or_chatter),
        )
        return

    conn.execute(
        '''INSERT INTO history VALUES (?,?,?,?)''',
        (
            strip(userid),
            strip(now()),
            strip(channelid),
            strip(eventid),
        ),
    )
    conn.commit()


def update_user_exited_last(user:Union[User,Chatter,PartialChatter], channel:Channel):
    now_str = str(datetime.datetime.now())
    conn.execute(
        f'''INSERT INTO viewers values (?,?,?,?,?,?)
        ON CONFLICT(userid,channel) DO UPDATE SET last_exited=?;
        ''',
        (
            strip(getattr(user, 'id', None)),
            strip(channel.name),
            strip(user.name),
            strip(now_str),
            strip(now_str),
            strip(now_str),
            strip(now_str),
        ),
    )
    conn.commit()
    insert_history(user, channel, 'part_channel')
