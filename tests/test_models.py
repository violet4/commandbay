
def test_user_creation(user_factory):
    user = user_factory.create(name="John Doe", email="john@example.com")
    assert user.name == "John Doe"
    assert user.email == "john@example.com"
