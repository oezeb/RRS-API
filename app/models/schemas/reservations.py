from marshmallow import fields, validate

from app import db
from app.models import fields as _fields

from . import Label, Many, Schema


class ReservationSchema(Schema):
    resv_id = fields.Int()
    username = fields.Str()
    room_id = fields.Int()
    session_id = fields.Int()
    privacy = _fields.resv_privacy()
    title = fields.Str()
    note = fields.Str()
    create_time = fields.DateTime(dump_only=True)
    update_time = fields.DateTime(dump_only=True)
    slot_id = fields.Int()
    status = _fields.resv_status()
    start_time = fields.DateTime()
    end_time = fields.DateTime()

class ResvTimeSlotSchema(Schema):
    slot_id = fields.Int()
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    status = _fields.resv_status()

class ResvStatusSchema(Label):
    status = _fields.resv_status()

class ResvPrivacySchema(Label):
    privacy = _fields.resv_privacy()

class ManyResvPrivacySchema(Many, ResvPrivacySchema): pass
class ManyResvStatusSchema(Many, ResvStatusSchema): pass
class ManyReservationSchema(Many, ReservationSchema): pass

# ---------- Endpoints specific schemas ----------

# /api/reservations

class ReservationsGetQuerySchema(ReservationSchema):
    start_date = fields.Date()
    end_date = fields.Date()
    create_date = fields.Date()
    update_date = fields.Date()

# /api/user/reservation

class UserReservationGetQuerySchema(ReservationsGetQuerySchema):
    pass

class UserReservationPostBodySchema(ReservationSchema):
    required_fields = ('room_id', 'title', 'start_time', 'end_time')
    def __init__(self, **kwargs):
        super().__init__(only=(
            'room_id', 'title', 'start_time', 'end_time', 'note', 'session_id'
        ), **kwargs)

class UserReservationPostResponseSchema(Schema):
    resv_id = fields.Int(required=True)
    slot_id = fields.Int(required=True)

class UserReservationPatchBodySchema(Schema):
    title = fields.Str()
    note = fields.Str()
    status = _fields.resv_status()
    
class UserReservationPatchPathSchema(Schema):
    resv_id = fields.Int(required=True)

class UserReservationSlotPatchBodySchema(Schema):
    status = _fields.resv_status(
        validate=validate.OneOf([db.ResvStatus.CANCELLED]),
        required=True
    )

class UserReservationSlotPatchPathSchema(Schema):
    resv_id = fields.Int(required=True)
    slot_id = fields.Int(required=True)

class UserReservationAdvancedPostBodySchema(Schema):
    class TimeSlot(Schema):
        start_time = fields.DateTime(required=True)
        end_time = fields.DateTime(required=True)
    room_id = fields.Int(required=True)
    title = fields.Str(required=True)
    session_id = fields.Int(required=True)
    time_slots = fields.List(
        fields.Nested(TimeSlot),
        validate=validate.Length(min=1),
        required=True
    )
    note = fields.Str()

class UserReservationAdvancedPostResponseSchema(Schema):
    resv_id = fields.Int(required=True)

# /api/admin/reservations

class AdminReservationGetQuerySchema(ReservationsGetQuerySchema):
    pass

class AdminReservationsPostBodySchema(ReservationSchema):
    required_fields = ('room_id', 'title', 'time_slots')
    
    class AdminResvPostBodyTimeSlot(ResvTimeSlotSchema):
        required_fields = ('start_time', 'end_time')
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.fields['status'].load_default = db.ResvStatus.PENDING
    
    time_slots = fields.List(
        fields.Nested(AdminResvPostBodyTimeSlot),
        validate=validate.Length(min=1),
        required=True
    )
    
    def __init__(self, **kwargs):
        super().__init__(exclude=('slot_id', 'start_time', 'end_time', 'status'), **kwargs)
        self.fields['privacy'].load_default = db.ResvPrivacy.PUBLIC

class AdminReservationsPostResponseSchema(Schema):
    resv_id = fields.Integer(required=True)
    username = fields.Str(required=True)

class AdminReservationsPatchBodySchema(Schema):
    title = fields.Str()
    note = fields.Str()
    status = _fields.resv_status()
    privacy = _fields.resv_privacy()

class AdminReservationsPatchPathSchema(Schema):
    resv_id = fields.Int(required=True)

class AdminReservationsSlotPatchPathSchema(Schema):
    resv_id = fields.Int(required=True)
    slot_id = fields.Int(required=True)

# /api/admin/reservations/privacy

class AdminReservationsPrivacyPatchPathSchema(Schema):
    privacy = _fields.resv_privacy(required=True)

# /api/admin/reservations/status

class AdminReservationsStatusPatchPathSchema(Schema):
    status = _fields.resv_status(required=True)