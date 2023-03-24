import os, json
from reservation_system import db

with open(os.path.join(os.path.dirname(__file__), 'data/users.json')) as f:
    users = json.load(f)

def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('reservation_system.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called

def test_(app):
    with app.app_context():
        db.insert(db.Tables.USERS, users)
        
        username_set = lambda users: set([e['username'] for e in users])
        assert username_set(users) <= username_set(db.select(db.Tables.USERS))
        _username_set = lambda users, role: set([e['username'] for e in users if ('role' not in e and role==0) or ('role' in e and e['role']==role)])
        for i in range(4):
            assert _username_set(users, i) <= username_set(db.select('users', where={'role': i}))
         
        for user in users: db.delete(db.Tables.USERS, {'username': user['username']})
        assert len(username_set(users).intersection(username_set(db.select(db.Tables.USERS)))) == 0
        for i in range(4):
            assert len(_username_set(users, i).intersection(username_set(db.select('users', where={'role': i})))) == 0
