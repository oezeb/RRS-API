from dateutil import parser
from datetime import datetime, timedelta

from flask_restful import Resource, request, abort, wraps

from reservation_system import db
from reservation_system.auth import auth_required
from werkzeug.security import generate_password_hash

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

class Base(Resource):
    table: str
    def get(self):
        return db.select(self.table, where=request.json), 200

    @auth_required
    def post(self): 
        return db.insert(self.table, data_list=request.json), 201

    @auth_required
    def patch(self): 
        return db.update(self.table, data=request.json['data'], where=request.json['where']), 200

    @auth_required
    def delete(self):
        return db.delete(self.table, where=request.json), 204

class Users(Base): 
    table = db.USERS
    @auth_required
    def post(self):
        data_list = request.json
        for data in data_list:
            if 'password' in data:
                data['password'] = generate_password_hash(data['password'])
        return db.insert(self.table, data_list=data_list), 201
    
    @auth_required
    def patch(self):
        data = request.json['data']
        if 'password' in data:
            data['password'] = generate_password_hash(data['password'])
        return db.update(self.table, data=data, where=request.json['where']), 200

class            Resv_trans(Base): table = db.RESV_TRANS
class     Resv_status_trans(Base): table = db.RESV_STATUS_TRANS
class Resv_secu_level_trans(Base): table = db.RESV_SECU_LEVEL_TRANS
class            Room_trans(Base): table = db.ROOM_TRANS
class       Room_type_trans(Base): table = db.ROOM_TYPE_TRANS
class     Room_status_trans(Base): table = db.ROOM_STATUS_TRANS
class         Session_trans(Base): table = db.SESSION_TRANS
class            User_trans(Base): table = db.USER_TRANS
class       User_role_trans(Base): table = db.USER_ROLE_TRANS
class             Languages(Base): table = db.LANGUAGES
class            Time_slots(Base): table = db.TIME_SLOTS
class          Reservations(Base): table = db.RESERVATIONS
class           Resv_status(Base): table = db.RESV_STATUS
class      Resv_secu_levels(Base): table = db.RESV_SECU_LEVELS
class                 Rooms(Base): table = db.ROOMS
class            Room_types(Base): table = db.ROOM_TYPES
class           Room_status(Base): table = db.ROOM_STATUS
class              Sessions(Base): table = db.SESSIONS
class            User_roles(Base): table = db.USER_ROLES
class               Periods(Base): table = db.PERIODS
class          Resv_windows(Base): table = db.RESV_WINDOWS

# ----------------------------------------------------------------