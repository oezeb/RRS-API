import base64

from marshmallow import fields

from mrbs import db
from mrbs.util import strftimedelta, strptimedelta


def resv_status(**kwargs):
    return fields.Int(
        metadata = dict(
            description = f"""Reservation status.
                {db.ResvStatus.PENDING}=pending, 
                {db.ResvStatus.CONFIRMED}=confirmed, 
                {db.ResvStatus.CANCELLED}=cancelled, 
                {db.ResvStatus.REJECTED}=rejected
            """,
            enum = [
                db.ResvStatus.PENDING, 
                db.ResvStatus.CONFIRMED, 
                db.ResvStatus.CANCELLED, 
                db.ResvStatus.REJECTED
            ],
        ),
        **kwargs
    )

def resv_privacy(**kwargs):
    return fields.Int(
        metadata = dict(
            description = f"""Reservation privacy level.
                {db.ResvPrivacy.PUBLIC}=public, 
                {db.ResvPrivacy.ANONYMOUS}=anonymous, 
                {db.ResvPrivacy.PRIVATE}=private
            """,
            enum = [
                db.ResvPrivacy.PUBLIC, 
                db.ResvPrivacy.ANONYMOUS, 
                db.ResvPrivacy.PRIVATE
            ],
        ),
        **kwargs
    )

def user_role(**kwargs):
    return fields.Int(
        metadata = dict(
            description = f"""User role.
                {db.UserRole.INACTIVE}=inactive, 
                {db.UserRole.RESTRICTED}=restricted, 
                {db.UserRole.GUEST}=guest, 
                {db.UserRole.BASIC}=basic, 
                {db.UserRole.ADVANCED}=advanced, 
                {db.UserRole.ADMIN}=admin
            """,
            enum = [
                db.UserRole.INACTIVE, 
                db.UserRole.RESTRICTED, 
                db.UserRole.GUEST, 
                db.UserRole.BASIC, 
                db.UserRole.ADVANCED, 
                db.UserRole.ADMIN
            ],
        ),
        **kwargs
    )


def setting_id(**kwargs):
    return fields.Int(
        metadata = dict(
            description = f"""Setting ID.
                {db.Setting.TIME_WINDOW}=time window, 
                {db.Setting.TIME_LIMIT}=time limit, 
                {db.Setting.MAX_DAILY}=max daily
            """,
            enum = [
                db.Setting.TIME_WINDOW, 
                db.Setting.TIME_LIMIT, 
                db.Setting.MAX_DAILY
            ],
        ),
        **kwargs
    )

def room_status(**kwargs):
    return fields.Int(
        metadata = dict(
            description = f"""Room status.
                {db.RoomStatus.UNAVAILABLE}=unavailable, 
                {db.RoomStatus.AVAILABLE}=available
            """,
            enum = [
                db.RoomStatus.UNAVAILABLE, 
                db.RoomStatus.AVAILABLE
            ],
        ),
        **kwargs
    )

def lang_code(**kwargs):
    return fields.Str(
        metadata=dict(
            description='Language code', 
            enum=[db.Language.EN],
        ),
        **kwargs
    )

class TimeDelta(fields.String):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.metadata['description'] = 'format hh:mm:ss'

    def _serialize(self, value, attr, obj, **kwargs):
        return None if value is None else strftimedelta(value)
    
    def _deserialize(self, value, attr, data, **kwargs):
        return None if value is None else strptimedelta(value)

class Image(fields.String):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.metadata['description'] = 'Base64 encoded image'

    def _serialize(self, value, attr, obj, **kwargs):
        return None if not value else base64.b64encode(value).decode('utf-8')

    def _deserialize(self, value, attr, data, **kwargs):
        return None if not value else base64.b64decode(value)
        