from base64 import b64decode
from datetime import datetime, timedelta

import jwt
from flask import Blueprint, Response, current_app
from webargs.flaskparser import use_kwargs
from werkzeug.security import check_password_hash

from mrbs import db
from mrbs.util import abort
from mrbs.models import schemas

bp = Blueprint('api_login', __name__)

@bp.route('/api/login', methods=['POST'])
@use_kwargs(schemas.LoginSchema, location='headers')
def post(Authorization):
    """Login using Basic Auth.
    `Authorization` format: `Basic <base64(username:password)>`
    ---
    post:
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
