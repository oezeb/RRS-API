from flask import g, request, current_app
from flask.views import MethodView
from werkzeug.security import check_password_hash, generate_password_hash

from mysql.connector import Error, errorcode

from reservation_system import db
from reservation_system.util import abort
from reservation_system.auth import auth_required

def init_api(app):
    for path, view in (
        ('user', User),
        ('user/reservation', Reservation),
    ):
        app.add_url_rule(f'/api/{path}', view_func=view.as_view(path))

class User(MethodView):
    @auth_required()
    def get(self):
        try:
            user = db.User.get(g.sub['username'])
            return user
        except Exception as e:
            current_app.logger.error(f"Error occurred while getting user: {e}")
            abort(404, message='User not found')

    @auth_required()
    def patch(self):
        """
        Update user info.
        - updatable fields: `email`, `password`
        - updating `password` requires `new_password` and `password`
        """
        data = request.json
        if set(data.keys()) - {'email', 'password', 'new_password'}:
            abort(400, message='Invalid field')
  
        if 'password' in data and 'new_password' in data:
            password = db.User.get_password(g.sub['username'])
            if not check_password_hash(password, data['password']):
                abort(401, message='Invalid password')
            password = generate_password_hash(data['new_password'])
        elif 'password' in data or 'new_password' in data:
            abort(400, message='Missing new password or password')
        else:
            password = None

        email = data.get('email', None)

        try: 
            db.User.update(g.sub['username'], email=email, password=password)
        except Exception as e:
            current_app.logger.error(f"Error occurred while updating user: {e}")
            abort(500, message='Failed to update user')

        return {'message': 'User updated successfully'}, 200

class Reservation(MethodView):
    @auth_required()
    def get(self):
        """
        Get reservations of current session of current user.
        - Optional query parameter `date` as `YYYY-MM-DD`
        allow user to get whole day reservations of a specific date.
        """
        where = request.args.to_dict()
        if 'session_id' not in where:
            where['session_id'] = db.Session.current()['session_id']
        where['username'] = g.sub['username']

        return db.Reservation.get(where)
    
    @auth_required()
    def post(self):
        """
        Create a new reservation.
        - Required fields: `room_id`, `title`, `time_slots`
            - `time_slots`: Non-empty list of (`start_time`, `end_time`)
        - Optional fields: `note`, `secu_level`
            - `secu_level`: default is `0`(public), user_role=2 can have `secu_level`=1(anonymous)
        - Auto generated fields: `status`, `session_id`
            - `status`: depends on the user role and the nature of the reservation
                user_role   |time_slots|in_time_window|in_time_limit|is_comb_of_periods|status   |reservation_type
                ------------|----------|--------------|-------------|------------------|---------|----------------
               -1 BLOCKED   |any       |any           |any          |any               |FORBIDDEN|any
                0 RESTRICTED|1         |YES           |YES          |YES               |0 PENDING|BASIC
                0 RESTRICTED|>1        |any           |any          |any               |FORBIDDEN|ADVANCED
                0 RESTRICTED|any       |NO            |any          |any               |FORBIDDEN|ADVANCED
                0 RESTRICTED|any       |any           |NO           |any               |FORBIDDEN|ADVANCED
                0 RESTRICTED|any       |any           |any          |NO                |FORBIDDEN|ADVANCED
                1 BASIC     |1         |YES           |YES          |YES               |1 CONFRIMED|BASIC
                1 BASIC     |>1        |any           |any          |YES               |0        |ADVANCED
                1 BASIC     |any       |NO            |any          |YES               |0        |ADVANCED
                1 BASIC     |any       |any           |NO           |YES               |0        |ADVANCED
                1 BASIC     |any       |any           |any          |NO                |FORBIDDEN|ADVANCED
                2 ADVANCED  |any       |any           |any          |YES               |1        |any
                2 ADVANCED  |any       |any           |any          |NO                |FORBIDDEN|any
                3 ADMIN     |any       |any           |any          |any               |1        |any
            - `session_id`: current session
        """
        if g.sub['role'] <= db.UserRole.BLOCKED:
            abort(403, message='Access denied')
        data = request.json

        # Check required fields
        if 'room_id' not in data or 'title' not in data or 'time_slots' not in data:
            abort(400, message='Missing required fields')
        if not data['time_slots']:
            abort(400, message='Time_slots cannot be empty')
        
        # Check optional fields
        if 'secu_level' not in data:
            data['secu_level'] = 0
        elif g.sub['role'] < db.UserRole.ADVANCED and data['secu_level'] > 0:
            abort(403, message='Access denied')
        elif g.sub['role'] == db.UserRole.ADVANCED and data['secu_level'] > 1:
            abort(403, message='Access denied')
        
        # Auto generate fields
        data['status'] = db.ResvStatus.PENDING
        if g.sub['role'] >= db.UserRole.ADMIN:
            data['status'] = db.ResvStatus.CONFIRMED
        else:
            is_comb_of_periods = db.Period.is_comb_of_periods(data['time_slots'])
            if not is_comb_of_periods:
                abort(400, message='Time_slots must be combination of periods')
            
            if g.sub['role'] == db.UserRole.ADVANCED:
                data['status'] = db.ResvStatus.CONFIRMED
            else:
                slot_num = len(data['time_slots'])
                in_time_window = db.Setting.in_time_window(data['time_slots'])
                in_time_limit = db.Setting.in_time_limit(data['time_slots'])

                if g.sub['role'] <= db.UserRole.RESTRICTED:
                    if slot_num > 1 or not in_time_window or not in_time_limit:
                        abort(400, message='Access denied')
                elif g.sub['role'] == db.UserRole.BASIC:
                    if slot_num == 1 and in_time_window and in_time_limit:
                        data['status'] = db.ResvStatus.CONFIRMED
        
        data['session_id'] = db.Session.current()['session_id']

        # Check other constraints
        if not db.Room.available(data['room_id']):
            abort(400, message='Room not available')
        if not db.Setting.below_max_daily(g.sub['username']):
            abort(400, message='Reservation per day limit reached')
        # There are more constraints, already implemented in the database.
        # See `schema.sql` and `db.py::init_db`
        # - `start_time` < `end_time`
        # - `start_time` and `end_time` within `session.start_time` and `session.end_time`
        # - `confirmed` and `pending` reservation `time_slots` do not overlap

        data['username'] = g.sub['username']
        try: 
            resv_id = db.Reservation.insert(data)
        except Error as err:
            current_app.logger.error(err)
            if err.errno == errorcode.ER_DUP_ENTRY:
                abort(409, message='Reservation already exists')
            else:
                abort(500, message=f'Database error: {err.msg}')

        return { 'resv_id': resv_id, 'message': 'Reservation created successfully'}, 201
    
    @auth_required()
    def patch(self):
        """
        Update reservation info.
        `request.json` should contain:
            - `resv_id`
            - `data`: contains the fields to be updated. `title`, `note`, `status`
                - `status` if exists=CANCELLED
        """
        if g.sub['role'] <= db.UserRole.BLOCKED:
            abort(403, message='Access denied')
        data = request.json
        if not data['resv_id'] or not data['data']:
            abort(400, message='Missing required fields')
        if 'status' in data['data'] and data['data']['status'] != db.ResvStatus.CANCELLED:
            abort(400, message='Invalid status')
        if set(data['data'].keys()) - {'title', 'note', 'status'}:
            abort(400, message='Invalid fields')
        
        try:
            db.Reservation.update(data['resv_id'], g.sub['username'], data['data'])
        except Error as err:
            abort(500, message=f'Database error: {err.msg}')

        return {'message': 'Reservation updated successfully'}, 200

    @auth_required()
    def delete(self):
        """
        Delete a time slot.
        `request.json` should contain:
            - Mandatory: `resv_id`, `slot_id`
        """
        if g.sub['role'] <= db.UserRole.BLOCKED:
            abort(403, message='Access denied')
        data = request.json
        if 'resv_id' not in data or 'slot_id' not in data:
            abort(400, message='Missing required fields')

        cnx = db.get_cnx(); cursor = cnx.cursor(dictionary=True)
        try:
            cursor.execute(f"""
                DELETE FROM {db.Reservation.TS_TABLE}
                WHERE resv_id = %s AND slot_id = %s AND username = %s
            """, (data['resv_id'], data['slot_id'], g.sub['username']))
            cnx.commit()
        except:
            abort(500, message='Database error')
        finally:
            cursor.close()
        return {'message': 'Time slot deleted successfully'}, 204