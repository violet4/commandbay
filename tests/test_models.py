
def test_user_creation(user_factory):
    user = user_factory.create(name="John Doe")
    assert user.name == "John Doe"
