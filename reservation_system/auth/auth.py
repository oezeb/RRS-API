from base64 import b64decode
import inspect
import logging
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import Response, current_app, g, request
from mysql.connector import Error, errorcode
from webargs.flaskparser import use_kwargs
from werkzeug.security import check_password_hash, generate_password_hash

from reservation_system import db
from reservation_system.util import abort


def login(Authorization):
    """`Authorization` format: `Basic <base64(username:password)>`"""
    token = Authorization.split(' ')[1]
    username, password = b64decode(token).decode().split(':')
    
    cnx = db.get_cnx()
    cursor = cnx.cursor(dictionary=True)

    cursor.execute(f"""
        SELECT password, role
        FROM {db.User.TABLE}
        WHERE username = '{username}'
    """)
    user = cursor.fetchone()
    print(user)

    if not user or not check_password_hash(user['password'], password):
        abort(401, message='Invalid username or password')

    max_age = timedelta(days=1)
    payload = {
        'exp': datetime.utcnow() + max_age,
        'iat': datetime.utcnow(),
        'sub': {
            'username': username,
            'role': user['role']
        }
    }
    key = current_app.config['SECRET_KEY']
    token = jwt.encode(payload, key, algorithm='HS256')
    # Send cookie response
    resp = Response()
    resp.set_cookie(
        'access_token', token, max_age, 
        # secure=True, 
        httponly=True, samesite='Strict'
    )
    return resp

def logout():
    resp = Response()
    resp.set_cookie('access_token', '', expires=0)
    return resp

def register(**data):
    """parameters:
        - `username`, `password`, `name`, `email`

        `email` is optional
    """
    data['role'] = db.UserRole.GUEST
    data['password'] = generate_password_hash(data['password'])

    try:
        db.insert(db.User.TABLE, data)
    except Error as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            abort(409, message='Username already exists')
        else:
            abort(500, message='Database error')

    return { 'username': data['username'], 'role': data['role'] }, 201

def auth_required(role: int=None):
    """Decorator for endpoints that require authentication.
    If authentication is successful:
        - Flask global `g` will have a `sub` attribute containing the user's username and role.
        - If the decorated function has a `username` or `role` parameter, it will be passed to the function.
    
    e.g.
    ```python
    from flask import g

    @auth_required(role=0)
    def foo(username):
        print(username, g.sub['username'], g.sub['role'])
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = request.cookies.get('access_token')
            if not token:
                abort(401, message='Token is missing')
            try:
                payload = jwt.decode(
                    token, 
                    current_app.config['SECRET_KEY'], 
                    algorithms=['HS256']
                )
            except jwt.ExpiredSignatureError:
                abort(401, message='Token is expired')
            except jwt.InvalidTokenError:
                abort(401, message='Token is invalid')
            except Exception as e:
                logging.error(e)
                abort(500, message='Internal server error')

            sub = payload['sub']
            if role is not None and sub['role'] < role:
                abort(403, message='Access denied')
            g.sub = sub

            params = inspect.signature(func).parameters
            if 'username' in params:
                kwargs['username'] = sub['username']
            if 'role' in params:
                kwargs['role'] = sub['role']

            return func(*args, **kwargs)
        return wrapper
    return decorator
