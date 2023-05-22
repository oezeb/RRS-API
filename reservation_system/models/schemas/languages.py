from marshmallow import fields

from reservation_system.models import fields as _fields

from .util import Many, Schema


class LanguageSchema(Schema):
    lang_code = _fields.lang_code()
    name = fields.Str()

class ManyLanguageSchema(Many, LanguageSchema): pass

# ---------- Endpoints specific schemas ----------

# /api/admin/languages

class AdminLanguagesPatchBodySchema(LanguageSchema):
    def __init__(self, *args, **kwargs):
        super().__init__(exclude=('lang_code',), *args, **kwargs)

class AdminLanguagesPatchPathSchema(Schema):
    lang_code = _fields.lang_code(required=True)