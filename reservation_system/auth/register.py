from flask.views import MethodView
from marshmallow import Schema, fields
from mysql.connector import Error, errorcode
from webargs.flaskparser import use_kwargs
from werkzeug.security import generate_password_hash

from reservation_system import db
from reservation_system.util import abort


class Register(MethodView):
    class RegisterSchema(Schema):
        username = fields.Str(required=True)
        password = fields.Str(required=True)
        name = fields.Str(required=True)
        email = fields.Email()
    
    @use_kwargs(RegisterSchema())
    def post(self, **data):
        """Register a new user
        parameters:
        - `username`, `password`, `name`, `email`

        `email` is optional
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
