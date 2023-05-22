from flask import Blueprint
from webargs.flaskparser import use_kwargs

from reservation_system import db
from reservation_system.models import schemas
from reservation_system.util import marshal_with

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
