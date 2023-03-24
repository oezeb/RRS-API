import pytest
from werkzeug.security import generate_password_hash

from reservation_system import create_app
from reservation_system.db import init_db, get_cnx, Tables

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
        cursor.execute(f"""
            INSERT INTO {Tables.USERS} (username, password, role) 
            VALUES ('test', '{generate_password_hash('test')}', 0);
        """)
        cnx.commit(); cursor.close()

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
