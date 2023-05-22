from marshmallow import fields

from reservation_system import db
from reservation_system.models import fields as _fields

from .util import Label, Many, Schema


class RoomSchema(Schema):
    room_id = fields.Int()
    name = fields.Str()
    type = fields.Int()
    status = _fields.room_status()
    capacity = fields.Int()
    image = _fields.Image()

class RoomTypeSchema(Label):
    type = fields.Int()

class RoomStatusSchema(Label):
    status = _fields.room_status()

class RoomTransSchema(Schema):
    room_id = fields.Int()
    name = fields.Str()


class ManyRoomStatusSchema(Many, RoomStatusSchema): pass
class ManyRoomTypeSchema(Many, RoomTypeSchema): pass
class ManyRoomSchema(Many, RoomSchema): pass
class ManyRoomTransSchema(Many, RoomTransSchema): pass

# ---------- Endpoints specific schemas ----------

# /api/rooms

class RoomsGetQuerySchema(RoomSchema):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, exclude=('image',), **kwargs)

# /api/admin/rooms

class AdminRoomsGetQuerySchema(RoomsGetQuerySchema):
    pass

class AdminRoomsPostBodySchema(RoomSchema):
    required_fields = ('name', 'type', 'capacity')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['status'].default = db.RoomStatus.AVAILABLE

class AdminRoomsPostResponseSchema(Schema):
    room_id = fields.Int(required=True)

class AdminRoomsPatchPathSchema(Schema):
    room_id = fields.Int(required=True)

class AdminRoomsDeletePathSchema(Schema):
    room_id = fields.Int(required=True)

# /api/admin/rooms/status

class AdminRoomsStatusPatchPathSchema(Schema):
    status = _fields.room_status(required=True)

# /api/admin/rooms/types

class AdminRoomsTypesPostBodySchema(RoomTypeSchema):
    required_fields = ('label',)

class AdminRoomsTypesPostResponseSchema(Schema):
    type = fields.Int(required=True)

class AdminRoomsTypesPatchPathSchema(Schema):
    type = fields.Int(required=True)

class AdminRoomsTypesDeletePathSchema(Schema):
    type = fields.Int(required=True)