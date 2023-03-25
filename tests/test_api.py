from werkzeug.security import check_password_hash
import logging
import json

from flask import current_app

BASE_URL = 'http://127.0.0.1:5000'

def test_gets(client, app):
    with app.app_context():
        res = client.get(f"{BASE_URL}/user_roles", json={})
        assert res.status_code == 200
        res = client.get(f"{BASE_URL}/resv_status", json={})
        assert res.status_code == 200
        res = client.get(f"{BASE_URL}/resv_secu_levels", json={})
        assert res.status_code == 200
        res = client.get(f"{BASE_URL}/room_status", json={})
        assert res.status_code == 200

def test_auth(client, app):
    with app.app_context():
        # try to add a reservation window
        res = client.post(
            f"{BASE_URL}/resv_windows",
            json=[{"time_window": "48:00", "is_current": 0}]
        )
        assert res.status_code == 401 # not logged in, unauthorized
        # login existing admin user
        res = client.post(
            f"{BASE_URL}/login", 
            json={'username': 'admin', 'password': 'admin'}
        )
        assert res.status_code == 200
        headers = {"Authorization": f"Bearer {res.json['token']}"}
        res = client.post(
            f"{BASE_URL}/resv_windows",
            headers=headers,
            json=[{"time_window": "48:00", "is_current": 0}]
        )
        assert res.status_code == 201 # created
        assert len(res.json) == 1
        res = client.get(f"{BASE_URL}/resv_windows", headers=headers, json={"window_id": res.json[0]})
        assert res.status_code == 200

def login(username, password, client):
    res = client.post(
        f"{BASE_URL}/login", 
        json={'username': username, 'password': password}
    )
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json['token']}"} # return headers

def test_system_only(client, app):
    with app.app_context():
        res = client.get(f"{BASE_URL}/user_roles", json={})
        assert res.status_code == 200
        # try to add new role
        res = client.post(
            f"{BASE_URL}/user_roles",
            headers=login("admin", "admin", client),
            json=[{"role": 4, "label": "test"}]
        )
        assert res.status_code == 403 # forbidden

def test_admin_only(client, app):
    with app.app_context():
        # try to add new period
        res = client.post(
            f"{BASE_URL}/periods",
            headers=login("advanced", "advanced", client),
            json=[{"start_date": "2021-01-01", "end_date": "2021-12-31"}]
        )
        assert res.status_code == 403 # forbidden
    
def test_edit_own(client, app):
    with app.app_context():
        # try to add user_trans for restricted user
        res = client.post(
            f"{BASE_URL}/user_trans",
            headers=login("basic", "basic", client),
            json=[{"username": "restricted", "lang_code": "zh", "name": "待审核用户"}]
        )
        assert res.status_code == 403 # forbidden
        res = client.post(
            f"{BASE_URL}/user_trans",
            headers=login("restricted", "restricted", client),
            json=[{"username": "restricted", "lang_code": "zh", "name": "待审核用户"}]
        )
        assert res.status_code == 201 # created
        res = client.post(
            f"{BASE_URL}/user_trans",
            headers=login("admin", "admin", client),
            json=[{"username": "restricted", "lang_code": "en", "name": "Pending User"}]
        )
        assert res.status_code == 201 # created
        res = client.patch(
            f"{BASE_URL}/user_trans",
            headers=login("advanced", "advanced", client),
            json={"data": {"name": "已审核用户"}, "where": {"username": "restricted"}}
        )
        assert res.status_code == 403 # forbidden
        res = client.patch(
            f"{BASE_URL}/user_trans",
            headers=login("restricted", "restricted", client),
            json={"data": {"name": "Pending"}, "where": {"username": "restricted", "lang_code": "en"}}
        )
        assert res.status_code == 200 # updated
        res = client.patch(
            f"{BASE_URL}/user_trans",
            headers=login("admin", "admin", client),
            json={"data": {"name": "已审核用户"}, "where": {"username": "restricted", "lang_code": "zh"}}
        )
        assert res.status_code == 200 # updated
        res = client.delete(
            f"{BASE_URL}/user_trans",
            headers=login("advanced", "advanced", client),
            json={"username": "restricted"}
        )
        assert res.status_code == 403 # forbidden
        res = client.delete(
            f"{BASE_URL}/user_trans",
            headers=login("restricted", "restricted", client),
            json={"username": "restricted", "lang_code": "en"}
        )
        assert res.status_code == 204 # deleted
        res = client.delete(
            f"{BASE_URL}/user_trans",
            headers=login("admin", "admin", client),
            json={"username": "restricted", "lang_code": "zh"}
        )
        assert res.status_code == 204 # deleted

        # try to add new user
        res = client.post(
            f"{BASE_URL}/users",
            headers=login("advanced", "advanced", client),
            json=[{"username": "test", "password": "test", "role": 0}]
        )
        assert res.status_code == 403 # forbidden
        res = client.post(
            f"{BASE_URL}/users",
            headers=login("admin", "admin", client),
            json=[{"username": "test", "password": "test", "role": 0}]
        )
        assert res.status_code == 201 # created
        res = client.patch(
            f"{BASE_URL}/users",
            headers=login("advanced", "advanced", client),
            json={"data": {"name": "Advanced"}, "where": {"username": "advanced"}}
        )
        assert res.status_code == 200 # updated
        res = client.patch(
            f"{BASE_URL}/users",
            headers=login("advanced", "advanced", client),
            json={"data": {"name": "Test"}, "where": {"username": "test"}}
        )
        assert res.status_code == 403 # forbidden
        res = client.patch(
            f"{BASE_URL}/users",
            headers=login("advanced", "advanced", client),
            json={"data": {"password": "New"}, "where": {"username": "advanced"}}
        )
        assert res.status_code == 403 # forbidden
        res = client.patch(
            f"{BASE_URL}/users",
            headers=login("admin", "admin", client),
            json={"data": {"name": "Test"}, "where": {"username": "test"}}
        )
        assert res.status_code == 200 # updated


def test_reservations(client, app):
    pass

def test_time_slots(client, app):
    pass