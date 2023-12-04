# import pytest
import time
from fastapi.testclient import TestClient
import uuid

from twitch_bot.server import app
from twitch_bot.resources.do_tts import ChatEventMessage
from twitch_bot.core.tts import tts

client = TestClient(app)

# assert response.status_code == 200
# assert response.json() == {"success": "true"}
# assert response.status_code == 503
# assert "error" in response.json()

def test_read_item():
    response = client.post("/tts", json=ChatEventMessage(user='user', platform_user_id=str(uuid.uuid4()), platform='twitch', text='message text').model_dump())
    response = client.post("/tts", json=ChatEventMessage(user='user', platform_user_id=str(uuid.uuid4()), platform='twitch', text='message text').model_dump())
    response = client.post("/tts", json=ChatEventMessage(user='user', platform_user_id=str(uuid.uuid4()), platform='twitch', text='message text').model_dump())
    time.sleep(1)

# @pytest.mark.parametrize("item_id", [101, 102, 103, 104, 105])
# def test_read_item_error(item_id):
#     response = client.get(f"/item/{item_id}")
