import logging
import jwt
from datetime import datetime, timedelta

from flask import current_app, g
from flask_restful import Resource, request, abort, wraps
from werkzeug.security import check_password_hash, generate_password_hash

from mysql.connector import Error, errorcode

from reservation_system import db

def init_auth(api):
    api.add_resource(          Login, '/login'           )
    api.add_resource(       Register, '/register'        )
    api.add_resource( ChangePassword, '/change_password' )

class Login(Resource):
    def post(self):
        username = request.json['username']
        password = request.json['password']

        cnx = db.get_cnx()
        cursor = cnx.cursor(dictionary=True)

        cursor.execute(f"""
            SELECT password, role
            FROM {db.USERS}
            WHERE username = '{username}'
        """)
        user = cursor.fetchone()

        if not user or not check_password_hash(user['password'], password):
            abort(401, message='Invalid username or password')
        
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'sub': {
                'username': username,
                'role': user['role']
            }
        }
        token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
        return {'token': token}
    
class Register(Resource):
    def post(self):
        """
        Register a new user.
        Data should include `username`, `password`, `role`, `name`, and `email`.
        Newly registered users `role` should be `0=restricted`.
        `email` is optional.
        """
        data = request.json
        if 'role' in data and data['role'] != 0:
            abort(403, message='New users are restricted by default')
        data['role'] = 0
        data['password'] = generate_password_hash(data['password'])

        cnx = db.get_cnx()
        cursor = cnx.cursor(dictionary=True)

        try:
            cursor.execute(f"""
                INSERT INTO {db.USERS}
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

class ChangePassword(Resource):
    def post(self):
        """
        Change password.
        User should be logged in(have a valid auth token)
        Data should include `password`, `new_password`.
        """
        sub = auth()
        username = sub['username']
        password = request.json['password']
        new_password = request.json['new_password']

        cnx = db.get_cnx()
        cursor = cnx.cursor(dictionary=True)

        cursor.execute(f"""
            SELECT password
            FROM {db.USERS}
            WHERE username = '{username}'
        """)
        user = cursor.fetchone()

        if not user or not check_password_hash(user['password'], password):
            abort(401, message='Invalid username or password')

        try:
            cursor.execute(f"""
                UPDATE {db.USERS}
                SET password = '{generate_password_hash(new_password)}'
                WHERE username = '{username}'
            """)
            cnx.commit()
        except Error as err:
            abort(500, message='Database error')
        finally:
            cursor.close()

        return {'message': 'Password changed successfully'}, 201

def auth():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        abort(401, message='Authorization header is missing')

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        abort(401, message='Token is expired')
    except jwt.InvalidTokenError:
        abort(401, message='Token is invalid')
    except Exception as e:
        logging.error(e)
        abort(500, message='Internal server error')

    return payload['sub']

def auth_required(role=0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sub = auth()
            if sub['role'] < role:
                abort(403, message='Access denied')
            g.sub = sub
            return func(*args, **kwargs)
        return wrapper
    return decorator
