from marshmallow import Schema, fields, validate

from reservation_system.models.db.reservation import Reservation
from reservation_system import db

class UserResvGetSchema(Schema):
    resv_id = Reservation.resv_id()
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

class UserResvGetQuerySchema(UserResvGetSchema):
    date = fields.Date(
        description='Date of reservations to get'
    )

class UserResvGetRespSchema(UserResvGetSchema):
    username = Reservation.username()
    
class UserResvPostBodySchema(Schema):
    room_id = Reservation.room_id(required=True)
    title = Reservation.title(required=True)
    note = Reservation.note()
    session_id = Reservation.session_id()
    start_time = Reservation.start_time(required=True)
    end_time = Reservation.end_time(required=True)

class UserResvPostRespSchema(Schema):
    resv_id = Reservation.resv_id(required=True)
    slot_id = Reservation.slot_id(required=True)

class UserResvPatchBodySchema(Schema):
    title = Reservation.title()
    note = Reservation.note()
    status = Reservation.status(validate=validate.OneOf([db.ResvStatus.CANCELLED]))

class UserResvPatchPathSchema(Schema):
    resv_id = Reservation.resv_id(required=True)

class UserResvSlotPatchBodySchema(Schema):
    status = Reservation.status(
        validate=validate.OneOf([db.ResvStatus.CANCELLED]),
        required=True
    )

class UserResvSlotPatchPathSchema(UserResvPatchPathSchema):
    slot_id = Reservation.slot_id(required=True)

class AdvancedResvPostSchema(Schema):
    class TimeSlotSchema(Schema):
        start_time = Reservation.start_time(required=True)
        end_time = Reservation.end_time(required=True)
    
    room_id = Reservation.room_id(required=True)
    title = Reservation.title(required=True)
    session_id = Reservation.session_id(required=True)
    note = Reservation.note()
    time_slots = fields.List(
        fields.Nested(TimeSlotSchema()), 
        required=True,
        validate=validate.Length(min=1)
    )
