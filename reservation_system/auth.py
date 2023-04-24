import logging
import jwt
from datetime import datetime, timedelta
import base64

from flask import current_app, g, request, Response
from flask.views import MethodView
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

from mysql.connector import Error, errorcode

from reservation_system import db
from reservation_system.util import abort

def init_auth(app):
    for path, view in (
        ('login', Login),
        ('register', Register),
        ('logout', Logout),
    ):
        app.add_url_rule(f'/api/{path}', view_func=view.as_view(path))

class Login(MethodView):
    def post(self):
        """headers: {'Authorization': 'Basic ' + btoa(${username}:${password})}"""
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
    
class Logout(MethodView):
    def post(self):
        resp = Response()
        resp.set_cookie('access_token', '', expires=0)
        return resp
    
class Register(MethodView):
    def post(self):
        """
        Register a new user.
        Data should include `username`, `password`, `role`, `name`, and `email`.
        Newly registered users `role` should be `0=restricted`.
        `email` is optional.
        """
        data = request.json
        if 'role' in data and data['role'] != 0:
            abort(403, message='New users should be restricted(role=0) by default')
        data['role'] = 0
        data['password'] = generate_password_hash(data['password'])

        cnx = db.get_cnx()
        cursor = cnx.cursor(dictionary=True)

        try:
            cursor.execute(f"""
                INSERT INTO {db.User.TABLE}
                ({', '.join(data.keys())})
                VALUES ({', '.join(['%s'] * len(data))})
            """, (*data.values(),))
            cnx.commit()
        except Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                abort(409, message='Username already exists')
            else:
                abort(500, message='Database error')
        finally:
            cursor.close()
        
        return {'message': 'User created successfully'}, 201

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
