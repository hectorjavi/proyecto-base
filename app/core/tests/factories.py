from apps.models.user.models import User


def make_user(**overrides):
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!",
        "first_name": "Test",
        "paternal_last_name": "User",
        "maternal_last_name": "Demo",
        "accepted_terms": True,
        "gender": User.MALE,
    }
    data.update(overrides)
    password = data.pop("password")
    user = User(**data)
    user.set_password(password)
    user.save()
    return user
