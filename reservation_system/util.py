import json
from flask import abort as flask_abort, Response

def abort(code, message=None):
    if message is None:
        flask_abort(code)
    else:
        abort(Response(json.dumps({'message': message}), code, mimetype='application/json'))
