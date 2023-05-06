from marshmallow import Schema

from reservation_system.models.db.period import Period

class PeriodGetRespSchema(Schema):
    period_id = Period.period_id()
    name = Period.name()
    start_time = Period.start_time()
    end_time = Period.end_time()

class PeriodGetQuerySchema(PeriodGetRespSchema):
    pass