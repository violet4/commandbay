
import factory

from commandbay.core.db import SessionLocal
from commandbay.models.user import User


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = SessionLocal()  # SQLAlchemy session

    user_id = factory.Sequence(lambda n: n)
    name = factory.Faker('name')
    platform_user_id = factory.Faker('uuid4')
    tts_included = factory.Faker('boolean')
    tts_nickname = factory.Faker('word')
    platform = 'twitch'
