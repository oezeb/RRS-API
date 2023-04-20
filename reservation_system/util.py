import json
from flask import abort as flask_abort, Response

from reservation_system import db

def abort(code, message=None):
    if message is None:
        flask_abort(code)
    else:
        abort(Response(json.dumps({'message': message}), code, mimetype='application/json'))

def time_slot_conflict(room_id, session_id, start_time, end_time):
    cnx = db.get_cnx(); cursor = cnx.cursor()
    # statuses: 0: pending, 1: approved, 2: cancelled, 3: rejected
    cursor.execute(f"""
        SELECT COUNT(*)
        FROM {db.TIME_SLOTS} NATURAL JOIN {db.RESERVATIONS}
        WHERE room_id = %s AND session_id = %s AND status = 1
        AND ((start_time = %s AND end_time = %s)
            OR  (start_time > %s AND start_time < %s)
            OR  (end_time > %s AND end_time < %s))
    """, (room_id, session_id, *(start_time, end_time)*3))
    conflict = cursor.fetchone()[0]
    cnx.commit(); cursor.close()
    return conflict

def current_session():
    cnx = db.get_cnx(); cursor = cnx.cursor(dictionary=True)
    cursor.execute(f"""
        SELECT *
        FROM {db.SESSIONS}
        WHERE is_current = 1
    """)
    session = cursor.fetchone()
    cnx.commit(); cursor.close()
    return session