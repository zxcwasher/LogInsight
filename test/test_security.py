from utils.security import get_password_hash, verify_hash
from utils.jwt import create_token

def test_password_hash():
    password = "@Kiev98251"

    hashed_password = get_password_hash(password)

    assert hashed_password != password

def test_verefity_password_hash():
    password = "@Kiev98251"
    hashed_password = get_password_hash (password)
    result = verify_hash(password, hashed_password)
    assert result is True

def test_verify_hash_with_wrong_password():
    password = "Strong123!"
    hashed_password = get_password_hash(password)

    result = verify_hash("Wrong123!", hashed_password)

    assert result is False


def test_hash_is_different_each_time():
    password = "Strong123!"

    hash_1 = get_password_hash(password)
    hash_2 = get_password_hash(password)

    assert hash_1 != hash_2




def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "anna",
            "email": "anna@example.com",
            "password": "Strong123!",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_user(client):
    client.post(
        "/auth/register",
        json={
            "username": "anna",
            "email": "anna@example.com",
            "password": "Strong123!",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "anna",
            "password": "Strong123!",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "username": "anna",
            "email": "anna@example.com",
            "password": "Strong123!",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "anna",
            "password": "Wrong123!",
        },
    )

    assert response.status_code == 401


def test_protected_logs_endpoint_without_token(client):
    response = client.post(
        "/logs/process",
        json={
            "raw_log": "ERROR payment-service status=500 TimeoutError",
        },
    )

    assert response.status_code == 403


def test_viewer_cannot_process_log(client):
    register_response = client.post(
        "/auth/register",
        json={
            "username": "anna",
            "email": "anna@example.com",
            "password": "Strong123!",
        },
    )

    token = register_response.json()["access_token"]

    response = client.post(
        "/logs/process",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "raw_log": "ERROR payment-service status=500 TimeoutError",
        },
    )

    assert response.status_code == 403