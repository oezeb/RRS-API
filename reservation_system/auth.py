import logging
import jwt
from datetime import datetime, timedelta

from flask import current_app
from flask_restful import Resource, request, abort, wraps
from werkzeug.security import check_password_hash, generate_password_hash

from mysql.connector import Error, errorcode

from reservation_system import db

def init_auth(api):
    api.add_resource(                Login, '/auth/login'           )
    api.add_resource(             Register, '/auth/register'        )

class Login(Resource):
    def post(self):
        username = request.json['username']
        password = request.json['password']

        cnx = db.get_cnx()
        cursor = cnx.cursor(dictionary=True)

        cursor.execute(f"""
            SELECT password, role
            FROM {db.USERS}
            WHERE username = '{username}'
        """)
        user = cursor.fetchone()

        if not user or not check_password_hash(user['password'], password):
            abort(401, message='Invalid username or password')
        
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'sub': {
                'username': username,
                'role': user['role']
            }
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        return {'token': token.decode('UTF-8')}
    
class Register(Resource):
    def post(self):
        """
        Register a new user.
        Data should include `username`, `password`, `role`, `name`, and `email`.
        Newly registered users `role` should be `0=restricted`.
        `email` is optional.
        """
        data = request.json
        data['role'] = 0 # New users are restricted by default

        cnx = db.get_cnx()
        cursor = cnx.cursor(dictionary=True)

        try:
            cursor.execute(f"""
                INSERT INTO {db.USERS}
                (username, password, role, name, email)
                VALUES
                (%s, %s, %s, %s, %s)
            """, (
                data['username'],
                generate_password_hash(data['password']),
                data['role'],
                data['name'],
                data.get('email', None)
            ))
            cnx.commit()
        except Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                abort(409, message='Username already exists')
            else:
                abort(500, message='Database error')
        finally:
            cursor.close()

def auth():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        abort(401, message='Authorization header is missing')

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        abort(401, message='Token is expired')
    except jwt.InvalidTokenError:
        abort(401, message='Token is invalid')

    return payload['sub']



def auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        sub = auth()
        username, role = sub['username'], sub['role']
        cnx = db.get_cnx(); cursor = cnx.cursor(dictionary=True)

        # System only: set at installation time and are crucial for making decisions.
        # Role 0: Restricted, 1: Basic, 2: Advanced, 3: Administrator
        # Resv_status 0: Pending, 1: Confirmed, 2: Cancelled, 3: Rejected
        # Resv_secu_levels 0: Public, 1: Anonymous, 2: Private
        # Room_status 0: Unavailable, 1: Available
        if request.path.endswith((
            '/user_roles', 
            '/resv_status', 
            '/resv_secu_levels', 
            '/room_status',
        )):
            if request.method in ('POST', 'PATCH', 'DELETE'):
                abort(403, message="Access denied")
            
        # Admin only
        elif request.path.endswith((
            '/resv_status', 
            '/resv_secu_levels',
            '/room_trans',
            '/room_type_trans',
            '/room_status_trans',
            '/user_role_trans',
            '/languages',
            '/rooms',
            '/room_types',
            '/sessions',
            '/periods',
            '/resv_windows',
        )):
            if request.method in ('POST', 'PATCH', 'DELETE'):
                if role < 3:
                    abort(403, message="Access denied")

        elif request.path.endswith((
            '/resv_trans',
            '/user_trans',
        )):
            if request.method == 'POST':
                if role < 3:
                    for data in request.json:
                        if data['username'] != username:
                            abort(401)
            elif request.method == 'PATCH':
                if role < 3:
                    if request.json['where']['username'] != username or 'username' in request.json['data']:
                        abort(401)
            elif request.method == 'DELETE':
                if role < 3 and request.json['username'] != username:
                        abort(401)

        # elif table == db.USERS:
        elif request.path.endswith('/users'):
            if request.method == 'POST': # Admin only can create users, Others should go through `/auth/register`
                    abort(401)
            elif request.method == 'PATCH': # Not Admin, can only edit their own but not their username or role
                if role < 3:
                    if request.json['where']['username'] != username or 'username' in request.json['data'] or 'role' in request.json['data']:
                        abort(401)
            elif request.method == 'DELETE': # Admin only can delete users
                if role < 3:
                    abort(401)
            
        elif request.path.endswith('/reservations'):
            if request.method == 'POST':
                if role < 3: # Non-administrator users
                    for resv in request.json:
                        # Non-administrator users can only create reservations for themselves
                        if resv['username'] != username:
                            abort(403)
                        # Non-administrator users can only create reservations for the current session
                        cursor.execute("""
                            SELECT session_id 
                            FROM sessions 
                            WHERE is_current = 1
                        """)
                        if resv['session_id'] != cursor.fetchone()['session_id']:
                            abort(403)
                        # Non-administrator users can only create reservations for available rooms 
                        cursor.execute("""
                            SELECT room_status 
                            FROM rooms 
                            WHERE room_id = %s
                        """, (resv['room_id'],))
                        if cursor.fetchone()['room_status'] != 1:
                            abort(403)
                        # Basic users can only create reservations for public or anonymous security levels
                        if role < 2 and resv['secu_level'] == 2:
                            abort(403)
                        # Restricted users can only create pending and public reservations
                        if role < 1 and (resv['status'] != 0 or resv['secu_level'] != 0):
                            abort(403)
            elif request.method == 'PATCH':
                # request.json contains a dictionary with keys 'data' and 'where'
                # 'data' is a dictionary that contains the data to be updated
                # 'where' is a dictionary that contains the conditions for the update.
                # all elements in 'where' will be joined by AND

                # Non-administrator users can only update their own reservations
                if 'username' not in request.json['where'] or request.json['where']['username'] != username:
                    abort(403)
                # Non-administrator users can only update reservations notes and status(to cancelled). they can update one or both at a time
                if not set(request.json['data'].keys()).issubset({'note', 'status'}):
                    abort(403)
                if 'status' in request.json['data'] and request.json['data']['status'] != 2:
                    abort(403)
        elif request.path.endswith('/time_slots'):
            if request.method == 'POST':
                if role < 3: # Non-administrator users
                    for slot in request.json:
                        start_time = datetime.fromisoformat(slot['start_time'])
                        end_time = datetime.fromisoformat(slot['end_time'])
                        if start_time >= end_time:
                            abort(403)
                        # Non-administrator users can only create time slots for their own reservations
                        if slot['username'] != username:
                            abort(403)
                        # Non-administrator users can only create time in free time slots(current time slot should not overlap with any existing time slots)
                        cursor.execute("""
                            SELECT slot_id 
                            FROM time_slots
                            WHERE start_time BETWEEN %s AND %s OR end_time BETWEEN %s AND %s
                        """, (slot['start_time'], slot['end_time'], slot['start_time'], slot['end_time']))
                        if cursor.fetchone() is not None:
                            abort(403)
                        # Non-administrator users can only create time slots between the open and close times of the room
                        cursor.execute("""
                            SELECT room_id
                            FROM reservations join rooms using(room_id)
                            WHERE resv_id = %s AND username = %s  AND open_time <= TIME(%s) AND close_time >= TIME(%s)
                        """, (slot['resv_id'], slot['username'], slot['start_time'], slot['end_time']))
                        if cursor.fetchone() is None:
                            abort(403)
                        # Non-administrator users can only create time slots between the start and end times of the current session
                        cursor.execute("""
                            SELECT session_id
                            FROM reservations join sessions using(session_id)
                            WHERE resv_id = %s AND username = %s AND is_current = 1 AND start_time <= %s AND end_time >= %s
                        """, (slot['resv_id'], slot['username'], slot['start_time'], slot['end_time']))
                        if cursor.fetchone() is None:
                            abort(403)
                        # Basic users are allowed to create only one time slot for confirmed reservations and the time slot should be in the reserving window
                        if role < 2:
                            cursor.execute("""
                                SELECT *
                                FROM reservations natural join time_slots
                                WHERE resv_id = %s AND username = %s AND status = 1
                            """, (slot['resv_id'], slot['username']))
                            if cursor.fetchone() is not None:
                                abort(403)
                            cursor.execute("""
                                SELECT time_window
                                FROM resv_windows
                                WHERE is_current = 1
                            """)
                            time_window = cursor.fetchone()['time_window']
                            if start_time < datetime.now() or end_time > datetime.now() + time_window:
                                abort(403)
            elif request.method == 'DELETE':
                # request.json is a dictionary that contains the conditions for the update.
                # all elements in 'request.json' will be joined by AND
                # Non-administrator users can only delete time slots for their own reservations
                if request.json['username'] != username:
                    abort(403)
                # Basic and Restricted users can only delete time slots for pending reservations
                if role < 2:
                    cursor.execute(f"""
                        SELECT *
                        FROM reservations natural join time_slots
                        WHERE {' AND '.join([f'{key} = %s' for key in request.json.keys()])} AND status != 0
                    """, tuple(request.json.values()))
                    if cursor.fetchone() is not None:
                        abort(403)
        cursor.close()

        return func(*args, **kwargs)
    return wrapper
