from marshmallow import fields

from reservation_system.models.db.user import User

class Notice:
    @staticmethod
    def notice_id(**kwargs):
        return fields.Int(
            description = 'Notice ID',
            **kwargs
        )
    
    @staticmethod
    def username(**kwargs):
        value = User.username(**kwargs)
        value.metadata['description'] = 'Notice author username'
        return value
    
    @staticmethod
    def title(**kwargs):
        return fields.Str(
            description = 'Notice title',
            **kwargs
        )
    
    @staticmethod
    def content(**kwargs):
        return fields.Str(
            description = 'Notice content',
            **kwargs
        )
    
    @staticmethod
    def create_time(**kwargs):
        return fields.DateTime(
            description = 'Notice creation time',
            **kwargs
        )
    
    @staticmethod
    def update_time(**kwargs):
        return fields.DateTime(
            description = 'Notice last update time',
            **kwargs
        )
