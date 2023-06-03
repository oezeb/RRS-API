from flask import Blueprint
from webargs.flaskparser import use_kwargs

from app import db
from app.models import schemas
from app.util import marshal_with

bp = Blueprint('api_reservations', __name__, url_prefix='/api/reservations')

@bp.route('/')
@use_kwargs(schemas.ReservationsGetQuerySchema, location='query')
@marshal_with(schemas.ManyReservationSchema, code=200)
def get(**kwargs):
    """Get reservations
    ---
    get:
      summary: Get reservations
      description: Get reservations
      tags:
        - Public
      parameters:
        - in: query
          schema: ReservationsGetQuerySchema
      responses:
        200:
          description: Success(OK)
          content:
            application/json:
              schema: ManyReservationSchema
    """
    for prefix in ['start', 'end', 'create', 'update']:
        date = f'{prefix}_date'
        if date in kwargs:
            time = f'{prefix}_time'
            kwargs[f'DATE({time})'] = kwargs.pop(date)

    res = db.select(
        db.Reservation.TABLE,
        order_by=['start_time', 'end_time'], 
        **kwargs
    )
    
    # check privacy
    for r in res:
        if r['privacy'] == db.ResvPrivacy.ANONYMOUS:
            r.pop('username'); r.pop('resv_id')
        if r['privacy'] == db.ResvPrivacy.PRIVATE:
            r.pop('username'); r.pop('resv_id')
            r.pop('title'); r.pop('note')
    return res

@bp.route('/status')
@use_kwargs(schemas.ResvStatusSchema, location='query')
@marshal_with(schemas.ManyResvStatusSchema, code=200)
def get_status(**kwargs):
    """Get reservation status
    ---
    get:
      summary: Get reservation status
      description: Get reservation status
      tags:
        - Public
      parameters:
        - in: query
          schema: ResvStatusSchema
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: ManyResvStatusSchema
    """
    return db.select(db.ResvStatus.TABLE, **kwargs)

@bp.route('/privacy')
@use_kwargs(schemas.ResvPrivacySchema, location='query')
@marshal_with(schemas.ManyResvPrivacySchema, code=200)
def get_privacy(**kwargs):
    """Get reservation privacy
    ---
    get:
      summary: Get reservation privacy
      description: Get reservation privacy
      tags:
        - Public
      parameters:
        - in: query
          schema: ResvPrivacySchema
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: ManyResvPrivacySchema
    """
    return db.select(db.ResvPrivacy.TABLE, **kwargs)
