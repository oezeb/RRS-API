import logging
import jwt

from flask import make_response, current_app, redirect
from flask_restful import Resource, request, abort
from werkzeug.security import check_password_hash, generate_password_hash

from mysql.connector import Error, errorcode

from reservation_system import db

def init_auth(api):
    api.add_resource(                 Auth, '/auth'                 )
    api.add_resource(                Login, '/auth/login'           )
    api.add_resource(             Register, '/auth/register'        )

class Register(Resource):
    def post(self):
        user = dict(request.json)
        user['password'] = generate_password_hash(user['password'])
        user['role'] = 0
        try:
            return db.insert(db.USERS, [user]), 201
        except Error as err:
            logging.warning(str(err))
            if err.errno == errorcode.ER_DUP_ENTRY:
                return f"Username {user['username']} already exists", 409 # conflict
            else:
                return "Registration failed. Please try again later", 500

class Login(Resource):
    def post(self):
        if 'username' not in request.json:
            return redirect('/auth', code=307)
        user = db.select(db.USERS, {'username': request.json['username']})[0]
        if not check_password_hash(user['password'], request.json['password']):
            abort(401)

        response = make_response()
        response.set_cookie(
            "user", 
            jwt.encode(
                {"username": request.json['username']}, 
                current_app.config['SECRET_KEY'], 
                algorithm="HS256"
            ),
        )
        return response

class Auth(Resource):
    def post(self):
        return self.auth()

    @staticmethod
    def auth():
        user = jwt.decode(
            request.cookies.get("user"), 
            current_app.config['SECRET_KEY'], 
            algorithms=["HS256"]
        )
        return db.select(db.USERS, {"username": user["username"]})[0]
