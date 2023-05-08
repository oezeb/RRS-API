from marshmallow import Schema, fields

from reservation_system.models.db.reservation import Reservation
from reservation_system.models.db.resv_privacy import ResvPrivacy
from reservation_system.models.db.resv_status import ResvStatus

# reservations
class ResvSchema(Schema):
    resv_id = Reservation.resv_id()
    username = Reservation.username()
    room_id = Reservation.room_id()
    session_id = Reservation.session_id()
    privacy = Reservation.privacy()
    title = Reservation.title()
    note = Reservation.note()
    create_time = Reservation.create_time()
    update_time = Reservation.update_time()
    slot_id = Reservation.slot_id()
    status = Reservation.status()
    start_time = Reservation.start_time()
    end_time = Reservation.end_time()

class RoomResvQuerySchema(ResvSchema):
    date = fields.Date(description='Date of reservations to get')

    def __init__(self, *args, **kwargs):
        super().__init__(exclude=['room_id'], *args, **kwargs)

class RoomResvPathSchema(Schema):
    room_id = Reservation.room_id()

# privacy
class ResvPrivacySchema(Schema):
    privacy = ResvPrivacy.privacy()
    label = ResvPrivacy.label()
    description = ResvPrivacy.description()

# status
class ResvStatusSchema(Schema):
    status = ResvStatus.status()
    label = ResvStatus.label()
    description = ResvStatus.description()