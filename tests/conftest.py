import os, json, csv
import random
import datetime

import pytest
from werkzeug.security import generate_password_hash

from reservation_system import create_app
from reservation_system.db import init_db, insert

with open(os.path.join(os.path.dirname(__file__), 'data/users.json')) as f:
    users = json.load(f)
    users.append({'username': 'test', 'password': generate_password_hash('test')})

def csv_to_dict(filename):
    with open(filename) as f:
        reader = csv.reader(f)
        data, cols = [], None
        for line in reader:
            if not cols: cols = line
            else: data.append(dict(zip(cols, line)))
    return data

periods = csv_to_dict(os.path.join(os.path.dirname(__file__), 'data/periods.csv'))
rooms = csv_to_dict(os.path.join(os.path.dirname(__file__), 'data/rooms.csv'))
sessions = csv_to_dict(os.path.join(os.path.dirname(__file__), 'data/sessions.csv'))
for i in range(len(sessions)): sessions[i]['is_current'] = int(sessions[i]['is_current'])


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'DATABASE':"room_reservations",
        'DB_USER':"test",
        'DB_PASSWORD':"password",
    })

    with app.app_context():
        init_db()
        insert("users", data_list=users)
        insert("periods", data_list=periods)
        insert("rooms", data_list=rooms)
        insert("sessions", data_list=sessions)
        insert("reservation_tickets", [{'username': 'test'}, {'username': 'test'}])
        insert("reservations", [
            {
                'reservation_id': 1, 
                'room_id': random.randint(1, len(rooms)), 
                'session_id': random.randint(1, len(sessions)),
                'start_time': datetime.datetime.now() - datetime.timedelta(hours=2),
                'end_time': datetime.datetime.now(),
            },
            {
                'reservation_id': 2, 
                'room_id': random.randint(1, len(rooms)), 
                'session_id': random.randint(1, len(sessions)),
                'start_time': datetime.datetime.now() - datetime.timedelta(hours=5),
                'end_time': datetime.datetime.now() - datetime.timedelta(hours=2),
            },
        ])


    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
