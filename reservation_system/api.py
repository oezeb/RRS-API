from flask.views import MethodView as MethodView
from webargs.flaskparser import use_kwargs

from reservation_system import db
from reservation_system.util import marshal_with
  
from reservation_system.models.api import reservations as resvs
from reservation_system.models.api import users
from reservation_system.models.api import rooms
from reservation_system.models.api import languages as langs
from reservation_system.models.api import sessions as sess
from reservation_system.models.api import notices as nots
from reservation_system.models.api import periods as perds
from reservation_system.models.api import settings as sets

# from reservation_system.models.util import BetweenField

# from marshmallow import Schema

# class Test(MethodView):
#     class TestSchema(Schema):
#         between = BetweenField()

#     @use_kwargs(TestSchema(), location='query')
#     @marshal_with(TestSchema(), code=200)
#     def get(self, **kwargs):
#         """Test
#         ---
#         description: Test
#         parameters:
#           - in: query
#             schema: TestSchema
#         responses:
#           200:
#             description: OK
#             content:
#               application/json:
#                 schema: TestSchema
#         """
#         print(kwargs)
#         return {'between': 12}

def init_api(app, spec):
    for path, view in (
        ('reservations'              , Reservations  ),
        ('reservations/status'       , ResvStatus    ),
        ('reservations/privacy'      , ResvPrivacy   ),
        ('users'                     , Users         ),
        ('users/roles'               , UserRoles     ),
        ('rooms'                     , Rooms         ),
        ('rooms/types'               , RoomTypes     ),
        ('rooms/status'              , RoomStatus    ),
        ('languages'                 , Languages     ),
        ('sessions'                  , Sessions      ),
        ('notices'                   , Notices       ),
        ('periods'                   , Periods       ),
        ('settings'                  , Settings      ),

        # ('test'                      , Test          ),
    ):
        register_view(app, spec, path, view)

def register_view(app, spec, path, view):
    url = f'/api/{path}'
    method_view = view.as_view(path)

    app.add_url_rule(url, view_func=method_view)

    with app.test_request_context():
        spec.path(view=method_view)

class Reservations(MethodView):
    @marshal_with(resvs.ResvSchema(many=True), code=200)
    @use_kwargs(resvs.ResvSchema(), location='query')
    def get(self, date=None, **kwargs):
        """Get reservations
        ---
        description: Get reservations
        parameters:
          - in: query
            schema: ResvSchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ResvSchema
        """
        if date: kwargs['DATE(start_time)'] = '%s' % date
        res = db.select(db.Reservation.TABLE, where=kwargs, 
                         order_by=['start_time', 'end_time'])
        # check privacy
        for r in res:
            if r['privacy'] == db.ResvPrivacy.ANONYMOUS:
                r.pop('username'); r.pop('resv_id')
            if r['privacy'] == db.ResvPrivacy.PRIVATE:
                r = {'time_slots': r['time_slots']}
        return res

class RoomResv(MethodView):
    def get(self, room_id):
        """Get room reservations
        ---
        description: Get room reservations
        parameters:
          - in: path
            schema: RoomResvPathSchema
        responses:
          200:
            description: OK
        """
        pass

class Users(MethodView):
    @marshal_with(users.UserGetRespSchema(many=True), code=200)
    @use_kwargs(users.UserGetQuerySchema(), location='query')
    def get(self, **kwargs):
        """Get users
        ---
        description: Get users
        parameters:
          - in: query
            schema: UserGetQuerySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: UserGetRespSchema
        """
        return db.select(db.User.TABLE, where=kwargs)
    
class Periods(MethodView):
    @marshal_with(perds.PeriodGetRespSchema(many=True), code=200)
    @use_kwargs(perds.PeriodGetQuerySchema(), location='query')
    def get(self, **kwargs):
        """Get periods
        ---
        description: Get periods
        parameters:
          - in: query
            schema: PeriodGetQuerySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: PeriodGetRespSchema
        """
        return db.select(db.Period.TABLE, where=kwargs)

class Notices(MethodView):
    @marshal_with(nots.NoticeGetRespSchema(many=True), code=200)
    @use_kwargs(nots.NoticeGetQuerySchema(), location='query')
    def get(self, **kwargs):
        """Get notices
        ---
        description: Get notices
        parameters:
          - in: query
            schema: NoticeGetQuerySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: NoticeGetRespSchema
        """
        return db.select(db.Notice.TABLE, where=kwargs, 
                         order_by=['create_time', 'update_time'])

class Sessions(MethodView):
    @marshal_with(sess.SessionGetRespSchema(many=True), code=200)
    @use_kwargs(sess.SessionGetQuerySchema(), location='query')
    def get(self, **kwargs):
        """Get sessions
        ---
        description: Get sessions
        parameters:
          - in: query
            schema: SessionGetQuerySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: SessionGetRespSchema
        """
        return db.select(db.Session.TABLE, where=kwargs)

class Rooms(MethodView):
    @marshal_with(rooms.RoomGetRespSchema(many=True), code=200)
    @use_kwargs(rooms.RoomGetQuerySchema(), location='query')
    def get(self, **kwargs):
        """Get rooms
        ---
        description: Get rooms
        parameters:
          - in: query
            schema: RoomGetQuerySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: RoomGetRespSchema
        """
        return db.select(db.Room.TABLE, where=kwargs)        

class RoomTypes(MethodView):
    @marshal_with(rooms.RoomTypeGetRespSchema(many=True), code=200)
    @use_kwargs(rooms.RoomTypeGetQuerySchema(), location='query')
    def get(self, **kwargs):
        """Get room types
        ---
        description: Get room types
        parameters:
          - in: query
            schema: RoomTypeGetQuerySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: RoomTypeGetRespSchema
        """
        return db.select(db.RoomType.TABLE, where=kwargs)

class Languages(MethodView):
    @marshal_with(langs.LangGetRespSchema(many=True), code=200)
    @use_kwargs(langs.LangGetQuerySchema(), location='query')
    def get(self, **kwargs):
        """Get languages
        ---
        description: Get languages
        parameters:
          - in: query
            schema: LangGetQuerySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: LangGetRespSchema
        """
        return db.select(db.Language.TABLE, where=kwargs)
    
class ResvStatus(MethodView):
    @marshal_with(resvs.ResvStatusSchema(many=True), code=200)
    @use_kwargs(resvs.ResvStatusSchema(), location='query')
    def get(self, **kwargs):
        """Get reservation status
        ---
        description: Get reservation status
        parameters:
          - in: query
            schema: ResvStatusSchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ResvStatusSchema
        """
        return db.select(db.ResvStatus.TABLE, where=kwargs)
    
class ResvPrivacy(MethodView):
    @marshal_with(resvs.ResvPrivacySchema(many=True), code=200)
    @use_kwargs(resvs.ResvPrivacySchema(), location='query')
    def get(self, **kwargs):
        """Get reservation privacy
        ---
        description: Get reservation privacy
        parameters:
          - in: query
            schema: ResvPrivacySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ResvPrivacySchema
        """
        return db.select(db.ResvPrivacy.TABLE, where=kwargs)
    
class RoomStatus(MethodView):
    @marshal_with(rooms.RoomStatusGetRespSchema(many=True), code=200)
    @use_kwargs(rooms.RoomStatusGetQuerySchema(), location='query')
    def get(self, **kwargs):
        return db.select(db.RoomStatus.TABLE, where=kwargs)
    
class UserRoles(MethodView):
    @marshal_with(users.UserRoleGetRespSchema(many=True), code=200)
    @use_kwargs(users.UserRoleGetQuerySchema(), location='query')
    def get(self, **kwargs):
        """Get user roles
        ---
        description: Get user roles
        parameters:
          - in: query
            schema: UserRoleGetQuerySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: UserRoleGetRespSchema
        """
        return db.select(db.UserRole.TABLE, where=kwargs)

class Settings(MethodView):
    @marshal_with(sets.SettingGetRespSchema(many=True), code=200)
    @use_kwargs(sets.SettingGetQuerySchema(), location='query')
    def get(self, **kwargs):
        """Get settings
        ---
        description: Get settings
        parameters:
          - in: query
            schema: SettingGetQuerySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: SettingGetRespSchema
        """
        return db.select(db.Setting.TABLE, where=kwargs)
