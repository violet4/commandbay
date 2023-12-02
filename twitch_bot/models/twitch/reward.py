import uuid
from sqlalchemy import Column, Integer, String, Uuid

from twitch_bot.core.db import Base, SessionLocal


class Reward(Base):
    """
    a reward is usually something redeemed by channel points
    """
    #TODO:keep track of which stream(er) this belongs to
    __tablename__ = 'reward'
    reward_id = Column(Integer, primary_key=True)
    platform_reward_id = Column(Uuid, unique=True)
    name = Column(String, nullable=False)
    tts_name = Column(String, nullable=True, default=None)
    # redemptions = relationship("Redemption", backref="reward")

    @classmethod
    def ensure_reward(cls, platform_reward_id: str, name: str):
        with SessionLocal(expire_on_commit=False) as sess:
            platform_reward_uuid = uuid.UUID(platform_reward_id)
            reward: Reward = sess.query(cls).where(cls.platform_reward_id==platform_reward_uuid).one_or_none()
            if reward is None:
                reward = Reward(platform_reward_id=platform_reward_uuid, name=name)
                sess.add(reward)
                sess.commit()
            if str(reward.name) != name:
                reward.name = name
                sess.commit()
            return reward
