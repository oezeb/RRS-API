from flask.views import MethodView
from marshmallow import Schema, fields, validate
from webargs.flaskparser import use_kwargs

from reservation_system.auth import login, logout, register

class Login(MethodView):
    class LoginSchema(Schema):
        Authorization = fields.String(
            required=True, 
            metadata=dict(description='Basic Auth'),
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
