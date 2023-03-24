from dateutil import parser
from datetime import datetime, timedelta

from flask_restful import Resource, request, abort, wraps

from reservation_system import db
from reservation_system.auth import Auth

def init_api(api):
    api.add_resource(           Resv_trans, '/resv_trans'           )
    api.add_resource(    Resv_status_trans, '/resv_status_trans'    )
    api.add_resource(Resv_secu_level_trans, '/resv_secu_level_trans')
    api.add_resource(           Room_trans, '/room_trans'           )
    api.add_resource(      Room_type_trans, '/room_type_trans'      )
    api.add_resource(    Room_status_trans, '/room_status_trans'    )
    api.add_resource(        Session_trans, '/session_trans'        )
    api.add_resource(           User_trans, '/user_trans'           )
    api.add_resource(      User_role_trans, '/user_role_trans'      )
    api.add_resource(            Languages, '/languages'            )
    api.add_resource(           Time_slots, '/time_slots'           )
    api.add_resource(         Reservations, '/reservations'         )
    api.add_resource(          Resv_status, '/resv_status'          )
    api.add_resource(     Resv_secu_levels, '/resv_secu_levels'     )
    api.add_resource(                Rooms, '/rooms'                )
    api.add_resource(           Room_types, '/room_types'           )
    api.add_resource(          Room_status, '/room_status'          )
    api.add_resource(             Sessions, '/sessions'             )
    api.add_resource(                Users, '/users'                )
    api.add_resource(           User_roles, '/user_roles'           )
    api.add_resource(              Periods, '/periods'              )
    api.add_resource(         Resv_windows, '/resv_windows'         )

def table_resource_auth(table, method):
    def auth_required(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = Auth.auth()

            # System only: fixed at installation time and are crucial for making decisions
            if table in (
                db.USER_ROLES,
                db.RESV_STATUS,
                db.RESV_SECU_LEVELS,
                db.ROOM_STATUS,
            ):
                """
                Role 0: Restricted, 1: Basic, 2: Advanced, 3: Administrator
                Resv_status 0: Pending, 1: Confirmed, 2: Cancelled, 3: Rejected
                Resv_secu_levels 0: Public, 1: Anonymous, 2: Private
                Room_status 0: Unavailable, 1: Available
                """
                if method in ("POST", "DELETE"): # System only can add or delete new roles
                    abort(401)
                elif method == "PATCH": # Admin can change labels and description
                    if user['role'] <= 2:
                        abort(401)

            # Admin only
            elif table in (
                db.RESV_STATUS_TRANS,
                db.RESV_SECU_LEVEL_TRANS,
                db.ROOM_TRANS,
                db.ROOM_TYPE_TRANS,
                db.ROOM_STATUS_TRANS,
                db.USER_ROLE_TRANS,
                db.LANGUAGES,
                db.ROOMS,
                db.ROOM_TYPES,
                db.SESSIONS,
                db.PERIODS,
                db.RESV_WINDOWS,

                db.RESERVATIONS, # Other Users should go though `/basic-reservation` and `/advanced-reservation`
                db.TIME_SLOTS,
            ):
                if method in ("POST", "PATCH", "DELETE"): # Admin only
                    if user['role'] <= 2:
                        abort(401)
            
            elif table in (
                db.RESV_TRANS,
                db.USER_TRANS,
            ):
                if method == "POST":
                    if user['role'] <= 2:
                        for data in request.json:
                            if data['username'] != user['username']:
                                abort(401)
                elif method == "PATCH":
                    if user['role'] <= 2:
                        if request.json['where']['username'] != user['username'] or 'username' in request.json['data']:
                            abort(401)
                elif method == "DELETE": # Not Admin, can only delete their own
                    if user['role'] <= 2:
                        if request.json['username'] != user['username']:
                            abort(401)

            elif table == db.USERS:
                if method == "POST": # Admin only can create users, Others should go through `/auth/register`
                    abort(401)
                elif method == "PATCH": # Not Admin, can only edit their own but not their username or role
                    if user['role'] <= 2:
                        if request.json['where']['username'] != user['username'] or 'username' in request.json['data'] or 'role' in request.json['data']:
                            abort(401)
                elif method == "DELETE": # Admin==3 can only
                    if user['role'] <= 2:
                        abort(401)

            elif table == db.RESERVATIONS:
                if method == "POST":
                    if user['role'] <= 2:
                        for data in request.json:
                            if (# not their own
                                data['username'] != user['username']
                            ) or (# role 0 can only create pending(satus 0) public(secu 0) reservations
                                user['role'] <= 0 and (data['status'] != 0 or data['secu_level'] != 0)
                            ) or (# role 1 can only create public(secu 0) reservations
                                user['role'] <= 1 and data['secu_level'] != 0
                            ) or (# role 2 can create anomymous(secu 1) reservations
                                user['role'] <= 1 and data['secu_level'] != 0
                            ) or (# room unavailable
                                db.select(db.ROOMS, {'room_id': data['room_id']})[0]['status'] == 0
                            ) or (# not current session
                                db.select(db.SESSIONS, {'session_id': data['session_id']})[0]['is_current'] == 0
                            ): abort(401)
                elif method == "PATCH":
                    if user['role'] <= 2:
                        if (# not their own
                            request.json['where']['username'] != user['username']
                         ) or (# cannot edit username
                            'username' in request.json['data']
                         ) or (# room unavailable
                            db.select(db.ROOMS, {'room_id': data['room_id']})[0]['status'] == 0
                        ) or (# not current session
                            db.select(db.SESSIONS, {'session_id': data['session_id']})[0]['is_current'] == 0
                        ): abort(401)
                        

                elif method == "DELETE":
                    pass

            elif table == db.TIME_SLOTS:
                if method == "POST":
                    pass
                elif method == "DELETE":
                    pass

            return func(*args, **kwargs)
        return wrapper
    return auth_required

class TableResource(Resource):
    table: str
    def get(self): 
        return db.select(self.table, where=request.json), 200

    @table_resource_auth(table=table, method='POST')
    def post(self): 
        return db.insert(self.table, data_list=request.json), 201

    @table_resource_auth(table=table, method='PATCH')
    def patch(self): 
        return db.update(self.table, data=request.json['data'], where=request.json['where']), 200

    @table_resource_auth(table=table, method='DELETE')
    def delete(self):
        return db.delete(self.table, where=request.json), 204

class            Resv_trans(TableResource): table = db.RESV_TRANS
class     Resv_status_trans(TableResource): table = db.RESV_STATUS_TRANS
class Resv_secu_level_trans(TableResource): table = db.RESV_SECU_LEVEL_TRANS
class            Room_trans(TableResource): table = db.ROOM_TRANS
class       Room_type_trans(TableResource): table = db.ROOM_TYPE_TRANS
class     Room_status_trans(TableResource): table = db.ROOM_STATUS_TRANS
class         Session_trans(TableResource): table = db.SESSION_TRANS
class            User_trans(TableResource): table = db.USER_TRANS
class       User_role_trans(TableResource): table = db.USER_ROLE_TRANS
class             Languages(TableResource): table = db.LANGUAGES
class            Time_slots(TableResource): table = db.TIME_SLOTS
class          Reservations(TableResource): table = db.RESERVATIONS
class           Resv_status(TableResource): table = db.RESV_STATUS
class      Resv_secu_levels(TableResource): table = db.RESV_SECU_LEVELS
class                 Rooms(TableResource): table = db.ROOMS
class            Room_types(TableResource): table = db.ROOM_TYPES
class           Room_status(TableResource): table = db.ROOM_STATUS
class              Sessions(TableResource): table = db.SESSIONS
class                 Users(TableResource): table = db.USERS
class            User_roles(TableResource): table = db.USER_ROLES
class               Periods(TableResource): table = db.PERIODS
class          Resv_windows(TableResource): table = db.RESV_WINDOWS

# ----------------------------------------------------------------

def validate_reservations(data):
    for reservation in data:
        
        if parser.parse(reservation['end_time']) <= parser.parse(reservation['start_time']):
            abort(400, message="Invalid reservation", reservation=reservation)

        cursor = db.get_cursor()
        cursor.execute(f"""
            SELECT * FROM 
                {Reservations.TABLE} 
            WHERE 
                (start_time BETWEEN '{reservation['start_time']}' AND '{reservation['end_time']}')
                OR
                (end_time BETWEEN '{reservation['start_time']}' AND '{reservation['end_time']}');
        """)
        if len(cursor.fetchall()) != 0:
            abort(400, message=f"Reservation time conflict", reservation=reservation)

        cursor.execute(f"""
            SELECT room_id FROM 
                {Rooms.TABLE}
            WHERE 
                room_id='{reservation['room_id']}' AND
                status=0 AND 
                open_time <= TIME('{reservation['start_time']}') AND 
                close_time >= TIME('{reservation['end_time']}');
        """)
        if len(cursor.fetchall()) == 0:
            abort(400, message="Room unavailable", reservation=reservation)
        
        cursor.execute(f"""
            SELECT session_id FROM
                {Sessions.TABLE}
            WHERE
                session_id={reservation['session_id']} AND
                is_current=1 AND 
                start_time <= '{reservation['start_time']}' AND 
                end_time >= '{reservation['end_time']}';
        """)
        if len(cursor.fetchall()) == 0:
            abort(400, message="Out of session space", reservation=reservation)