
from flask import Blueprint
from webargs.flaskparser import use_kwargs

from app import db
from app.auth import auth_required
from app.models import schemas
from app.util import marshal_with

bp = Blueprint('api_admin_settings', __name__, url_prefix='/api/admin/settings')

@bp.route('/')
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.SettingSchema, location='query')
@marshal_with(schemas.ManySettingSchema, code=200)
def get(**kwargs):
    """Get settings
    ---
    get:
      summary: Get settings
      description: Get settings
      tags:
        - Admin
        - Admin Settings
      security:
        - cookieAuth: []
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

@bp.route('/<int:id>', methods=['PATCH'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminSettingsPatchBodySchema)
@use_kwargs(schemas.AdminSettingsPatchPathSchema, location='path')
def patch(id, **kwargs):
    """Update setting
    ---
    patch:
      summary: Update setting
      description: Update setting
      tags:
        - Admin
        - Admin Settings
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminSettingsPatchPathSchema
      requestBody:
        content:
          application/json:
            schema: AdminSettingsPatchBodySchema
      responses:
        204:
          description: Success(No Content)
    """
    if kwargs: db.update(db.Setting.TABLE, data=kwargs, id=id)
    return '', 204
