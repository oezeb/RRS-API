
from flask import Blueprint
from webargs.flaskparser import use_kwargs

from mrbs import db
from mrbs.auth import auth_required
from mrbs.models import schemas
from mrbs.util import marshal_with

bp = Blueprint('api_admin_rooms', __name__, url_prefix='/api/admin/rooms')

@bp.route('/')
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminRoomsGetQuerySchema, location='query')
@marshal_with(schemas.ManyRoomSchema, code=200)
def get(**kwargs):
    """Get rooms
    ---
    get:
      summary: Get rooms
      description: Get rooms
      tags:
        - Admin
        - Admin Rooms
      security:
        - cookieAuth: []
      parameters:
        - in: query
          schema: RoomSchema
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: ManyRoomSchema
    """
    return db.select(db.Room.TABLE, **kwargs)

@bp.route('/', methods=['POST'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminRoomsPostBodySchema)
@marshal_with(schemas.AdminRoomsPostResponseSchema, code=201)
def post(**kwargs):
    """Create room
    ---
    post:
      summary: Create room
      description: Create room
      tags:
        - Admin
        - Admin Rooms
      security:
        - cookieAuth: []
      requestBody:
        content:
          application/json:
            schema: AdminRoomsPostBodySchema
      responses:
        201:
          description: Created
          content:
            application/json:
              schema: AdminRoomsPostResponseSchema
    """
    # print(type(kwargs['image']))
    res = db.insert(db.Room.TABLE, data=kwargs)
    return {'room_id': res['lastrowid']}, 201

@bp.route('/<int:room_id>', methods=['PATCH'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminRoomsPatchPathSchema, location='path')
@use_kwargs(schemas.AdminRoomsPatchBodySchema)
def patch(room_id, **kwargs):
    """Update room
    ---
    patch:
      summary: Update room
      description: Update room
      tags:
        - Admin
        - Admin Rooms
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminRoomsPatchPathSchema
      requestBody:
        content:
          application/json:
            schema: RoomSchema
      responses:
        204:
          description: Success(No Content)
    """
    if kwargs: db.update(db.Room.TABLE, data=kwargs, room_id=room_id)
    return '', 204

@bp.route('/<int:room_id>', methods=['DELETE'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminRoomsDeletePathSchema, location='path')
def delete(room_id):
    """Delete room
    ---
    delete:
      summary: Delete room
      description: Delete room
      tags:
        - Admin
        - Admin Rooms
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminRoomsDeletePathSchema
      responses:
        204:
          description: Success(No Content)
    """
    db.delete(db.Room.TABLE, room_id=room_id)
    return '', 204


@bp.route('/types')
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.RoomTypeSchema, location='query')
@marshal_with(schemas.ManyRoomTypeSchema, code=200)
def get_types(**kwargs):
    """Get room types
    ---
    get:
      summary: Get room types
      description: Get room types
      tags:
        - Admin
        - Admin Rooms
      security:
        - cookieAuth: []
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

@bp.route('/types', methods=['POST'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminRoomsTypesPostBodySchema)
@marshal_with(schemas.AdminRoomsTypesPostResponseSchema, code=201)
def post_type(**kwargs):
    """Create room type
    ---
    post:
      summary: Create room type
      description: Create room type
      tags:
        - Admin
        - Admin Rooms
      security:
        - cookieAuth: []
      requestBody:
        content:
          application/json:
            schema: AdminRoomsTypesPostBodySchema
      responses:
        201:
          description: Created
          content:
            application/json:
              schema: AdminRoomsTypesPostResponseSchema
    """
    res = db.insert(db.RoomType.TABLE, data=kwargs)
    return {'type': res['lastrowid']}, 201

@bp.route('/types/<int:type>', methods=['PATCH'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminRoomsTypesPatchPathSchema, location='path')
@use_kwargs(schemas.Label)
def patch_type(type, **kwargs):
    """Update room type
    ---
    patch:
      summary: Update room type
      description: Update room type
      tags:
        - Admin
        - Admin Rooms
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminRoomsTypesPatchPathSchema
      requestBody:
        content:
          application/json:
            schema: Label
      responses:
        204:
          description: Success(No Content)
    """
    if kwargs: db.update(db.RoomType.TABLE, data=kwargs, type=type)
    return '', 204

@bp.route('/types/<int:type>', methods=['DELETE'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminRoomsTypesDeletePathSchema, location='path')
def delete_type(type):
    """Delete room type
    ---
    delete:
      summary: Delete room type
      description: Delete room type
      tags:
        - Admin
        - Admin Rooms
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminRoomsTypesDeletePathSchema
      responses:
        204:
          description: Success(No Content)
    """
    db.delete(db.RoomType.TABLE, type=type)
    return '', 204
    
@bp.route('/status')
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.RoomStatusSchema, location='query')
@marshal_with(schemas.ManyRoomStatusSchema, code=200)
def get_status(**kwargs):
    """Get room status
    ---
    get:
      summary: Get room status
      description: Get room status
      tags:
        - Admin
        - Admin Rooms
      security:
        - cookieAuth: []
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

@bp.route('/status/<int:status>', methods=['PATCH'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminRoomsStatusPatchPathSchema, location='path')
@use_kwargs(schemas.Label)
def patch_status(status, **kwargs):
    """Update room status
    ---
    patch:
      summary: Update room status
      description: Update room status
      tags:
        - Admin
        - Admin Rooms
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminRoomsStatusPatchPathSchema
      requestBody:
        content:
          application/json:
            schema: Label
      responses:
        204:
          description: Success(No Content)
    """
    if kwargs: db.update(db.RoomStatus.TABLE, data=kwargs, status=status)
    return '', 204
