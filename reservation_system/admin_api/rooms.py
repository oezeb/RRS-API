from mysql.connector import Error, errorcode
from flask import g

from reservation_system import db
from reservation_system.util import abort

def create_room(**kwargs):
    """Create room.
    - required fields: `name`, `capacity`, `type`
    - optional fields: `status`
    """
    if 'status' not in kwargs:
        kwargs['status'] = db.RoomStatus.AVAILABLE

    try:
        res = db.insert(db.Room.TABLE, kwargs)
    except Error as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            abort(409, message='Room already exists')
        else:
            abort(500, message=f'Database error: {err.msg}')

    return {'room_id': res['lastrowid']}, 201

# def update_room(room_id, **kwargs):
#     db.update(db.Room.TABLE, data=kwargs, room_id=room_id)
#     return {}, 204

# def delete_room(room_id):
#     db.delete(db.Room.TABLE, room_id=room_id)
#     return {}, 204