import pytest
from pydantic import ValidationError
from schemas.user import UserRegister

def test_user_register_data_valid():
    user = UserRegister(
        username = ("zxc_washer"),
        email = "zxc_washer2004@gmail.com",
        password = "qwertY12@"
    )

    assert user.username == "zxc_washer"
    assert user.email == "zxc_washer2004@gmail.com"
    assert user.password == "qwertY12@"

def test_invalid_email():
    with pytest.raises(ValidationError):
        UserRegister(
            username = "zxc_washer",
            email = "not-email",
            password = "qwertY12@"
        )
def test_short_password():
    with pytest.raises(ValidationError):
        UserRegister(
            username = "zxc_washer",
            email = "zxc_washer2004@gmail.com",
            password = "qw1"

        )
def test_user_register_password_without_digit():
    with pytest.raises(ValidationError):
        UserRegister(
            username="anna",
            email="anna@example.com",
            password="StrongPass!"
        )


def test_user_register_password_without_special_symbol():
    with pytest.raises(ValidationError):
        UserRegister(
            username="anna",
            email="anna@example.com",
            password="Strong123"
        )