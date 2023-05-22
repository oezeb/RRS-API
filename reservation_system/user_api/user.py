from flask import Blueprint, current_app
from mysql.connector import Error
from webargs.flaskparser import use_kwargs
from werkzeug.security import check_password_hash, generate_password_hash

from reservation_system import db
from reservation_system.auth import auth_required
from reservation_system.models import schemas
from reservation_system.util import abort, marshal_with

bp = Blueprint('api_user', __name__, url_prefix='/api/user')

@bp.route('/')
@auth_required(role=db.UserRole.RESTRICTED)
@marshal_with(schemas.UserSchema, code=200)
def get(username):
    """Get user info.
    ---
    get:
      summary: Get info
      description: Get user info.
      tags:
        - User
      security:
        - cookieAuth: []
      responses:
        200:
          description: Success(OK)
          content:
            application/json:
              schema: UserSchema
        404:
          description: User not found
    """
    res = db.select(db.User.TABLE, username=username)
    if not res:
        abort(404, message='User not found')
    return res[0]

@bp.route('/', methods=['PATCH'])
@auth_required(role=db.UserRole.RESTRICTED)
@use_kwargs(schemas.UserPatchBodySchema)
def patch(username, **kwargs):
    """Update user info.
    Can only update password and email.
    Updating password requires `password` and `new_password` in `kwargs`.
    ---
    patch:
      summary: Update info
      description: Update user info.
      tags:
        - User
      security:
        - cookieAuth: []
      requestBody:
        content:
          application/json:
            schema: UserPatchBodySchema
      responses:
        204:
          description: Success(No Content)
        401:
          description: Invalid password
        404:
          description: User not found
    """
    if 'password' in kwargs and 'new_password' in kwargs:
        # get user from db
        res = db.select(db.User.TABLE, username=username)
        if not res:
            abort(404, message='User not found')
        user = res[0]

        # check password
        if not check_password_hash(user['password'], kwargs['password']):
            abort(401, message='Invalid password')
        kwargs['password'] = generate_password_hash(kwargs['new_password'])
        kwargs.pop('new_password')
    elif 'password' in kwargs or 'new_password' in kwargs:
        abort(400, message='Missing new password or password')

    if len(kwargs) > 0:
        try:
            db.update(db.User.TABLE, data=kwargs, username=username)
        except Error as err:
            current_app.logger.error(f"Error occurred while updating user: {err}")
            abort(500, message='Failed to update user')

    return '', 204
