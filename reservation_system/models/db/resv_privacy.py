from marshmallow import fields

from reservation_system import db

class ResvPrivacy:
    @staticmethod
    def privacy(**kwargs):
        return fields.Int(
            description = f"""Reservation privacy level.
                {db.ResvPrivacy.PUBLIC}=public, 
                {db.ResvPrivacy.ANONYMOUS}=anonymous, 
                {db.ResvPrivacy.PRIVATE}=private""",
            enum = [
                db.ResvPrivacy.PUBLIC, 
                db.ResvPrivacy.ANONYMOUS, 
                db.ResvPrivacy.PRIVATE
            ],
            **kwargs
        )
    
    @staticmethod
    def label(**kwargs):
        return fields.Str(
            description = 'Reservation privacy label',
            **kwargs
        )
    
    @staticmethod
    def description(**kwargs):
        return fields.Str(
            description = 'Reservation privacy description',
            **kwargs
        )
    
