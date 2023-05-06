from marshmallow import Schema

from reservation_system.models.db.room import Room
from reservation_system.models.db.room_type import RoomType
from reservation_system.models.db.room_status import RoomStatus

# rooms
class RoomGetRespSchema(Schema):
    room_id = Room.room_id()
    name = Room.name()
    type = Room.type()
    status = Room.status()
    capacity = Room.capacity()
    image = Room.image()

class RoomGetQuerySchema(RoomGetRespSchema):
    pass

# types
class RoomTypeGetRespSchema(Schema):
    type = RoomType.type()
    label = RoomType.label()
    description = RoomType.description()

class RoomTypeGetQuerySchema(RoomTypeGetRespSchema):
    pass

# status
class RoomStatusGetRespSchema(Schema):
    status = RoomStatus.status()
    label = RoomStatus.label()
    description = RoomStatus.description()

class RoomStatusGetQuerySchema(RoomStatusGetRespSchema):
    pass