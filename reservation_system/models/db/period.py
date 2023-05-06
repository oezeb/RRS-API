from marshmallow import fields

from reservation_system.models.util import TimeDeltaField

class Period: 
    @staticmethod
    def period_id(**kwargs):
        return fields.Int(
            description = 'Period ID',
            **kwargs
        )
    
    @staticmethod
    def name(**kwargs):
        return fields.Str(
            description = 'Period name',
            **kwargs
        )
    
    @staticmethod
    def start_time(**kwargs):
        return TimeDeltaField(
            description = 'Period start time',
            **kwargs
        )
    
    @staticmethod
    def end_time(**kwargs):
        return TimeDeltaField(
            description = 'Period end time',
            **kwargs
        )
    
