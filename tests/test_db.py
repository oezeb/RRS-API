import json
import os

from reservation_system import db


def test_select(app_with_data):
    with app_with_data.app_context():
        with open(os.path.join(os.path.dirname(__file__), 'data', 'users.json')) as f:
            users = {user['username']: user for user in json.load(f)}
        
        res = db.select(
            db.User.TABLE,
            columns=['username', 'role'],
            order_by=['role'],
        )
        assert len(res) == len(users)
        role = db.UserRole.INACTIVE
        for row in res:
            assert set(row.keys()) == {'username', 'role'}
            assert row['username'] in users
            assert row['role'] >= role
            role = row['role']
        
        res = db.select(db.User.TABLE, role=db.UserRole.ADMIN)
        assert all(row['role'] == db.UserRole.ADMIN for row in res)

def test_insert(app):
    with app.app_context():
        res = db.insert(db.RoomType.TABLE, {'label': 'test'})
        assert res['rowcount'] == 1 
        assert res['lastrowid'] is not None

        id = res['lastrowid']
        res = db.select(db.RoomType.TABLE, type=id)
        assert len(res) == 1 and res[0]['label'] == 'test'

def test_update(app_with_data):
    with app_with_data.app_context():
        user = db.select(db.User.TABLE)[0]
        email = 'test@mail.com'
        res = db.update(
            db.User.TABLE, 
            data={'email': email}, 
            username=user['username']
        )
        assert res['rowcount'] == 1

        res = db.select(db.User.TABLE, username=user['username'])
        assert len(res) == 1 and res[0]['email'] == email

def test_delete(app_with_data):
    with app_with_data.app_context():
        user = db.select(db.User.TABLE)[0]
        res = db.delete(db.User.TABLE, username=user['username'])
        assert res['rowcount'] == 1

        res = db.select(db.User.TABLE, username=user['username'])
        assert len(res) == 0
