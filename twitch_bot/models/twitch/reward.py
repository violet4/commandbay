

# do_tts.known_redemptions
    # responses={503: {"model": ErrorResponseModel}},

    #     error_response = ErrorResponseModel(error="couldn't communicate with arduino", detail=str(e))

    #     raise HTTPException(503, detail=error_response.model_dump())


from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import relationship

from twitch_bot.core.db import Base


class Reward(Base):
    """
    a reward is usually something redeemed by channel points
    """
    #TODO:keep track of which stream(er) this belongs to
    __tablename__ = 'reward'
    reward_id = Column(Uuid, primary_key=True)
    name = Column(String, nullable=False)
    tts_name = Column(String, nullable=True, default=None)
    # redemptions = relationship("Redemption", backref="reward")


# class Redemption(Base):
#     """
#     a redemption is a user-generated instance of a reward
#     """
#     __tablename__ = 'redemption'
#     redemption_id = Column(Integer, primary_key=True)
#     reward_id = Column(Integer, ForeignKey('reward.reward_id'))
#     user_id = Column(Integer, ForeignKey('user.user_id'))
