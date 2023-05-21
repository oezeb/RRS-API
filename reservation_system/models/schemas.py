from marshmallow import Schema as _Schema, fields

from reservation_system.models import fields as _fields

class Schema(_Schema):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if hasattr(self, 'required_fields'):
            for field in self.required_fields:
                if field in self.fields:
                    self.fields[field].required = True

class Label(Schema):
    label = fields.Str()
    description = fields.Str()

# reservations
class ReservationSchema(Schema):
    resv_id = fields.Int()
    username = fields.Str()
    room_id = fields.Int()
    session_id = fields.Str()
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
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    status = _fields.resv_status()

class ResvStatusSchema(Label):
    status = _fields.resv_status()

class ResvPrivacySchema(Label):
    privacy = _fields.resv_privacy()

# users
class UserSchema(Schema):
    username = fields.Str()
    email = fields.Str()
    name = fields.Str()
    role = _fields.user_role()
    password = fields.Str(load_only=True)

class UserRoleSchema(Label):
    role = _fields.user_role()

# periods
class PeriodSchema(Schema):
    period_id = fields.Int()
    start_time = _fields.TimeDelta()
    end_time = _fields.TimeDelta()

# notices
class NoticeSchema(Schema):
    notice_id = fields.Int()
    username = fields.Str()
    title = fields.Str()
    content = fields.Str()
    create_time = fields.DateTime(dump_only=True)
    update_time = fields.DateTime(dump_only=True)

# sessions
class SessionSchema(Schema):
    session_id = fields.Int()
    name = fields.Str()
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    is_current = fields.Bool()

# rooms
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

# languages
class LanguageSchema(Schema):
    lang_code = _fields.lang_code()
    name = fields.Str()

# settings
class SettingSchema(Schema):
    id = _fields.setting_id()
    name = fields.Str()
    value = fields.Str()
    description = fields.Str()

# --- Translations --- #

class ResvTransSchema(Schema):
    resv_id = fields.Int()
    username = fields.Str()
    title = fields.Str()
    note = fields.Str()

class UserTransSchema(Schema):
    username = fields.Str()
    name = fields.Str()

class RoomTransSchema(Schema):
    room_id = fields.Int()
    name = fields.Str()

class SessionTransSchema(Schema):
    session_id = fields.Int()
    name = fields.Str()

class NoticeTransSchema(Schema):
    notice_id = fields.Int()
    title = fields.Str()
    content = fields.Str()

class SettingTransSchema(Schema):
    id = _fields.setting_id()
    name = fields.Str()
    description = fields.Str()

# --- Many --- #
class Many:
    """Order is important. Extend this class first, then extend Schema."""
    def __init__(self, many=None, **kwargs):
        super().__init__(many=True, **kwargs)

class ManySettingSchema(Many, SettingSchema): pass
class ManyLanguageSchema(Many, LanguageSchema): pass
class ManyRoomStatusSchema(Many, RoomStatusSchema): pass
class ManyRoomTypeSchema(Many, RoomTypeSchema): pass
class ManyRoomSchema(Many, RoomSchema): pass
class ManySessionSchema(Many, SessionSchema): pass
class ManyNoticeSchema(Many, NoticeSchema): pass
class ManyPeriodSchema(Many, PeriodSchema): pass
class ManyUserRoleSchema(Many, UserRoleSchema): pass
class ManyUserSchema(Many, UserSchema): pass
class ManyResvPrivacySchema(Many, ResvPrivacySchema): pass
class ManyResvStatusSchema(Many, ResvStatusSchema): pass
class ManyReservationSchema(Many, ReservationSchema): pass

class ManyResvTransSchema(Many, ResvTransSchema): pass
class ManyUserTransSchema(Many, UserTransSchema): pass
class ManyRoomTransSchema(Many, RoomTransSchema): pass
class ManySessionTransSchema(Many, SessionTransSchema): pass
class ManyNoticeTransSchema(Many, NoticeTransSchema): pass
class ManySettingTransSchema(Many, SettingTransSchema): pass