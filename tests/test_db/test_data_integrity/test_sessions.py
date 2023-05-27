"""
Test session data integrity
===========================
The sessions table has the following constraints:
    - start_time < end_time
    - No overlapping sessions
"""
from mysql.connector import Error

from mrbs import db

def test_sessions(app):
    with app.app_context():
        # start_time < end_time
        try:
            db.insert(db.Session.TABLE, {
                'start_time': '2020-01-01 12:00:00',
                'end_time': '2020-01-01 10:00:00',
                'name': 'test'
            })
            print("Insert session start_time > end_time")
            assert False
        except Error as e:
            assert e.sqlstate == 'HY000'

        # No overlapping sessions
        res = db.insert(db.Session.TABLE, {
            'start_time': '2020-01-01 10:00:00',
            'end_time': '2020-01-01 12:00:00',
            'name': 'test'
        })
        assert res['rowcount'] == 1

        for start, end in (
            ('2020-01-01 09:00:00', '2020-01-01 11:00:00'),
            ('2020-01-01 11:00:00', '2020-01-01 13:00:00'),
            ('2020-01-01 09:00:00', '2020-01-01 13:00:00'),
            ('2020-01-01 10:00:00', '2020-01-01 12:00:00'),
            ('2020-01-01 09:00:00', '2020-01-01 12:00:00'),
            ('2020-01-01 10:00:00', '2020-01-01 13:00:00'),
        ):
            try:
                db.insert(db.Session.TABLE, {
                    'start_time': start,
                    'end_time': end,
                    'name': 'test'
                })
                print("Insert session overlapping")
                assert False
            except Error as e:
                assert e.sqlstate == '45000'

        res = db.insert(db.Session.TABLE, {
            'start_time': '2020-01-01 12:00:00',
            'end_time': '2020-01-01 14:00:00',
            'name': 'test'
        })
        assert res['rowcount'] == 1
        session_id = res['lastrowid']
        try:
            db.update(db.Session.TABLE, data={'start_time': '2020-01-01 11:00:00'}, session_id=session_id)
            print("Update session overlapping")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
        