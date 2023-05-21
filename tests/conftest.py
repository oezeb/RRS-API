import base64
import json
import logging
import os

import click
import pytest
from flask import Flask
from werkzeug.security import generate_password_hash

from reservation_system import create_app, db

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'DATABASE':"room_reservations",
        'DB_USER':"test",
        'DB_PASSWORD':"password",
    })

    with app.app_context():
        db.init_db()
    yield app

@pytest.fixture
def client(app):
    return app.test_client(use_cookies=True)

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def app_with_data(app):
    with app.app_context():
        def _insert(table, data_list):
            cnx = db.get_cnx(); cursor = cnx.cursor()
            for data in data_list:
                cols = ', '.join(data.keys())
                values = ', '.join(['%s'] * len(data))
                query = f"INSERT INTO {table} ({cols}) VALUES ({values})"

                cursor.execute(query, tuple(data.values()))
            cnx.commit(); cursor.close()
        
        for filename, table in (
            (   'periods.json', db.Period.TABLE  ),
            (   'sessions.json', db.Session.TABLE  ),
            (   'room_types.json', db.RoomType.TABLE  ),
            (   'rooms.json', db.Room.TABLE  ),
            (   'users.json', db.User.TABLE  ),
            (   'notices.json', db.Notice.TABLE ),
        ):
            with open(os.path.join(os.path.dirname(__file__), 'data', filename)) as f:
                data = json.load(f)
            
            if table == db.User.TABLE:
                roles = range(db.UserRole.ADMIN, db.UserRole.INACTIVE - 1, -1)
                for i in range(len(data)):
                    data[i]['password'] = generate_password_hash(data[i]['password'])
                    data[i]['role'] = roles[i % len(roles)]
            if table == db.Room.TABLE:
                for i in range(len(data)):
                    if 'image' in data[i]:
                        data[i]['image'] = base64.b64decode(data[i]['image'])
            if table == db.Notice.TABLE:
                cnx = db.get_cnx(); cursor = cnx.cursor()
                cursor.execute(f"SELECT username FROM {db.User.TABLE} WHERE role = {db.UserRole.ADMIN}")
                admin = cursor.fetchone()[0]
                cursor.close()
                for i in range(len(data)):
                    data[i]['username'] = admin
            
            _insert(table, data)
        yield app
