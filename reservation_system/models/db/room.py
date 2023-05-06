from marshmallow import fields

from reservation_system.models.util import ImageField

from reservation_system.models.db.room_type import RoomType
from reservation_system.models.db.room_status import RoomStatus

class Room: 
    @staticmethod
    def room_id(**kwargs):
        return fields.Int(
            description = 'Room ID',
            **kwargs
        )
    
    @staticmethod
    def name(**kwargs):
        return fields.Str(
            description = 'Room name',
            **kwargs
        )
    
    @staticmethod
    def type(**kwargs):
        return RoomType.type(**kwargs)
    
    @staticmethod
    def status(**kwargs):
        return RoomStatus.status(**kwargs)
    
    @staticmethod
    def capacity(**kwargs):
        return fields.Int(
            description = 'Room capacity',
            **kwargs
        )
    
    @staticmethod
    def image(**kwargs):
        return ImageField(
            description = 'Room image (base64 encoded)',
            **kwargs
        )
    
