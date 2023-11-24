from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from twitch_bot.resources.app import app

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

from pydantic import BaseModel

class UserSchema(BaseModel):
    name: str
    email: str


engine = create_engine('postgresql://localhost/violet')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# @app.post("/users/")
def create_user(user: UserSchema):
    db = SessionLocal()
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    return {"name": user.name, "email": user.email}
