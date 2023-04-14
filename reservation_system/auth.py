import logging
import jwt
from datetime import datetime, timedelta
import base64

from flask import current_app, g, request, Response
from flask.views import MethodView
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

from mysql.connector import Error, errorcode

from reservation_system import db
from reservation_system.util import abort

def init_auth(app):
    for path, view in (
        ('login', Login),
        ('register', Register),
        ('logout', Logout),
        ('user', User),
        ('reservation', Reservation),
    ):
        app.add_url_rule(f'/api/{path}', view_func=view.as_view(path))

class Login(MethodView):
    def post(self):
        """headers: {'Authorization': 'Basic ' + btoa(${username}:${password})}"""
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            abort(401, message='Authorization header is missing')
        auth_token = auth_header.split(' ')[1]
        username, password = base64.b64decode(auth_token).decode('utf-8').split(':')


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

        max_age = timedelta(days=1)
        payload = {
            'exp': datetime.utcnow() + max_age,
            'iat': datetime.utcnow(),
            'sub': {
                'username': username,
                'role': user['role']
            }
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        # Send cookie response
        resp = Response()
        resp.set_cookie('access_token', token, 
                        max_age=max_age.total_seconds(),
                        httponly=True,
                        # secure=True, 
                        samesite='Strict'
                    )
        return resp
    
class Logout(MethodView):
    def post(self):
        resp = Response()
        resp.set_cookie('access_token', '', expires=0)
        return resp
    
class Register(MethodView):
    def post(self):
        """
        Register a new user.
        Data should include `username`, `password`, `role`, `name`, and `email`.
        Newly registered users `role` should be `0=restricted`.
        `email` is optional.
        """
        data = request.json
        if 'role' in data and data['role'] != 0:
            abort(403, message='New users should be restricted(role=0) by default')
        data['role'] = 0
        data['password'] = generate_password_hash(data['password'])

        cnx = db.get_cnx()
        cursor = cnx.cursor(dictionary=True)

        try:
            cursor.execute(f"""
                INSERT INTO {db.USERS}
                ({', '.join(data.keys())})
                VALUES ({', '.join(['%s'] * len(data))})
            """, (*data.values(),))
            cnx.commit()
        except Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                abort(409, message='Username already exists')
            else:
                abort(500, message='Database error')
        finally:
            cursor.close()
        
        return {'message': 'User created successfully'}, 201

def auth_required(role=0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = request.cookies.get('access_token')
            if not token:
                abort(401, message='Token is missing')
            try:
                payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                abort(401, message='Token is expired')
            except jwt.InvalidTokenError:
                abort(401, message='Token is invalid')
            except Exception as e:
                logging.error(e)
                abort(500, message='Internal server error')

            sub = payload['sub']
            if sub['role'] < role:
                abort(403, message='Access denied')
            g.sub = sub
            return func(*args, **kwargs)
        return wrapper
    return decorator

class User(MethodView):
    @auth_required()
    def get(self):
        """
        Get user info.
        User should be logged in(have a valid auth token)
        """
        username = g.sub['username']
        cnx = db.get_cnx(); cursor = cnx.cursor(dictionary=True)
        cursor.execute(f"""
            SELECT username, name, email, role
            FROM {db.USERS}
            WHERE username = '{username}'
        """)
        user = cursor.fetchone()
        if not user:
            abort(404, message='User not found')
        return user

    @auth_required()
    def patch(self):
        """
        Update user info.
        User should be logged in(have a valid auth token)
        User should be admin or updating own info
        Data may include `name`, or `email` only.
        If data includes `new_password`, it should include `password` as well.
        """
        print(request.json)
        username = g.sub['username']
        data = request.json
        if 'username' in data or 'role' in data:
            abort(403, message='Access denied')
        
        new_password = data.pop('new_password', None)
        password = data.pop('password', None)
        if new_password and not password:
            abort(400, message='Old password is missing')
        cnx = db.get_cnx(); cursor = cnx.cursor(dictionary=True)
        if password and new_password:
            cursor.execute(f"""
                SELECT password
                FROM {db.USERS}
                WHERE username = '{username}'
            """)
            user = cursor.fetchone()
            if not user or not check_password_hash(user['password'], password):
                abort(401, message='Invalid password')
            data['password'] = generate_password_hash(new_password)
        
        cursor.execute(f"""
            UPDATE {db.USERS}
            SET {', '.join([f'{k} = %s' for k in data])}
            WHERE username = '{username}'
        """, (*data.values(),))
        cnx.commit(); cursor.close()
        return {'message': 'User updated successfully'}, 200

def time_slot_conflict(room_id, session_id, start_time, end_time):
    cnx = db.get_cnx(); cursor = cnx.cursor()
    # statuses: 0: pending, 1: approved, 2: cancelled, 3: rejected
    cursor.execute(f"""
        SELECT COUNT(*)
        FROM {db.TIME_SLOTS} NATURAL JOIN {db.RESERVATIONS}
        WHERE room_id = {room_id} AND session_id = {session_id} AND status = 1
        AND ((start_time BETWEEN '{start_time}' AND '{end_time}')
            OR (end_time BETWEEN '{start_time}' AND '{end_time}'))
    """)
    conflict = cursor.fetchone()[0]
    cnx.commit(); cursor.close()
    return conflict

def current_session():
    cnx = db.get_cnx(); cursor = cnx.cursor()
    cursor.execute(f"""
        SELECT session_id
        FROM {db.SESSIONS}
        WHERE is_current = 1
    """)
    session_id = cursor.fetchone()
    cnx.commit(); cursor.close()
    return session_id[0] if session_id else None

class Reservation(MethodView):
    def get(self):
        """
        Get reservation info of current session.
        As a `reservation` can have multiple `time_slots`,
        this endpoint returns two types of data:
        - By default, it will join `reservations` and `time_slots` tables. 
        So for each `time_slot`, the `reservations` info will be repeated.
        - The `time_slots` will be grouped by `reservation` if `group_by_resv` is `true`.
        There will be a `time_slots` field in the response, which is a list of `time_slots` for each `reservation`.
        """
        session_id = current_session()
        if not session_id:
            abort(404, message='Session not found')
        where = request.args.to_dict()
        where['session_id'] = session_id
        group_by_resv = where.pop('group_by_resv', 'false').lower() == 'true'
        if group_by_resv:
            ts_where = {}
            for k in ['slot_id', 'date', 'start_time', 'end_time']:
                if k in where: ts_where[k] = where.pop(k)
            table = f"{db.RESERVATIONS}"
            if 'lang_code' in where:
                table += f" JOIN {db.RESV_TRANS} USING (resv_id, username)"
            resvs = db.select(table, where)
            
            if 'date' in ts_where:
                date = ts_where.pop('date')
                ts_where['DATE(start_time)'] = date
                ts_where['DATE(end_time)'] = date
            for resv in resvs:
                resv['time_slots'] = db.select(db.TIME_SLOTS, {**ts_where, 'resv_id': resv['resv_id'], 'username': resv['username']})
            return resvs
        else:
            table = f"{db.RESERVATIONS} NATURAL JOIN {db.TIME_SLOTS}"
            if 'lang_code' in where:
                table += f" JOIN {db.RESV_TRANS} USING (resv_id, username)"
            if 'date' in where:
                date = where.pop('date')
                where['DATE(start_time)'] = date
                where['DATE(end_time)'] = date
            return db.select(table, where)
    
    @auth_required()
    def post(self):
        """
        Create a new reservation.
        `request.json` should contain:
            - Mandatory: 
                - `room_id`
                - `title`
                - Not empty list of time_slots with [`start_time`, `end_time`]
            - Optional:
                - `note`
                - `secu_level`: default is `0`(public), user_role=2 can have `secu_level`=1(anonymous)
        `status` and `session_id` will be generated automatically.
            - `status`: depends on the user role and the nature of the reservation
                - user_role<0: cannot create reservation(abort 403)
                - user_role=0: `status`=0
                - user_role=1: `status`=1 if len(time_slots)==1 else 0
                - user_role>=2: `status`=1
            - `session_id`: default is current session
        """
        if g.sub['role'] < 0:
            abort(403, message='Access denied')
        data = request.json
        if 'room_id' not in data or 'title' not in data or 'time_slots' not in data:
            abort(400, message='Missing required fields')
        if 'secu_level' not in data:
            data['secu_level'] = 0
        elif g.sub['role'] < 2 and data['secu_level'] > 0:
            abort(403, message='Access denied')
        elif g.sub['role'] == 2 and data['secu_level'] > 1:
            abort(403, message='Access denied')
        if not data['time_slots']:
            abort(400, message='Time_slots cannot be empty')

        data['status'] = 0
        if g.sub['role'] == 1 and len(data['time_slots']) == 1:
            data['status'] = 1
        elif g.sub['role'] >= 2:
            data['status'] = 1
        data['session_id'] = current_session()
        if not data['session_id']:
            abort(404, message='Session not found')

        # check time_slots conflict
        for ts in data['time_slots']:
            if time_slot_conflict(data['room_id'], data['session_id'], ts['start_time'], ts['end_time']):
                abort(400, message='Time slot conflict')

        cnx = db.get_cnx(); cursor = cnx.cursor(dictionary=True)      
        try:
            cursor.execute(f"""
                INSERT INTO {db.RESERVATIONS}
                (username, room_id, title, note, secu_level, status, session_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (g.sub['username'], data['room_id'], data['title'], data['note'], data['secu_level'], data['status'], data['session_id']))
            resv_id = cursor.lastrowid
            cursor.executemany(f"""
                INSERT INTO {db.TIME_SLOTS}
                (resv_id, username, start_time, end_time)
                VALUES (%s, %s, %s, %s)
            """, [(resv_id, g.sub['username'], ts['start_time'], ts['end_time']) for ts in data['time_slots']])
            cnx.commit()
        except Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                abort(409, message='Reservation already exists')
            else:
                abort(500, message='Database error')
        finally:
            cursor.close()
        return {'message': 'Reservation created successfully'}, 201

    @auth_required()
    def patch(self):
        """
        Update reservation info.
        `request.json` should contain:
            - Mandatory: `resv_id`
            - Optional:
                - `title`
                - `note`
                - `status` only set to `2`(cancelled)
        """
        if g.sub['role'] < 0:
            abort(403, message='Access denied')
        data = request.json
        keys = set(data.keys())
        if keys - {'resv_id', 'title', 'note', 'status'}:
            abort(400, message='Invalid fields')
        if 'resv_id' not in keys:
            abort(400, message='Missing required fields')
        resv_id = data.pop('resv_id')
        if not data:
            abort(400, message='Missing required fields')
        if 'status' in data and data['status'] != 2:
            abort(400, message='Invalid status')
        data['session_id'] = current_session()
        if not data['session_id']:
            abort(404, message='Session not found')

        cnx = db.get_cnx(); cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute(f"""
                UPDATE {db.RESERVATIONS}
                SET {', '.join([f'{k} = %s' for k in data])}
                WHERE resv_id = {resv_id} AND username = '{g.sub['username']}'
            """, (*data.values(),))
            cnx.commit()
        except:
            abort(500, message='Database error')
        finally:
            cursor.close()
        return {'message': 'Reservation updated successfully'}, 200
    
    @auth_required(role=3) # TODO: remove, users should not be able to delete reservations, they can cancel them(patch status)
    def delete(self):
        """
        Delete a reservation or a timeslot in a reservation.
        `request.json` should contain:
            - Mandatory: `resv_id`
            - Optional: `slot_id`
        """
        if g.sub['role'] < 0:
            abort(403, message='Access denied')
        data = request.json
        if 'resv_id' not in data:
            abort(400, message='Missing required fields')
        cnx = db.get_cnx(); cursor = cnx.cursor(dictionary=True)
        try:
            if 'slot_id' in data:
                cursor.execute(f"""
                    DELETE FROM {db.TIME_SLOTS}
                    WHERE slot_id = %s AND resv_id = %s AND username = %s
                """ , (data['slot_id'], data['resv_id'], g.sub['username']))
            else:
                cursor.execute(f"""
                    DELETE FROM {db.RESERVATIONS}
                    WHERE resv_id = %s AND username = %s
                """ , (data['resv_id'], g.sub['username']))
            cnx.commit()
        except:
            abort(500, message='Database error')
        finally:
            cursor.close()
        return {'message': 'Reservation deleted successfully'}, 200
