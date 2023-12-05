from typing import cast
from sqlalchemy import VARCHAR, Boolean, Column, Integer, String, UniqueConstraint

from commandbay.core.db import Base, SessionLocal


class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    # twitch users can change their names once every 6 months.
    # this should reflect the current valid name accounting for name changes.
    name = Column(String)
    tts_included = Column(Boolean, default=True)
    tts_nickname = Column(VARCHAR(20), nullable=True, default=None)
    platform = Column(String, nullable=False, default='twitch')
    # e.g. twitch user id
    platform_user_id = Column(String, nullable=False)
    UniqueConstraint(platform, platform_user_id, name='user_unique_platform_platform_user_id')

    @classmethod
    def ensure_user_exists(cls, name:str, platform_user_id:str, platform:str) -> 'User':
        # for more complex objects we use or joinedload subqueryload
        # e.g. user = session.query(User).options(joinedload(User.foreign_relationship))...
        with SessionLocal(expire_on_commit=False) as sess:
            existing_user = sess.query(User).where(
                User.platform_user_id==platform_user_id,
                User.platform==platform,
            ).one_or_none()

            if existing_user is not None:
                # update username if their name changed
                if cast(str, existing_user.name) != name:
                    existing_user.name = name
                    sess.commit()
                return existing_user

            new_user = cls(
                name=name,
                platform_user_id=platform_user_id,
                platform=platform,
            )
            sess.add(new_user)
            sess.commit()
            return new_user
            # # for some reason our caller is not able to access new_user.tts_nickname
            # return sess.query(User).where(User.id==new_user.user_id).one_or_none()
