from marshmallow import fields

from .util import Many, Schema


class SessionSchema(Schema):
    session_id = fields.Integer()
    name = fields.String()
    start_time = fields.DateTime()
    end_time = fields.DateTime()
    is_current = fields.Boolean()

class SessionTransSchema(Schema):
    session_id = fields.Int()
    name = fields.Str()

class ManySessionSchema(Many, SessionSchema): pass
class ManySessionTransSchema(Many, SessionTransSchema): pass

# ---------- Endpoints specific schemas ----------

# /api/admin/sessions

class AdminSessionsPostBodySchema(SessionSchema):
    required_fields = ('name', 'start_time', 'end_time')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['is_current'].load_default = False

class AdminSessionsPostResponseSchema(Schema):
    session_id = fields.Int(required=True)

class AdminSessionsPatchPathSchema(Schema):
    session_id = fields.Int(required=True)

class AdminSessionsPatchBodySchema(Schema):
    session_id = fields.Int()
    name = fields.Str()
    is_current = fields.Boolean()

class AdminSessionsDeletePathSchema(Schema):
    session_id = fields.Int(required=True)