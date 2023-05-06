from marshmallow import fields

from reservation_system.models.db.user_role import UserRole

class User: 
    @staticmethod
    def username(**kwargs):
        if 'description' not in kwargs:
            kwargs['description'] = 'User username'
        return fields.Str(**kwargs)
    
    @staticmethod
    def name(**kwargs):
        if 'description' not in kwargs:
            kwargs['description'] = 'User full name'
        return fields.Str(**kwargs)
    
    @staticmethod
    def password(**kwargs):
        if 'description' not in kwargs:
            kwargs['description'] = 'User password'
        return fields.Str(**kwargs)
    
    @staticmethod
    def email(**kwargs):
        if 'description' not in kwargs:
            kwargs['description'] = 'User email'
        return fields.Email(**kwargs)
    
    @staticmethod
    def role(**kwargs):
        return UserRole.role(**kwargs)
    
