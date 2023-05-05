import base64
BASE_URL = "http://127.0.0.1:5000/api"

def test_register(client, app):
    with app.app_context():
        res = client.post(
            f"{BASE_URL}/register", 
            json={'username': 'test', 'password': 'test', 'name': '测试用户', 'role': 1}
        )
        assert res.status_code == 403
        res = client.post(
            f"{BASE_URL}/register", 
            json={'username': 'test', 'password': 'test', 'name': '测试用户', 'role': 0}
        )
        assert res.status_code == 201
        res = client.post(
            f"{BASE_URL}/register", 
            json={'username': 'test', 'password': 'again', 'name': '测试', 'role': 0}
        )
        assert res.status_code == 409
        
def test_login(client, app):
    with app.app_context():
        res = client.post(
            f"{BASE_URL}/login", 
            headers={
                "Authorization" : f"Basic {base64.b64encode(b'fake:admin').decode('utf-8')}"
            }
        )
        assert res.status_code == 401
        res = client.post(
            f"{BASE_URL}/login",
            headers={
                "Authorization": f"Basic {base64.b64encode(b'admin:admin').decode('utf-8')}"
            }
        )
        assert res.status_code == 200
        assert 'access_token' in res.headers['Set-Cookie']