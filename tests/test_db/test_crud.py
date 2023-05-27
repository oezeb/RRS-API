from mrbs import db
from data import insert_data, get_users, get_room_types

def test_select(app):
    with app.app_context():
        insert_data(only=['users'])
        users = {user['username']: user for user in get_users()}
        
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
        type = get_room_types()[0]
        res = db.insert(db.RoomType.TABLE, type)
        assert res['rowcount'] == 1

        id = res['lastrowid']
        res = db.select(db.RoomType.TABLE, type=id)
        assert len(res) == 1 and res[0]['label'] == type['label']

def test_update(app):
    with app.app_context():
        user = get_users()[0]
        res = db.insert(db.User.TABLE, user)
        assert res['rowcount'] == 1

        email = 'test@mail.com'
        res = db.update(
            db.User.TABLE, 
            data={'email': email}, 
            username=user['username']
        )
        assert res['rowcount'] == 1

        res = db.select(db.User.TABLE, username=user['username'])
        assert len(res) == 1 and res[0]['email'] == email

def test_delete(app):
    with app.app_context():
        user = get_users()[0]
        res = db.insert(db.User.TABLE, user)
        assert res['rowcount'] == 1

        res = db.delete(db.User.TABLE, username=user['username'])
        assert res['rowcount'] == 1

        res = db.select(db.User.TABLE, username=user['username'])
        assert len(res) == 0
