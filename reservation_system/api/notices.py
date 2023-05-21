from flask.views import MethodView
from webargs.flaskparser import use_kwargs

from reservation_system import db
from reservation_system.models import schemas
from reservation_system.util import marshal_with


class Notices(MethodView):
    @use_kwargs(schemas.NoticeSchema(), location='query')
    @marshal_with(schemas.ManyNoticeSchema(), code=200)
    def get(self, **kwargs):
        """Get notices
        ---
        summary: Get notices
        description: Get notices
        tags:
          - Public
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
        return db.select(db.Notice.TABLE, order_by=['create_time', 'update_time'], **kwargs)
