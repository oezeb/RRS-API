from flask import Blueprint
from webargs.flaskparser import use_kwargs

from mrbs import db
from mrbs.models import schemas
from mrbs.util import marshal_with

bp = Blueprint('api_languages', __name__, url_prefix='/api/languages')

@bp.route('/')
@use_kwargs(schemas.LanguageSchema, location='query')
@marshal_with(schemas.ManyLanguageSchema, code=200)
def get(**kwargs):
    """Get languages
    ---
    get:
      summary: Get languages
      description: Get languages
      tags:
        - Public
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

