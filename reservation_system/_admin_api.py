# from datetime import datetime, timedelta
# from mysql.connector import Error, errorcode

# from flask import g, request, Blueprint, Response
# from flask.views import MethodView
# from functools import wraps
# from werkzeug.security import generate_password_hash
# from webargs.flaskparser import use_kwargs

# from marshmallow import Schema, fields, validate

# from reservation_system import db, api
# from reservation_system.api import register_view
# from reservation_system.auth import auth_required
# from reservation_system.util import abort, marshal_with
# from reservation_system.models import fields as custom_fields
# from reservation_system.models import schemas
# from reservation_system import user_api

# def init_api(app, spec):
#     for path, view in (
#         ('reservations'              , Reservations  ),
#         # ('reservations/status'       , ResvStatus    ),
#         # ('reservations/privacy'      , ResvPrivacy   ),
#         # ('users'                     , Users         ),
#         # ('users/roles'               , UserRoles     ),
#         # ('rooms'                     , Rooms         ),
#         # ('rooms/types'               , RoomTypes     ),
#         # ('rooms/status'              , RoomStatus    ),
#         # ('languages'                 , Languages     ),
#         # ('sessions'                  , Sessions      ),
#         # ('notices'                   , Notices       ),
#         ('periods'                   , GetPostPeriod      ),
#         ('periods/<int:id>'          , PatchDeletePeriod   ),
#         ('settings'                  , GetSettings      ),
#         ('settings/<int:id>'         , PatchSetting ),
#     ):
#         path = 'admin/'+path
#         register_view(app, spec, path, view)

# class AdminView(MethodView):
#     decorators = [auth_required(role=db.UserRole.ADMIN)]

# class Reservations(AdminView):
#     # @use_kwargs(api.ResvGetQuerySchema(), location='query')
#     @marshal_with(schemas.ManyReservationSchema(), code=200)
#     def get(self, start_date=None, end_date=None, create_date=None, update_date=None, **kwargs):
#         """Get reservations
#         ---
#         summary: Get reservations
#         description: Get reservations
#         tags:
#           - Admin
#         security:
#           - cookieAuth: []
#         parameters:
#           - in: query
#             schema: GetResvQuerySchema
#         responses:
#           200:
#             description: Success(OK)
#             content:
#               application/json:
#                 schema: ManyReservationSchema
#         """
#         if start_date:  kwargs['DATE(start_time)']  = '%s' % start_date
#         if end_date:    kwargs['DATE(end_time)']    = '%s' % end_date
#         if create_date: kwargs['DATE(create_time)'] = '%s' % create_date
#         if update_date: kwargs['DATE(update_time)'] = '%s' % update_date

#         return db.select(db.Reservation.TABLE, where=kwargs, 
#                          order_by=['start_time', 'end_time'])
    
#     class AdminResvPostBodySchema(Schema):
#         class TimeSlot(Schema):
#             start_time = fields.DateTime(required=True)
#             end_time = fields.DateTime(required=True)
#             status = custom_fields.resv_status()
#         room_id = fields.Int(required=True)
#         title = fields.Str(required=True)
#         session_id = fields.Int(required=True)
#         time_slots = fields.List(fields.Nested(TimeSlot), required=True)
#         note = fields.Str()
#         username = fields.Str()
#         privacy = custom_fields.resv_privacy()
    
#     @use_kwargs(AdminResvPostBodySchema())
#     @marshal_with(user_api.AdvancedResvPostResponseSchema(), code=201)
#     def post(self, time_slots, **kwargs):
#         """Create a reservation
#         ---
#         summary: Create a reservation
#         description: Create a reservation
#         tags:
#           - Admin
#         security:
#           - cookieAuth: []
#         requestBody:
#           content:
#             application/json:
#               schema: AdminResvPostBodySchema
#         responses:
#           201:
#             description: Success(Created)
#             content:
#               application/json:
#                 schema: AdvancedResvPostResponseSchema
#         """
#         if 'username' not in kwargs:
#             kwargs['username'] = g.user['username']
#         if 'privacy' not in kwargs:
#             kwargs['privacy'] = db.ResvPrivacy.PUBLIC
#         for slot in time_slots:
#             if 'status' not in slot:
#                 slot['status'] = db.ResvStatus.CONFIRMED
        
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
#                 (resv_id, username, start_time, end_time, status)
#                 VALUES ({resv_id}, '{kwargs['username']}', %s, %s, %s)
#             """, [(slot['start_time'], slot['end_time'], slot['status']) for slot in time_slots])
#             cnx.commit()
#         except Exception as e:
#             cnx.rollback()
#             abort(500, str(e))
#         finally:
#             cursor.close()
        
#         return {'resv_id': resv_id}, 201
    
    
# class GetSettings(AdminView, api.Settings):
#     def get(self):
#         """Get settings
#         ---
#         summary: Get settings
#         description: Get settings
#         tags:
#           - Admin
#         security:
#           - cookieAuth: []
#         parameters:
#           - in: query
#             schema: SettingSchema
#         responses:
#           200:
#             description: OK
#             content:
#               application/json:
#                 schema: ManySettingSchema
#         """
#         return super().get()

# class PatchSetting(AdminView):
#     class PatchPathSchema(Schema):
#         id = fields.Int(required=True)

#     class PatchBodySchema(schemas.SettingSchema):
#         def __init__(self, exclude=None, **kwargs):
#             super().__init__(exclude=['id'], **kwargs)
        
#     @use_kwargs(PatchPathSchema(), location='path')
#     @use_kwargs(PatchBodySchema())
#     def patch(self, id, **kwargs):
#         """Update a setting
#         ---
#         summary: Update a setting
#         description: Update a setting
#         tags:
#           - Admin
#         security:
#           - cookieAuth: []
#         parameters:
#           - in: path
#             schema: PatchPathSchema
#         requestBody:
#           content:
#             application/json:
#               schema: PatchBodySchema
#         responses:
#           204:
#             description: Success(No Content)
#         """
#         if len(kwargs) > 0:
#             db.update(db.Setting.TABLE, [{
#                 'data': kwargs,
#                 'where': {'id': id}
#             }])
#         return {}, 204
    
# class GetPostPeriod(AdminView, api.Periods):
#     def get(self):
#         """Get periods
#         ---
#         summary: Get periods
#         description: Get periods
#         tags:
#           - Admin
#         security:
#           - cookieAuth: []
#         parameters:
#           - in: query
#             schema: PeriodSchema
#         responses:
#           200:
#             description: OK
#             content:
#               application/json:
#                 schema: ManyPeriodSchema
#         """
#         return super().get()

#     class PostPeriodsBodySchema(Schema):
#         start_time = custom_fields.TimeDelta(required=True, validate=validate.Range(min=timedelta(0), max=timedelta(days=1)))
#         end_time = custom_fields.TimeDelta(required=True, validate=validate.Range(min=timedelta(0), max=timedelta(days=1)))
    
#     class PostPeriodResponseSchema(schemas.Many, Schema):
#         period_id = fields.Int(required=True)
    
#     @use_kwargs(PostPeriodsBodySchema())
#     @marshal_with(PostPeriodResponseSchema(), code=201)
#     def post(self, **kwargs):
#         """Create a period
#         ---
#         summary: Create a period
#         description: Create a period
#         tags:
#           - Admin
#         security:
#           - cookieAuth: []
#         requestBody:
#           content:
#             application/json:
#               schema: PostPeriodsBodySchema
#         responses:
#           201:
#             description: Success(Created)
#             content:
#               application/json:
#                 schema: PostPeriodResponseSchema
#         """
#         print(kwargs)
#         return Response(status=500)
#         res = db.insert(db.Period.TABLE, kwargs)
#         return [{'period_id': id} for id in res['lastrowid']], 201

# class PatchDeletePeriod(AdminView):
#     class PatchDeletePeriodPathSchema(Schema):
#         id = fields.Int(required=True)


#     @use_kwargs(PatchDeletePeriodPathSchema(), location='path')
#     @use_kwargs(schemas.PeriodSchema())
#     def patch(self, id, **kwargs):
#         """Update a period
#         ---
#         summary: Update a period
#         description: Update a period
#         tags:
#           - Admin
#         security:
#           - cookieAuth: []
#         parameters:
#           - in: path
#             schema: PatchDeletePeriodPathSchema
#         requestBody:
#           content:
#             application/json:
#               schema: PeriodSchema
#         responses:
#           204:
#             description: Success(No Content)
#         """
#         if len(kwargs) > 0:
#             db.update(db.Period.TABLE, [{
#                 'data': kwargs,
#                 'where': {'period_id': id}
#             }])
#         return {}, 204
    
#     @use_kwargs(PatchDeletePeriodPathSchema(), location='path')
#     def delete(self, id):
#         """Delete a period
#         ---
#         summary: Delete a period
#         description: Delete a period
#         tags:
#           - Admin
#         security:
#           - cookieAuth: []
#         parameters:
#           - in: path
#             schema: PatchDeletePeriodPathSchema
#         responses:
#           204:
#             description: Success(No Content)
#         """
#         db.delete(db.Period.TABLE, [{'period_id': id}])
#         return {}, 204


# # class Post(AdminView):
# #     # `self.table` must be set in subclass
# #     def post(self):
# #         return db.insert(self.table, request.json), 201

# # class Patch(AdminView):
# #     # `self.table` must be set in subclass
# #     # `self.patch_required` must be set in subclass
# #     #     - it is a list of required columns for `where`
# #     def patch(self):
# #         """`request.json` must be a list of objects with `data` and `where`"""
# #         print(request.json)
# #         for data in request.json:
# #             where = data['where']
# #             for col in self.patch_required:
# #                 if col not in where:
# #                     abort(400, f'{col} is required')
# #         return db.update_many(self.table, request.json)


# # class Delete(AdminView):
# #     # `self.table` must be set in subclass
# #     # `self.patch_required` must be set in subclass
# #     #     - it is a list of required columns for `where`
# #     def delete(self):
# #         """`request.json` must be a list of objects representing `where`"""
# #         for where in request.json:
# #             for col in self.delete_required:
# #                 if col not in where:
# #                     abort(400, f'{col} is required')
# #         return db.delete_many(self.table, request.json)
    
# # class GetReservation(AdminView):
# #     # @marshal_with(
# #         # db.Reservation.schema(many=True), 
# #         # code=200, description='Success'
# #     # )
# #     @doc(description='Get reservations',
# #          tags=['Admin'], params={
# #         'date': {
# #             'in': 'path', 
# #             'type': 'string', 
# #             'format': 'date', 
# #             'description': 'Date of reservations to get'
# #         },
# #         # **db.Reservation.args()
# #         },
# #         **openapi_cookie_auth
# #     )   
# #     def get(self, date=None):
# #         args = request.args
# #         if date: args['DATE(start_time)'] = 'DATE(%s)' % date
# #         return db.select(db.Reservation.TABLE, where=args,
# #                         order_by=['start_time', 'end_time'])
# # class AdminPostResvSchema(Schema):
# #     class TimeSlotSchema(Schema):
# #         start_time = fields.DateTime(required=True)
# #         end_time = fields.DateTime(required=True)
# #         status = fields.Int(default=db.ResvStatus.CONFIRMED)
# #     username = fields.Str()
# #     room_id = fields.Int(required=True)
# #     title = fields.Str(required=True)
# #     note = fields.Str()
# #     session_id = fields.Int()
# #     privacy = fields.Int(default=db.ResvPrivacy.PUBLIC)
# #     time_slots = fields.List(
# #         fields.Nested(TimeSlotSchema()), 
# #         required=True,
# #         validate=validate.Length(min=1)
# #     )

# # class Reservations(GetReservation):
# #     @use_kwargs(AdminPostResvSchema())
# #     # @marshal_with(db.Reservation.schema(only=['resv_id'], many=True), code=201, description='Success')
# #     @doc(description='Create reservations', tags=['Admin'], **openapi_cookie_auth)
# #     def post(self, time_slots, **kwargs):
# #         if 'username' not in kwargs:
# #             kwargs['username'] = g.sub['username']
        
# #         cnx = db.get_cnx(); cursor = cnx.cursor()
# #         try:
# #             cursor.execute(f"""
# #                 INSERT INTO {db.Reservation.RESV_TABLE}
# #                 ({', '.join(kwargs.keys())})
# #                 VALUES ({', '.join(['%s']*len(kwargs))})
# #             """, tuple(kwargs.values()))
# #             resv_id = cursor.lastrowid
# #             cursor.executemany(f"""
# #                 INSERT INTO {db.Reservation.TS_TABLE}
# #                 (resv_id, username, status, start_time, end_time)
# #                 VALUES ({resv_id}, '{g.sub['username']}', %s, %s, %s)
# #             """, [(ts['status'], ts['start_time'], ts['end_time']) for ts in time_slots])
# #             cnx.commit()
# #         except Exception as e:
# #             abort(500, str(e))
# #         finally:
# #             cursor.close()
        
# #         return {'resv_id': resv_id}, 201
    
# # class PatchReservation(AdminView):
# #     class PatchResvSchema(Schema):
# #         title = fields.Str()
# #         note = fields.Str()
# #         status = fields.Int()
# #         privacy = fields.Int()

# #     @marshal_with(Schema(), code=200, description='Success')
# #     @use_kwargs(PatchResvSchema())
# #     @doc(description='Update reservations', tags=['Admin'],
# #         params={
# #             'resv_id': {
# #                 'in': 'path',
# #                 'type': 'integer',
# #                 'description': 'Reservation ID',
# #             },
# #             'username': {
# #                 'in': 'path',
# #                 'type': 'string',
# #                 'description': 'Reservation owner',
# #             },
# #             'slot_id': {
# #                 'in': 'path',
# #                 'type': 'integer',
# #                 'description': 'Reservation time slot ID',
# #             },
# #         },
# #         **openapi_cookie_auth)
# #     def patch(self, resv_id, username=None, slot_id=None, **kwargs):
# #         where = {'resv_id': resv_id}
# #         if username: where['username'] = username
# #         if slot_id: 
# #             where['slot_id'] = slot_id
# #         return db.update(db.Reservation.TABLE, [{
# #             'where': where,
# #             'data': kwargs
# #         }])

# # class Users(AdminView):
# #     def get(self):
# #         return db.User.get(where=request.args.to_dict())
    
# #     def post(self):
# #         data_list = request.json
# #         for data in data_list:
# #             if 'role' not in data:
# #                 data['role'] = db.UserRole.RESTRICTED
# #         data['password'] = generate_password_hash(data['password'])
# #         try:
# #             return db.insert(db.User.TABLE, data_list), 201
# #         except Error as e:
# #             if e.errno == errorcode.ER_DUP_ENTRY:
# #                 abort(409, 'username already exists')
# #             else:
# #                 abort(500, str(e))
    
# #     def patch(self):
# #         for data in request.json:
# #             if 'username' not in data['where']:
# #                 abort(400, 'username is required')
# #             if 'password' in data['data']:
# #                 data['data']['password'] = generate_password_hash(data['data']['password'])
# #         return db.update_many(db.User.TABLE, request.json)
    
# # class Rooms(Delete, api.Rooms):
# #     table = db.Room.TABLE
# #     delete_required = ['room_id']

# #     def post(self):
# #         return db.Room.insert(request.json), 201

# #     def patch(self):
# #         for data in request.json:
# #             if 'room_id' not in data['where']:
# #                 abort(400, 'room_id is required')
# #         return db.Room.update_many(request.json)

# # class Periods(Post, Patch, Delete, api.Periods):
# #     table = db.Period.TABLE
# #     patch_required = ['period_id']
# #     delete_required = ['period_id']
    
# # class Notices(Post, Patch, Delete, api.Notices):
# #     table = db.Notice.TABLE
# #     patch_required = ['notice_id']
# #     delete_required = ['notice_id']
    
# # class Sessions(Post, Patch, Delete, api.Sessions):
# #     table = db.Session.TABLE
# #     patch_required = ['session_id']
# #     delete_required = ['session_id']
    
# # class RoomTypes(Post, Patch, Delete, api.RoomTypes):
# #     table = db.RoomType.TABLE
# #     patch_required = ['type']
# #     delete_required = ['type']

# # #
# # class Languages(Patch, api.Languages):
# #     table = db.Language.TABLE
# #     patch_required = ['lang_code']
    
# # class ResvStatus(Patch, api.ResvStatus):
# #     table = db.ResvStatus.TABLE
# #     patch_required = ['status']

# # class ResvPrivacy(Patch, api.ResvPrivacy):
# #     table = db.ResvPrivacy.TABLE
# #     patch_required = ['privacy']

# # class RoomStatus(Patch, api.RoomStatus):
# #     table = db.RoomStatus.TABLE
# #     patch_required = ['status']

# # class UserRoles(Patch, api.UserRoles):
# #     table = db.UserRole.TABLE
# #     patch_required = ['role']

# # class Settings(Patch, api.Settings):
# #     table = db.Setting.TABLE
# #     patch_required = ['id']
