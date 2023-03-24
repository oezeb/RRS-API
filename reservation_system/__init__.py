import os
from flask import Flask
from flask_restful import Api

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    if test_config is not None:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    flask_api = Api(app)

    # ensure the instance folder exists
    try: os.makedirs(app.instance_path)
    except OSError: pass

    from . import db, api, auth
    db.init_app(app)
    api.init_api(flask_api)
    auth.init_auth(flask_api)
    
    return app
