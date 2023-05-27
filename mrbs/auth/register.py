from flask import Blueprint
from mysql.connector import Error, errorcode
from webargs.flaskparser import use_kwargs
from werkzeug.security import generate_password_hash

from mrbs import db
from mrbs.util import abort
from mrbs.models import schemas

bp = Blueprint('api_register', __name__, url_prefix='/api/register')

    
@bp.route('/', methods=['POST'])
@use_kwargs(schemas.RegisterSchema)
def post(**data):
    """Register a new user
    parameters:
    - `username`, `password`, `name`, `email`

    `email` is optional
    ---
    post:
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
