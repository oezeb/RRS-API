from flask import Blueprint
from webargs.flaskparser import use_kwargs

from app import db
from app.models import schemas
from app.util import marshal_with

bp = Blueprint('api_notices', __name__, url_prefix='/api/notices')

@bp.route('/')
@use_kwargs(schemas.NoticeSchema, location='query')
@marshal_with(schemas.ManyNoticeSchema, code=200)
def get(**kwargs):
    """Get notices
    ---
    get:
      summary: Get notices
      description: Get notices
      tags:
        - Public
      parameters:
        - in: query
          schema: NoticeSchema
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: ManyNoticeSchema
    """
    return db.select(db.Notice.TABLE, order_by=['create_time', 'update_time'], **kwargs)
