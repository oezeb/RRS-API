from marshmallow import fields

from reservation_system import db

class UserRole: 
    @staticmethod
    def role(**kwargs):
        return fields.Int(
            description = f"""User role. 
                {db.UserRole.INACTIVE}=inactive, 
                {db.UserRole.RESTRICTED}=restricted, 
                {db.UserRole.GUEST}=guest, 
                {db.UserRole.BASIC}=basic, 
                {db.UserRole.ADVANCED}=advanced, 
                {db.UserRole.ADMIN}=admin""",
            enum = [
                db.UserRole.INACTIVE, 
                db.UserRole.RESTRICTED, 
                db.UserRole.GUEST, 
                db.UserRole.BASIC, 
                db.UserRole.ADVANCED, 
                db.UserRole.ADMIN
            ],
            **kwargs
        )
    
    @staticmethod
    def label(**kwargs):
        return fields.Str(
            description = 'User role label',
            **kwargs
        )
    
    @staticmethod
    def description(**kwargs):
        return fields.Str(
            description = 'User role description',
            **kwargs
        )
    
