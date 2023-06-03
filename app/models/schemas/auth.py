from marshmallow import fields, validate

from . import Schema

class LoginSchema(Schema):
    Authorization = fields.String(
        required=True, 
        metadata=dict(description='Basic Auth'),
        validate=validate.Regexp(
            '^Basic [a-zA-Z0-9+/=]+$', 
            error='Invalid Authorization header'
        )
    )

class RegisterSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    name = fields.Str(required=True)
    email = fields.Email()