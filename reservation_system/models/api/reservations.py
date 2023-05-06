from marshmallow import Schema, fields

from reservation_system.models.db.reservation import Reservation
from reservation_system.models.db.resv_privacy import ResvPrivacy
from reservation_system.models.db.resv_status import ResvStatus

# reservations
class ResvGetSchema(Schema):
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

class ResvGetQuerySchema(ResvGetSchema):
    date = fields.Date(
        description='Date of reservations to get',
    )

class ResvGetRespSchema(ResvGetSchema):
    pass

# privacy
class ResvPrivacyGetRespSchema(Schema):
    privacy = ResvPrivacy.privacy()
    label = ResvPrivacy.label()
    description = ResvPrivacy.description()

class ResvPrivacyGetQuerySchema(ResvPrivacyGetRespSchema):
    pass

# status
class ResvStatusGetRespSchema(Schema):
    status = ResvStatus.status()
    label = ResvStatus.label()
    description = ResvStatus.description()

class ResvStatusGetQuerySchema(ResvStatusGetRespSchema):
    pass