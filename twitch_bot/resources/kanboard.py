from fastapi import APIRouter, Body

from twitch_bot.core.kanboard import Kanboard


class KanboardResource:
    router = APIRouter()

    def __init__(self):
        self._kanboard = Kanboard()

    @router.post('/new')
    async def new_kanboard_ticket(self, title:str=Body(...)):
        title_prefix = '!remind '
        if title.startswith(title_prefix):
            title = title[len(title_prefix):]

        self._kanboard.add_task(title)
        return {'success': True}
