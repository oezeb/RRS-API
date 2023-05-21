from flask.views import MethodView
from webargs.flaskparser import use_kwargs

from reservation_system import db
from reservation_system.models import schemas
from reservation_system.util import marshal_with


class Rooms(MethodView):
    class RoomsGetQuerySchema(schemas.RoomSchema):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, exclude=('image',), **kwargs)

    @use_kwargs(RoomsGetQuerySchema(), location='query')
    @marshal_with(schemas.ManyRoomSchema(), code=200)
    def get(self, **kwargs):
        """Get rooms
        ---
        summary: Get rooms
        description: Get rooms
        tags:
          - Public
        parameters:
          - in: query
            schema: RoomsGetQuerySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ManyRoomSchema
        """
        return db.select(db.Room.TABLE, **kwargs)
       
class RoomTypes(MethodView):
    @use_kwargs(schemas.RoomTypeSchema(), location='query')
    @marshal_with(schemas.ManyRoomTypeSchema(), code=200)
    def get(self, **kwargs):
        """Get room types
        ---
        summary: Get room types
        description: Get room types
        tags:
          - Public
        parameters:
          - in: query
            schema: RoomTypeSchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ManyRoomTypeSchema
        """
        return db.select(db.RoomType.TABLE, **kwargs)

class RoomStatus(MethodView):
    @use_kwargs(schemas.RoomStatusSchema(), location='query')
    @marshal_with(schemas.ManyRoomStatusSchema(), code=200)
    def get(self, **kwargs):
        """Get room status
        ---
        summary: Get room status
        description: Get room status
        tags:
          - Public
        parameters:
          - in: query
            schema: RoomStatusSchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: ManyRoomStatusSchema
        """
        return db.select(db.RoomStatus.TABLE, **kwargs)
