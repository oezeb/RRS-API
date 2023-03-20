from werkzeug.security import check_password_hash
import logging

HEADERS = {'Content-Type': 'application/json'}
BASE_URL = 'http://127.0.0.1:5000'

# Users
USERS_URL = f'{BASE_URL}/users'
def test_users_get(client):
    res = client.get(USERS_URL, headers=HEADERS, json={'username': 'test'})
    assert res.status_code == 200
    assert len(res.json) == 1
    assert res.json[0]['username'] == 'test'
    assert check_password_hash(res.json[0]['password'], 'test')

def test_users_post(client):
    res = client.post(USERS_URL, headers=HEADERS, json=[{'username': 'test2', 'password': 'test2'}])
    assert res.status_code == 201

def test_users_delete(client):
    res = client.delete(USERS_URL, headers=HEADERS, json={'username': 'test'})
    assert res.status_code == 204

# auth
def test_register(client):
    url = f"{BASE_URL}/auth/register"
    res = client.post(url, headers=HEADERS, json={'username': 'test2', 'password': 'test'})
    assert res.status_code == 201
    res = client.post(url, headers=HEADERS, json={'username': 'test2', 'password': 'test'})
    assert res.status_code == 409

def test_uname_passwrd_auth(client):
    url = f"{BASE_URL}/auth"
    res = client.post(url, headers=HEADERS, json={'username': 'test', 'password': 'test'})
    assert res.status_code == 200

def test_token_auth(client, app):
    url = f"{BASE_URL}/auth"
    res = client.post(url, headers=HEADERS, json={'username': 'test', 'password': 'test'})
    assert res.status_code == 200
    # res = client.get(url, cookies=res.cookies)
    # assert res.status_code == 200

# 
def test_reservation(client, app):
    with app.app_context():
        res = client.post(f"{BASE_URL}/reservation_tickets", headers=HEADERS, json=[{'username': 'test'}])
        assert len(res.json['auto_increments']) == 1
        ticket = res.json['auto_increments'][0]
        res = client.get(f"{BASE_URL}/sessions", headers=HEADERS, json={'is_current': 1})
        assert len(res.json) > 0
        session_id = res.json[0]['session_id']
        res = client.post(f"{BASE_URL}/reservations", headers=HEADERS, json=[{
            'reservation_id': ticket,
            'room_id': 1,
            'session_id': session_id,
            'start_time': '2023-03-20 15:30',
            'end_time': '2023-03-20 16:30',
        }])
        assert res.status_code == 201
    