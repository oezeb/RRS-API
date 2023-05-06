from marshmallow import fields

from reservation_system import db

class ResvStatus:
    @staticmethod
    def status(**kwargs):
        return fields.Int(
            description = f"""Reservation status.
                {db.ResvStatus.PENDING}=pending, 
                {db.ResvStatus.CONFIRMED}=confirmed, 
                {db.ResvStatus.CANCELLED}=cancelled, 
                {db.ResvStatus.REJECTED}=rejected""",
            enum = [
                db.ResvStatus.PENDING, 
                db.ResvStatus.CONFIRMED, 
                db.ResvStatus.CANCELLED, 
                db.ResvStatus.REJECTED
            ],
            **kwargs
        )
    
    @staticmethod
    def label(**kwargs):
        return fields.Str(
            description = 'Reservation status label',
            **kwargs
        )
    
    @staticmethod
    def description(**kwargs):
        return fields.Str(
            description = 'Reservation status description',
            **kwargs
        )
    
