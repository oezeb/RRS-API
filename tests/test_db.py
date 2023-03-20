import os, json

from werkzeug.security import generate_password_hash
from reservation_system import db


from conftest import users, periods

def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('reservation_system.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called

def test_get_users(app):
    with app.app_context():
        username_set = lambda users: set([e['username'] for e in users])
        assert username_set(users) == username_set(db.select('users'))
        _username_set = lambda users, level: set([e['username'] for e in users if ('level' not in e and level==0) or ('level' in e and e['level']==level)])
        for i in range(4):
            assert _username_set(users, i) == username_set(db.select('users', where={'level': i}))

def test_remove_users(app):
    with app.app_context():
        db.delete('users', where={'username': 'test'})

def test_get_periods(app):
    with app.app_context():
        period_set = lambda periods: set([e['period_id'] if 'period_id' in e else i+1 for i, e in enumerate(periods)])
        assert period_set(periods) == period_set(db.select('periods'))

def test_remove_periods(app):
    with app.app_context():
        db.delete('periods', where={'period_id': 1})
