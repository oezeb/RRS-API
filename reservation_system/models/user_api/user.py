from marshmallow import Schema

from reservation_system.models.db.user import User

class GetRespSchema(Schema):
    username = User.username(required=True)
    name = User.name(required=True)
    email = User.email(required=True)
    role = User.role(required=True)

class PatchBodySchema(Schema):
    name = User.name()
    email = User.email()
    password = User.password()
    new_password = User.password(description='New password')
