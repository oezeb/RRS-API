from flask import request
from flask_apispec import MethodResource
from flask_apispec import marshal_with, doc

from reservation_system import db

def init_api(app, docs):
    for path, view in (
        ('reservations'              , Reservations  ),
        ('reservations/<string:date>', Reservations  ),
        ('reservations/status'       , ResvStatus    ),
        ('reservations/privacy'      , ResvPrivacy   ),
        ('users'                     , Users         ),
        ('users/roles'               , UserRoles     ),
        ('languages'                 , Languages     ),
        ('rooms'                     , Rooms         ),
        ('rooms/types'               , RoomTypes     ),
        ('rooms/status'              , RoomStatus    ),
        ('sessions'                  , Sessions      ),
        ('notices'                   , Notices       ),
        ('periods'                   , Periods       ),
        ('settings'                  , Settings      ),
    ):
        app.add_url_rule(f'/api/{path}', 
            view_func=view.as_view(path))
        docs.register(view, endpoint=path)

class Reservations(MethodResource):
    @marshal_with(
            db.Reservation.schema(many=True), 
            code=200, description='Success'
    )
    @doc(description='Get reservations',
         params={
        'date': {
            'in': 'path', 
            'type': 'string', 
            'format': 'date', 
            'description': 'Date of reservations to get'
        },
        **db.Reservation.args()}
    )
    def get(self, date: str = None):
        args = request.args
        if date: args['DATE(start_time)'] = 'DATE(%s)' % date
        res = db.select(db.Reservation.TABLE, where=args, 
                        order_by=['start_time', 'end_time'])
        # check privacy
        for r in res:
            if r['privacy'] == db.ResvPrivacy.ANONYMOUS:
                r.pop('username'); r.pop('resv_id')
            if r['privacy'] == db.ResvPrivacy.PRIVATE:
                r = {'time_slots': r['time_slots']}
        return res

class Users(MethodResource):
    @marshal_with(db.User.schema(many=True, 
                    only=['username', 'name']), 
                    code=200, description='Success')
    @doc(description='Get users', 
         params=db.User.args(exclude=['password']))
    def get(self):
        return db.select(db.User.TABLE, where=request.args)

class Periods(MethodResource):
    @marshal_with(db.Period.schema(many=True), 
                  code=200, description='Success')
    @doc(description='Get periods', 
         params=db.Period.args())
    def get(self):
        return db.select(db.Period.TABLE, where=request.args)

class Notices(MethodResource):
    @marshal_with(db.Notice.schema(many=True), 
                  code=200, description='Success')
    @doc(description='Get notices',
         params=db.Notice.args()
    )
    def get(self):
        return db.select(db.Notice.TABLE, where=request.args, 
                         order_by=['create_time', 'update_time'])

class Sessions(MethodResource):
    @marshal_with(db.Session.schema(many=True), 
                  code=200, description='Success')
    @doc(description='Get sessions',
         params=db.Session.args()
    )
    def get(self):
        return db.select(db.Session.TABLE, where=request.args, 
                         order_by=['start_time', 'end_time'])

class Rooms(MethodResource):
    @marshal_with(db.Room.schema(many=True), 
                  code=200, description='Success')
    @doc(description='Get rooms',
         params=db.Room.args()
    )
    def get(self):
        return db.select(db.Room.TABLE, where=request.args)

class RoomTypes(MethodResource): 
    @marshal_with(db.RoomType.schema(many=True), 
                  code=200, description='Success')
    @doc(description='Get room types',
         params=db.RoomType.args()
    )
    def get(self):
        return db.RoomType.get(where=request.args)

class Languages(MethodResource):
    @marshal_with(db.Language.schema(many=True), 
                  code=200, description='Success')
    @doc(description='Get languages',
         params=db.Language.args()
    )
    def get(self):
        return db.select(db.Language.TABLE, where=request.args)
    
class ResvStatus(MethodResource): 
    @marshal_with(db.ResvStatus.schema(many=True), 
                  code=200, description='Success')
    @doc(description='Get reservation status',
         params=db.ResvStatus.args()
    )
    def get(self):
        return db.select(db.ResvStatus.TABLE, where=request.args)
    
class ResvPrivacy(MethodResource): 
    @marshal_with(db.ResvPrivacy.schema(many=True), 
                  code=200, description='Success')
    @doc(description='Get reservation privacy settings',
         params=db.ResvPrivacy.args()
    )
    def get(self):
        return db.select(db.ResvPrivacy.TABLE, where=request.args)
    
class RoomStatus(MethodResource): 
    @marshal_with(db.RoomStatus.schema(many=True), 
                  code=200, description='Success')
    @doc(description='Get room status',
         params=db.RoomStatus.args()
    )
    def get(self):
        return db.select(db.RoomStatus.TABLE, where=request.args)
    
class UserRoles(MethodResource):
    @marshal_with(db.UserRole.schema(many=True), 
                  code=200, description='Success')
    @doc(description='Get user roles',
         params=db.UserRole.args()
    )
    def get(self):
        return db.select(db.UserRole.TABLE, where=request.args)
    
class Settings(MethodResource):
    @marshal_with(db.Setting.schema(many=True), 
                  code=200, description='Success')
    @doc(description='Get settings',
         params=db.Setting.args()
    )
    def get(self):
        return db.select(db.Setting.TABLE, where=request.args)
