from marshmallow import fields

from app import db
from app.models import fields as _fields

from .util import Label, Many, Schema


class UserSchema(Schema):
    username = fields.Str()
    email = fields.Str()
    name = fields.Str()
    role = _fields.user_role()
    password = fields.Str(load_only=True)

class UserRoleSchema(Label):
    role = _fields.user_role()

class ManyUserRoleSchema(Many, UserRoleSchema): pass
class ManyUserSchema(Many, UserSchema): pass

# ---------- Endpoints specific schemas ----------

# /api/users

class UsersGetQuerySchema(Schema):
    username = fields.Str()
    name = fields.Str()

class UsersGetResponseSchema(Many, Schema):
    username = fields.Str()
    name = fields.Str()

# /api/user

class UserPatchBodySchema(Schema):
    email = fields.Str()
    password = fields.Str(load_only=True)
    new_password = fields.Str(load_only=True)

# /api/admin/users

class AdminUsersPostBodySchema(UserSchema):
    required_fields = ('username', 'name', 'password')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['role'].load_default = db.UserRole.GUEST

class AdminUsersPostResponseSchema(Schema):
    username = fields.Str(required=True)

class AdminUsersPatchPathSchema(Schema):
    username = fields.Str(required=True)

# /api/admin/users/roles

class AdminUsersRolesPatchPathSchema(Schema):
    role = _fields.user_role(required=True)
