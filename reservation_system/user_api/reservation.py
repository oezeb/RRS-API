from datetime import datetime

from flask import current_app
from mysql.connector import Error, errorcode

from reservation_system import db
from reservation_system.util import abort
from reservation_system.user_api import util

def get_reservations(username, **kwargs):
    return util.get_reservations(username=username, **kwargs)

def create_reservation(username, role, start_time, end_time, **kwargs):
    """Create a new reservation.
    - Required fields: `room_id`, `title`, `start_time`, `end_time`
    - Optional fields: `note`, `session_id`
    - Auto generated fields: `username`, `privacy`=`public`, 
    `status`=`pending` if `role`<=`GUEST` else `approved`
    """
    now = datetime.now()
    if start_time > end_time:
        abort(400, message='Invalid time range')
    
    if start_time < now:
        abort(400, message='Cannot reserve in the past')

    # time window check
    tm = util.time_window()
    if tm is not None:
        if end_time > now + tm:
            abort(400, message='Cannot reserve too far in the future')
    # time limit check
    tm = util.time_limit()
    if tm is not None:
        if end_time - start_time > tm:
            abort(400, message='Cannot reserve too long')
    
    # max daily reservation check
    md = util.max_daily()
    if md is not None:
        where = {
            'username': username,
            'DATE(create_time)': '%s' % now.strftime('%Y-%m-%d')
        }

        res = db.select(
            db.Reservation.TABLE, 
            columns=['COUNT(DISTINCT resv_id) AS num'],
            **where
        )
        if res[0]['num'] >= md:
            abort(400, message='Exceed max daily reservation limit')

    # time range is combined periods check
    if not util.is_combined_periods(start_time, end_time):
        abort(400, message='Time range is not combined periods')
    
    # room availability check
    if not util.room_is_available(kwargs['room_id']):
        abort(400, message='Room is not available')

    # add auto generated fields
    kwargs['username'] = username
    kwargs['privacy'] = db.ResvPrivacy.PUBLIC
    time_slots = [{'start_time': start_time, 'end_time': end_time}]
    if role <= db.UserRole.GUEST:
        time_slots[0]['status'] = db.ResvStatus.PENDING
    else:
        time_slots[0]['status'] = db.ResvStatus.CONFIRMED

    cnx = db.get_cnx(); cursor = cnx.cursor()
    try:
        resv_id = util.insert_reservation(cursor, **kwargs)
        slot_id = util.insert_time_slots(cursor, resv_id, username, time_slots)
        cnx.commit()
    except Error as err:
        cnx.rollback()
        current_app.logger.error(err)
        if err.errno == errorcode.ER_DUP_ENTRY:
            abort(409, message='Reservation already exists')
        else:
            abort(500, message=f'Database error: {err.msg}')
    finally:
        cursor.close()

    return {'resv_id': resv_id, 'slot_id': slot_id}, 201

def update_reservation(resv_id, username, **kwargs):
    try:
        db.update(db.Reservation.TABLE, data=kwargs, resv_id=resv_id, username=username)
    except Exception as err:
        current_app.logger.error(err)
        abort(500, message=f'Database error: {err.msg}')

    return {}, 204

def update_reservation_slot(resv_id, slot_id, username, **kwargs):
    try:
        db.update(db.Reservation.TABLE, data=kwargs, resv_id=resv_id, slot_id=slot_id, username=username)
    except Exception as err:
        current_app.logger.error(err)
        abort(500, message=f'Database error: {err.msg}')
    
    return {}, 204

def create_advanced_reservation(username, role, time_slots, **kwargs):
    """Create advanced reservation.
    - required fields: `room_id`, `title`, `session_id`, `time_slots`
    - Optional fields: `note`
    - Auto generated fields: `username`, `privacy`=`public`,
        `status`=`pending` if `role`<=`BASIC` else `approved`
    """
    now = datetime.now()
    for slot in time_slots:
        start_time = slot['start_time']
        end_time = slot['end_time']
        if start_time > end_time:
            abort(400, message='Invalid time range')
        
        if start_time < now:
            abort(400, message='Cannot reserve in the past')
            
        # time range is combined periods check
        if not util.is_combined_periods(start_time, end_time):
            abort(400, message='Time range is not combined periods')
    
    # room availability check
    if not util.room_is_available(kwargs['room_id']):
        abort(400, message='Room is not available')
    
    # add auto generated fields
    kwargs['username'] = username
    kwargs['privacy'] = db.ResvPrivacy.PUBLIC
    if role <= db.UserRole.BASIC:
        for slot in time_slots:
            slot['status'] = db.ResvStatus.PENDING
    else:
        for slot in time_slots:
            slot['status'] = db.ResvStatus.CONFIRMED
    
    cnx = db.get_cnx(); cursor = cnx.cursor()
    try:
        print(time_slots)
        resv_id = util.insert_reservation(cursor, **kwargs)
        id = util.insert_time_slots(cursor, resv_id, kwargs['username'], time_slots)
        cnx.commit()
    except Error as err:
        print(err)
        cnx.rollback()
        if err.errno == errorcode.ER_DUP_ENTRY:
            abort(409, message='Reservation already exists')
        else:
            abort(500, message=f'Database error: {err.msg}')
    finally:
        cursor.close()
        
    return {'resv_id': resv_id}, 201
