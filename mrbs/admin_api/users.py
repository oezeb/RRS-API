
from flask import Blueprint
from webargs.flaskparser import use_kwargs
from werkzeug.security import generate_password_hash

from mrbs import db
from mrbs.auth import auth_required
from mrbs.models import schemas
from mrbs.util import marshal_with

bp = Blueprint('api_admin_users', __name__, url_prefix='/api/admin/users')

@bp.route('/')
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminUsersGetQuerySchema, location='query')
@marshal_with(schemas.ManyUserSchema, code=200)
def get(**kwargs):
    """Get users
    ---
    get:
      summary: Get users
      description: Get users
      tags:
        - Admin
        - Admin Users
      security:
        - cookieAuth: []
      parameters:
        - in: query
          schema: UserSchema
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: ManyUserSchema
    """
    return db.select(db.User.TABLE, **kwargs)

@bp.route('/', methods=['POST'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminUsersPostBodySchema)
@marshal_with(schemas.AdminUsersPostResponseSchema, code=201)
def post(**kwargs):
    """Create user
    ---
    post:
      summary: Create user
      description: Create user
      tags:
        - Admin
        - Admin Users
      security:
        - cookieAuth: []
      requestBody:
        content:
          application/json:
            schema: AdminUsersPostBodySchema
      responses:
        201:
          description: Created
          content:
            application/json:
              schema: AdminUsersPostResponseSchema
    """
    kwargs['password'] = generate_password_hash(kwargs['password'])
    db.insert(db.User.TABLE, data=kwargs)
    return {'username': kwargs['username']}, 201

@bp.route('/<string:username>', methods=['PATCH'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminUsersPatchPathSchema, location='path')
@use_kwargs(schemas.UserSchema)
def patch(**kwargs):
    """Update user
    ---
    patch:
      summary: Update user
      description: Update user
      tags:
        - Admin
        - Admin Users
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminUsersPatchPathSchema
      requestBody:
        content:
          application/json:
            schema: UserSchema
      responses:
        204:
          description: Success(No Content)
    """
    if kwargs:
        username = kwargs.pop('username')
        if 'password' in kwargs:
            kwargs['password'] = generate_password_hash(kwargs['password'])
        db.update(db.User.TABLE, data=kwargs, username=username)
    return '', 204

@bp.route('/roles')
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.UserRoleSchema, location='query')
@marshal_with(schemas.ManyUserRoleSchema, code=200)
def get_roles(**kwargs):
    """Get user roles
    ---
    get:
      summary: Get user roles
      description: Get user roles
      tags:
        - Admin
        - Admin Users
      security:
        - cookieAuth: []
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

@bp.route('/roles/<string:role>', methods=['PATCH'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminUsersRolesPatchPathSchema, location='path')
@use_kwargs(schemas.Label)
def patch_roles(role, **kwargs):
    """Update user roles
    ---
    patch:
      summary: Update user roles
      description: Update user roles
      tags:
        - Admin
        - Admin Users
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminUsersRolesPatchPathSchema
      requestBody:
        content:
          application/json:
            schema: Label
      responses:
        204:
          description: Success(No Content)
    """
    if kwargs: db.update(db.UserRole.TABLE, data=kwargs, role=role)
    return '', 204