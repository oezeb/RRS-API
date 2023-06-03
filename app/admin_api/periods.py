
from flask import Blueprint
from webargs.flaskparser import use_kwargs

from app import db
from app.auth import auth_required
from app.models import schemas
from app.util import marshal_with

bp = Blueprint('api_admin_periods', __name__, url_prefix='/api/admin/periods')

@bp.route('/')
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.PeriodSchema, location='query')
@marshal_with(schemas.ManyPeriodSchema, code=200)
def get(**kwargs):
    """Get periods
    ---
    get:
      summary: Get periods
      description: Get periods
      tags:
        - Admin
        - Admin Periods
      security:
        - cookieAuth: []
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
    return db.select(db.Period.TABLE, order_by=['start_time', 'end_time'], **kwargs)

@bp.route('/', methods=['POST'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminPeriodsPostBodySchema)
@marshal_with(schemas.AdminPeriodsPostResponseSchema, code=201)
def post(**kwargs):
    """Create period
    ---
    post:
      summary: Create period
      description: Create period
      tags:
        - Admin
        - Admin Periods
      security:
        - cookieAuth: []
      requestBody:
        content:
          application/json:
            schema: AdminPeriodsPostBodySchema
      responses:
        201:
          description: Created
          content:
            application/json:
              schema: AdminPeriodsPostResponseSchema
    """
    res = db.insert(db.Period.TABLE, data=kwargs)
    return {'period_id': res['lastrowid']}, 201

@bp.route('/<int:period_id>', methods=['PATCH'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminPeriodsPatchPathSchema, location='path')
@use_kwargs(schemas.AdminPeriodsPatchBodySchema)
def patch(period_id, **kwargs):
    """Update period
    ---
    patch:
      summary: Update period
      description: Update period
      tags:
        - Admin
        - Admin Periods
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminPeriodsPatchPathSchema
      requestBody:
        content:
          application/json:
            schema: PeriodSchema
      responses:
        204:
          description: Success(No Content)
    """
    if kwargs: db.update(db.Period.TABLE, data=kwargs, period_id=period_id)
    return '', 204

@bp.route('/<int:period_id>', methods=['DELETE'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminPeriodsDeletePathSchema, location='path')
def delete(period_id):
    """Delete period
    ---
    delete:
      summary: Delete period
      description: Delete period
      tags:
        - Admin
        - Admin Periods
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminPeriodsDeletePathSchema
      responses:
        204:
          description: Success(No Content)
    """
    db.delete(db.Period.TABLE, period_id=period_id)
    return '', 204
