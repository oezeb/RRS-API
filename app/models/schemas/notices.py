from marshmallow import fields

from .util import Many, Schema


class NoticeSchema(Schema):
    notice_id = fields.Int()
    username = fields.Str()
    title = fields.Str()
    content = fields.Str()
    create_time = fields.DateTime(dump_only=True)
    update_time = fields.DateTime(dump_only=True)

class ManyNoticeSchema(Many, NoticeSchema): pass

# ---------- Endpoints specific schemas ----------

# /api/admin/notices

class AdminNoticesPostBodySchema(NoticeSchema):
    required_fields = ('title', 'content')

class AdminNoticesPostResponseSchema(Schema):
    notice_id = fields.Int(required=True)
    username = fields.Str(required=True)

class AdminNoticesPatchPathSchema(Schema):
    notice_id = fields.Int(required=True)
    username = fields.Str(required=True)

class AdminNoticesPatchBodySchema(Schema):
    title = fields.Str()
    content = fields.Str()

class AdminNoticesDeletePathSchema(Schema):
    notice_id = fields.Int(required=True)
    username = fields.Str(required=True)

