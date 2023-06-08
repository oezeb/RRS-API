from .db import *
from .schema import *


def init_app(app):
    app.teardown_appcontext(close_cnx)
    app.cli.add_command(init_db_command)