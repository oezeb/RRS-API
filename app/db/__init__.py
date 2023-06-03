from app.db.db import *
from app.db.schema import *


def init_app(app):
    app.teardown_appcontext(close_cnx)
    app.cli.add_command(init_db_command)