from flask import Blueprint
from webargs.flaskparser import use_kwargs

from mrbs import db
from mrbs.models import schemas
from mrbs.util import marshal_with

bp = Blueprint('api_sessions', __name__, url_prefix='/api/sessions')

@bp.route('/')
@use_kwargs(schemas.SessionSchema, location='query')
@marshal_with(schemas.ManySessionSchema, code=200)
def get(**kwargs):
    """Get sessions
    ---
    get:
      summary: Get sessions
      description: Get sessions
      tags:
        - Public
      parameters:
        - in: query
          schema: SessionSchema
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: ManySessionSchema
    """
    return db.select(db.Session.TABLE, **kwargs)   
