from marshmallow import Schema

from reservation_system.models.db.user import User
from reservation_system.models.db.user_role import UserRole

# users
class UserGetRespSchema(Schema):
    username = User.username()
    name = User.name()

class UserGetQuerySchema(UserGetRespSchema):
    pass

# roles
class UserRoleGetRespSchema(Schema):
    role = UserRole.role()
    label = UserRole.label()
    description = UserRole.description()

class UserRoleGetQuerySchema(UserRoleGetRespSchema):
    pass