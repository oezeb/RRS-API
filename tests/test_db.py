import os, json
from reservation_system import db

def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('reservation_system.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called

def test_select(app):
    with app.app_context():
        zh = db.select(db.LANGUAGES, where={'lang_code': 'zh'})
        assert len(zh) == 1 and zh[0]['name'] == '中文'
        assert len(db.select(db.PERIODS)) == 11
        assert len(db.select(db.SESSIONS)) == 2

def test_insert(app):
    with app.app_context():
        db.insert(db.SESSION_TRANS, data_list=[{
            'session_id': 1, # 2022 Fall Semester
            'lang_code': 'zh',
            'name': '2022年秋學期'
        }])
        zh = db.select(db.SESSION_TRANS, where={'session_id': 1, 'lang_code': 'zh'})
        assert len(zh) == 1 and zh[0]['name'] == '2022年秋學期'
        last_ids = db.insert(db.ROOM_TYPES, data_list=[{
            'label': 'Fake Room Type',
        }])
        assert len(last_ids) == 1
        types = db.select(db.ROOM_TYPES, where={'type': last_ids[0]})
        assert len(types) == 1 and types[0]['label'] == 'Fake Room Type'

def test_delete(app):
    with app.app_context():
        db.delete(db.SESSIONS, where={'session_id': 1})
        ss = db.select(db.SESSIONS, where={'session_id': 1})
        assert len(ss) == 0
        db.delete(db.USERS)
        users = db.select(db.USERS)
        assert len(users) == 0


def test_update(app):
    with app.app_context():
        db.update(db.ROOMS, data={'name': 'Fake Room'})
        rooms = db.select(db.ROOMS)
        assert set([room['name'] for room in rooms]) == {'Fake Room'}
        db.update(db.USERS, data={'name': 'Admin'}, where={'username': 'admin'})
        admin = db.select(db.USERS, where={'username': 'admin'})
        assert len(admin) == 1 and admin[0]['name'] == 'Admin'
