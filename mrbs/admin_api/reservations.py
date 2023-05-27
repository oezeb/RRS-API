
from flask import Blueprint
from webargs.flaskparser import use_kwargs

from mrbs import db
from mrbs.auth import auth_required
from mrbs.models import schemas
from mrbs.util import marshal_with

bp = Blueprint('api_admin_reservations', __name__, url_prefix='/api/admin/reservations')

@bp.route('/')
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminReservationGetQuerySchema, location='query')
@marshal_with(schemas.ManyReservationSchema, code=200)
def get(**kwargs):
    """Get reservations
    ---
    get:
      summary: Get reservations
      description: Get reservations
      tags:
        - Admin
        - Admin Reservations
      security:
        - cookieAuth: []
      parameters:
        - in: query
          schema: AdminReservationGetQuerySchema
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: ManyReservationSchema
    """
    return db.select(db.Reservation.TABLE, order_by=['start_time', 'end_time'], **kwargs)

@bp.route('/', methods=['POST'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminReservationsPostBodySchema)
@marshal_with(schemas.AdminReservationsPostResponseSchema, code=201)
def post(**kwargs):
    """Create reservation
    ---
    post:
      summary: Create reservation
      description: Create reservation
      tags:
        - Admin
        - Admin Reservations
      security:
        - cookieAuth: []
      requestBody:
        content:
          application/json:
            schema: AdminReservationsPostBodySchema
      responses:
        201:
          description: Created
          content:
            application/json:
              schema: AdminReservationsPostResponseSchema
    """
    res = db.insert(db.Reservation.TABLE, data=kwargs)
    return {'resv_id': res['lastrowid']}, 201

@bp.route('/<int:resv_id>', methods=['PATCH'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminReservationsPatchPathSchema, location='path')
@use_kwargs(schemas.AdminReservationsPatchBodySchema)
def patch(resv_id, **kwargs):
    """Update reservation
    ---
    patch:
      summary: Update reservation
      description: Update reservation
      tags:
        - Admin
        - Admin Reservations
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminReservationsPatchPathSchema
      requestBody:
        content:
          application/json:
            schema: AdminReservationsPatchBodySchema
      responses:
        204:
          description: Success(No Content)
    """
    username = kwargs.pop('username')
    db.update(db.Reservation.TABLE, data=kwargs, resv_id=resv_id, username=username)
    return '', 204

@bp.route('/<int:resv_id>/<int:slot_id>', methods=['PATCH'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminReservationsSlotPatchPathSchema, location='path')
@use_kwargs(schemas.AdminReservationsPatchBodySchema)
def patch_slot(resv_id, slot_id, **kwargs):
    """Update reservation slot
    ---
    patch:
      summary: Update reservation slot
      description: Update reservation slot
      tags:
        - Admin
        - Admin Reservations
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminReservationsSlotPatchPathSchema
      requestBody:
        content:
          application/json:
            schema: AdminReservationsPatchBodySchema
      responses:
        204:
          description: Success(No Content)
    """
    username = kwargs.pop('username')
    db.update(db.Reservation.TABLE, data=kwargs, resv_id=resv_id, slot_id=slot_id, username=username)
    return '', 204

@bp.route('/privacy')
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.ResvPrivacySchema, location='query')
@marshal_with(schemas.ManyResvPrivacySchema, code=200)
def get_privacy(**kwargs):
    """Get reservation privacy
    ---
    get:
      summary: Get reservation privacy
      description: Get reservation privacy
      tags:
        - Admin
        - Admin Reservations
      security:
        - cookieAuth: []
      parameters:
        - in: query
          schema: ResvPrivacySchema
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: ManyResvPrivacySchema
    """
    return db.select(db.ResvPrivacy.TABLE, **kwargs)

@bp.route('/privacy/<int:privacy>', methods=['PATCH'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminReservationsPrivacyPatchPathSchema, location='path')
@use_kwargs(schemas.Label)
def patch_privacy(privacy, **kwargs):
    """Update reservation privacy
    ---
    patch:
      summary: Update reservation privacy
      description: Update reservation privacy
      tags:
        - Admin
        - Admin Reservations
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminReservationsPrivacyPatchPathSchema
      requestBody:
        content:
          application/json:
            schema: Label
      responses:
        204:
          description: Success(No Content)
    """
    db.update(db.ResvPrivacy.TABLE, data=kwargs, privacy=privacy)
    return '', 204

@bp.route('/status')
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.ResvStatusSchema, location='query')
@marshal_with(schemas.ManyResvStatusSchema, code=200)
def get_status(**kwargs):
    """Get reservation status
    ---
    get:
      summary: Get reservation status
      description: Get reservation status
      tags:
        - Admin
        - Admin Reservations
      security:
        - cookieAuth: []
      parameters:
        - in: query
          schema: ResvStatusSchema
      responses:
        200:
          description: OK
          content:
            application/json:
              schema: ManyResvStatusSchema
    """
    return db.select(db.ResvStatus.TABLE, **kwargs)

@bp.route('/status/<int:status>', methods=['PATCH'])
@auth_required(role=db.UserRole.ADMIN)
@use_kwargs(schemas.AdminReservationsStatusPatchPathSchema, location='path')
@use_kwargs(schemas.Label)
def patch_status(status, **kwargs):
    """Update reservation status
    ---
    patch:
      summary: Update reservation status
      description: Update reservation status
      tags:
        - Admin
        - Admin Reservations
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: AdminReservationsStatusPatchPathSchema
      requestBody:
        content:
          application/json:
            schema: Label
      responses:
        204:
          description: Success(No Content)
    """
    db.update(db.ResvStatus.TABLE, data=kwargs, status=status)
    return '', 204

# @bp.route('/')
# @auth_required(role=db.UserRole.ADMIN)
# @use_kwargs(_schemas.AdminGetReservationsQuerySchema(), location='query')
# @marshal_with(schemas.ManyReservationSchema(), code=200)
# def get(**kwargs):
#     """Get reservations.
#     ---
#     get:
#       summary: Get reservations
#       description: Get reservations
#       tags:
#         - Admin
#       parameters:
#         - in: query
#           schema: AdminGetReservationsQuerySchema
#       responses:
#         200:
#           description: OK
#           content:
#             application/json:
#               schema: ManyReservationSchema
#     """
#     return util.get_reservations(**kwargs)

# @bp.route('/', methods=['POST'])
# @auth_required(role=db.UserRole.ADMIN)
# @use_kwargs(_schemas.AdminResvPostBodySchema())
# @marshal_with(_schemas.AdninResvPostResponseSchema(), code=201)
# def post(time_slots, **kwargs):
#     """Create advanced reservation.
#     - required fields: `room_id`, `title`, `session_id`, `time_slots`
#     - Optional fields: `note`, `username`, `privacy` and `status` in `time_slots`
#         - defaults:
#             - `username`: current user
#             - `privacy`: `PUBLIC`
#             - `status`: `CONFIRMED`
#     ---
#     post:
#       summary: Create a reservation
#       description: Create a reservation
#       tags:
#         - Admin
#       security:
#         - cookieAuth: []
#       requestBody:
#         content:
#           application/json:
#             schema: AdminResvPostBodySchema
#       responses:
#         201:
#           description: Success(Created)
#           content:
#             application/json:
#               schema: AdninResvPostResponseSchema
#     """
#     if 'username' not in kwargs:
#         kwargs['username'] = g.user['username']
#     if 'privacy' not in kwargs:
#         kwargs['privacy'] = db.ResvPrivacy.PUBLIC
#     for slot in time_slots:
#         if 'status' not in slot:
#             slot['status'] = db.ResvStatus.CONFIRMED
    
#     cnx = db.get_cnx(); cursor = cnx.cursor()
#     try:
#         resv_id = util.insert_reservation(cursor, **kwargs)
#         util.insert_time_slots(cursor, resv_id, kwargs['username'], time_slots)
#         cnx.commit()
#     except Error as err:
#         cnx.rollback()
#         if err.errno == errorcode.ER_DUP_ENTRY:
#             abort(409, message='Reservation already exists')
#         else:
#             abort(500, message=f'Database error: {err.msg}')
#     finally:
#         cursor.close()
        
#     return {'resv_id': resv_id}, 201

# @bp.route('/<int:resv_id>', methods=['PATCH'])
# @auth_required(role=db.UserRole.ADMIN)
# @use_kwargs(_schemas.AdminPatchReservationBodySchema())
# def patch(resv_id, **kwargs):
#     """Update a reservation
#       ---
#       summary: Update a reservation
#       description: Update a reservation
#       tags:
#         - Admin
#       security:
#         - cookieAuth: []
#       parameters:
#         - in: path
#           schema: AdminPatchReservationPathSchema
#       requestBody:
#         content:
#           application/json:
#             schema: AdminPatchReservationBodySchema
#       responses:
#         204:
#           description: Success(No Content)
#     """
#     username = kwargs.pop('username', g.user['username'])
#     db.update(db.Reservation.TABLE, data=kwargs, resv_id=resv_id, username=username)
#     return {}, 204

# @bp.route('/<int:resv_id>/<int:slot_id>', methods=['PATCH'])
# @auth_required(role=db.UserRole.ADMIN)
# @use_kwargs(_schemas.AdminPatchReservationSlotBodySchema())
# def patch_time_slot(resv_id, slot_id, **kwargs):
#     username = kwargs.pop('username', g.user['username'])
#     db.update(db.ReservationSlot.TABLE, data=kwargs, resv_id=resv_id, slot_id=slot_id, username=username)
#     return {}, 204

# @bp.route('/privacy')
# @auth_required(role=db.UserRole.ADMIN)
# # @use_kwargs(
# def get_resv_privacy(**kwargs):
#     return db.select(db.ResvPrivacy.TABLE, **kwargs)

# def update_resv_privacy(privacy, **kwargs):
#     """Update reservation privacy.
#     - required fields: `privacy`
#     - optional fields: `label` and `description`
#     """
#     try:
#         db.update(db.ResvPrivacy.TABLE, data=kwargs, privacy=privacy)
#     except Error as err:
#         abort(500, message=f'Database error: {err.msg}')

#     return {}, 204

# def get_resv_status(**kwargs):
#     return db.select(db.ResvStatus.TABLE, **kwargs)

# def update_resv_status(status, **kwargs):
#     """Update reservation status.
#     - required fields: `status`
#     - optional fields: `label` and `description`
#     """
#     if len(kwargs) > 0:
#         db.update(db.ResvStatus.TABLE, data=kwargs, status=status)
#     return {}, 204