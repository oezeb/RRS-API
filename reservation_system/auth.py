import logging
import jwt
from datetime import datetime, timedelta
import base64

from flask import current_app, g, request, Response
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

from mysql.connector import Error, errorcode

from flask_apispec import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs

from reservation_system import db
from reservation_system.util import abort

def init_auth(app, docs):
    for path, view in (
        (   'login', Login   ),
        ('register', Register),
        (  'logout', Logout  ),
    ):
        app.add_url_rule(f'/api/{path}', view_func=view.as_view(path))
        docs.register(view, endpoint=path)

class Login(MethodResource):
    @doc(description='Login using Basic Auth', tags=['Auth'], 
        components={
            'securitySchemes': {
                'basicAuth': {
                    'type': 'http',
                    'scheme': 'basic'
                }
            }
        },
        security=[{'basicAuth': []}]
    )
    @marshal_with(None, code=200, description='Success')
    @marshal_with(None, code=401, description='Invalid username or password')
    def post(self):
        # headers: {'Authorization': 'Basic ' + btoa(${username}:${password})}
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            abort(401, message='Authorization header is missing')
        auth_token = auth_header.split(' ')[1]
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
    
class Logout(MethodResource):
    @doc(description='Logout', tags=['Auth'])
    @marshal_with(None, code=200, description='Success')
    def post(self):
        resp = Response()
        resp.set_cookie('access_token', '', expires=0)
        return resp
    
class Register(MethodResource):
    @doc(description='Register a new user', tags=['Auth'])
    @marshal_with(None, code=201, description='Success')
    @marshal_with(None, code=409, description='Username already exists')
    @use_kwargs(db.User.schema(exclude=['role']))
    def post(self, **kwargs):
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

openapi_cookie_auth = {
    'components': {
        'securitySchemes': {
            'cookieAuth': {
                'type': 'apiKey',
                'in': 'cookie',
                'name': 'access_token'
            }
        }
    },
    'security': [{'cookieAuth': []}]
}
