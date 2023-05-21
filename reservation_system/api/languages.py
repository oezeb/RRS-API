from flask.views import MethodView
from webargs.flaskparser import use_kwargs

from reservation_system import db
from reservation_system.models import schemas
from reservation_system.util import marshal_with


class Languages(MethodView):
    @use_kwargs(schemas.LanguageSchema(), location='query')
    @marshal_with(schemas.ManyLanguageSchema(), code=200)
    def get(self, **kwargs):
        """Get languages
        ---
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
