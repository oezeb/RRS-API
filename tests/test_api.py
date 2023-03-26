from datetime import datetime, timedelta

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
        # try to add a new language without logging in
        res = client.post(
            f"{BASE_URL}/languages",
            json=[{"lang_code": "fr", "name": "French"}]
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
            f"{BASE_URL}/languages",
            headers=headers,
            json=[{"lang_code": "fr", "name": "French"}]
        )
        assert res.status_code == 201 # created
        assert len(res.json) == 1
        res = client.get(f"{BASE_URL}/languages", json={"lang_code": "fr"})
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
    post = lambda user, json: client.post(
        f"{BASE_URL}/reservations",
        headers=login(user, user, client),
        json=json
    )
    patch = lambda user, json: client.patch(
        f"{BASE_URL}/reservations",
        headers=login(user, user, client),
        json=json
    )

    res = post("admin", [{"username": "advanced", "room_id": 1, "session_id": 1, "secu_level": 2, "status": 1}])
    assert res.status_code == 201 # created
    assert len(res.json) == 1
    advanced_resv_id = res.json[0]
    res = post("advanced", [{"username": "basic", "room_id": 1, "session_id": 1, "secu_level": 0, "status": 1}])
    assert res.status_code == 403 # forbidden, cannot reserve for others
    res = post("advanced", [{"username": "advanced", "room_id": 1, "session_id": 1, "secu_level": 2, "status": 1}])
    assert res.status_code == 403 # forbidden, not current session
    res = post("advanced", [{"username": "advanced", "room_id": 2, "session_id": 2, "secu_level": 2, "status": 1}])
    assert res.status_code == 403 # forbidden, room not available
    res = post("advanced", [{"username": "advanced", "room_id": 1, "session_id": 2, "secu_level": 2, "status": 1}])
    assert res.status_code == 201 # created
    res = post("basic", [{"username": "basic", "room_id": 1, "session_id": 2, "secu_level": 2, "status": 1}])
    assert res.status_code == 403 # forbidden, can not create private secu_level
    res = post("restricted", [{"username": "restricted", "room_id": 1, "session_id": 2, "secu_level": 0, "status": 1}])
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
    res = client.post(
        f"{BASE_URL}/reservations",
        headers=login("basic", "basic", client),
        json=[{"username": "basic", "room_id": 1, "session_id": 2, "secu_level": 0, "status": 1}]
    )
    assert res.status_code == 201 # created
    confirmed_resv_id = res.json[0]
    res = client.post(
        f"{BASE_URL}/reservations",
        headers=login("basic", "basic", client),
        json=[{"username": "basic", "room_id": 1, "session_id": 2, "secu_level": 0, "status": 0}]
    )
    assert res.status_code == 201 # created
    pending_resv_id = res.json[0]
    res = client.post(
        f"{BASE_URL}/reservations",
        headers=login("admin", "admin", client),
        json=[{"username": "advanced", "room_id": 2, "session_id": 2, "secu_level": 0, "status": 0}]
    )
    assert res.status_code == 201 # created
    unavailable_room_resv_id = res.json[0]
    res = client.post(
        f"{BASE_URL}/reservations",
        headers=login("admin", "admin", client),
        json=[{"username": "advanced", "room_id": 3, "session_id": 1, "secu_level": 0, "status": 0}]
    )
    assert res.status_code == 201 # created
    unavailable_session_resv_id = res.json[0]

    res = client.post(
        f"{BASE_URL}/time_slots",
        headers=login("admin", "admin", client),
        json=[{"username": "basic", "resv_id": confirmed_resv_id, "start_time": "2023-04-01 11:00", "end_time": "2023-04-01 9:00"}]
    )
    assert res.status_code == 400 # bad start/end time
    res = client.post(
        f"{BASE_URL}/time_slots",
        headers=login("admin", "admin", client),
        json=[{"username": "basic", "resv_id": confirmed_resv_id, "start_time": "2023-04-01 2:00", "end_time": "2023-04-01 3:00"}]
    )
    assert res.status_code == 403 # forbidden, not in room opening hours
    res = client.post(
        f"{BASE_URL}/time_slots",
        headers=login("admin", "admin", client),
        json=[{"username": "basic", "resv_id": confirmed_resv_id, "start_time": "2024-04-01 2:00", "end_time": "2024-04-01 3:00"}]
    )
    assert res.status_code == 403 # forbidden, not in session
    res = client.post(
        f"{BASE_URL}/time_slots",
        headers=login("admin", "admin", client),
        json=[{"username": "basic", "resv_id": confirmed_resv_id, "start_time": "2023-04-01 9:00", "end_time": "2023-04-01 11:00"}]
    )
    assert res.status_code == 201 # created
    confirmed_slot_id = res.json[0]
    res = client.post(
        f"{BASE_URL}/time_slots",
        headers=login("admin", "admin", client),
        json=[{"username": "basic", "resv_id": confirmed_resv_id, "start_time": "2023-04-01 9:00", "end_time": "2023-04-01 11:00"}]
    )
    assert res.status_code == 403 # forbidden, time slot already exists
    res = client.post(
        f"{BASE_URL}/time_slots",
        headers=login("advanced", "advanced", client),
        json=[{"username": "basic", "resv_id": confirmed_resv_id, "start_time": "2023-04-01 14:00", "end_time": "2023-04-01 16:00"}]
    )
    assert res.status_code == 403 # forbidden, can not create time slot for others
    res = client.post(
        f"{BASE_URL}/time_slots",
        headers=login("advanced", "advanced", client),
        json=[{"username": "advanced", "resv_id": unavailable_room_resv_id, "start_time": "2023-04-01 14:00", "end_time": "2023-04-01 16:00"}]
    )
    assert res.status_code == 403 # forbidden, room is not available
    res = client.post(
        f"{BASE_URL}/time_slots",
        headers=login("advanced", "advanced", client),
        json=[{"username": "advanced", "resv_id": unavailable_session_resv_id, "start_time": "2023-04-01 14:00", "end_time": "2023-04-01 16:00"}]
    )
    assert res.status_code == 403 # forbidden, session is not available
    res = client.post(
        f"{BASE_URL}/time_slots",
        headers=login("basic", "basic", client),
        json=[{"username": "basic", "resv_id": confirmed_resv_id, "start_time": "2023-04-01 14:00", "end_time": "2023-04-01 16:00"}]
    )
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
    res = client.post(
        f"{BASE_URL}/time_slots",
        headers=login("basic", "basic", client),
        json=[{"username": "basic", "resv_id": confirmed_resv_id, "start_time": "2023-04-01 14:00", "end_time": "2023-04-01 16:00"}]
    )
    assert res.status_code == 403 # forbidden, not in reservation window
    res = client.post(
        f"{BASE_URL}/time_slots",
        headers=login("basic", "basic", client),
        json=[{"username": "basic", "resv_id": confirmed_resv_id, "start_time": datetime.now().strftime("%Y-%m-%d %H:%M"), "end_time": (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")}]
    )
    # assert res.status_code == 201 # created