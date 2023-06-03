from data import insert_data, get_users, get_rooms, get_periods, insert_resv
from test_auth import auth_client
from datetime import datetime, timedelta

from app import db
from app.user_api import util

BASE_URL = "http://127.0.0.1:5000/api"

def test_get_user(client, app):
    with app.app_context():
        insert_data(only=['users'])
        users = get_users()

        auth_client(client, users[0]['username'], users[0]['password'])
        
        res = client.get(f"{BASE_URL}/user")
        assert res.status_code == 200
        assert 'username' in res.json
        assert res.json['username'] == users[0]['username']

def test_patch_user(client, app):
    with app.app_context():
        insert_data(only=['users'])
        users = get_users()
        
        auth_client(client, users[0]['username'], users[0]['password'])
        
        res = client.patch(
            f"{BASE_URL}/user",
            json={
                'email': 'test@mail.com',
                'password': users[0]['password'],
                'new_password': 'test',
            }
        )
        assert res.status_code == 204
        auth_client(client, users[0]['username'], 'test')

def test_get_reservation(client, app):
    with app.app_context():
        insert_data(only=['users', 'rooms'])
        users = get_users()
        rooms = get_rooms()

        for username, start, end in (
            (users[0]['username'], '2020-01-01 00:00:00', '2020-01-01 01:00:00'),
            (users[1]['username'], '2020-01-01 01:00:00', '2020-01-01 02:00:00'),
        ):
            resv = {
                'username': username,
                'room_id': rooms[0]['room_id'],
                'title': 'test',
                'privacy': db.ResvPrivacy.PUBLIC,
                'start_time': start,
                'end_time': end,
                'status': db.ResvStatus.PENDING,
            }
            insert_resv(**resv)
        
        auth_client(client, users[0]['username'], users[0]['password'])

        res = client.get(f"{BASE_URL}/user/reservation")
        assert res.status_code == 200
        assert all([resv['username'] == users[0]['username'] for resv in res.json])

def test_post_reservation(client, app):
    """
    Posting a reservation should meet the following conditions:
    - now <= start_time < end_time <= now + time_window
    - end_time - start_time <= time_limit
    - time range is a combination of periods
    - room is available
    - max_reservations_per_day is not exceeded
    """
    with app.app_context():
        insert_data(['users', 'rooms', 'periods'])
        users = {user['username']: user for user in get_users()}
        rooms = get_rooms()
        periods = get_periods()

        res = db.select(db.User.TABLE, role=db.UserRole.BASIC)
        assert len(res) > 0
        username = res[0]['username']
        password = users[username]['password']

        auth_client(client, username, password)

        today = datetime.today()
        today_str = today.strftime('%Y-%m-%d')
        res = db.select(db.Room.TABLE, status=db.RoomStatus.AVAILABLE)
        assert len(res) > 0
        room_id = res[0]['room_id']
        period = periods[0]

        resv = {
            'room_id': room_id,
            'start_time': f"{today_str} {period['start_time']}",
            'end_time': f"{today_str} {period['end_time']}",
            'title': 'test',
        }

        # now <= start_time
        start_time = resv['start_time']
        resv['start_time'] = (today + timedelta(days=-1)).strftime('%Y-%m-%d %H:%M:%S')
        res = client.post(f"{BASE_URL}/user/reservation", json=resv)
        assert res.status_code == 400
        resv['start_time'] = start_time

        # end_time <= now + time_window
        end_time = resv['end_time']
        tm = util.time_window()
        assert tm is not None
        resv['end_time'] = (today + tm).strftime('%Y-%m-%d %H:%M:%S')
        res = client.post(f"{BASE_URL}/user/reservation", json=resv)
        assert res.status_code == 400
        resv['end_time'] = end_time

        # end_time - start_time <= time_limit
        end_time = resv['end_time']
        tm = util.time_limit()
        assert tm is not None
        resv['end_time'] = (today + tm).strftime('%Y-%m-%d %H:%M:%S')
        res = client.post(f"{BASE_URL}/user/reservation", json=resv)
        assert res.status_code == 400
        resv['end_time'] = end_time





        
        



def test_patch_reservation(client, app):
    with app.app_context():
        insert_data(only=['users', 'rooms'])
        users = get_users()
        rooms = get_rooms()

        resv = {
            'username': users[0]['username'],
            'room_id': rooms[0]['room_id'],
            'start_time': '2020-01-01 00:00:00',
            'end_time': '2020-01-01 01:00:00',
            'title': 'test',
            'privacy': db.ResvPrivacy.PUBLIC,
            'status': db.ResvStatus.PENDING,
        }
        resv_id = insert_resv(**resv)

        auth_client(client, users[0]['username'], users[0]['password'])

        res = client.patch(
            f"{BASE_URL}/user/reservation/{resv_id}",
            json={
                'room_id': rooms[0]['room_id'],
                'title': 'test-patch'
            }
        )
        assert res.status_code == 204

        res = db.select(
            db.Reservation.TABLE,
            username=users[0]['username'],
            resv_id=resv_id,
        )
        assert len(res) == 1
        assert res[0]['title'] == 'test-patch'

def test_post_advanced_reservation(client, app):
    pass
