from datetime import datetime
from data import insert_data
from app import db, util

BASE_URL = 'http://127.0.0.1:5000/api'

def test_get_reservations(client, app):
    with app.app_context():
        insert_data(only=['users', 'rooms'])
        rooms = db.select(db.Room.TABLE)
        users = db.select(db.User.TABLE)

        for title, privacy, start, end in (
            ('public', db.ResvPrivacy.PUBLIC, '2020-01-01 00:00:00', '2020-01-01 01:00:00'),
            ('anonymous', db.ResvPrivacy.ANONYMOUS, '2020-01-01 02:00:00', '2020-01-01 03:00:00'),
            ('private', db.ResvPrivacy.PRIVATE, '2020-01-01 04:00:00', '2020-01-01 05:00:00'),
        ):
            res = db.insert(db.Reservation.RESV_TABLE, {
                'room_id': rooms[0]['room_id'],
                'username': users[0]['username'],
                'title': title,
                'privacy': privacy,
            })
            assert res['rowcount'] == 1
            resv_id = res['lastrowid']
            res = db.insert(db.Reservation.TS_TABLE, {
                'resv_id': resv_id,
                'username': users[0]['username'],
                'start_time': start,
                'end_time': end,
                'status': db.ResvStatus.PENDING,
            })
            assert res['rowcount'] == 1

        res = client.get(f'{BASE_URL}/reservations')
        assert res.status_code == 200
        assert len(res.json) == 3
        for resv in res.json:
            if resv['privacy'] == db.ResvPrivacy.ANONYMOUS:
                assert 'username' not in resv
                assert 'resv_id' not in resv
            elif resv['privacy'] == db.ResvPrivacy.PRIVATE:
                assert 'username' not in resv
                assert 'resv_id' not in resv
                assert 'title' not in resv
                assert 'note' not in resv

        today = datetime.today().strftime('%Y-%m-%d')
        res = client.get(f'{BASE_URL}/reservations?create_date={today}')
        assert res.status_code == 200
        assert all([resv['create_time'].startswith(today) for resv in res.json])


def test_get_reservations_status(client, app):
    with app.app_context():
        res = client.get(f'{BASE_URL}/reservations/status?status={db.ResvStatus.PENDING}')
        assert res.status_code == 200
        assert len(res.json) == 1
        assert res.json[0]['status'] == db.ResvStatus.PENDING

def test_get_reservations_privacy(client, app):
    with app.app_context():
        res = client.get(f'{BASE_URL}/reservations/privacy?privacy={db.ResvPrivacy.PUBLIC}')
        assert res.status_code == 200
        assert len(res.json) == 1
        assert res.json[0]['privacy'] == db.ResvPrivacy.PUBLIC

def test_get_users(client, app):
    with app.app_context():
        insert_data(only=['users'])
        users = {user['username']: user for user in db.select(db.User.TABLE)}

        res = client.get(f'{BASE_URL}/users')
        assert res.status_code == 200
        assert len(res.json) == len(users)
        for user in res.json:
            assert user['username'] in users
            assert set(user.keys()) == {'username', 'name'}

        username = list(users.keys())[0]
        res = client.get(f'{BASE_URL}/users?username={username}')
        assert res.status_code == 200
        assert len(res.json) == 1
        assert res.json[0]['username'] == username

def test_get_users_roles(client, app):
    with app.app_context():
        res = client.get(f'{BASE_URL}/users/roles?role={db.UserRole.ADMIN}')
        assert res.status_code == 200
        assert len(res.json) == 1
        assert res.json[0]['role'] == db.UserRole.ADMIN
    
def test_get_rooms(client, app):
    with app.app_context():
        insert_data(only=['rooms'])
        rooms = {room['room_id']: room for room in db.select(db.Room.TABLE)}

        res = client.get(f'{BASE_URL}/rooms')
        assert res.status_code == 200
        assert len(res.json) == len(rooms)
        for room in res.json:
            assert room['room_id'] in rooms
        
        type = list(rooms.values())[0]['type']
        res = client.get(f'{BASE_URL}/rooms?type={type}')
        assert res.status_code == 200
        assert all(room['type'] == type for room in res.json)

def test_get_rooms_types(client, app):
    with app.app_context():
        insert_data(only=['room_types'])
        types = {type['type']: type for type in db.select(db.RoomType.TABLE)}

        res = client.get(f'{BASE_URL}/rooms/types')
        assert res.status_code == 200
        assert len(res.json) == len(types)

        type = list(types.values())[0]['type']
        res = client.get(f'{BASE_URL}/rooms/types?type={type}')
        assert res.status_code == 200
        assert len(res.json) == 1

def test_get_rooms_status(client, app):
    with app.app_context():
        res = client.get(f'{BASE_URL}/rooms/status?status={db.RoomStatus.AVAILABLE}')
        assert res.status_code == 200
        assert len(res.json) == 1
        assert res.json[0]['status'] == db.RoomStatus.AVAILABLE

def test_get_languages(client, app):
    with app.app_context():
        res = client.get(f'{BASE_URL}/languages?lang_code={db.Language.EN}')
        assert res.status_code == 200
        assert len(res.json) == 1
        assert res.json[0]['lang_code'] == db.Language.EN

def test_get_sessions(client, app):
    with app.app_context():
        insert_data(only=['sessions'])
        sessions = {session['session_id']: session for session in db.select(db.Session.TABLE)}

        res = client.get(f'{BASE_URL}/sessions')
        assert res.status_code == 200
        assert len(res.json) == len(sessions)
        for session in res.json:
            assert session['session_id'] in sessions

        name = list(sessions.values())[0]['name']
        res = client.get(f'{BASE_URL}/sessions?name={name}')
        assert res.status_code == 200
        assert all(session['name'] == name for session in res.json)

def test_get_notices(client, app):
    with app.app_context():
        insert_data(only=['notices'])
        notices = {notice['notice_id']: notice for notice in db.select(db.Notice.TABLE)}

        res = client.get(f'{BASE_URL}/notices')
        assert res.status_code == 200
        assert len(res.json) == len(notices)
        for notice in res.json:
            assert notice['notice_id'] in notices

        title = list(notices.values())[0]['title']
        res = client.get(f'{BASE_URL}/notices?title={title}')
        assert res.status_code == 200
        assert all(notice['title'] == title for notice in res.json)

def test_get_periods(client, app):
    with app.app_context():
        insert_data(only=['periods'])
        periods = {period['period_id']: period for period in db.select(db.Period.TABLE)}

        res = client.get(f'{BASE_URL}/periods')
        assert res.status_code == 200
        assert len(res.json) == len(periods)
        for period in res.json:
            assert period['period_id'] in periods
        
        start_time = list(periods.values())[0]['start_time']
        res = client.get(f'{BASE_URL}/periods?start_time={start_time}')
        assert res.status_code == 200
        start_time = util.strftimedelta(start_time)
        assert all(period['start_time'] == start_time for period in res.json)

def test_get_settings(client, app):
    with app.app_context():
        res = client.get(f'{BASE_URL}/settings?id={db.Setting.TIME_WINDOW}')
        assert res.status_code == 200
        assert len(res.json) == 1
        assert res.json[0]['id'] == db.Setting.TIME_WINDOW
