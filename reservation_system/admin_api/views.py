from flask import redirect
from flask.views import MethodView
from marshmallow import Schema, fields, validate
from webargs.flaskparser import use_kwargs

from reservation_system import db
from reservation_system.models import fields as _fields
from reservation_system.models import schemas
from reservation_system.admin_api import reservations as resv
from reservation_system.admin_api import users
from reservation_system.admin_api import settings, periods
from reservation_system.auth import auth_required
from reservation_system.util import marshal_with
from reservation_system.models import fields as _fields
from reservation_system.api import views as api_views

class AdminView(MethodView):
    decorators = [auth_required(role=db.UserRole.ADMIN)]

# ------------------------------------------------------------
# GET/POST
# ------------------------------------------------------------

# ------ Reservations ------

class GetPostReservations(AdminView):
    class AdminGetReservationQuerySchema(schemas.ReservationSchema):
        start_date = fields.Date()
        end_date = fields.Date()
        create_date = fields.Date()
        update_date = fields.Date()

    class AdminResvPostBodySchema(schemas.ReservationSchema):
        required_fields = ('room_id', 'title', 'time_slots')
        class AdminResvPostBodyTimeSlot(schemas.ResvTimeSlotSchema):
            required_fields = ('start_time', 'end_time')
        time_slots = fields.List(
            fields.Nested(AdminResvPostBodyTimeSlot),
            validate=validate.Length(min=1),
            required=True
        )
        def __init__(self, **kwargs):
            super().__init__(exclude=('start_time', 'end_time', 'status'), **kwargs)
    
    class AdninResvPostResponseSchema(Schema):
        resv_id = fields.Int(required=True)
        slot_id = fields.Int(required=True)
    
    @use_kwargs(AdminGetReservationQuerySchema(), location='query')
    @marshal_with(schemas.ManyReservationSchema(), code=200)
    def get(self, **kwargs):
        """Get reservations
        ---
        summary: Get reservations
        description: Get reservations
        tags:
          - Admin
        security:
          - cookieAuth: []
        parameters:
          - in: query
            schema: AdminGetReservationQuerySchema
        responses:
          200:
            description: Success(OK)
            content:
              application/json:
                schema: ManyReservationSchema
        """
        return resv.get_reservations(**kwargs)
    
    @use_kwargs(AdminResvPostBodySchema())
    @marshal_with(AdninResvPostResponseSchema(), code=201)
    def post(self, **kwargs):
        """Create a reservation
        ---
        summary: Create a reservation
        description: Create a reservation
        tags:
          - Admin
        security:
          - cookieAuth: []
        requestBody:
          content:
            application/json:
              schema: AdminResvPostBodySchema
        responses:
          201:
            description: Success(Created)
            content:
              application/json:
                schema: AdninResvPostResponseSchema
        """
        return resv.create_reservation(**kwargs)
    
# ------ Users ------

class GetPostUsers(AdminView):
    class AdminPostUserBodySchema(schemas.UserSchema):
        required_fields = ('username', 'password', 'role', 'name')
    
    class AdminPostUserResponseSchema(Schema):
        username = fields.Str(required=True)
    
    @use_kwargs(schemas.UserSchema(), location='query')
    @marshal_with(schemas.ManyUserSchema(), code=200)
    def get(self, **kwargs):
        """Get users
        ---
        summary: Get users
        description: Get users
        tags:
          - Admin
        security:
          - cookieAuth: []
        parameters:
          - in: query
            schema: UserSchema
        responses:
          200:
            description: Success(OK)
            content:
              application/json:
                schema: ManyUserSchema
        """
        return db.select(db.User.TABLE, **kwargs)
    
    @use_kwargs(AdminPostUserBodySchema())
    @marshal_with(AdminPostUserResponseSchema(), code=201)
    def post(self, **kwargs):
        """Create user
        ---
        summary: Create user
        description: Create user
        tags:
          - Admin
        security:
          - cookieAuth: []
        requestBody:
          content:
            application/json:
              schema: AdminPostUserBodySchema
        responses:
          201:
            description: Success(Created)
            content:
              application/json:
                schema: AdminPostUserResponseSchema
        """
        return users.create_user(**kwargs)

class GetPostPeriods(AdminView, api_views.Periods):
    class AdminPostPeriodBodySchema(schemas.PeriodSchema):
        required_fields = ('start_time', 'end_time')
      
    class AdminPostPeriodResponseSchema(Schema):
        period_id = fields.Int(required=True)
    
    def get(self):
        """Get periods
        ---
        summary: Get periods
        description: Get periods
        tags:
          - Admin
        security:
          - cookieAuth: []
        parameters:
          - in: query
            schema: PeriodSchema
        responses:
          200:
            description: Success(OK)
            content:
              application/json:
                schema: ManyPeriodSchema
        """
        return super().get()
    
    @use_kwargs(AdminPostPeriodBodySchema())
    @marshal_with(AdminPostPeriodResponseSchema(), code=201)
    def post(self, **kwargs):
        """Create period
        ---
        summary: Create period
        description: Create period
        tags:
          - Admin
        security:
          - cookieAuth: []
        requestBody:
          content:
            application/json:
              schema: AdminPostPeriodBodySchema
        responses:
          201:
            description: Success(Created)
            content:
              application/json:
                schema: AdminPostPeriodResponseSchema
        """
        return periods.create_period(**kwargs)

# ------ Reservation privacy ------ 

class GetReservationPrivacy(AdminView, api_views.ResvPrivacy):
    def get(self):
        """Get reservation privacy
        ---
        summary: Get reservation privacy
        description: Get reservation privacy
        tags:
          - Admin
        security:
          - cookieAuth: []
        parameters:
          - in: query
            schema: ResvPrivacySchema
        responses:
          200:
            description: Success(OK)
            content:
              application/json:
                schema: ManyResvPrivacySchema
        """
        return super().get()
        
# ------ Reservation status ------

class GetReservationStatus(AdminView, api_views.ResvStatus):
    def get(self):
        """Get reservation status
        ---
        summary: Get reservation status
        description: Get reservation status
        tags:
          - Admin
        security:
          - cookieAuth: []
        parameters:
          - in: query
            schema: ResvStatusSchema
        responses:
          200:
            description: Success(OK)
            content:
              application/json:
                schema: ManyResvStatusSchema
        """
        return super().get()
    
# ------ User roles ------

class GetUserRoles(AdminView, api_views.UserRoles):
    def get(self):
        """Get user roles
        ---
        summary: Get user roles
        description: Get user roles
        tags:
          - Admin
        security:
          - cookieAuth: []
        parameters:
          - in: query
            schema: UserRoleSchema
        responses:
          200:
            description: Success(OK)
            content:
              application/json:
                schema: ManyUserRoleSchema
        """
        return super().get()


# ------------------------------------------------------------
# PATCH/DELETE
# ------------------------------------------------------------

class PatchReservation(AdminView):
    class AdminPatchReservationBodySchema(Schema):
        title = fields.Str()
        note = fields.Str()
        status = _fields.resv_status()
        privacy = _fields.resv_privacy()

    class AdminPatchReservationPathSchema(Schema):
        resv_id = fields.Int(required=True)

    @use_kwargs(AdminPatchReservationBodySchema())
    @use_kwargs(AdminPatchReservationPathSchema(), location='path')
    @marshal_with(Schema(), code=204)
    def patch(self, **kwargs):
        """Update a reservation
        ---
        summary: Update a reservation
        description: Update a reservation
        tags:
          - Admin
        security:
          - cookieAuth: []
        parameters:
          - in: path
            schema: AdminPatchReservationPathSchema
        requestBody:
          content:
            application/json:
              schema: AdminPatchReservationBodySchema
        responses:
          204:
            description: Success(No Content)
        """
        return resv.update_reservation(**kwargs)

class PatchReservationSlot(AdminView):
    class AdminPatchReservationSlotBodySchema(Schema):
        status = _fields.resv_status()

    class AdminPatchReservationSlotPathSchema(Schema):
        resv_id = fields.Int(required=True)
        slot_id = fields.Int(required=True)

    @use_kwargs(AdminPatchReservationSlotBodySchema())
    @use_kwargs(AdminPatchReservationSlotPathSchema(), location='path')
    @marshal_with(Schema(), code=204)
    def patch(self, **kwargs):
        """Update a reservation slot
        ---
        summary: Update a reservation slot
        description: Update a reservation slot
        tags:
          - Admin
        security:
          - cookieAuth: []
        parameters:
          - in: path
            schema: AdminPatchReservationSlotPathSchema
        requestBody:
          content:
            application/json:
              schema: AdminPatchReservationSlotBodySchema
        responses:
          204:
            description: Success(No Content)
        """
        return resv.update_reservation_slot(**kwargs)


class PatchReservationPrivacy(AdminView):
    class AdminPatchReservationPrivacyBodySchema(schemas.ResvPrivacySchema):
        def __init__(self, **kwargs):
            super().__init__(exclude=('privacy',), **kwargs)
    
    class AdminPatchReservationPrivacyPathSchema(Schema):
        privacy = _fields.resv_privacy(required=True)
        
    @use_kwargs(AdminPatchReservationPrivacyBodySchema())
    @use_kwargs(AdminPatchReservationPrivacyPathSchema(), location='path')
    @marshal_with(Schema(), code=204)
    def patch(self, **kwargs):
        """Update reservation privacy
        ---
        summary: Update reservation privacy
        description: Update reservation privacy
        tags:
          - Admin
        security:
          - cookieAuth: []
        parameters:
          - in: path
            schema: AdminPatchReservationPrivacyPathSchema
        requestBody:
          content:
            application/json:
              schema: AdminPatchReservationPrivacyBodySchema
        responses:
          204:
            description: Success(No Content)
        """
        return resv.update_resv_privacy(**kwargs)

class PatchReservationStatus(AdminView):
    class AdminPatchReservationStatusBodySchema(schemas.ResvStatusSchema):
        def __init__(self, **kwargs):
            super().__init__(exclude=('status',), **kwargs)
    
    class AdminPatchReservationStatusPathSchema(Schema):
        status = _fields.resv_status(required=True)
    
    @use_kwargs(AdminPatchReservationStatusBodySchema())
    @use_kwargs(AdminPatchReservationStatusPathSchema(), location='path')
    @marshal_with(Schema(), code=204)
    def patch(self, **kwargs):
        """Update reservation status
        ---
        summary: Update reservation status
        description: Update reservation status
        tags:
          - Admin
        security:
          - cookieAuth: []
        parameters:
          - in: path
            schema: AdminPatchReservationStatusPathSchema
        requestBody:
          content:
            application/json:
              schema: AdminPatchReservationStatusBodySchema
        responses:
          204:
            description: Success(No Content)
        """
        return resv.update_resv_status(**kwargs)

# ------------------------------------------------------------
# Users
# ------------------------------------------------------------
    
class PatchUser(AdminView):
    class AdminPatchUserBodySchema(schemas.UserSchema):
        def __init__(self, **kwargs):
            super().__init__(exclude=('username',), **kwargs)
    
    class AdminPatchUserPathSchema(Schema):
        username = fields.Str(required=True)
    
    @use_kwargs(AdminPatchUserBodySchema())
    @use_kwargs(AdminPatchUserPathSchema(), location='path')
    @marshal_with(Schema(), code=204)
    def patch(self, **kwargs):
        """Update user
        ---
        summary: Update user
        description: Update user
        tags:
          - Admin
        security:
          - cookieAuth: []
        parameters:
          - in: path
            schema: AdminPatchUserPathSchema
        requestBody:
          content:
            application/json:
              schema: AdminPatchUserBodySchema
        responses:
          204:
            description: Success(No Content)
        """
        return users.update_user(**kwargs)
    

    
class PatchUserRole(AdminView):
    class AdminPatchUserRoleBodySchema(schemas.UserRoleSchema):
        def __init__(self, **kwargs):
            super().__init__(exclude=('role',), **kwargs)
    
    class AdminPatchUserRolePathSchema(Schema):
        role = _fields.user_role(required=True)
    
    @use_kwargs(AdminPatchUserRoleBodySchema())
    @use_kwargs(AdminPatchUserRolePathSchema(), location='path')
    @marshal_with(Schema(), code=204)
    def patch(self, **kwargs):
        """Update user role
        ---
        summary: Update user role
        description: Update user role
        tags:
          - Admin
        security:
          - cookieAuth: []
        parameters:
          - in: path
            schema: AdminPatchUserRolePathSchema
        requestBody:
          content:
            application/json:
              schema: AdminPatchUserRoleBodySchema
        responses:
          204:
            description: Success(No Content)
        """
        print(kwargs)
        return users.update_user_role(**kwargs)

# ------------------------------------------------------------
# Settings
# ------------------------------------------------------------
    
class PatchSetting(AdminView):
    class AdminPatchSettingsBodySchema(schemas.SettingSchema):
        def __init__(self, **kwargs):
            super().__init__(exclude=('id',), **kwargs)
    
    class AdminPatchSettingsPathSchema(Schema):
        id = _fields.setting_id(required=True)
    
    @use_kwargs(AdminPatchSettingsBodySchema())
    @use_kwargs(AdminPatchSettingsPathSchema(), location='path')
    @marshal_with(Schema(), code=204)
    def patch(self, **kwargs):
        """Update settings
        ---
        summary: Update settings
        description: Update settings
        tags:
          - Admin
        security:
          - cookieAuth: []
        parameters:
          - in: path
            schema: AdminPatchSettingsPathSchema
        requestBody:
          content:
            application/json:
              schema: AdminPatchSettingsBodySchema
        responses:
          204:
            description: Success(No Content)
        """
        return settings.update_setting(**kwargs)

