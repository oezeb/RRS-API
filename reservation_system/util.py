import json
from datetime import timedelta
from functools import wraps

from flask import Response
from flask import abort as flask_abort
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
                
            if not isinstance(schema, Schema):
                schema = schema()
            data = schema.dump(res)
            if _code is None:
                return data
            return data, _code

        return wrapper
    return decorator

def register_blueprint(app, spec, module):
    app.register_blueprint(module.bp)
    with app.test_request_context():
        for name in dir(module):
            if name.startswith(('get', 'post', 'patch', 'delete')):
                spec.path(view=getattr(module, name))

def strptimedelta(time_str: str):
    """Convert `hh:mm:ss` or `hh:mm` format string to timedelta object."""
    time_str = time_str.split(':')
    h, m = time_str[:2]
    s = time_str[2] if len(time_str) > 2 else 0
    return timedelta(hours=int(h), minutes=int(m), seconds=int(s))

def strftimedelta(time_delta: timedelta):
    """Convert timedelta object to `HH:MM:SS` format string."""
    seconds = time_delta.total_seconds()
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return "%02d:%02d:%02d" % (h, m, s)
