from marshmallow import fields

class Session:
    @staticmethod
    def session_id(**kwargs):
        return fields.Int(
            description = 'Session ID',
            **kwargs
        )
    
    @staticmethod
    def name(**kwargs):
        return fields.Str(
            description = 'Session name',
            **kwargs
        )
    
    @staticmethod
    def start_time(**kwargs):
        return fields.DateTime(
            description = 'Session start time',
            **kwargs
        )
    
    @staticmethod
    def end_time(**kwargs):
        return fields.DateTime(
            description = 'Session end time',
            **kwargs
        )
    
    @staticmethod
    def is_current(**kwargs):
        return fields.Boolean(
            # description = '0 if not current session, any other value otherwise',
            # enum = [0, 1],
            description = 'Whether this session is current',
            **kwargs
        )
    
