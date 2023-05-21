from mysql.connector import Error, errorcode
from werkzeug.security import generate_password_hash

from reservation_system import db
from reservation_system.util import abort


# def get_users(**kwargs):
#     return db.select(db.User.TABLE, **kwargs)

def create_user(**kwargs):
    """Create user.
    - required fields: `username`, `name`, `password`, and `role`
    - optional fields: `email`
    """
    kwargs['password'] = generate_password_hash(kwargs['password'])
    try:
        db.insert(db.User.TABLE, kwargs)
    except Error as err:
        print(err)
        if err.errno == errorcode.ER_DUP_ENTRY:
            abort(409, message='User already exists')
        else:
            abort(500, message=f'Database error: {err.msg}')
    return {'username': kwargs['username']}, 201

# def update_user(username, **kwargs):
#     """Update user.
#     - required fields: `username`
#     - optional fields: `name`, `password`, `role` and `email`
#     """
#     if 'password' in kwargs:
#         kwargs['password'] = generate_password_hash(kwargs['password'])

#     try:
#         db.update(db.User.TABLE, data=kwargs, username=username)
#     except Error as err:
#         abort(500, message=f'Database error: {err.msg}')

#     return {}, 204

# def get_user_roles(**kwargs):
#     return db.select(db.UserRole.TABLE, **kwargs)

# def update_user_role(role, **kwargs):
#     """Update user role.
#     - required fields: `role`
#     - optional fields: `label` and `description`
#     """
#     try:
#         db.update(db.UserRole.TABLE, data=kwargs, role=role)
#     except Error as err:
#         abort(500, message=f'Database error: {err.msg}')

#     return {}, 204