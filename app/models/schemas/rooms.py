from marshmallow import fields, validate

from app import db
from app.models import fields as _fields

from . import Label, Many, Schema


class RoomSchema(Schema):
    room_id = fields.Int()
    name = fields.Str()
    type = fields.Int()
    status = _fields.room_status()
    capacity = fields.Int()
    # image can be None
    image = _fields.Image()

class RoomTypeSchema(Label):
    type = fields.Int()

class RoomStatusSchema(Label):
    status = _fields.room_status()

class ManyRoomStatusSchema(Many, RoomStatusSchema): pass
class ManyRoomTypeSchema(Many, RoomTypeSchema): pass
class ManyRoomSchema(Many, RoomSchema): pass

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
        self.fields['status'].load_default = db.RoomStatus.AVAILABLE

class AdminRoomsPostResponseSchema(Schema):
    room_id = fields.Int(required=True)

class AdminRoomsPatchPathSchema(Schema):
    room_id = fields.Int(required=True)

class AdminRoomsPatchBodySchema(RoomSchema):
    def __init__(self, **kwargs):
        super().__init__(exclude=('room_id',), **kwargs)

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