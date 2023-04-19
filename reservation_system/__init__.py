import os
from flask import Flask

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    if test_config is not None:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try: os.makedirs(app.instance_path)
    except OSError: pass

    from . import db, auth, api, user_api, admin_api
    db.init_app(app)
    auth.init_auth(app)
    api.init_api(app)
    user_api.init_api(app)
    admin_api.init_api(app)
    
    return app
