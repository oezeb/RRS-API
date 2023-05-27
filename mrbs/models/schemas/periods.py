from marshmallow import fields

from mrbs.models import fields as _fields

from .util import Many, Schema


class PeriodSchema(Schema):
    period_id = fields.Int()
    start_time = _fields.TimeDelta()
    end_time = _fields.TimeDelta()

class ManyPeriodSchema(Many, PeriodSchema): pass

# ---------- Endpoints specific schemas ----------

# /api/admin/periods

class AdminPeriodsPostBodySchema(PeriodSchema):
    required_fields = ('start_time', 'end_time')

class AdminPeriodsPostResponseSchema(Schema):
    period_id = fields.Int(required=True)

class AdminPeriodsPatchPathSchema(Schema):
    period_id = fields.Int(required=True)

class AdminPeriodsPatchBodySchema(PeriodSchema):
    def __init__(self, **kwargs):
        super().__init__(exclude=('period_id',), **kwargs)

class AdminPeriodsDeletePathSchema(Schema):
    period_id = fields.Int(required=True)