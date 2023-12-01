from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from twitch_bot.core.db import Base


class ChatMessage(Base):
    __tablename__ = 'chat'
    chat_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    message = Column(String)
