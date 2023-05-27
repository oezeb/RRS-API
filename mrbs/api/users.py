from flask import Blueprint
from webargs.flaskparser import use_kwargs

from mrbs import db
from mrbs.models import schemas
from mrbs.util import marshal_with

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

@bp.route('/<string:lang_code>')
@use_kwargs(schemas.UserTransGetQuerySchema, location='query')
@use_kwargs(schemas.UserTransGetPathSchema, location='path')
@marshal_with(schemas.ManyUserTransSchema, code=200)
def get_trans(**kwargs):
    """Get user translations
    ---
    get:
      summary: Get user translations
      description: Get user translations
      tags:
        - Public
      parameters:
        - in: path
          schema: UserTransGetPathSchema
        - in: query
          schema: UserTransGetQuerySchema
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: ManyUserTransSchema
    """
    return db.select(db.UserTrans.TABLE, **kwargs)

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

@bp.route('/roles/<string:lang_code>')
@use_kwargs(schemas.UserRoleTransGetQuerySchema, location='query')
@use_kwargs(schemas.UserRoleTransGetPathSchema, location='path')
@marshal_with(schemas.ManyUserRoleTransSchema, code=200)
def get_role_trans(**kwargs):
    """Get user role translations
    ---
    get:
      summary: Get user role translations
      description: Get user role translations
      tags:
        - Public
      parameters:
        - in: path
          schema: UserRoleTransGetPathSchema
        - in: query
          schema: UserRoleTransGetQuerySchema
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: ManyUserRoleTransSchema
    """
    return db.select(db.UserRoleTrans.TABLE, **kwargs)
