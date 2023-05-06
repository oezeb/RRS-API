from marshmallow import fields

from reservation_system import db

class Language: 
    @staticmethod
    def lang_code(**kwargs):
        return fields.Str(
            description='Language code',
            enum=[db.Language.EN],
            **kwargs
        )
    
    @staticmethod
    def name(**kwargs):
        return fields.Str(
            description='Language name',
            **kwargs
        )
    
