from marshmallow import fields

class RoomType:
    @staticmethod
    def type(**kwargs):
        return fields.Int(
            description = 'Room type',
            **kwargs
        )
    
    @staticmethod
    def label(**kwargs):
        return fields.Str(
            description = 'Room type label',
            **kwargs
        )
    
    @staticmethod
    def description(**kwargs):
        return fields.Str(
            description = 'Room type description',
            **kwargs
        )
    
