from sqlalchemy import Column, Integer, String, UniqueConstraint
from twitch_bot.core.db import Base


class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    name = Column(String)
    platform = Column(String, nullable=False, default='twitch')
    platform_user_id = Column(String, nullable=True)
    UniqueConstraint(name, platform)
