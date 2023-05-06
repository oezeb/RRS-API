from marshmallow import Schema

from reservation_system.models.db.language import Language

class LangGetRespSchema(Schema):
    lang_code = Language.lang_code()
    name = Language.name()

class LangGetQuerySchema(LangGetRespSchema):
    pass