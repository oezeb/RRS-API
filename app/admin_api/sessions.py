
from flask import Blueprint
from webargs.flaskparser import use_kwargs

from app import db
from app.auth import auth_required
from app.models import schemas
from app.util import marshal_with

bp = Blueprint('api_admin_sessions', __name__, url_prefix='/api/admin/sessions')

@bp.route('/')
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.SessionSchema, location='query')
@marshal_with(schemas.ManySessionSchema, code=200)
def get(**kwargs):
    """Get sessions
    ---
    get:
      summary: Get sessions
      description: Get sessions
      tags:
        - Admin
        - Admin Sessions
      security:
        - cookieAuth: []
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

@bp.route('/', methods=['POST'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminSessionsPostBodySchema)
@marshal_with(schemas.AdminSessionsPostResponseSchema, code=201)
def post(**kwargs):
    """Create session
    ---
    post:
      summary: Create session
      description: Create session
      tags:
        - Admin
        - Admin Sessions
      security:
        - cookieAuth: []
      requestBody:
        content:
          application/json:
            schema: AdminSessionsPostBodySchema
      responses:
        201:
          description: Created
          content:
            application/json:
              schema: AdminSessionsPostResponseSchema
    """
    res = db.insert(db.Session.TABLE, data=kwargs)
    return {'session_id': res['lastrowid']}, 201

@bp.route('/<int:session_id>', methods=['PATCH'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminSessionsPatchPathSchema, location='path')
@use_kwargs(schemas.AdminSessionsPatchBodySchema)
def patch(session_id, **kwargs):
    """Update session
    ---
    patch:
      summary: Update session
      description: Update session
      tags:
        - Admin
        - Admin Sessions
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminSessionsPatchPathSchema
      requestBody:
        content:
          application/json:
            schema: SessionSchema
      responses:
        204:
          description: Success(No Content)
    """
    db.update(db.Session.TABLE, data=kwargs, session_id=session_id)
    return '', 204

@bp.route('/<int:session_id>', methods=['DELETE'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminSessionsDeletePathSchema, location='path')
def delete(session_id):
    """Delete session
    ---
    delete:
      summary: Delete session
      description: Delete session
      tags:
        - Admin
        - Admin Sessions
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminSessionsDeletePathSchema
      responses:
        204:
          description: Success(No Content)
    """
    db.delete(db.Session.TABLE, session_id=session_id)
    return '', 204
