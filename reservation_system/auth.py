import logging
import jwt
from datetime import datetime, timedelta
import base64

from flask import current_app, g, request, Response
from functools import wraps
from webargs.flaskparser import use_kwargs
from werkzeug.security import check_password_hash, generate_password_hash

from mysql.connector import Error, errorcode

from reservation_system import db
from reservation_system.util import abort
from reservation_system.api import MethodView, register_view
from reservation_system.models.auth import login
from reservation_system.models.auth import register

def init_auth(app, spec):
    spec.components.security_scheme('basicAuth', {
        'type': 'http',
        'scheme': 'basic'
        })
    spec.components.security_scheme('cookieAuth', {
        'type': 'apiKey',
        'in': 'cookie',
        'name': 'access_token'
        })
    
    for path, view in (
        (   'login', Login   ),
        ('register', Register),
        (  'logout', Logout  ),
    ):
        register_view(app, spec, path, view)

class Login(MethodView):
    schemas = {
        'login.post.headers': login.PostHeaderSchema
    }

    @use_kwargs(login.PostHeaderSchema, location='headers')
    def post(self, Authorization):
        """Login using Basic Auth.
        ---
        description: Login using Basic Auth. Returns a cookie containing a JWT access token.
        tags:
          - Auth
        security:
          - basicAuth: []
        requestBody:
          content:
            application/json:
              schema: PostHeaderSchema
        responses:
          200:
            description: OK
          401:
            description: Invalid username or password
        """
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
    
class Logout(MethodView):
    def post(self):
        """Logout
        ---
        description: Logout. Clears the JWT access token cookie.
        tags:
          - Auth
        responses:
          200:
            description: OK
        """
        resp = Response()
        resp.set_cookie('access_token', '', expires=0)
        return resp

class Register(MethodView):
    schemas = {
        'register.post.body': register.PostBodySchema
    }

    @use_kwargs(register.PostBodySchema())
    def post(self, **kwargs):
        """Register a new user
        ---
        description: Register a new user
        tags:
          - Auth
        requestBody:
          content:
            application/json:
              schema: PostBodySchema
        responses:
          201:
            description: Created
          409:
            description: Username already exists
        """
        kwargs['role'] = db.UserRole.GUEST
        kwargs['password'] = generate_password_hash(kwargs['password'])

        try:
            db.insert(db.User.TABLE, [kwargs])
        except Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                abort(409, message='Username already exists')
            else:
                abort(500, message='Database error')
    
        return Response(status=201)

def auth_required(role: int=None):
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
            return func(*args, **kwargs)
        return wrapper
    return decorator
