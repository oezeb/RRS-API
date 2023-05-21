from flask.views import MethodView
from marshmallow import Schema, fields, validate
from webargs.flaskparser import use_kwargs

from reservation_system import db
from reservation_system.models import fields as _fields
from reservation_system.models import schemas
from reservation_system.user_api import reservation as resv
from reservation_system.user_api import user
from reservation_system.auth import auth_required
from reservation_system.util import marshal_with

class User(MethodView):
    class UserPatchBodySchema(schemas.UserSchema):
        new_password = fields.Str()
        def __init__(self, *args, **kwargs):
            super().__init__(only=('email', 'password', 'new_password'), *args, **kwargs)

    @auth_required(role=db.UserRole.RESTRICTED)
    @marshal_with(schemas.UserSchema(), code=200)
    def get(self, username):
        """Get user info.
        ---
        summary: Get info
        description: Get user info.
        tags:
          - User
        security:
          - cookieAuth: []
        responses:
          200:
            description: Success(OK)
            content:
              application/json:
                schema: UserSchema
          404:
            description: User not found
        """
        return user.get_user(username)

    @auth_required(role=db.UserRole.RESTRICTED)
    @use_kwargs(UserPatchBodySchema())
    def patch(self, username, **kwargs):
        """Update user info.
        ---
        summary: Update info
        description: Update user info.
        tags:
          - User
        security:
          - cookieAuth: []
        requestBody:
          content:
            application/json:
              schema: UserPatchBodySchema
        responses:
          204:
            description: Success(No Content)
          401:
            description: Invalid password
          404:
            description: User not found
        """
        return user.update_user(username, **kwargs)

class GetPostReservation(MethodView):
    class UserGetReservationQuerySchema(schemas.ReservationSchema):
        start_date = fields.Date()
        end_date = fields.Date()
        create_date = fields.Date()
        update_date = fields.Date()
    
    class UserResvPostBodySchema(schemas.ReservationSchema):
        required_fields = ('room_id', 'title', 'start_time', 'end_time')
        def __init__(self, **kwargs):
            super().__init__(only=(
                'room_id', 'title', 'start_time', 'end_time', 'note', 'session_id'
            ), **kwargs)
    
    class UserResvPostResponseSchema(Schema):
        resv_id = fields.Int(required=True)
        slot_id = fields.Int(required=True)

    @auth_required(role=db.UserRole.RESTRICTED)
    @use_kwargs(UserGetReservationQuerySchema, location='query')
    @marshal_with(schemas.ManyReservationSchema(), code=200)
    def get(self, username, **kwargs):
        """Get user reservations.
        ---
        summary: Get reservations
        description: Get user reservations.
        tags:
          - User
        security:
          - cookieAuth: []
        parameters:
          - in: query
            schema: UserGetReservationQuerySchema
        responses:
          200:
            description: Success(OK)
            content:
              application/json:
                schema: ManyReservationSchema
        """
        return resv.get_reservations(username=username, **kwargs)
    
    @auth_required(role=db.UserRole.GUEST)
    @use_kwargs(UserResvPostBodySchema())
    @marshal_with(UserResvPostResponseSchema(), code=201)
    def post(self, username, role, **kwargs):
        """Create a new reservation.
        ---
        summary: Create reservation
        description: Create a new reservation.
        tags:
          - User
        security:
          - cookieAuth: []
        requestBody:
          content:
            application/json:
              schema: UserResvPostBodySchema
        responses:
          201:
            description: Success(Created)
            content:
              application/json:
                schema: UserResvPostResponseSchema
        """
        return resv.create_reservation(username, role, **kwargs)

class PatchReservation(MethodView):
    class ResvPatchBodySchema(Schema):
        title = fields.Str()
        note = fields.Str()
        status = _fields.resv_status()
        
    class UserResvPatchPathSchema(Schema):
        resv_id = fields.Int(required=True)

    @auth_required(role=db.UserRole.GUEST)
    @use_kwargs(ResvPatchBodySchema())
    @use_kwargs(UserResvPatchPathSchema, location='path')
    def patch(self, resv_id, username, **kwargs):
        """Update reservation info. reservation status can only be set to CANCELLED.
        ---
        summary: Update reservation info
        description: Update reservation info.
        tags:
          - User
        security:
          - cookieAuth: []
        parameters:
          - in: path
            schema: UserResvPatchPathSchema
        requestBody:
          content:
            application/json:
              schema: ResvPatchBodySchema
        responses:
          204:
            description: Success(No Content)
        """
        return resv.update_reservation(resv_id, username, **kwargs)
  
class PatchReservationSlot(MethodView):
    class UserResvSlotPatchBodySchema(Schema):
        status = _fields.resv_status(
            validate=validate.OneOf([db.ResvStatus.CANCELLED]),
            required=True
        )

    class UserResvSlotPatchPathSchema(Schema):
        resv_id = fields.Int(required=True)
        slot_id = fields.Int(required=True)

    @auth_required(role=db.UserRole.GUEST)
    @use_kwargs(UserResvSlotPatchBodySchema())
    @use_kwargs(UserResvSlotPatchPathSchema(), location='path')
    def patch(self, resv_id, slot_id, username, **kwargs):
        """Update reservation time slot info. reservation status can only be set to CANCELLED.
        ---
        summary: Update time slot info
        description: Update reservation time slot info.
        tags:
          - User
        security:
          - cookieAuth: []
        parameters:
          - in: path
            schema: UserResvSlotPatchPathSchema
        requestBody:
          content:
            application/json:
              schema: UserResvSlotPatchBodySchema
        responses:
          204:
            description: Success(No Content)
        """
        return resv.update_reservation_slot(resv_id, slot_id, username, **kwargs)

class AdvancedResv(MethodView):
    class AdvancedResvPostBodySchema(Schema):
        class TimeSlot(Schema):
            start_time = fields.DateTime(required=True)
            end_time = fields.DateTime(required=True)
        room_id = fields.Int(required=True)
        title = fields.Str(required=True)
        session_id = fields.Int(required=True)
        time_slots = fields.List(
            fields.Nested(TimeSlot),
            validate=validate.Length(min=1),
            required=True
        )
        note = fields.Str()

    class AdvancedResvPostResponseSchema(Schema):
        resv_id = fields.Int(required=True)

    @auth_required(role=db.UserRole.BASIC)
    @use_kwargs(AdvancedResvPostBodySchema())
    @marshal_with(AdvancedResvPostResponseSchema(), code=201)
    def post(self, username, role, **kwargs):
        """Create advanced reservation.
        ---
        summary: Create advanced reservation
        description: Create advanced reservation.
        tags:
          - User
        security:
          - cookieAuth: []
        requestBody:
          content:
            application/json:
              schema: AdvancedResvPostBodySchema
        responses:
          201:
            description: Success(Created)
            content:
              application/json:
                schema: AdvancedResvPostResponseSchema
        """
        return resv.create_advanced_reservation(username, role, **kwargs)
