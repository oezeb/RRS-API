import logging
from dateutil.parser import parse

from flask import g, request
from flask.views import MethodView
from werkzeug.security import check_password_hash, generate_password_hash

from mysql.connector import Error, errorcode

from reservation_system import db
from reservation_system.util import abort, time_slot_conflict, current_session
from reservation_system.auth import auth_required

logger = logging.getLogger(__name__)

def init_user_api(app):
    for path, view in (
        ('user', User),
        ('user/reservation', Reservation),
    ):
        app.add_url_rule(f'/api/{path}', view_func=view.as_view(path))

class User(MethodView):
    @auth_required()
    def get(self):
        """
        Get user info.
        User should be logged in(have a valid auth token)
        """
        username = g.sub['username']
        cnx = db.get_cnx(); cursor = cnx.cursor(dictionary=True)
        cursor.execute(
            "SELECT username, name, email, role FROM %s WHERE username = %s", 
            (db.USERS, username)
        )
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

class Reservation(MethodView):
    @auth_required()
    def get(self):
        """
        Get reservation info of current session.
        As a `reservation` can have multiple `time_slots`,
        this endpoint returns two types of data:
        - By default, it will join `reservations` and `time_slots` tables. 
        So for each `time_slot`, the `reservations` info will be repeated.
        - The `time_slots` will be grouped by `reservation` if `group_by_resv` is `true`.
        There will be a `time_slots` field in the response, which is a list of `time_slots` for each `reservation`.

        Extra query parameters:
            - `group_by_resv`: `true` or `false`. Default is `false`.
            - `lang_code`: `en`(for now)
        """
        where = request.args.to_dict()
        if 'session_id' not in where:
            where['session_id'] = db.Session.current()['session_id']
        where['username'] = g.sub['username']
        
        date = where.pop('date', None)
        group_by_resv = where.pop('group_by_resv', 'false').lower() == 'true'
        
        if group_by_resv:
            ts_where = {}
            for k in ['slot_id', 'start_time', 'end_time']:
                if k in where: ts_where[k] = where.pop(k)
            table = f"{db.RESERVATIONS}"
            if 'lang_code' in where:
                table += f" JOIN {db.RESV_TRANS} USING (resv_id, username)"
            resvs = db.select(table, where)
            
            if date:
                ts_where['DATE(start_time)'] = date
                ts_where['DATE(end_time)'] = date
            for resv in resvs:
                resv['time_slots'] = db.select(
                    db.TIME_SLOTS, 
                    {**ts_where, 'resv_id': resv['resv_id']},
                    order_by=['start_time', 'end_time']
                )
            return resvs
        else:
            table = f"{db.RESERVATIONS} NATURAL JOIN {db.TIME_SLOTS}"
            if 'lang_code' in where:
                table += f" JOIN {db.RESV_TRANS} USING (resv_id, username)"
            if date:
                where['DATE(start_time)'] = date
                where['DATE(end_time)'] = date
            return db.select(table, where, order_by=['start_time', 'end_time'])
    
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
        session = db.Session.current()
        data['session_id'] = session['session_id']
        if not data['session_id']:
            abort(404, message='Session not found')

        if not db.Room.available(data['room_id']):
            abort(400, message='Room not available')
        if not db.Setting.in_time_window(data['time_slots']):
            abort(400, message='Time slot not in time window')
        if not db.Setting.in_time_limit(data['time_slots']):
            abort(400, message='Time slot not in time limit')
        if not db.Setting.below_max_daily(g.sub['username']):
            abort(400, message='Reservation per day limit reached')

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
                abort(500, message=f'Database error: {err.msg}')
        finally:
            cursor.close()
        return { 'resv_id': resv_id, 'message': 'Reservation created successfully'}, 201

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
        session = current_session()
        data['session_id'] = session['session_id']
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

    @auth_required()
    def delete(self):
        """
        Delete a time slot.
        `request.json` should contain:
            - Mandatory: `resv_id`, `slot_id`
        """
        if g.sub['role'] < 0:
            abort(403, message='Access denied')
        data = request.json
        if 'resv_id' not in data or 'slot_id' not in data:
            abort(400, message='Missing required fields')

        cnx = db.get_cnx(); cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute(f"""
                DELETE FROM {db.TIME_SLOTS}
                WHERE resv_id = %s AND slot_id = %s AND username = %s
            """, (data['resv_id'], data['slot_id'], g.sub['username']))
            cnx.commit()
        except:
            abort(500, message='Database error')
        finally:
            cursor.close()
        return {'message': 'Time slot deleted successfully'}, 200