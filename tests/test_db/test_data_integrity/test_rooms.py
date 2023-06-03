 
"""
Test room data integrity
========================

Room Status
-----------
The room status table contains constant values that are set at
the initialization of the database. Therefore, it is forbidden
to insert, delete or update room status.
"""
from mysql.connector import Error

from app import db

def test_room_status(app):
    with app.app_context():
        # forbidden to insert room status
        try:
            db.insert(db.RoomStatus.TABLE, {'status': -1, 'label': 'test'})
            print("Insert room status forbidden")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
        
        # forbidden to delete room status
        try:
            db.delete(db.RoomStatus.TABLE)
            print("Delete room status forbidden")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
        
        # forbidden to update room status status
        try:
            db.update(db.RoomStatus.TABLE, data={'status': -1}, status=db.RoomStatus.AVAILABLE)
            print("Update room status status forbidden")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
