import json
from functools import wraps

from flask import abort as flask_abort, Response

from marshmallow import Schema

def abort(code, message=None):
    if message is None:
        flask_abort(code)
    else:
        abort(Response(json.dumps({'message': message}), code, mimetype='application/json'))

def marshal_with(schema: Schema, code: int=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            
            if (isinstance(res, tuple)):
                res, _code = res
                if code is not None:
                    _code = code
            else:
                _code = code

            data = schema.dump(res)
            if _code is None:
                return data
            return data, _code

        return wrapper
    return decorator