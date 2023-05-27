from marshmallow import fields

from mrbs.models import fields as _fields

from .util import Many, Schema


class SettingSchema(Schema):
    id = _fields.setting_id()
    name = fields.Str()
    value = fields.Str()
    description = fields.Str()

class SettingTransSchema(Schema):
    id = _fields.setting_id()
    name = fields.Str()
    description = fields.Str()

class ManySettingSchema(Many, SettingSchema): pass
class ManySettingTransSchema(Many, SettingTransSchema): pass

# ---------- Endpoints specific schemas ----------

# /api/admin/settings

class AdminSettingsPatchBodySchema(SettingSchema):
    def __init__(self, **kwargs):
        super().__init__(exclude=('id',), **kwargs)

class AdminSettingsPatchPathSchema(Schema):
    id = _fields.setting_id(required=True)