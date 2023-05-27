from flask import Blueprint
from webargs.flaskparser import use_kwargs

from mrbs import db
from mrbs.models import schemas
from mrbs.util import marshal_with

bp = Blueprint('api_settings', __name__, url_prefix='/api/settings')

@bp.route('/')
@use_kwargs(schemas.SettingSchema, location='query')
@marshal_with(schemas.ManySettingSchema, code=200)
def get(**kwargs):
    """Get settings
    ---
    get:
      summary: Get settings
      description: Get settings
      tags:
        - Public
      parameters:
        - in: query
          schema: SettingSchema
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: ManySettingSchema
    """
    return db.select(db.Setting.TABLE, **kwargs)
