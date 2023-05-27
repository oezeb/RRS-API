
from flask import Blueprint
from webargs.flaskparser import use_kwargs

from mrbs import db
from mrbs.auth import auth_required
from mrbs.models import schemas
from mrbs.util import marshal_with

bp = Blueprint('api_admin_languages', __name__, url_prefix='/api/admin/languages')

@bp.route('/')
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.LanguageSchema, location='query')
@marshal_with(schemas.ManyLanguageSchema, code=200)
def get(**kwargs):
    """Get languages
    ---
    get:
      summary: Get languages
      description: Get languages
      tags:
        - Admin
        - Admin Languages
      security:
        - cookieAuth: []
      parameters:
        - in: query
          schema: LanguageSchema
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: ManyLanguageSchema
    """
    return db.select(db.Language.TABLE, **kwargs)

@bp.route('/<string:lang_code>', methods=['PATCH'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminLanguagesPatchPathSchema, location='path')
@use_kwargs(schemas.AdminLanguagesPatchBodySchema)
def patch(lang_code, **kwargs):
    """Update language
    ---
    patch:
      summary: Update language
      description: Update language
      tags:
        - Admin
        - Admin Languages
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminLanguagesPatchPathSchema
      requestBody:
        content:
          application/json:
            schema: AdminLanguagesPatchBodySchema
      responses:
        204:
          description: Success(No Content)
    """
    if kwargs: db.update(db.Language.TABLE, data=kwargs, lang_code=lang_code)
    return '', 204
