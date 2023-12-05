from typing import List, Optional, cast
import logging
import uuid

from fastapi import APIRouter, Body
from sqlalchemy import Column
from commandbay.core.db import SessionLocal

from commandbay.models.twitch.reward import Reward
from commandbay.resources.utils import HtmlBaseModel


rewards_router = APIRouter()

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)


class PutReward(HtmlBaseModel):
    tts_name: Optional[str] = None


class RewardResponse(HtmlBaseModel):
    reward_id: int
    platform_reward_id: uuid.UUID
    name: str
    tts_name: Optional[str]
    class Config:
        from_attributes = True


@rewards_router.get(r"", response_model=List[RewardResponse])
def get_rewards():
    with SessionLocal() as sess:
        return [
            RewardResponse.model_validate(reward)
            for reward in sess.query(Reward)
        ]


@rewards_router.put("/{reward_id}", response_model=RewardResponse)
def put_reward(
    reward_id:int,
    put_reward:PutReward=Body(...),
):
    tts_name = put_reward.tts_name

    with SessionLocal() as sess:
        reward = sess.query(Reward).where(Reward.reward_id==reward_id).one()
        if tts_name == '':
            tts_name = None
        reward.tts_name = cast(Column[str], tts_name)
        sess.commit()
        return RewardResponse.model_validate(reward)
