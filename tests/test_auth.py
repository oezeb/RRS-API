BASE_URL = "http://127.0.0.1:5000"

def test_register(client, app):
    with app.app_context():
        res = client.post(
            f"{BASE_URL}/register", 
            json={'username': 'test', 'password': 'test', 'role': 1}
        )
        assert res.status_code == 403
        res = client.post(
            f"{BASE_URL}/register", 
            json={'username': 'test', 'password': 'test'}
        )
        assert res.status_code == 201
        res = client.post(
            f"{BASE_URL}/register", 
            json={'username': 'test', 'password': 'again'}
        )
        assert res.status_code == 409
        
def test_login(client, app):
    with app.app_context():
        res = client.post(
            f"{BASE_URL}/login", 
            json={'username': 'admin', 'password': 'test'}
        )
        assert res.status_code == 401
        res = client.post(
            f"{BASE_URL}/login", 
            json={'username': 'admin', 'password': 'admin'}
        )
        assert res.status_code == 200 

def test_change_password(client, app):
    with app.app_context():
        res = client.post(
            f"{BASE_URL}/change_password", 
            json={'username': 'admin', 'password': 'admin', 'new_password': 'test'}
        )
        assert res.status_code == 401
        res = client.post(
            f"{BASE_URL}/login", 
            json={'username': 'admin', 'password': 'admin'}
        )
        assert res.status_code == 200
        headers = {"Authorization": f"Bearer {res.json['token']}"}
        res = client.post(
            f"{BASE_URL}/change_password", 
            headers=headers, json={'username': 'admin', 'password': 'test', 'new_password': 'test'}
        )
        assert res.status_code == 401
        res = client.post(
            f"{BASE_URL}/change_password", 
            headers=headers, json={'username': 'admin', 'password': 'admin', 'new_password': 'test'}
        )
        assert res.status_code == 201
        res = client.post(
            f"{BASE_URL}/login", 
            json={'username': 'admin', 'password': 'admin'}
        )
        assert res.status_code == 401
        res = client.post(
            f"{BASE_URL}/login", 
            json={'username': 'admin', 'password': 'test'}
        )
        assert res.status_code == 200
