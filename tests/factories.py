
import factory

from commandbay.core.db import SessionLocal
from commandbay.models.user import User


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = SessionLocal()  # SQLAlchemy session

    # id = factory.Sequence(lambda n: n)
    name = factory.Faker('name')
    email = factory.Faker('email')