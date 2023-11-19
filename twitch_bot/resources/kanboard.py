from typing import Optional
from fastapi import APIRouter, Body
from pydantic import BaseModel

from twitch_bot.core.kanboard import Kanboard


kanboard_router = APIRouter()
_kanboard: Optional[Kanboard] = None


def ensure_kanboard():
    global _kanboard
    if _kanboard is None:
        _kanboard = Kanboard()
    return _kanboard


class NewKanboardTicket(BaseModel):
    title: str


@kanboard_router.post('/new')
def new_kanboard_ticket(new_ticket_info:NewKanboardTicket=Body(...)):
    kanboard = ensure_kanboard()

    title_prefix = '!remind '
    title = new_ticket_info.title
    if title.startswith(title_prefix):
        title = title[len(title_prefix):]

    task = kanboard.add_task(title)
    if task is None:
        return {'success': False}
    return {'success': True}
