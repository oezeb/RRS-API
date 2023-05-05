from datetime import datetime, timedelta
import base64

from flask import Flask
from flask.testing import FlaskClient

BASE_URL = 'http://127.0.0.1:5000/api'

def test_gets(client: FlaskClient, app: Flask):
    with app.app_context():
        res = client.get(f"{BASE_URL}/user_roles", json={})
        assert res.status_code == 200
        res = client.get(f"{BASE_URL}/resv_status", json={})
        assert res.status_code == 200
        res = client.get(f"{BASE_URL}/resv_secu_levels", json={})
        assert res.status_code == 200
        res = client.get(f"{BASE_URL}/room_status", json={})
        assert res.status_code == 200

def login(username, password, client):
    res = client.post(
        f"{BASE_URL}/login",
        headers={
            "Authorization": f"Basic {base64.b64encode(f'{username}:{password}'.encode('utf-8')).decode('utf-8')}"
        }
    )
    assert res.status_code == 200
    assert 'access_token' in res.headers['Set-Cookie']
    client.set_cookie('localhost', 'access_token', res.headers['Set-Cookie'].split('=')[1].split(';')[0])

def test_auth(client: FlaskClient, app: Flask):
    with app.app_context():
        # try to add a new language without logging in
        res = client.post(
            f"{BASE_URL}/languages",
            json=[{"lang_code": "fr", "name": "French"}]
        )
        assert res.status_code == 401 # not logged in, unauthorized
        # login existing admin user
        login("admin", "admin", client)
        res = client.post(
            f"{BASE_URL}/languages",
            json=[{"lang_code": "fr", "name": "French"}]
        )
        assert res.status_code == 201 # created
        assert len(res.json) == 1
        res = client.get(f"{BASE_URL}/languages", json={"lang_code": "fr"})
        assert res.status_code == 200

def test_system_only(client, app):
    with app.app_context():
        res = client.get(f"{BASE_URL}/user_roles", json={})
        assert res.status_code == 200
        # try to add new role
        login("admin", "admin", client)
        res = client.post(
            f"{BASE_URL}/user_roles",
            json=[{"role": 4, "label": "test"}]
        )
        assert res.status_code == 403 # forbidden

def test_admin_only(client, app):
    with app.app_context():
        # try to add new period
        login("advanced", "advanced", client)
        res = client.post(
            f"{BASE_URL}/periods",
            json=[{"start_date": "2021-01-01", "end_date": "2021-12-31"}]
        )
        assert res.status_code == 403 # forbidden
    
def test_edit_own(client, app):
    with app.app_context():
        # try to add user_trans for restricted user
        login("basic", "basic", client)
        res = client.post(
            f"{BASE_URL}/user_trans",
            json=[{"username": "restricted", "lang_code": "zh", "name": "待审核用户"}]
        )
        assert res.status_code == 403 # forbidden
        login("restricted", "restricted", client)
        res = client.post(
            f"{BASE_URL}/user_trans",
            json=[{"username": "restricted", "lang_code": "zh", "name": "待审核用户"}]
        )
        assert res.status_code == 201 # created
        login("admin", "admin", client)
        res = client.post(
            f"{BASE_URL}/user_trans",
            json=[{"username": "restricted", "lang_code": "en", "name": "Pending User"}]
        )
        assert res.status_code == 201 # created
        login("advanced", "advanced", client)
        res = client.patch(
            f"{BASE_URL}/user_trans",
            json={"data": {"name": "已审核用户"}, "where": {"username": "restricted"}}
        )
        assert res.status_code == 403 # forbidden
        login("restricted", "restricted", client)
        res = client.patch(
            f"{BASE_URL}/user_trans",
            json={"data": {"name": "Pending"}, "where": {"username": "restricted", "lang_code": "en"}}
        )
        assert res.status_code == 200 # updated
        login("admin", "admin", client)
        res = client.patch(
            f"{BASE_URL}/user_trans",
            json={"data": {"name": "已审核用户"}, "where": {"username": "restricted", "lang_code": "zh"}}
        )
        assert res.status_code == 200 # updated
        login("advanced", "advanced", client)
        res = client.delete(
            f"{BASE_URL}/user_trans",
            json={"username": "restricted"}
        )
        assert res.status_code == 403 # forbidden
        login("restricted", "restricted", client)
        res = client.delete(
            f"{BASE_URL}/user_trans",
            json={"username": "restricted", "lang_code": "en"}
        )
        assert res.status_code == 204 # deleted
        login("admin", "admin", client)
        res = client.delete(
            f"{BASE_URL}/user_trans",
            json={"username": "restricted", "lang_code": "zh"}
        )
        assert res.status_code == 204 # deleted

        # try to add new user
        login("advanced", "advanced", client)
        res = client.post(
            f"{BASE_URL}/users",
            json=[{"username": "test", "password": "test", "name": "测试", "role": 0}]
        )
        assert res.status_code == 403 # forbidden
        login("admin", "admin", client)
        res = client.post(
            f"{BASE_URL}/users",
            json=[{"username": "test", "password": "test", "name": "测试", "role": 0}]
        )
        assert res.status_code == 201 # created
        login("advanced", "advanced", client)
        res = client.patch(
            f"{BASE_URL}/users",
            json={"data": {"name": "Advanced"}, "where": {"username": "advanced"}}
        )
        assert res.status_code == 200 # updated
        res = client.patch(
            f"{BASE_URL}/users",
            json={"data": {"name": "Test"}, "where": {"username": "test"}}
        )
        assert res.status_code == 403 # forbidden
        res = client.patch(
            f"{BASE_URL}/users",
            json={"data": {"password": "New"}, "where": {"username": "advanced"}}
        )
        assert res.status_code == 403 # forbidden
        login("admin", "admin", client)
        res = client.patch(
            f"{BASE_URL}/users",
            json={"data": {"name": "Test"}, "where": {"username": "test"}}
        )
        assert res.status_code == 200 # updated

def reservations_post(client, user, json): 
    login(user, user, client)
    return client.post(
        f"{BASE_URL}/reservations",
        json=json
    )
def reservations_patch(client, user, json):
    login(user, user, client)
    return client.patch(
        f"{BASE_URL}/reservations",
        json=json
    )
def test_reservations(client, app):
    post = lambda user, json: reservations_post(client, user, json)
    patch = lambda user, json: reservations_patch(client, user, json)

    res = post("admin", [{"username": "advanced", "room_id": 1, "session_id": 1, "secu_level": 2, "status": 1, "title": "Math Class"}])
    assert res.status_code == 201 # created
    assert len(res.json) == 1
    advanced_resv_id = res.json[0]
    res = post("advanced", [{"username": "basic", "room_id": 1, "session_id": 1, "secu_level": 0, "status": 1, "title": "Bio Class"}])
    assert res.status_code == 403 # forbidden, cannot reserve for others
    res = post("advanced", [{"username": "advanced", "room_id": 1, "session_id": 1, "secu_level": 2, "status": 1, "title": "Bio Class"}])
    assert res.status_code == 403 # forbidden, not current session
    res = post("advanced", [{"username": "advanced", "room_id": 2, "session_id": 2, "secu_level": 2, "status": 1, "title": "Bio Class"}])
    assert res.status_code == 403 # forbidden, room not available
    res = post("advanced", [{"username": "advanced", "room_id": 1, "session_id": 2, "secu_level": 2, "status": 1, "title": "Bio Class"}])
    assert res.status_code == 201 # created
    res = post("basic", [{"username": "basic", "room_id": 1, "session_id": 2, "secu_level": 2, "status": 1, "title": "Geo Class"}])
    assert res.status_code == 403 # forbidden, can not create private secu_level
    res = post("restricted", [{"username": "restricted", "room_id": 1, "session_id": 2, "secu_level": 0, "status": 1, "title": "Geo Class"}])
    assert res.status_code == 403 # forbidden, can not create confirmed status

    res = patch("admin", {"data": {"status": 2}, "where": {"username": "advanced", "resv_id": advanced_resv_id}})
    assert res.status_code == 200 # updated
    res = patch("basic", {"data": {"note": "Hello"}, "where": {"username": "advanced", "resv_id": advanced_resv_id}})
    assert res.status_code == 403 # forbidden, can not update others
    res = patch("advanced", {"data": {"room_id": 3}, "where": {"username": "advanced", "resv_id": advanced_resv_id}})
    assert res.status_code == 403 # forbidden, can not update room
    res = patch("advanced", {"data": {"status": 3}, "where": {"username": "advanced", "resv_id": advanced_resv_id}})
    assert res.status_code == 403 # forbidden, can only update status to 2(cancelled)
    res = patch("advanced", {"data": {"status": 2, "note": "Hello"}, "where": {"username": "advanced", "resv_id": advanced_resv_id}})
    assert res.status_code == 200 # updated
    res = client.delete(
        f"{BASE_URL}/reservations",
        headers=login("advanced", "advanced", client),
        json={"where": {"username": "advanced", "resv_id": advanced_resv_id}}
    )
    assert res.status_code == 403 # forbidden, can not delete reservations

def test_time_slots(client, app):
    res = reservations_post(client, "basic", [{"username": "basic", "room_id": 1, "session_id": 2, "secu_level": 0, "status": 1, "title": "Geo Class"}])
    assert res.status_code == 201 # created
    confirmed_resv_id = res.json[0]
    res = reservations_post(client, "basic", [{"username": "basic", "room_id": 1, "session_id": 2, "secu_level": 0, "status": 0, "title": "Bio Class"}])
    assert res.status_code == 201 # created
    pending_resv_id = res.json[0]
    res = reservations_post(client, "admin", [{"username": "advanced", "room_id": 2, "session_id": 2, "secu_level": 0, "status": 0, "title": "History Class"}])
    assert res.status_code == 201 # created
    unavailable_room_resv_id = res.json[0]
    res = reservations_post(client, "admin", [{"username": "advanced", "room_id": 3, "session_id": 1, "secu_level": 0, "status": 0, "title": "Fake Meeting"}])
    assert res.status_code == 201 # created
    unavailable_session_resv_id = res.json[0]

    post = lambda user, json: client.post(
        f"{BASE_URL}/time_slots",
        headers=login(user, user, client),
        json=json
    )


    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    # bad start/end time
    start = today + timedelta(days=1, hours=11)
    end = today + timedelta(days=1, hours=9)
    res = post("admin", [{"username": "basic", "resv_id": confirmed_resv_id, "start_time": start.isoformat(' '), "end_time": end.isoformat(' ')}])
    assert res.status_code == 400 # bad start/end time
    # not in room opening hours
    start = today + timedelta(days=1, hours=2)
    end = today + timedelta(days=1, hours=3)
    res = post("admin", [{"username": "basic", "resv_id": confirmed_resv_id, "start_time": start.isoformat(' '), "end_time": end.isoformat(' ')}])
    assert res.status_code == 403 # forbidden, not in room opening hours
    # not in session
    res = post("admin", [{"username": "basic", "resv_id": confirmed_resv_id, "start_time": "2025-04-01 9:00", "end_time": "2025-04-01 11:00"}])
    assert res.status_code == 403 # forbidden, not in session
    # 
    start = today + timedelta(days=1, hours=9)
    end = today + timedelta(days=1, hours=11)
    res = post("admin", [{"username": "basic", "resv_id": confirmed_resv_id, "start_time": start.isoformat(' '), "end_time": end.isoformat(' ')}])
    assert res.status_code == 201 # created
    # time slot already exists
    confirmed_slot_id = res.json[0]
    res = post("admin", [{"username": "basic", "resv_id": confirmed_resv_id, "start_time": start.isoformat(' '), "end_time": end.isoformat(' ')}])
    assert res.status_code == 403 # forbidden, time slot already exists
    #  can not create time slot for others
    start = today + timedelta(days=1, hours=14)
    end = today + timedelta(days=1, hours=16)
    res = post("advanced", [{"username": "basic", "resv_id": confirmed_resv_id, "start_time": start.isoformat(' '), "end_time": end.isoformat(' ')}])
    assert res.status_code == 403 # forbidden, can not create time slot for others
    #  room is not available
    res = post("advanced", [{"username": "advanced", "resv_id": unavailable_room_resv_id, "start_time": start.isoformat(' '), "end_time": end.isoformat(' ')}])
    assert res.status_code == 403 # forbidden, room is not available
    res = post("advanced", [{"username": "advanced", "resv_id": unavailable_session_resv_id, "start_time": start.isoformat(' '), "end_time": end.isoformat(' ')}])
    assert res.status_code == 403 # forbidden, session is not available
    res = post("basic", [{"username": "basic", "resv_id": confirmed_resv_id, "start_time": start.isoformat(' '), "end_time": end.isoformat(' ')}])
    assert res.status_code == 403 # forbidden, basic user confirmed reservation can not have more than one time slot
    res = client.delete(
        f"{BASE_URL}/time_slots",
        headers=login("basic", "basic", client),
        json={"username": "basic", "slot_id": confirmed_slot_id, "resv_id": confirmed_resv_id}
    )
    assert res.status_code == 403 # forbidden, basic user can not delete confirmed time slot
    res = client.delete(
        f"{BASE_URL}/time_slots",
        headers=login("admin", "admin", client),
        json={"username": "basic", "slot_id": confirmed_slot_id, "resv_id": confirmed_resv_id}
    )
    assert res.status_code == 204 # deleted
    # not in reservation window
    start = today + timedelta(days=5, hours=14)
    end = today + timedelta(days=5, hours=16)
    res = post("basic", [{"username": "basic", "resv_id": confirmed_resv_id, "start_time": start.isoformat(' '), "end_time": end.isoformat(' ')}])
    assert res.status_code == 403 # forbidden, not in reservation window
    # exceeds maximum reservation time
    start = today + timedelta(days=1, hours=9)
    end = today + timedelta(days=1, hours=17)
    res = post("basic", [{"username": "basic", "resv_id": confirmed_resv_id, "start_time": start.isoformat(' '), "end_time": end.isoformat(' ')}])
    assert res.status_code == 403 # forbidden, exceeds maximum reservation time
    start = today + timedelta(days=1, hours=9)
    end = today + timedelta(days=1, hours=11)
    res = post("basic", [{"username": "basic", "resv_id": confirmed_resv_id, "start_time": start.isoformat(' '), "end_time": end.isoformat(' ')}])
    assert res.status_code == 201 # created

    res = reservations_post(client, "advanced", [{"username": "advanced", "room_id": 3, "session_id": 2, "secu_level": 0, "status": 0, "title": "硕士论文答辩"}])
    assert res.status_code == 201 # created
    resv_id = res.json[0]
    res = client.post(
        f"{BASE_URL}/resv_trans",
        headers=login("advanced", "advanced", client),
        json=[{"username": "advanced", "resv_id": resv_id, "lang_code": "en", "title": "Master Thesis Defense"}]
    )
    assert res.status_code == 201 # created
    start = today + timedelta(days=1, hours=14, minutes=30)
    end = today + timedelta(days=1, hours=16, minutes=30)
    res = post("advanced", [{"username": "advanced", "resv_id": resv_id, "start_time": start.isoformat(' '), "end_time": end.isoformat(' ')}])
    assert res.status_code == 201 # created
    res = reservations_post(client, "restricted", [{"username": "restricted", "room_id": 3, "session_id": 2, "secu_level": 0, "status": 0, "title": "商务会议"}])
    assert res.status_code == 201 # created
    resv_id = res.json[0]
    res = client.post(
        f"{BASE_URL}/resv_trans",
        headers=login("restricted", "restricted", client),
        json=[{"username": "restricted", "resv_id": resv_id, "lang_code": "en", "title": "Business Meeting"}]
    )
    assert res.status_code == 201 # created
    start = today + timedelta(days=1, hours=18)
    end = today + timedelta(days=1, hours=21, minutes=30)
    res = post("restricted", [{"username": "restricted", "resv_id": resv_id, "start_time": start.isoformat(' '), "end_time": end.isoformat(' ')}])
    assert res.status_code == 201 # created

def test_populate(client):
    # post notices
    login("admin", "admin", client)
    res = client.post(
        f"{BASE_URL}/notices",
        json=[{
            "username": "admin",
            "title": "系统维护",
            "content": "系统将于2020年1月1日0时至2020年1月1日1时进行维护，期间将无法使用。",
        }]
    )
    assert res.status_code == 201 # created
    res = client.post(
        f"{BASE_URL}/notices",
        json=[{
            "username": "admin",
            "title": "简单通知公告",
            "content": "测试图片是否能够正常显示。\n\n![图片](http://127.0.0.1:5000/static/attachments/1.jpg)\n",
            "update_time": (datetime.now() + timedelta(days=1)).isoformat(' ')
        }]
    )
    assert res.status_code == 201 # created