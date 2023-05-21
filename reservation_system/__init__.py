import os

from flask import Flask
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

from reservation_system import models, db, api, auth, user_api, admin_api, util

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

    spec = APISpec(
        title='Reservation System',
        version='1.0.0',
        openapi_version='3.0.0',
        info=dict(title='Reservation System', version='1.0.0'),
        plugins=[FlaskPlugin(), MarshmallowPlugin()]
    )
    
    db.init_app(app)
    api.init_api(app, spec)
    auth.init_auth(app, spec)
    user_api.init_api(app, spec)
    admin_api.init_api(app, spec)

    # save docs in instance folder
    import json
    with open(os.path.join(app.instance_path, 'docs.json'), 'w') as f:
        json.dump(spec.to_dict(), f)

    # serve docs
    from flask import send_from_directory
    @app.route('/api/docs.json')
    def docs():
        return send_from_directory(app.instance_path, 'docs.json')

    return app

__all__ = ['create_app', 'models', 'db', 'api', 'auth', 'user_api', 'admin_api', 'util']
