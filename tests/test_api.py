
from reservation_system import db

BASE_URL = 'http://127.0.0.1:5000/api'

def test_get_reservations(client, app_with_data):
    pass

def test_get_reservations_status(client, app_with_data):
    pass

def test_get_reservations_privacy(client, app_with_data):
    pass

def test_get_users(client, app_with_data):
    with app_with_data.app_context():
        users = {}
        for user in db.select(db.User.TABLE):
            users[user['username']] = user

        res = client.get(f'{BASE_URL}/users')
        assert res.status_code == 200
        assert len(res.json) == len(users)
        for user in res.json:
            assert user['username'] in users
            assert set(user.keys()) == {'username', 'name'}

        res = client.get(f'{BASE_URL}/users?role=1')
        assert res.status_code == 200
        assert len(res.json) == 1

def test_get_users_roles(client, app_with_data):
    pass

def test_get_rooms(client, app_with_data):
    pass

def test_get_rooms_types(client, app_with_data):
    pass

def test_get_rooms_status(client, app_with_data):
    pass

def test_get_languages(client, app_with_data):
    pass

def test_get_sessions(client, app_with_data):
    pass

def test_get_notices(client, app_with_data):
    pass

def test_get_periods(client, app_with_data):
    pass

def test_get_settings(client, app_with_data):
    pass

