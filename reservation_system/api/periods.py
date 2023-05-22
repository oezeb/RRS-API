from flask import Blueprint
from webargs.flaskparser import use_kwargs

from reservation_system import db
from reservation_system.models import schemas
from reservation_system.util import marshal_with

bp = Blueprint('api_periods', __name__, url_prefix='/api/periods')

@bp.route('/')
@use_kwargs(schemas.PeriodSchema, location='query')
@marshal_with(schemas.ManyPeriodSchema, code=200)
def get(**kwargs):
    """Get periods
    ---
    get:
      summary: Get periods
      description: Get periods
      tags:
        - Public
      parameters:
        - in: query
          schema: PeriodSchema
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: ManyPeriodSchema
    """
    return db.select(db.Period.TABLE, **kwargs)
