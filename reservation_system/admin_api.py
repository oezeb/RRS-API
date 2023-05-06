from datetime import datetime, timedelta
from mysql.connector import Error, errorcode

from flask import g, request, Blueprint
from functools import wraps
from werkzeug.security import generate_password_hash

from marshmallow import Schema, fields, validate

from reservation_system import db, api
# from reservation_system.auth import auth_required, openapi_cookie_auth
from reservation_system.util import abort

# def init_api(app, docs):
#     for path, view in (
#         ('reservations'              , Reservations  ),
#         ('reservations/<string:date>', GetReservation),
#         ('reservations/<int:resv_id>', PatchReservation),
#         ('reservations/<int:resv_id>/<string:username>', PatchReservation),
#         ('reservations/<int:resv_id>/<int:slot_id>', PatchReservation),
#         ('reservations/<int:resv_id>/<string:username>/<int:slot_id>', PatchReservation),
#         ('reservations/<int:resv_id>/<int:slot_id>/<string:username>', PatchReservation),
#         ('reservations/status'       , ResvStatus    ),
#         ('reservations/privacy'      , ResvPrivacy   ),
#         ('users'                     , Users         ),
#         ('users/roles'               , UserRoles     ),
#         ('languages'                 , Languages     ),
#         ('rooms'                     , Rooms         ),
#         ('rooms/types'               , RoomTypes     ),
#         ('rooms/status'              , RoomStatus    ),
#         ('sessions'                  , Sessions      ),
#         ('notices'                   , Notices       ),
#         ('periods'                   , Periods       ),
#         ('settings'                  , Settings      ),
#     ):
#         app.add_url_rule(f'/api/admin/{path}', view_func=view.as_view(f'admin/{path}'))
#         docs.register(view, endpoint=f'admin/{path}')

# class AdminView(MethodResource):
#     decorators = [auth_required(role=db.UserRole.ADMIN)]

# class Post(AdminView):
#     # `self.table` must be set in subclass
#     def post(self):
#         return db.insert(self.table, request.json), 201

# class Patch(AdminView):
#     # `self.table` must be set in subclass
#     # `self.patch_required` must be set in subclass
#     #     - it is a list of required columns for `where`
#     def patch(self):
#         """`request.json` must be a list of objects with `data` and `where`"""
#         print(request.json)
#         for data in request.json:
#             where = data['where']
#             for col in self.patch_required:
#                 if col not in where:
#                     abort(400, f'{col} is required')
#         return db.update_many(self.table, request.json)


# class Delete(AdminView):
#     # `self.table` must be set in subclass
#     # `self.patch_required` must be set in subclass
#     #     - it is a list of required columns for `where`
#     def delete(self):
#         """`request.json` must be a list of objects representing `where`"""
#         for where in request.json:
#             for col in self.delete_required:
#                 if col not in where:
#                     abort(400, f'{col} is required')
#         return db.delete_many(self.table, request.json)
    
# class GetReservation(AdminView):
#     # @marshal_with(
#         # db.Reservation.schema(many=True), 
#         # code=200, description='Success'
#     # )
#     @doc(description='Get reservations',
#          tags=['Admin'], params={
#         'date': {
#             'in': 'path', 
#             'type': 'string', 
#             'format': 'date', 
#             'description': 'Date of reservations to get'
#         },
#         # **db.Reservation.args()
#         },
#         **openapi_cookie_auth
#     )   
#     def get(self, date=None):
#         args = request.args
#         if date: args['DATE(start_time)'] = 'DATE(%s)' % date
#         return db.select(db.Reservation.TABLE, where=args,
#                         order_by=['start_time', 'end_time'])
# class AdminPostResvSchema(Schema):
#     class TimeSlotSchema(Schema):
#         start_time = fields.DateTime(required=True)
#         end_time = fields.DateTime(required=True)
#         status = fields.Int(default=db.ResvStatus.CONFIRMED)
#     username = fields.Str()
#     room_id = fields.Int(required=True)
#     title = fields.Str(required=True)
#     note = fields.Str()
#     session_id = fields.Int()
#     privacy = fields.Int(default=db.ResvPrivacy.PUBLIC)
#     time_slots = fields.List(
#         fields.Nested(TimeSlotSchema()), 
#         required=True,
#         validate=validate.Length(min=1)
#     )

# class Reservations(GetReservation):
#     @use_kwargs(AdminPostResvSchema())
#     # @marshal_with(db.Reservation.schema(only=['resv_id'], many=True), code=201, description='Success')
#     @doc(description='Create reservations', tags=['Admin'], **openapi_cookie_auth)
#     def post(self, time_slots, **kwargs):
#         if 'username' not in kwargs:
#             kwargs['username'] = g.sub['username']
        
#         cnx = db.get_cnx(); cursor = cnx.cursor()
#         try:
#             cursor.execute(f"""
#                 INSERT INTO {db.Reservation.RESV_TABLE}
#                 ({', '.join(kwargs.keys())})
#                 VALUES ({', '.join(['%s']*len(kwargs))})
#             """, tuple(kwargs.values()))
#             resv_id = cursor.lastrowid
#             cursor.executemany(f"""
#                 INSERT INTO {db.Reservation.TS_TABLE}
#                 (resv_id, username, status, start_time, end_time)
#                 VALUES ({resv_id}, '{g.sub['username']}', %s, %s, %s)
#             """, [(ts['status'], ts['start_time'], ts['end_time']) for ts in time_slots])
#             cnx.commit()
#         except Exception as e:
#             abort(500, str(e))
#         finally:
#             cursor.close()
        
#         return {'resv_id': resv_id}, 201
    
# class PatchReservation(AdminView):
#     class PatchResvSchema(Schema):
#         title = fields.Str()
#         note = fields.Str()
#         status = fields.Int()
#         privacy = fields.Int()

#     @marshal_with(Schema(), code=200, description='Success')
#     @use_kwargs(PatchResvSchema())
#     @doc(description='Update reservations', tags=['Admin'],
#         params={
#             'resv_id': {
#                 'in': 'path',
#                 'type': 'integer',
#                 'description': 'Reservation ID',
#             },
#             'username': {
#                 'in': 'path',
#                 'type': 'string',
#                 'description': 'Reservation owner',
#             },
#             'slot_id': {
#                 'in': 'path',
#                 'type': 'integer',
#                 'description': 'Reservation time slot ID',
#             },
#         },
#         **openapi_cookie_auth)
#     def patch(self, resv_id, username=None, slot_id=None, **kwargs):
#         where = {'resv_id': resv_id}
#         if username: where['username'] = username
#         if slot_id: 
#             where['slot_id'] = slot_id
#         return db.update(db.Reservation.TABLE, [{
#             'where': where,
#             'data': kwargs
#         }])

# class Users(AdminView):
#     def get(self):
#         return db.User.get(where=request.args.to_dict())
    
#     def post(self):
#         data_list = request.json
#         for data in data_list:
#             if 'role' not in data:
#                 data['role'] = db.UserRole.RESTRICTED
#         data['password'] = generate_password_hash(data['password'])
#         try:
#             return db.insert(db.User.TABLE, data_list), 201
#         except Error as e:
#             if e.errno == errorcode.ER_DUP_ENTRY:
#                 abort(409, 'username already exists')
#             else:
#                 abort(500, str(e))
    
#     def patch(self):
#         for data in request.json:
#             if 'username' not in data['where']:
#                 abort(400, 'username is required')
#             if 'password' in data['data']:
#                 data['data']['password'] = generate_password_hash(data['data']['password'])
#         return db.update_many(db.User.TABLE, request.json)
    
# class Rooms(Delete, api.Rooms):
#     table = db.Room.TABLE
#     delete_required = ['room_id']

#     def post(self):
#         return db.Room.insert(request.json), 201

#     def patch(self):
#         for data in request.json:
#             if 'room_id' not in data['where']:
#                 abort(400, 'room_id is required')
#         return db.Room.update_many(request.json)

# class Periods(Post, Patch, Delete, api.Periods):
#     table = db.Period.TABLE
#     patch_required = ['period_id']
#     delete_required = ['period_id']
    
# class Notices(Post, Patch, Delete, api.Notices):
#     table = db.Notice.TABLE
#     patch_required = ['notice_id']
#     delete_required = ['notice_id']
    
# class Sessions(Post, Patch, Delete, api.Sessions):
#     table = db.Session.TABLE
#     patch_required = ['session_id']
#     delete_required = ['session_id']
    
# class RoomTypes(Post, Patch, Delete, api.RoomTypes):
#     table = db.RoomType.TABLE
#     patch_required = ['type']
#     delete_required = ['type']

# #
# class Languages(Patch, api.Languages):
#     table = db.Language.TABLE
#     patch_required = ['lang_code']
    
# class ResvStatus(Patch, api.ResvStatus):
#     table = db.ResvStatus.TABLE
#     patch_required = ['status']

# class ResvPrivacy(Patch, api.ResvPrivacy):
#     table = db.ResvPrivacy.TABLE
#     patch_required = ['privacy']

# class RoomStatus(Patch, api.RoomStatus):
#     table = db.RoomStatus.TABLE
#     patch_required = ['status']

# class UserRoles(Patch, api.UserRoles):
#     table = db.UserRole.TABLE
#     patch_required = ['role']

# class Settings(Patch, api.Settings):
#     table = db.Setting.TABLE
#     patch_required = ['id']
