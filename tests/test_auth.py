import base64

from data import insert_data, get_users

BASE_URL = "http://127.0.0.1:5000/api"

def test_register(client, app):
    with app.app_context():
        user = get_users()[0]
        user.pop('role')
        res = client.post(
            f"{BASE_URL}/register",
            json=user
        )
        assert res.status_code == 201
        
def test_login(client, app):
    with app.app_context():
        insert_data(only=['users'])
        user = get_users()[0]
        auth_client(client, user['username'], user['password'])


def auth_client(client, username, password):
    cred = f"{username}:{password}"
    token = base64.b64encode(cred.encode()).decode()
    res = client.post(
        f"{BASE_URL}/login",
        headers={ "Authorization" : f"Basic {token}" }
    )
    assert res.status_code == 200
    assert 'access_token' in res.headers['Set-Cookie']