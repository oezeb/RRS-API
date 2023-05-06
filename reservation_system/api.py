from flask.views import MethodView as _MethodView
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
    ):
        register_view(app, spec, path, view)

def register_view(app, spec, path, view):
    url = f'/api/{path}'
    method_view = view.as_view(path)

    app.add_url_rule(url, view_func=method_view)

    view().register_schemas(spec)
    with app.test_request_context():
        spec.path(view=method_view)

class MethodView(_MethodView):
    schemas = {}
    
    def register_schemas(self, spec):
        for name, value in self.schemas.items():
            if name not in spec.components.schemas:
              spec.components.schema(name, schema=value)

class Reservations(MethodView):
    schemas = {
        'Resvervations Get Method Query Schema': resvs.ResvGetQuerySchema,
        'Resvervations Get Method Response Schema': resvs.ResvGetRespSchema,
    }

    @marshal_with(resvs.ResvGetRespSchema(many=True), code=200)
    @use_kwargs(resvs.ResvGetQuerySchema(), location='query')
    def get(self, date=None, **kwargs):
        """Get reservations
        ---
        description: Get reservations
        parameters:
          - in: query
            schema: ResvGetQuerySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ResvGetRespSchema
        """
        if date: kwargs['DATE(start_time)'] = 'DATE(%s)' % date
        res = db.select(db.Reservation.TABLE, where=kwargs, 
                         order_by=['start_time', 'end_time'])
        # check privacy
        for r in res:
            if r['privacy'] == db.ResvPrivacy.ANONYMOUS:
                r.pop('username'); r.pop('resv_id')
            if r['privacy'] == db.ResvPrivacy.PRIVATE:
                r = {'time_slots': r['time_slots']}
        return res

class Users(MethodView):
    schemas = {
        'Users Get Method Query Schema': users.UserGetQuerySchema,
        'Users Get Method Response Schema': users.UserGetRespSchema,
    }

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
    schemas = {
        'Periods Get Method Query Schema': perds.PeriodGetQuerySchema,
        'Periods Get Method Response Schema': perds.PeriodGetRespSchema,
    }

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
    schemas = {
        'Notices Get Method Query Schema': nots.NoticeGetQuerySchema,
        'Notices Get Method Response Schema': nots.NoticeGetRespSchema,
    }

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
    schemas = {
        'Sessions Get Method Query Schema': sess.SessionGetQuerySchema,
        'Sessions Get Method Response Schema': sess.SessionGetRespSchema,
    }

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
    schemas = {
        'Rooms Get Method Query Schema': rooms.RoomGetQuerySchema,
        'Rooms Get Method Response Schema': rooms.RoomGetRespSchema,
    }

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
    schemas = {
        'RoomTypes Get Method Query Schema': rooms.RoomTypeGetQuerySchema,
        'RoomTypes Get Method Response Schema': rooms.RoomTypeGetRespSchema,
    }

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
    schemas = {
        'Languages Get Method Query Schema': langs.LangGetQuerySchema,
        'Languages Get Method Response Schema': langs.LangGetRespSchema,
    }

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
    schemas = {
        'ResvStatus Get Method Query Schema': resvs.ResvStatusGetQuerySchema,
        'ResvStatus Get Method Response Schema': resvs.ResvStatusGetRespSchema,
    }

    @marshal_with(resvs.ResvStatusGetRespSchema(many=True), code=200)
    @use_kwargs(resvs.ResvStatusGetQuerySchema(), location='query')
    def get(self, **kwargs):
        """Get reservation status
        ---
        description: Get reservation status
        parameters:
          - in: query
            schema: ResvStatusGetQuerySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ResvStatusGetRespSchema
        """
        return db.select(db.ResvStatus.TABLE, where=kwargs)
    
class ResvPrivacy(MethodView):
    schemas = {
        'ResvPrivacy Get Method Query Schema': resvs.ResvPrivacyGetQuerySchema,
        'ResvPrivacy Get Method Response Schema': resvs.ResvPrivacyGetRespSchema,
    }

    @marshal_with(resvs.ResvPrivacyGetRespSchema(many=True), code=200)
    @use_kwargs(resvs.ResvPrivacyGetQuerySchema(), location='query')
    def get(self, **kwargs):
        """Get reservation privacy
        ---
        description: Get reservation privacy
        parameters:
          - in: query
            schema: ResvPrivacyGetQuerySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ResvPrivacyGetRespSchema
        """
        return db.select(db.ResvPrivacy.TABLE, where=kwargs)
    
class RoomStatus(MethodView):
    schemas = {
        'RoomStatus Get Method Query Schema': rooms.RoomStatusGetQuerySchema,
        'RoomStatus Get Method Response Schema': rooms.RoomStatusGetRespSchema,
    }

    @marshal_with(rooms.RoomStatusGetRespSchema(many=True), code=200)
    @use_kwargs(rooms.RoomStatusGetQuerySchema(), location='query')
    def get(self, **kwargs):
        return db.select(db.RoomStatus.TABLE, where=kwargs)
    
class UserRoles(MethodView):
    schemas = {
        'UserRoles Get Method Query Schema': users.UserRoleGetQuerySchema,
        'UserRoles Get Method Response Schema': users.UserRoleGetRespSchema,
    }

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
    schemas = {
        'Settings Get Method Query Schema': sets.SettingGetQuerySchema,
        'Settings Get Method Response Schema': sets.SettingGetRespSchema,
    }

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
