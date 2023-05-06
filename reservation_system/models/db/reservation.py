from marshmallow import fields

from reservation_system.models.db.user import User
from reservation_system.models.db.room import Room
from reservation_system.models.db.session import Session
from reservation_system.models.db.resv_privacy import ResvPrivacy
from reservation_system.models.db.resv_status import ResvStatus

class Reservation:
    RESV_TABLE = "reservations"
    TS_TABLE = "time_slots"
    TABLE = f"{RESV_TABLE} NATURAL JOIN {TS_TABLE}"

    # fields
    @staticmethod
    def resv_id(**kwargs):
        return fields.Int(
            description = 'Reservation ID',
            **kwargs
        )
    
    @staticmethod
    def username(**kwargs):
        value = User.username(**kwargs)
        value.metadata['description'] = 'Reservation owner username'
        return value
    
    @staticmethod
    def room_id(**kwargs):
        value = Room.room_id(**kwargs)
        value.metadata['description'] = 'Reserved room ID'
        return value
    
    @staticmethod
    def session_id(**kwargs):
        value = Session.session_id(**kwargs)
        value.metadata['description'] = 'Reservation session ID'
        return value
    
    @staticmethod
    def privacy(**kwargs):
        return ResvPrivacy.privacy(**kwargs)
    
    @staticmethod
    def title(**kwargs):
        return fields.Str(
            description = 'Reservation title',
            **kwargs
        )
    
    @staticmethod
    def note(**kwargs):
        return fields.Str(
            description = 'Reservation note',
            **kwargs
        )
    
    @staticmethod
    def create_time(**kwargs):
        return fields.DateTime(
            description = 'Reservation creation time',
            **kwargs
        )
    
    @staticmethod
    def update_time(**kwargs):
        return fields.DateTime(
            description = 'Reservation update time',
            **kwargs
        )
    
    @staticmethod
    def slot_id(**kwargs):
        return fields.Int(
            description = 'Reservation time slot ID',
            **kwargs
        )
    
    @staticmethod
    def start_time(**kwargs):
        return fields.DateTime(
            description = 'Reservation start time',
            **kwargs
        )
    
    @staticmethod
    def end_time(**kwargs):
        return fields.DateTime(
            description = 'Reservation end time',
            **kwargs
        )
    
    @staticmethod
    def status(**kwargs):
        return ResvStatus.status(**kwargs)
