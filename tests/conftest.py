import pytest
from werkzeug.security import generate_password_hash
import click
import logging

from reservation_system import create_app
from reservation_system.db import init_db, get_cnx, User

from flask import Flask

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        cnx = get_cnx(); cursor = cnx.cursor()
        query = f"""
            INSERT INTO {User.TABLE} (username, password, name, role)
            VALUES (%s, %s, %s, %s);
        """
        cursor.executemany(query, [
            ('restricted', generate_password_hash('restricted'), '待审核用户', 0),
            (     'basic', generate_password_hash('basic'     ), '基础用户', 1),
            (  'advanced', generate_password_hash('advanced'  ), '高级用户', 2),
            (     'admin', generate_password_hash('admin'     ), '管理员', 3),
        ])
        cnx.commit(); cursor.close()
    yield app

@pytest.fixture
def client(app: Flask):
    return app.test_client(use_cookies=True)

@pytest.fixture
def runner(app: Flask):
    return app.test_cli_runner()
