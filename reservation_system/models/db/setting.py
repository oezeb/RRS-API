from marshmallow import fields

from reservation_system import db

class Setting: 
    @staticmethod
    def id(**kwargs):
        return fields.Int(
            description = f"""Setting ID. 
                {db.Setting.TIME_WINDOW}=time window, 
                {db.Setting.TIME_LIMIT}=time limit, 
                {db.Setting.MAX_DAILY}=max daily""",
            enum = [
                db.Setting.TIME_WINDOW, 
                db.Setting.TIME_LIMIT, 
                db.Setting.MAX_DAILY
            ],
            **kwargs
        )
    
    @staticmethod
    def name(**kwargs):
        return fields.Str(
            description = 'Setting name',
            **kwargs
        )
    
    @staticmethod
    def value(**kwargs):
        return fields.Str(
            description = 'Setting value',
            **kwargs
        )
    
    @staticmethod
    def description(**kwargs):
        return fields.Str(
            description = 'Setting description',
            **kwargs
        )
