from flask import request
from flask.views import MethodView

from reservation_system import db

def init_api(app):
    for path, view in (
        (    'reservations', Reservations  ),
        (           'users', Users         ),
        (       'languages', Languages     ),
        (     'resv_status', ResvStatus    ),
        ('resv_secu_levels', ResvSecuLevels),
        (           'rooms', Rooms         ),
        (      'room_types', RoomTypes     ),
        (     'room_status', RoomStatus    ),
        (        'sessions', Sessions      ),
        (         'notices', Notices       ),
        (      'user_roles', UserRoles     ),
        (         'periods', Periods       ),
        (        'settings', Settings      ),
    ):
        app.add_url_rule(f'/api/{path}', view_func=view.as_view(path))

class Reservations(MethodView):
    def get(self):
        """args may contain `date` as `YYYY-MM-DD` to get whole day's reservations"""
        args = request.args.to_dict()
        return db.Reservation.get(where=args)

class Periods(MethodView):
    def get(self):
        # `timedelta` is not JSON serializable
        return db.Period.get(where=request.args.to_dict())

class Notices(MethodView):
    def get(self):
        # sort by `create_time`, `update_time`
        return db.Notice.get(where=request.args.to_dict())

class Sessions(MethodView):
    def get(self):
        # `timedelta` is not JSON serializable
        return db.Session.get(where=request.args.to_dict())

class Rooms(MethodView):
    def get(self):
        # convert `image` to base64
        return db.Room.get(where=request.args.to_dict())
        
class Users(MethodView):
    def get(self):
        # avoid exposing sensitive data like `password`
        args = request.args.to_dict()
        db.User.get(where=args)
        return db.select(db.User.TABLE, where=args, columns=('username', 'name'))

class SimpleGetView(MethodView):
    def get(self):
        args = request.args.to_dict()
        return db.select(self.TABLE, where=args)

class      Languages(SimpleGetView): TABLE = db.  Language.TABLE
class     ResvStatus(SimpleGetView): TABLE = db.ResvStatus.TABLE
class ResvSecuLevels(SimpleGetView): TABLE = db. SecuLevel.TABLE
class      RoomTypes(SimpleGetView): TABLE = db.  RoomType.TABLE
class     RoomStatus(SimpleGetView): TABLE = db.RoomStatus.TABLE
class      UserRoles(SimpleGetView): TABLE = db.  UserRole.TABLE
class       Settings(SimpleGetView): TABLE = db.   Setting.TABLE
