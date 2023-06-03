
from flask import Blueprint, g
from webargs.flaskparser import use_kwargs

from app import db
from app.auth import auth_required
from app.models import schemas
from app.util import marshal_with

bp = Blueprint('api_admin_notices', __name__, url_prefix='/api/admin/notices')

@bp.route('/')
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.NoticeSchema, location='query')
@marshal_with(schemas.ManyNoticeSchema, code=200)
def get(**kwargs):
    """Get notices
    ---
    get:
      summary: Get notices
      description: Get notices
      tags:
        - Admin
        - Admin Notices
      security:
        - cookieAuth: []
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
    return db.select(db.Notice.TABLE, order_by=['update_time', 'create_time'], **kwargs)

@bp.route('/', methods=['POST'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminNoticesPostBodySchema)
@marshal_with(schemas.AdminNoticesPostResponseSchema, code=201)
def post(**kwargs):
    """Create notice
    ---
    post:
      summary: Create notice
      description: Create notice
      tags:
        - Admin
        - Admin Notices
      security:
        - cookieAuth: []
      requestBody:
        content:
          application/json:
            schema: AdminNoticesPostBodySchema
      responses:
        201:
          description: Created
          content:
            application/json:
              schema: AdminNoticesPostResponseSchema
    """
    kwargs['username'] = g.sub['username']
    res = db.insert(db.Notice.TABLE, data=kwargs)
    return {'notice_id': res['lastrowid'], 'username': kwargs['username']}, 201

@bp.route('/<int:notice_id>/<string:username>', methods=['PATCH'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminNoticesPatchPathSchema, location='path')
@use_kwargs(schemas.AdminNoticesPatchBodySchema)
def patch(notice_id, username, **kwargs):
    """Update notice
    ---
    patch:
      summary: Update notice
      description: Update notice
      tags:
        - Admin
        - Admin Notices
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminNoticesPatchPathSchema
      requestBody:
        content:
          application/json:
            schema: AdminNoticesPatchBodySchema
      responses:
        204:
          description: Success(No Content)
    """
    if kwargs: db.update(db.Notice.TABLE, data=kwargs, notice_id=notice_id, username=username)
    return '', 204

@bp.route('/<int:notice_id>/<string:username>', methods=['DELETE'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminNoticesDeletePathSchema, location='path')
def delete(notice_id, username):
    """Delete notice
    ---
    delete:
      summary: Delete notice
      description: Delete notice
      tags:
        - Admin
        - Admin Notices
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminNoticesDeletePathSchema
      responses:
        204:
          description: Success(No Content)
    """
    db.delete(db.Notice.TABLE, notice_id=notice_id, username=username)
    return '', 204
