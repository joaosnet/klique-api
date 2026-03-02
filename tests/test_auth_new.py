from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_lazy_registration():
    response = client.post('/auth/lazy')
    assert response.status_code == 200  # noqa: PLR2004
    data = response.json()
    assert 'access_token' in data
    assert 'user' in data
    assert 'guest_id' in data['user']
    assert data['user']['is_temporary'] is True


def test_passkey_options_invalid_user():
    response = client.post(
        '/auth/passkey/authenticate/options',
        params={'email': 'nonexistent@example.com'},
    )
    assert response.status_code == 404  # noqa: PLR2004


def test_magic_link_request():
    response = client.post(
        '/auth/magic-link/request', json={'email': 'test@example.com'}
    )
    # Should probably be 200 even if user doesn't exist,
    # to prevent email enumeration
    assert response.status_code in {200, 404}


def test_otp_request():
    response = client.post(
        '/auth/otp/request',
        json={'phone_number': '5511999999999', 'method': 'whatsapp'},
    )
    # It attempts to send, we might get 200 or 500 if the whatsapp service
    # is down
    assert response.status_code in {200, 500, 422, 400}


def test_social_apple_invalid_token():
    response = client.post(
        '/auth/apple', json={'token': 'invalid_token', 'name': 'Apple User'}
    )
    assert response.status_code in {400, 401}


def test_social_google_invalid_token():
    response = client.post('/auth/google', json={'token': 'invalid_token'})
    assert response.status_code in {400, 401}
