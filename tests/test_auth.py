import base64, os, json

BASE_URL = "http://127.0.0.1:5000/api"

def test_register(client, app):
    with app.app_context():
        res = client.post(
            f"{BASE_URL}/register", 
            json={
                'username': 'test', 
                'password': 'test', 
                'name': '测试用户'
            }
        )
        assert res.status_code == 201
        
def test_login(client, app_with_data):
    with app_with_data.app_context():
        curr_dir = os.path.dirname(__file__)
        with open(os.path.join(curr_dir, 'data', 'users.json')) as f:
            user = json.load(f)[0]
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
    return client