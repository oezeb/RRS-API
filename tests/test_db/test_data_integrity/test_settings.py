"""
Test settings data integrity
============================

The settings table contains constant values that are set at
the initialization of the database. Therefore, it is forbidden
to insert, delete or update settings.

Additionally, the time_window and time_limit settings must
have a valid format (hh:mm:ss) and the max_daily setting
must be a positive integer.
"""
from mysql.connector import Error

from app import db

def test_settings(app):
    with app.app_context():
        # Forbidden to insert settings
        try:
            db.insert(db.Setting.TABLE, {'id': -1, 'value': 'test'})
            print("Insert setting forbidden")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'

        # Forbidden to delete settings
        try:
            db.delete(db.Setting.TABLE)
            print("Delete setting forbidden")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'

        # Forbidden to update settings id
        try:
            db.update(db.Setting.TABLE, data={'id': -1}, id=db.Setting.TIME_WINDOW)
            print("Update setting id forbidden")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
        
        # time_window format: hh:mm:ss
        try:
            db.update(db.Setting.TABLE, data={'value': 'test'}, id=db.Setting.TIME_WINDOW)
            print("Update setting value invalid format")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
        
        # time_limit format: hh:mm:ss
        try:
            db.update(db.Setting.TABLE, data={'value': 'test'}, id=db.Setting.TIME_LIMIT)
            print("Update setting value invalid format")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
        
        # max_daily is an integer
        try:
            db.update(db.Setting.TABLE, data={'value': 'test'}, id=db.Setting.MAX_DAILY)
            print("Update setting value invalid format")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
