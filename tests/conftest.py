import pytest
from werkzeug.security import generate_password_hash

from reservation_system import create_app
from reservation_system.db import init_db, get_cnx, USERS

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
            INSERT INTO {USERS} (username, password, role)
            VALUES (%s, %s, %s);
        """
        cursor.executemany(query, [
            ('restricted', generate_password_hash('restricted'), 0),
            (     'basic', generate_password_hash('basic'     ), 1),
            (  'advanced', generate_password_hash('advanced'  ), 2),
            (     'admin', generate_password_hash('admin'     ), 3),
        ])
        cnx.commit(); cursor.close()

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
