from marshmallow import Schema, fields, validate

from reservation_system.models.db.user import User

class PostBodySchema(Schema):
    username = User.username(required=True)
    password = User.password(required=True)
    name = User.name(required=True)
    email = User.email()
    