import os, json

import pytest
from werkzeug.security import generate_password_hash

from reservation_system import create_app
from reservation_system.db import init_db, insert_users



with open(os.path.join(os.path.dirname(__file__), 'users.json')) as f:
    users = json.load(f)
    users.append({'username': 'test', 'password': generate_password_hash('test')})

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')
    

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'DATABASE':"room_reservations",
    })

    with app.app_context():
        init_db()
        insert_users(users)

    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    return AuthActions(client)
