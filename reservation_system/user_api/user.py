from flask import current_app
from mysql.connector import Error
from werkzeug.security import check_password_hash, generate_password_hash

from reservation_system import db
from reservation_system.util import abort


def get_user(username):
    res = db.select(db.User.TABLE, username=username)
    if not res:
        abort(404, message='User not found')
    return res[0]

def update_user(username, **kwargs):
    """Can only update password and email.
    Updating password requires `password` and `new_password` in `kwargs`.
    """
    if 'password' in kwargs and 'new_password' in kwargs:
        user  = get_user(username)
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

    return {}, 204
