from marshmallow import Schema

from reservation_system.models.db.setting import Setting

class SettingGetRespSchema(Schema):
    id = Setting.id()
    name = Setting.name()
    value = Setting.value()
    description = Setting.description()

class SettingGetQuerySchema(SettingGetRespSchema):
    pass