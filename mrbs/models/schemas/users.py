from marshmallow import fields

from mrbs import db
from mrbs.models import fields as _fields

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
    lang_code = _fields.lang_code()
    username = fields.Str()
    name = fields.Str()

class UserRoleTransSchema(Label):
    lang_code = _fields.lang_code()
    role = _fields.user_role()

class ManyUserRoleSchema(Many, UserRoleSchema): pass
class ManyUserSchema(Many, UserSchema): pass
class ManyUserTransSchema(Many, UserTransSchema): pass
class ManyUserRoleTransSchema(Many, UserRoleTransSchema): pass

# ---------- Endpoints specific schemas ----------

# /api/users

class UsersGetQuerySchema(Schema):
    username = fields.Str()
    name = fields.Str()

class UsersGetResponseSchema(Many, UsersGetQuerySchema):
    pass

# /api/users/<string:lang_code>

class UserTransGetPathSchema(Schema):
    lang_code = _fields.lang_code(required=True)

class UserTransGetQuerySchema(Schema):
    username = fields.Str()
    name = fields.Str()

# /api/users/roles/<string:lang_code>

class UserRoleTransGetPathSchema(Schema):
    lang_code = _fields.lang_code(required=True)

class UserRoleTransGetQuerySchema(Label):
    role = _fields.user_role()

# /api/user

class UserPatchBodySchema(UserSchema):
    new_password = fields.Str()
    def __init__(self, **kwargs):
        super().__init__(only=('email', 'password', 'new_password'), **kwargs)

# /api/admin/users

class AdminUsersGetQuerySchema(UserSchema):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, exclude=('password',), **kwargs)

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
