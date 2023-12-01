import code
from typing import List, Optional, Union, cast
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column
from sqlalchemy.exc import IntegrityError

from twitch_bot.core.db import SessionLocal
from twitch_bot.models.user import User
from twitch_bot.resources.utils import ErrorResponseModel


user_router = APIRouter()


class UserInfoSchema(BaseModel):
    name: str
    platform: str
    platform_user_id: Optional[str] = None
    tts_included: bool
    tts_nickname: Optional[str]


class UserResponseSchema(UserInfoSchema):
    user_id: int
    class Config:
        # allows us to create UserResponseSchema objects
        # from sqlalchemy row objects using
        # UserResponseSchema.model_validate(db_user_row)
        from_attributes = True


class UserUpdateableSchema(BaseModel):
    tts_nickname: Optional[str] = None
    tts_included: Optional[bool] = None


@user_router.put("/{user_id}", response_model=UserResponseSchema)
def update_user(user_id:int, updates:UserUpdateableSchema=Body(...)):
    with SessionLocal() as sess:
        db_user = sess.query(User).where(User.user_id==user_id).one_or_none()
        if db_user is None:
            raise HTTPException(
                status_code=404,
                detail="user_id not found",
            )

        if updates.tts_nickname is not None:
            db_user.tts_nickname = cast(Column[str], updates.tts_nickname if updates.tts_nickname else None)  #TODO:don't cast; sa.TypeDecorator?
        if updates.tts_included is not None:
            db_user.tts_included = cast(Column[bool], updates.tts_included)

        try:
            sess.commit()
        except IntegrityError as e:
            raise HTTPException(
                status_code=409,
                detail=f'{type(e).__name__}: {e.__cause__}'
            )

        return UserResponseSchema.model_validate(db_user)


@user_router.get("", response_model=List[UserResponseSchema])
def get_users():
    with SessionLocal() as sess:
        return [
            UserResponseSchema.model_validate(user)
            for user in sess.query(User)
        ]
