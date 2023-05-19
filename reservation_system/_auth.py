import base64
import logging
import inspect
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import Response, current_app, g, request
from flask.views import MethodView
from marshmallow import Schema, fields, validate
from mysql.connector import Error, errorcode
from webargs.flaskparser import use_kwargs
from werkzeug.security import check_password_hash, generate_password_hash

from reservation_system import db
from reservation_system.api import register_view
from reservation_system.util import abort


def init_auth(app, spec):
    # register security schemes
    for name, scheme in (
        ('basicAuth',  {'type': 'http', 'scheme': 'basic'}),
        ('cookieAuth', {'type': 'apiKey', 'in': 'cookie', 'name': 'access_token'}),
    ): spec.components.security_scheme(name, scheme)
    
    # register views
    for path, view in (
        (   'login', Login   ),
        ('register', Register),
        (  'logout', Logout  ),
    ): register_view(app, spec, path, view)


def login(Authorization):
    """`Authorization` format: `Basic <base64(username:password)>`"""
    auth_token = Authorization.split(' ')[1]
    username, password = base64.b64decode(auth_token).decode('utf-8').split(':')

    cnx = db.get_cnx()
    cursor = cnx.cursor(dictionary=True)

    cursor.execute(f"""
        SELECT password, role
        FROM {db.User.TABLE}
        WHERE username = '{username}'
    """)
    user = cursor.fetchone()

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
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    # Send cookie response
    resp = Response()
    resp.set_cookie('access_token', token, 
                    max_age=max_age.total_seconds(),
                    httponly=True,
                    # secure=True, 
                    samesite='Strict'
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
                payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
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

# Views
class Login(MethodView):
    class LoginSchema(Schema):
        Authorization = fields.String(
            required=True, 
            description='Basic Auth', 
            validate=validate.Regexp(
                '^Basic [a-zA-Z0-9+/=]+$', 
                error='Invalid Authorization header'
            )
        )
    
    @use_kwargs(LoginSchema, location='headers')
    def post(self, Authorization):
        """Login using Basic Auth.
        ---
        summary: Login
        description: Login using Basic Auth. Returns a cookie containing a JWT access token.
        tags:
          - Auth
        security:
          - basicAuth: []
        parameters:
          - in: header
            name: Authorization
            schema:
              LoginSchema
        responses:
          200:
            description: OK
          401:
            description: Invalid username or password
        """
        return login(Authorization)
    
class Logout(MethodView):
    def post(self):
        """Logout
        ---
        summary: Logout
        description: Clears the JWT access token cookie.
        tags:
          - Auth
        responses:
          200:
            description: OK
        """
        return logout()

class Register(MethodView):
    class RegisterSchema(Schema):
        username = fields.Str(required=True)
        password = fields.Str(required=True)
        name = fields.Str(required=True)
        email = fields.Email()
    
    @use_kwargs(RegisterSchema())
    def post(self, **kwargs):
        """Register a new user
        ---
        summary: Register
        description: Register a new user
        tags:
          - Auth
        requestBody:
          content:
            application/json:
              schema: RegisterSchema
        responses:
          201:
            description: Created
          409:
            description: Username already exists
        """
        return register(**kwargs)
