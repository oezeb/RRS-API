from flask import Blueprint
from webargs.flaskparser import use_kwargs

from app import db
from app.models import schemas
from app.util import marshal_with

bp = Blueprint('api_users', __name__, url_prefix='/api/users')

@bp.route('/')
@use_kwargs(schemas.UsersGetQuerySchema, location='query')
@marshal_with(schemas.UsersGetResponseSchema, code=200)
def get(**kwargs):
    """Get users
    ---
    get:
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

@bp.route('/roles')
@use_kwargs(schemas.UserRoleSchema, location='query')
@marshal_with(schemas.ManyUserRoleSchema, code=200)
def get_roles(**kwargs):
    """Get user roles
    ---
    get:
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
