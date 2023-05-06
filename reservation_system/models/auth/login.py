from marshmallow import Schema, fields, validate

class PostHeaderSchema(Schema):
    Authorization = fields.String(
        required=True, 
        description='Basic Auth', 
        validate=validate.Regexp(
            '^Basic [a-zA-Z0-9+/=]+$', 
            error='Invalid Authorization header'
        )
    )