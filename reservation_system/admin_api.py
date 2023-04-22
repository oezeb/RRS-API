from datetime import datetime, timedelta
import dateutil.parser

from flask import g, request, Blueprint
from flask.views import MethodView
from functools import wraps
from werkzeug.security import generate_password_hash

from reservation_system import db, api
from reservation_system.auth import auth_required
from reservation_system.util import abort

def init_api(app):
    for path, view in (
        (    'admin/reservations', Reservations  ),
        (           'admin/users', Users         ),
        (       'admin/languages', Languages     ),
        (     'admin/resv_status', ResvStatus    ),
        ('admin/resv_secu_levels', ResvSecuLevels),
        (           'admin/rooms', Rooms         ),
        (      'admin/room_types', RoomTypes     ),
        (     'admin/room_status', RoomStatus    ),
        (        'admin/sessions', Sessions      ),
        (         'admin/notices', Notices       ),
        (      'admin/user_roles', UserRoles     ),
        (         'admin/periods', Periods       ),
        (        'admin/settings', Settings      ),
    ):
        app.add_url_rule(f'/api/{path}', view_func=view.as_view(path))

class AdminView(MethodView):
    decorators = [auth_required(role=db.UserRole.ADMIN)]

class Post(AdminView):
    # `self.table` must be set in subclass
    def post(self):
        return db.insert(self.table, request.json), 201

class Patch(AdminView):
    # `self.table` must be set in subclass
    # `self.patch_required` must be set in subclass
    #     - it is a list of required columns for `where`
    def patch(self):
        data = request.json['data']
        where = request.json['where']
        for col in self.patch_required:
            if col not in where:
                abort(400, f'{col} is required')
        return db.update(self.table, data, where)

class Delete(AdminView):
    # `self.table` must be set in subclass
    # `self.patch_required` must be set in subclass
    #     - it is a list of required columns for `where`
    def delete(self):
        where = request.json
        for col in self.delete_required:
            if col not in where:
                abort(400, f'{col} is required')
        return db.delete(self.table, where)
    
# 
class Reservations(AdminView):
    def get(self):
        """args may contain `date` as `YYYY-MM-DD` to get whole day's reservations"""
        args = request.args.to_dict()
        return db.Reservation.get(where=args)
    
    def post(self):
        """create reservations"""
        data = request.json
        if 'username' not in data:
            data['username'] = g.sub['username']
        if 'secu_level' not in data:
            data['secu_level'] = db.SecuLevel.PUBLIC
        if 'status' not in data:
            data['status'] = db.ResvStatus.CONFIRMED
        return db.Reservation.insert(data), 201
    
    def patch(self):
        """update reservations"""
        data = request.json['data']
        where = request.json['where']
        if 'resv_id' not in where:
            abort(400, 'resv_id is required')
        if 'username' not in where:
            where['username'] = g.sub['username']
        slot_id = where.get('slot_id', None)
        return db.Reservation.update(where['resv_id'], where['username'], data, slot_id)
    
class Users(AdminView):
    def get(self):
        return db.User.get(where=request.args.to_dict())
    
    def post(self):
        data = request.json
        if 'role' not in data:
            data['role'] = db.UserRole.RESTRICTED
        data['password'] = generate_password_hash(data['password'])
        return db.insert(db.User.TABLE, [data]), 201
    
    def patch(self):
        data = request.json['data']
        where = request.json['where']
        if 'username' not in where:
            abort(400, 'username is required')
        return db.update(db.User.TABLE, data, where)


class Periods(Post, Patch, Delete, api.Periods):
    table = db.Period.TABLE
    patch_required = ['period_id']
    delete_required = ['period_id']
    
class Notices(Post, Patch, Delete, api.Notices):
    table = db.Notice.TABLE
    patch_required = ['notice_id']
    delete_required = ['notice_id']
    
class Sessions(Post, Patch, Delete, api.Sessions):
    table = db.Session.TABLE
    patch_required = ['session_id']
    delete_required = ['session_id']
    
class Rooms(Post, Patch, Delete, api.Rooms):
    table = db.Room.TABLE
    patch_required = ['room_id']
    delete_required = ['room_id']
    
class RoomTypes(Post, Patch, Delete, api.RoomTypes):
    table = db.RoomType.TABLE
    patch_required = ['type']
    delete_required = ['type']

#
class Languages(Patch, api.Languages):
    table = db.Language.TABLE
    patch_required = ['lang_code']
    
class ResvStatus(Patch, api.ResvStatus):
    table = db.ResvStatus.TABLE
    patch_required = ['status']

class ResvSecuLevels(Patch, api.ResvSecuLevels):
    table = db.SecuLevel.TABLE
    patch_required = ['secu_level']

class RoomStatus(Patch, api.RoomStatus):
    table = db.RoomStatus.TABLE
    patch_required = ['status']

class UserRoles(Patch, api.UserRoles):
    table = db.UserRole.TABLE
    patch_required = ['role']

class Settings(Patch, api.Settings):
    table = db.Setting.TABLE
    patch_required = ['id']
