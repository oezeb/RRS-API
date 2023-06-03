from flask import Blueprint
from webargs.flaskparser import use_kwargs

from app import db
from app.models import schemas
from app.util import marshal_with

bp = Blueprint('api_rooms', __name__, url_prefix='/api/rooms')

@bp.route('/')
@use_kwargs(schemas.RoomsGetQuerySchema, location='query')
@marshal_with(schemas.ManyRoomSchema, code=200)
def get(**kwargs):
    """Get rooms
    ---
    get:
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

@bp.route('/types')
@use_kwargs(schemas.RoomTypeSchema, location='query')
@marshal_with(schemas.ManyRoomTypeSchema, code=200)
def get_types(**kwargs):
    """Get room types
    ---
    get:
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

@bp.route('/status')
@use_kwargs(schemas.RoomStatusSchema, location='query')
@marshal_with(schemas.ManyRoomStatusSchema, code=200)
def get_status(**kwargs):
    """Get room status
    ---
    get:
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
