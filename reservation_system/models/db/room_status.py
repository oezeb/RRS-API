from marshmallow import fields

from reservation_system import db

class RoomStatus:
    @staticmethod
    def status(**kwargs):
        return fields.Int(
            description = f"""Room status.
                {db.RoomStatus.UNAVAILABLE}=unavailable, 
                {db.RoomStatus.AVAILABLE}=available""",
            enum = [
                db.RoomStatus.UNAVAILABLE, 
                db.RoomStatus.AVAILABLE
            ],
            **kwargs
        )
    
    @staticmethod
    def label(**kwargs):
        return fields.Str(
            description = 'Room status label',
            **kwargs
        )
    
    @staticmethod
    def description(**kwargs):
        return fields.Str(
            description = 'Room status description',
            **kwargs
        )
    
