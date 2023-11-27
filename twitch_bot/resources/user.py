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


class UserResponseSchema(UserInfoSchema):
    user_id: int
    class Config:
        orm_mode = True
        from_attributes = True


@user_router.post("", response_model=UserResponseSchema)
def create_user(user: UserInfoSchema):
    with SessionLocal() as sess:
        db_user = User(name=user.name, platform=user.platform)
        sess.add(db_user)
        try:
            sess.commit()
        except IntegrityError as e:
            raise HTTPException(
                status_code=409,
                detail=f'{type(e).__name__}: {e.__cause__}'
            )

        return UserResponseSchema.model_validate(db_user)


class UserUpdateableSchema(BaseModel):
    name: Optional[str] = None


@user_router.put("/{user_id}", response_model=UserResponseSchema)
def update_user(user_id:int, updates:UserUpdateableSchema=Body(...)):
    print("updates", updates)
    with SessionLocal() as sess:
        db_user = sess.query(User).where(User.user_id==user_id).one_or_none()
        if db_user is None:
            raise HTTPException(
                status_code=404,
                detail="user_id not found",
            )

        if updates.name is not None:
            db_user.name = cast(Column[str], updates.name)  #TODO:don't cast

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
