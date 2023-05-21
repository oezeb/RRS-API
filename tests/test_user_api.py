import base64, os, json

from test_auth import auth_client

BASE_URL = "http://127.0.0.1:5000/api"

def test_get_user(client, app_with_data):
    with app_with_data.app_context():
        with open(os.path.join(os.path.dirname(__file__), 'data', 'users.json')) as f:
            user = json.load(f)[0]
        
        auth_client(client, user['username'], user['password'])
        
        res = client.get(f"{BASE_URL}/user")
        assert res.status_code == 200
        assert 'username' in res.json
        assert res.json['username'] == user['username']

def test_patch_user(client, app_with_data):
    with app_with_data.app_context():
        with open(os.path.join(os.path.dirname(__file__), 'data', 'users.json')) as f:
            user = json.load(f)[0]
        
        auth_client(client, user['username'], user['password'])
        
        res = client.patch(
            f"{BASE_URL}/user",
            json={
                'email': 'test@mail.com',
                'password': user['password'],
                'new_password': 'test',
            }
        )
        assert res.status_code == 204
        auth_client(client, user['username'], 'test')

def test_get_reservations(client, app_with_data):
    pass

def test_post_reservations(client, app_with_data):
    pass

def test_patch_reservations(client, app_with_data):
    pass

def test_post_advanced_reservations(client, app_with_data):
    pass