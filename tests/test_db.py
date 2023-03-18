import os, json
import pandas as pd

import pytest
from reservation_system.db import insert_users, get_user

with open(os.path.join(os.path.dirname(__file__), 'users.json')) as f:
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

def test_insert_users(app):
    with app.app_context():
        insert_users([{'username': 'a', 'password': 'a'}])

def test_get_user(app):
    with app.app_context():
        for i, user in enumerate(users):
            _user = get_user(user['username'])
            if 'level' not in user:
                _user.pop('level')
            assert _user == users[i]

# def test_get_users(app):
#     with app.app_context():
#         insert_users(users)
#         def get_df(users):
#             res = {'level': []}
#             for user in users:
#                 if 'level' not in user: res['level'].append(None)
#                 for key, value in user.items():
#                     if key not in res: res[key] = [value]
#                     else: res[key].append(value)
#             return pd.DataFrame(res)
#         users_df = get_df(users)
#         assert set(users_df['username']) == set(get_df(get_users())['username'])
#         assert set(users_df[users_df['level']==1]['username']) == set(get_df(get_users(where={'level': 1}))['username'])
