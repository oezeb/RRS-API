from mysql.connector import Error, errorcode
from flask import g

from reservation_system import db
from reservation_system.user_api import reservation as resv
from reservation_system.user_api import util
from reservation_system.util import abort


def get_reservations(**kwargs):
    return util.get_reservations(**kwargs)

def create_reservation(time_slots, **kwargs):
    """Create advanced reservation.
    - required fields: `room_id`, `title`, `session_id`, `time_slots`
    - Optional fields: `note`, `username`, `privacy` and `status` in `time_slots`
        - defaults:
            - `username`: current user
            - `privacy`: `PUBLIC`
            - `status`: `CONFIRMED`
    """
    if 'username' not in kwargs:
        kwargs['username'] = g.user['username']
    if 'privacy' not in kwargs:
        kwargs['privacy'] = db.ResvPrivacy.PUBLIC
    for slot in time_slots:
        if 'status' not in slot:
            slot['status'] = db.ResvStatus.CONFIRMED
    
    cnx = db.get_cnx(); cursor = cnx.cursor()
    try:
        resv_id = util.insert_reservation(cursor, **kwargs)
        util.insert_time_slots(cursor, resv_id, kwargs['username'], time_slots)
        cnx.commit()
    except Error as err:
        cnx.rollback()
        if err.errno == errorcode.ER_DUP_ENTRY:
            abort(409, message='Reservation already exists')
        else:
            abort(500, message=f'Database error: {err.msg}')
    finally:
        cursor.close()
        
    return {'resv_id': resv_id}, 201

def update_reservation(resv_id, **kwargs):
    if 'username' not in kwargs:
        kwargs['username'] = g.user['username']
    return resv.update_reservation(resv_id, **kwargs)

def update_reservation_slot(resv_id, slot_id, **kwargs):
    if 'username' not in kwargs:
        kwargs['username'] = g.user['username']
    return resv.update_reservation_slot(resv_id, slot_id, **kwargs)

# def get_resv_privacy(**kwargs):
#     return db.select(db.ResvPrivacy.TABLE, **kwargs)

# def update_resv_privacy(privacy, **kwargs):
#     """Update reservation privacy.
#     - required fields: `privacy`
#     - optional fields: `label` and `description`
#     """
#     try:
#         db.update(db.ResvPrivacy.TABLE, data=kwargs, privacy=privacy)
#     except Error as err:
#         abort(500, message=f'Database error: {err.msg}')

#     return {}, 204

# def get_resv_status(**kwargs):
#     return db.select(db.ResvStatus.TABLE, **kwargs)

# def update_resv_status(status, **kwargs):
#     """Update reservation status.
#     - required fields: `status`
#     - optional fields: `label` and `description`
#     """
#     if len(kwargs) > 0:
#         db.update(db.ResvStatus.TABLE, data=kwargs, status=status)
#     return {}, 204