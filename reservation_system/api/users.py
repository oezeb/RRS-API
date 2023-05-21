from flask.views import MethodView
from marshmallow import Schema, fields
from webargs.flaskparser import use_kwargs

from reservation_system import db
from reservation_system.models import schemas
from reservation_system.util import marshal_with


class Users(MethodView):
    class UsersGetQuerySchema(Schema):
        username = fields.Str()
        name = fields.Str()
    
    class UsersGetResponseSchema(schemas.Many, UsersGetQuerySchema):
        pass
            
    @use_kwargs(UsersGetQuerySchema(), location='query')
    @marshal_with(UsersGetResponseSchema(), code=200)
    def get(self, **kwargs):
        """Get users
        ---
        summary: Get users
        description: Get users
        tags:
          - Public
        parameters:
          - in: query
            schema: UsersGetQuerySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: UsersGetResponseSchema
        """
        return db.select(db.User.TABLE, **kwargs)

class UserRoles(MethodView):
    @use_kwargs(schemas.UserRoleSchema(), location='query')
    @marshal_with(schemas.ManyUserRoleSchema(), code=200)
    def get(self, **kwargs):
        """Get user roles
        ---
        summary: Get user roles
        description: Get user roles
        tags:
          - Public
        parameters:
          - in: query
            schema: UserRoleSchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ManyUserRoleSchema
        """
        return db.select(db.UserRole.TABLE, **kwargs)
