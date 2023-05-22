from marshmallow import fields

from reservation_system import db
from reservation_system.models import fields as _fields

from .util import Label, Many, Schema


class UserSchema(Schema):
    username = fields.Str()
    email = fields.Str()
    name = fields.Str()
    role = _fields.user_role()
    password = fields.Str(load_only=True)

class UserRoleSchema(Label):
    role = _fields.user_role()

class UserTransSchema(Schema):
    username = fields.Str()
    name = fields.Str()

class ManyUserRoleSchema(Many, UserRoleSchema): pass
class ManyUserSchema(Many, UserSchema): pass
class ManyUserTransSchema(Many, UserTransSchema): pass

# ---------- Endpoints specific schemas ----------

# /api/users

class UsersGetQuerySchema(Schema):
    username = fields.Str()
    name = fields.Str()

class UsersGetResponseSchema(Many, UsersGetQuerySchema):
    pass

# /api/user

class UserPatchBodySchema(UserSchema):
    new_password = fields.Str()
    def __init__(self, **kwargs):
        super().__init__(only=('email', 'password', 'new_password'), **kwargs)

# /api/admin/users

class AdminUsersGetQuerySchema(Schema):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, exclude=('password',), **kwargs)

class AdminUsersPostBodySchema(UserSchema):
    required_fields = ('username', 'name', 'password')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['role'].default = db.UserRole.GUEST

class AdminUsersPostResponseSchema(Schema):
    username = fields.Str(required=True)

class AdminUsersPatchPathSchema(Schema):
    username = fields.Str(required=True)

# /api/admin/users/roles

class AdminUsersRolesPatchPathSchema(Schema):
    role = _fields.user_role(required=True)

