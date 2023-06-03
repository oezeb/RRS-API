
import inspect
import logging
from functools import wraps

import jwt
from flask import current_app, g, request

from app.util import abort, register_blueprint

from . import login, logout, register


def init_auth(app, spec):
    for module in (
        login,
        register,
        logout,
    ): register_blueprint(app, spec, module)
    
    # register security schemes
    for name, scheme in (
        ('basicAuth',  {'type': 'http', 'scheme': 'basic'}),
        ('cookieAuth', {'type': 'apiKey', 'in': 'cookie', 'name': 'access_token'}),
    ): spec.components.security_scheme(name, scheme)

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
                payload = jwt.decode(
                    token, 
                    current_app.config['SECRET_KEY'], 
                    algorithms=['HS256']
                )
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

__all__ = ['init_auth', 'auth_required']
