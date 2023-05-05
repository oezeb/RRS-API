from datetime import datetime, timedelta
import dateutil.parser

from flask import g, request, Blueprint
from flask.views import MethodView
from functools import wraps
from werkzeug.security import generate_password_hash

from reservation_system import db
from reservation_system.auth import auth_required
from reservation_system.util import abort

def init_api(app):
    for path, view in (
        ('resv_trans', Resv_trans),
        ('resv_status_trans', Resv_status_trans),   
        ('resv_secu_level_trans', Resv_secu_level_trans),
        ('room_trans', Room_trans),
        ('room_type_trans', Room_type_trans),
        ('room_status_trans', Room_status_trans),
        ('session_trans', Session_trans),
        ('user_trans', User_trans),
        ('user_role_trans', User_role_trans),
        ('setting_trans', Setting_trans),
        ('notice_trans', Notice_trans),
        ('languages', Languages),
        ('time_slots', Time_slots),
        ('reservations', Reservations),
        ('resv_status', Resv_status),
        ('resv_secu_levels', Resv_secu_levels),
        ('rooms', Rooms),
        ('room_types', Room_types),
        ('room_status', Room_status),
        ('sessions', Sessions),
        ('users', Users),
        ('user_roles', User_roles),
        ('periods', Periods),
        ('settings', Settings),
        ('notices', Notices),
    ):
        # app.add_url_rule(f'/api/{path}', view_func=view.as_view(path))
        pass

def check_user(role=0):
    """
    This decorator checks for users < `role` if they are editing only their owns stuff.
    The user should be already authenticated, and `sub` should be in `g`.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'sub' not in g:
                abort(401, message='Unauthorized')
            if g.sub['role'] <= role:
                if request.method == 'POST':
                    for item in request.json:
                        if item['username'] != g.sub['username']:
                            abort(403, message='Forbidden')
                elif request.method == 'PATCH':
                    data, where = request.json['data'], request.json['where']
                    if 'username' in data or where['username'] != g.sub['username']:
                        abort(403, message='Forbidden')
                elif request.method == "DELETE":
                    if request.json['username'] != g.sub['username']:
                        abort(403, message='Forbidden')
            return func(*args, **kwargs)
        return wrapper
    return decorator

def check_reservations(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'sub' not in g:
            abort(401, message='Unauthorized')
        if request.path.endswith('/reservations'):
            if g.sub['role'] < 3: # Non-administrator users
                cnx = db.get_cnx(); cursor = cnx.cursor(dictionary=True, buffered=True)
                if request.method == 'POST':
                    for resv in request.json:
                        # Non-administrator users can only create reservations for the current session
                        cursor.execute(f"SELECT session_id FROM {db.SESSIONS} WHERE is_current = 1")
                        if resv['session_id'] != cursor.fetchone()['session_id']:
                            abort(403, message='Forbidden, Not current session')
                        # Non-administrator users can only create reservations for available rooms 
                        cursor.execute(f"SELECT status FROM {db.ROOMS} WHERE room_id = %s", (resv['room_id'],))
                        if cursor.fetchone()['status'] != 1:
                            abort(403, message="Forbidden, Room is not available")
                        # Non-administrator users number of reservations should not exceed 3 per day
                        # resv_time_window ID = 1, max_resv_time ID = 2, max_resv_per_day ID = 3
                        cursor.execute(f"SELECT * FROM {db.SETTINGS} WHERE id = 3")
                        max_resv_per_day = int(cursor.fetchone()['value'])
                        cursor.execute(f"""
                            SELECT resv_id FROM {db.RESERVATIONS}
                            WHERE username = %s AND DATE(create_time) = DATE(%s)
                        """, (g.sub['username'], datetime.today()))
                        if cursor.rowcount >= max_resv_per_day:
                            abort(403, message='Forbidden, Exceeds maximum reservations per day')
                        # Basic users can only create reservations for public or anonymous security levels
                        if g.sub['role'] < 2 and resv['secu_level'] == 2:
                            abort(403, message="Forbidden, Creating private reservations")
                        # Restricted users can only create pending and public reservations
                        if g.sub['role'] < 1 and (resv['status'] != 0 or resv['secu_level'] != 0):
                            abort(403, message="Forbidden, Creating non-pending or non-public reservations")
                elif request.method == 'PATCH':
                    # Non-administrator users can only update reservations notes, status(to cancelled==2),
                    # create_time, update_time, and cancel_time
                    if not set(request.json['data'].keys()).issubset({'note', 'status', "create_time", "update_time", "cancel_time"}):
                        abort(403, message='Forbidden, Not allowed to update')
                    if 'status' in request.json['data'] and request.json['data']['status'] != 2:
                        abort(403, message='Forbidden, Can only cancel reservations')
                cursor.close()
        return func(*args, **kwargs)
    return wrapper

def check_time_slots(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'sub' not in g:
            abort(401, message='Unauthorized')
        if request.path.endswith('/time_slots'):
            cnx = db.get_cnx(); cursor = cnx.cursor(dictionary=True, buffered=True)
            if request.method == 'POST':
                for slot in request.json:
                    start_time = dateutil.parser.parse(slot['start_time'])
                    end_time   = dateutil.parser.parse(slot['end_time'])
                    now = datetime.now().replace(second=0, microsecond=0)
                    print(start_time, end_time)
                    if start_time >= end_time or start_time < now:
                        abort(400, message='Invalid time slot')
                    # No overlapping time slots
                    cursor.execute(f"SELECT * from {db.RESERVATIONS} WHERE resv_id = %s", (slot['resv_id'],))
                    if cursor.rowcount == 0:
                        abort(404, message='Reservation not found')
                    resv = cursor.fetchone()
                    cursor.execute(f"""
                        SELECT slot_id FROM {db.TIME_SLOTS} natural join {db.RESERVATIONS}
                        WHERE room_id = %s AND session_id = %s AND start_time BETWEEN %s AND %s OR end_time BETWEEN %s AND %s
                    """, (resv['room_id'], resv['session_id'], *(start_time, end_time)*2,))
                    if cursor.rowcount > 0:
                        abort(403, message='Forbidden, Overlapping time slots')
                    # In room opening hours and session
                    cursor.execute(f"""
                        SELECT rooms.status as room_status, reservations.status as resv_status, is_current
                        FROM {db.RESERVATIONS} join {db.ROOMS} using(room_id) join {db.SESSIONS} using(session_id)
                        WHERE resv_id = %s AND username = %s
                            AND open_time <= TIME(%s) AND close_time >= TIME(%s)
                            AND start_time <= %s AND end_time >= %s
                    """, (slot['resv_id'], slot['username'], *(slot['start_time'], slot['end_time'])*2,))
                    if cursor.rowcount == 0:
                        abort(403, message='Forbidden, Not in room opening hours or not any session')
                    res = cursor.fetchone()
                    # Non-administrator users can only create time slots for available rooms and current session
                    if res['room_status'] != 1 or res['is_current'] != 1:
                        abort(403, message='Forbidden, Room is not available or not current session')
                    # Basic users are allowed to create only one time slot for confirmed reservations and 
                    # the time slot should be in the reserving window and
                    # reservation total time should not exceed 4 hours
                    # resv_time_window ID = 1, max_resv_time ID = 2, max_resv_per_day ID = 3
                    if g.sub['role'] < 2 and res['resv_status'] == 1:
                        cursor.execute(f"""
                            SELECT * FROM {db.RESERVATIONS} NATURAL JOIN {db.TIME_SLOTS}
                            WHERE resv_id = %s AND username = %s AND status = 1
                        """, (slot['resv_id'], slot['username']))
                        if cursor.rowcount > 0:
                            abort(403, message='Forbidden, Only one time slot per confirmed reservation')
                        cursor.execute(f"SELECT * FROM {db.SETTINGS} WHERE id IN (1, 2)")
                        for setting in cursor:
                            h, m, s = setting['value'].split(':')
                            if setting['id'] == 1: # resv_time_window
                                resv_time_window = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
                            elif setting['id'] == 2: # max_resv_time
                                max_resv_time = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
                        if start_time < now or end_time > now + resv_time_window:
                            abort(403, message='Forbidden, Time slot is not in the reserving window')
                        if end_time - start_time > max_resv_time:
                            abort(403, message='Forbidden, Time slot exceeds maximum reservation time')
            elif request.method == 'DELETE':
                # Basic and Restricted users can only delete time slots for pending reservations
                if g.sub['role'] < 2:
                    cursor.execute(f"""
                        SELECT * FROM {db.RESERVATIONS} NATURAL JOIN {db.TIME_SLOTS}
                        WHERE {' AND '.join([f'{k} = %s' for k in request.json.keys()])} AND status != 0
                    """, (*request.json.values(),))
                    if cursor.fetchone():
                        abort(403, message='Forbidden, Can only delete time slots for pending reservations')
            cursor.close()
        return func(*args, **kwargs)
    return wrapper

# ----------------------------------------------------------------
# Reservations
# ----------------------------------------------------------------
class Reservations(MethodView):
    def get(self):
        where = request.args.to_dict()
        table = db.RESERVATIONS
        if 'lang_code' in where:
            table += f" JOIN {db.RESV_TRANS} USING(resv_id, username)"
        return db.select(table, where=where), 200

    @auth_required(role=0) # any auth user
    @check_user(role=2) # user <= advanced edit their own
    @check_reservations
    def post(self):
        data_list = []
        for item in request.json:
            item['create_time'] = datetime.now()
            data_list.append(item)
        return db.insert(db.RESERVATIONS, data_list) or {}, 201
        
    @auth_required(role=0) # any auth user
    @check_user(role=2) # user <= advanced edit their own
    @check_reservations
    def patch(self): 
        data = request.json['data']
        data['update_time'] = datetime.now()
        return db.update(db.RESERVATIONS, data, where=request.json['where']) or {}, 200

    @auth_required(role=3) # admin
    def delete(self):
        return db.delete(db.RESERVATIONS, where=request.json) or {}, 204
    
# ----------------------------------------------------------------
# Time_slots
# ----------------------------------------------------------------
class Time_slots(MethodView):
    def get(self):
        where = request.args.to_dict()
        table = f"{db.TIME_SLOTS} NATURAL JOIN {db.RESERVATIONS}"
        if 'lang_code' in where:
            table += f" JOIN {db.RESV_TRANS} USING(resv_id, username)"
        if 'date' in where:
            date = where.pop('date')
            where['DATE(start_time)'] = date
            where['DATE(end_time)'] = date
        return db.select(table, where=where), 200

    @auth_required(role=0) # any auth user
    @check_user(role=2) # user <= advanced edit their own
    @check_time_slots
    def post(self):
        return db.insert(db.TIME_SLOTS, data_list=request.json), 201
        
    @auth_required(role=3) # admin
    def patch(self): 
        return db.update(db.TIME_SLOTS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=0) # any auth user
    @check_user(role=2) # user <= advanced edit their own
    @check_time_slots
    def delete(self):
        return db.delete(db.TIME_SLOTS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# Users
# ----------------------------------------------------------------
class Users(MethodView):
    def get(self):
        where = request.args.to_dict()
        table = db.USERS
        if 'lang_code' in where:
            table += f" JOIN {db.USER_TRANS} USING (username)"
        return db.select(table, where=where), 200

    @auth_required(role=3) # admin
    def post(self):
        data_list = request.json
        for data in data_list:
            data['password'] = generate_password_hash(data['password'])
        return db.insert(db.USERS, data_list=data_list), 201
        
    @auth_required(role=0) # any auth user
    @check_user(role=2) # user <= advanced edit their own
    def patch(self):
        data = request.json['data']
        # Regular users cannot change their role, or username, or password(only through `/change_password`)
        if g.sub['role'] < 3 and ('role' in data or 'username' in data or 'password' in data):
            abort(403, message='Forbidden')
        
        if 'password' in data:
            data['password'] = generate_password_hash(data['password'])
        return db.update(db.USERS, data=data, where=request.json['where']) or {}, 200

    @auth_required(role=3) # admin
    def delete(self):
        return db.delete(db.USERS, where=request.json) or {}, 204
    
# ----------------------------------------------------------------
# Resv_trans
# ----------------------------------------------------------------
class Resv_trans(MethodView):
    def get(self):
        where = request.args.to_dict()
        return db.select(db.RESV_TRANS, where=where), 200

    @auth_required(role=0) # any auth user
    @check_user(role=2) # user <= advanced edit their own
    def post(self):
        return db.insert(db.RESV_TRANS, data_list=request.json), 201
        
    @auth_required(role=0) # any auth user
    @check_user(role=2) # user <= advanced edit their own
    def patch(self): 
        return db.update(db.RESV_TRANS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=0) # any auth user
    @check_user(role=2) # user <= advanced edit their own
    def delete(self):
        return db.delete(db.RESV_TRANS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# User_trans
# ----------------------------------------------------------------
class User_trans(MethodView):
    def get(self):
        where = request.args.to_dict()
        return db.select(db.USER_TRANS, where=where), 200

    @auth_required(role=0) # any auth user
    @check_user(role=2) # user <= advanced edit their own
    def post(self):
        return db.insert(db.USER_TRANS, data_list=request.json), 201
        
    @auth_required(role=0) # any auth user
    @check_user(role=2) # user <= advanced edit their own
    def patch(self): 
        return db.update(db.USER_TRANS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=0) # any auth user
    @check_user(role=2) # user <= advanced edit their own
    def delete(self):
        return db.delete(db.USER_TRANS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# Resv_status_trans
# ----------------------------------------------------------------
class Resv_status_trans(MethodView):
    def get(self):
        where = request.args.to_dict()
        return db.select(db.RESV_STATUS_TRANS, where=where), 200

    @auth_required(role=3) # admin
    def post(self):
        return db.insert(db.RESV_STATUS_TRANS, data_list=request.json), 201
        
    @auth_required(role=3) # admin
    def patch(self): 
        return db.update(db.RESV_STATUS_TRANS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=3) # admin
    def delete(self):
        return db.delete(db.RESV_STATUS_TRANS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# Resv_secu_level_trans
# ----------------------------------------------------------------
class Resv_secu_level_trans(MethodView):
    def get(self):
        where = request.args.to_dict()
        return db.select(db.RESV_SECU_LEVEL_TRANS, where=where), 200

    @auth_required(role=3) # admin
    def post(self):
        return db.insert(db.RESV_SECU_LEVEL_TRANS, data_list=request.json), 201
        
    @auth_required(role=3) # admin
    def patch(self): 
        return db.update(db.RESV_SECU_LEVEL_TRANS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=3) # admin
    def delete(self):
        return db.delete(db.RESV_SECU_LEVEL_TRANS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# Room_trans
# ----------------------------------------------------------------
class Room_trans(MethodView):
    def get(self):
        where = request.args.to_dict()
        return db.select(db.ROOM_TRANS, where=where), 200

    @auth_required(role=3) # admin
    def post(self):
        return db.insert(db.ROOM_TRANS, data_list=request.json), 201
        
    @auth_required(role=3) # admin
    def patch(self): 
        return db.update(db.ROOM_TRANS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=3) # admin
    def delete(self):
        return db.delete(db.ROOM_TRANS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# Room_type_trans
# ----------------------------------------------------------------
class Room_type_trans(MethodView):
    def get(self):
        where = request.args.to_dict()
        return db.select(db.ROOM_TYPE_TRANS, where=where), 200

    @auth_required(role=3) # admin
    def post(self):
        return db.insert(db.ROOM_TYPE_TRANS, data_list=request.json), 201
        
    @auth_required(role=3) # admin
    def patch(self): 
        return db.update(db.ROOM_TYPE_TRANS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=3) # admin
    def delete(self):
        return db.delete(db.ROOM_TYPE_TRANS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# Room_status_trans
# ----------------------------------------------------------------
class Room_status_trans(MethodView):
    def get(self):
        where = request.args.to_dict()
        return db.select(db.ROOM_STATUS_TRANS, where=where), 200

    @auth_required(role=3) # admin
    def post(self):
        return db.insert(db.ROOM_STATUS_TRANS, data_list=request.json), 201
        
    @auth_required(role=3) # admin
    def patch(self): 
        return db.update(db.ROOM_STATUS_TRANS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=3) # admin
    def delete(self):
        return db.delete(db.ROOM_STATUS_TRANS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# Session_trans
# ----------------------------------------------------------------
class Session_trans(MethodView):
    def get(self):
        where = request.args.to_dict()
        return db.select(db.SESSION_TRANS, where=where), 200

    @auth_required(role=3) # admin
    def post(self):
        return db.insert(db.SESSION_TRANS, data_list=request.json), 201
        
    @auth_required(role=3) # admin
    def patch(self): 
        return db.update(db.SESSION_TRANS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=3) # admin
    def delete(self):
        return db.delete(db.SESSION_TRANS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# User_role_trans
# ----------------------------------------------------------------
class User_role_trans(MethodView):
    def get(self):
        where = request.args.to_dict()
        return db.select(db.USER_ROLE_TRANS, where=where), 200

    @auth_required(role=3) # admin
    def post(self):
        return db.insert(db.USER_ROLE_TRANS, data_list=request.json), 201
        
    @auth_required(role=3) # admin
    def patch(self): 
        return db.update(db.USER_ROLE_TRANS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=3) # admin
    def delete(self):
        return db.delete(db.USER_ROLE_TRANS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# Setting_trans
# ----------------------------------------------------------------
class Setting_trans(MethodView):
    def get(self):
        where = request.args.to_dict()
        return db.select(db.SETTING_TRANS, where=where), 200

    @auth_required(role=3) # admin
    def post(self):
        return db.insert(db.SETTING_TRANS, data_list=request.json), 201
        
    @auth_required(role=3) # admin
    def patch(self): 
        return db.update(db.SETTING_TRANS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=3) # admin
    def delete(self):
        return db.delete(db.SETTING_TRANS, where=request.json) or {}, 204
    
# ----------------------------------------------------------------
# Notice_trans
# ----------------------------------------------------------------
class Notice_trans(MethodView):
    def get(self):
        where = request.args.to_dict()
        return db.select(db.NOTICE_TRANS, where=where), 200
    
    
    @auth_required(role=3) # admin
    def post(self):
        return db.insert(db.NOTICE_TRANS, data_list=request.json), 201
        
    @auth_required(role=3) # admin
    def patch(self): 
        return db.update(db.NOTICE_TRANS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=3) # admin
    def delete(self):
        return db.delete(db.NOTICE_TRANS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# Languages
# ----------------------------------------------------------------
class Languages(MethodView):
    def get(self):
        where = request.args.to_dict()
        return db.select(db.LANGUAGES, where=where), 200

    @auth_required(role=3) # admin
    def post(self):
        return db.insert(db.LANGUAGES, data_list=request.json), 201
        
    @auth_required(role=3) # admin
    def patch(self): 
        return db.update(db.LANGUAGES, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=3) # admin
    def delete(self):
        return db.delete(db.LANGUAGES, where=request.json) or {}, 204

# ----------------------------------------------------------------
# Rooms
# ----------------------------------------------------------------
class Rooms(MethodView):
    def get(self):
        where = request.args.to_dict()
        table = db.ROOMS
        if 'lang_code' in where:
            table += f" JOIN {db.ROOM_TRANS} USING (room_id)"
        return db.select(table, where=where), 200

    @auth_required(role=3) # admin
    def post(self):
        return db.insert(db.ROOMS, data_list=request.json), 201
        
    @auth_required(role=3) # admin
    def patch(self): 
        return db.update(db.ROOMS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=3) # admin
    def delete(self):
        return db.delete(db.ROOMS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# Room_types
# ----------------------------------------------------------------
class Room_types(MethodView):
    def get(self):
        where = request.args.to_dict()
        table = db.ROOM_TYPES
        if 'lang_code' in where:
            table += f" JOIN {db.ROOM_TYPE_TRANS} USING (type)"
        return db.select(table, where=where), 200

    @auth_required(role=3) # admin
    def post(self):
        return db.insert(db.ROOM_TYPES, data_list=request.json), 201
        
    @auth_required(role=3) # admin
    def patch(self): 
        return db.update(db.ROOM_TYPES, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=3) # admin
    def delete(self):
        return db.delete(db.ROOM_TYPES, where=request.json) or {}, 204

# ----------------------------------------------------------------
# Sessions
# ----------------------------------------------------------------
class Sessions(MethodView):
    def get(self):
        where = request.args.to_dict()
        table = db.SESSIONS
        if 'lang_code' in where:
            table += f" JOIN {db.SESSION_TRANS} USING (session_id)"
        return db.select(table, where=where), 200

    @auth_required(role=3) # admin
    def post(self):
        return db.insert(db.SESSIONS, data_list=request.json), 201
        
    @auth_required(role=3) # admin
    def patch(self): 
        return db.update(db.SESSIONS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=3) # admin
    def delete(self):
        return db.delete(db.SESSIONS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# Periods
# ----------------------------------------------------------------
class Periods(MethodView):
    def get(self):
        where = request.args.to_dict()
        return db.select(db.PERIODS, where=where), 200

    @auth_required(role=3) # admin
    def post(self):
        #TODO: check if the period is valid(not overlapping with other periods)
        return db.insert(db.PERIODS, data_list=request.json), 201
        
    @auth_required(role=3) # admin
    def patch(self): 
        #TODO: check if the period is valid(not overlapping with other periods)
        return db.update(db.PERIODS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=3) # admin
    def delete(self):
        return db.delete(db.PERIODS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# Notices
# ----------------------------------------------------------------
class Notices(MethodView):
    def get(self):
        where = request.args.to_dict()
        table = db.NOTICES
        if 'lang_code' in where:
            table += f" JOIN {db.NOTICE_TRANS} USING (notice_id)"
        return db.select(table, where=where), 200

    @auth_required(role=3) # admin
    def post(self):
        data_list = []
        for notice in request.json:
            notice['create_time'] = datetime.now()
            data_list.append(notice)
        return db.insert(db.NOTICES, data_list), 201
        
    @auth_required(role=3) # admin
    def patch(self): 
        data = request.json['data']
        data['update_time'] = datetime.now()
        return db.update(db.NOTICES, data=data, where=request.json['where']) or {}, 200

    @auth_required(role=3) # admin
    def delete(self):
        return db.delete(db.NOTICES, where=request.json) or {}, 204
    
# ----------------------------------------------------------------
# Settings
# ----------------------------------------------------------------
class Settings(MethodView):
    def get(self):
        where = request.args.to_dict()
        table = db.SETTINGS
        if 'lang_code' in where:
            table += f" JOIN {db.SESSION_TRANS} USING (id)"
        return db.select(table, where=where), 200

    @auth_required(role=4) # system
    def post(self):
        return db.insert(db.SETTINGS, data_list=request.json), 201
        
    @auth_required(role=4) # system
    def patch(self): 
        return db.update(db.SETTINGS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=4) # system
    def delete(self):
        return db.delete(db.SETTINGS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# Resv_status
# ----------------------------------------------------------------
class Resv_status(MethodView):
    def get(self):
        where = request.args.to_dict()
        table = db.RESV_STATUS
        if 'lang_code' in where:
            table += f" JOIN {db.RESV_STATUS_TRANS} USING (status)"
        return db.select(table, where=where), 200

    @auth_required(role=4) # system
    def post(self):
        return db.insert(db.RESV_STATUS, data_list=request.json), 201
        
    @auth_required(role=4) # system
    def patch(self): 
        return db.update(db.RESV_STATUS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=4) # system
    def delete(self):
        return db.delete(db.RESV_STATUS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# Resv_secu_levels
# ----------------------------------------------------------------
class Resv_secu_levels(MethodView):
    def get(self):
        where = request.args.to_dict()
        table = db.RESV_SECU_LEVELS
        if 'lang_code' in where:
            table += f" JOIN {db.RESV_SECU_LEVEL_TRANS} USING (secu_level)"
        return db.select(table, where=where), 200

    @auth_required(role=4) # system
    def post(self):
        return db.insert(db.RESV_SECU_LEVELS, data_list=request.json), 201
        
    @auth_required(role=4) # system
    def patch(self): 
        return db.update(db.RESV_SECU_LEVELS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=4) # system
    def delete(self):
        return db.delete(db.RESV_SECU_LEVELS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# Room_status
# ----------------------------------------------------------------
class Room_status(MethodView):
    def get(self):
        where = request.args.to_dict()
        table = db.ROOM_STATUS
        if 'lang_code' in where:
            table += f" JOIN {db.ROOM_STATUS_TRANS} USING (status)"
        return db.select(table, where=where), 200

    @auth_required(role=4) # system
    def post(self):
        return db.insert(db.ROOM_STATUS, data_list=request.json), 201
        
    @auth_required(role=4) # system
    def patch(self): 
        return db.update(db.ROOM_STATUS, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=4) # system
    def delete(self):
        return db.delete(db.ROOM_STATUS, where=request.json) or {}, 204

# ----------------------------------------------------------------
# User_roles
# ----------------------------------------------------------------
class User_roles(MethodView):
    def get(self):
        where = request.args.to_dict()
        table = db.USER_ROLES
        if 'lang_code' in where:
            table += f" JOIN {db.USER_ROLE_TRANS} USING (role)"
            return db.select(table), 200
        # print(table)
        return db.select(table, where=where), 200

    @auth_required(role=4) # system
    def post(self):
        return db.insert(db.USER_ROLES, data_list=request.json), 201
        
    @auth_required(role=4) # system
    def patch(self): 
        return db.update(db.USER_ROLES, data=request.json['data'], where=request.json['where']) or {}, 200

    @auth_required(role=4) # system
    def delete(self):
        return db.delete(db.USER_ROLES, where=request.json) or {}, 204
