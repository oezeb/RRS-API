from flask.views import MethodView
from webargs.flaskparser import use_kwargs

from reservation_system import db
from reservation_system.models import schemas
from reservation_system.util import marshal_with


class Settings(MethodView):
    @use_kwargs(schemas.SettingSchema(), location='query')
    @marshal_with(schemas.ManySettingSchema(), code=200)
    def get(self, **kwargs):
        """Get settings
        ---
        summary: Get settings
        description: Get settings
        tags:
          - Public
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
