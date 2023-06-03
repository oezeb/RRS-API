from datetime import datetime

from flask import Blueprint, current_app
from mysql.connector import Error, errorcode
from webargs.flaskparser import use_kwargs

from app import db
from app.auth import auth_required
from app.models import schemas
from app.user_api import util
from app.util import abort, marshal_with

bp = Blueprint('api_user_reservation', __name__, url_prefix='/api/user/reservation')

@bp.route('/')
@auth_required(role=db.UserRole.RESTRICTED)
@use_kwargs(schemas.UserReservationGetQuerySchema, location='query')
@marshal_with(schemas.ManyReservationSchema, code=200)
def get(username, **kwargs):
    """Get user reservations.
    ---
    get:
      summary: Get reservations
      description: Get user reservations.
      tags:
        - User
      security:
        - cookieAuth: []
      parameters:
        - in: query
          schema: UserReservationGetQuerySchema
      responses:
        200:
          description: Success(OK)
          content:
            application/json:
              schema: ManyReservationSchema
    """
    return util.get_reservations(username=username, **kwargs)
    
@bp.route('/', methods=['POST'])
@auth_required(role=db.UserRole.GUEST)
@use_kwargs(schemas.UserReservationPostBodySchema)
@marshal_with(schemas.UserReservationPostResponseSchema, code=201)
def post(username, role, start_time, end_time, **kwargs):
    """Create a new reservation.
    - Required fields: `room_id`, `title`, `start_time`, `end_time`
    - Optional fields: `note`, `session_id`
    - Auto generated fields: `username`, `privacy`=`public`, 
    `status`=`pending` if `role`<=`GUEST` else `approved`
    ---
    post:
      summary: Create reservation
      description: Create a new reservation.
      tags:
        - User
      security:
        - cookieAuth: []
      requestBody:
        content:
          application/json:
            schema: UserReservationPostBodySchema
      responses:
        201:
          description: Success(Created)
          content:
            application/json:
              schema: UserReservationPostResponseSchema
    """
    now = datetime.now()
    if start_time > end_time:
        abort(400, message='Invalid time range')
    
    if start_time < now:
        abort(400, message='Cannot reserve in the past')

    # time window check
    tm = util.time_window()
    if tm is not None:
        if end_time > now + tm:
            abort(400, message='Cannot reserve too far in the future')
    # time limit check
    tm = util.time_limit()
    if tm is not None:
        if end_time - start_time > tm:
            abort(400, message='Cannot reserve too long')
    
    # max daily reservation check
    md = util.max_daily()
    if md is not None:
        where = {
            'username': username,
            'DATE(create_time)': '%s' % now.strftime('%Y-%m-%d')
        }

        res = db.select(
            db.Reservation.TABLE, 
            columns=['COUNT(DISTINCT resv_id) AS num'],
            **where
        )
        if res[0]['num'] >= md:
            abort(400, message='Exceed max daily reservation limit')

    # time range is combined periods check
    if not util.is_combined_periods(start_time, end_time):
        abort(400, message='Time range is not combined periods')
    
    # room availability check
    if not util.room_is_available(kwargs['room_id']):
        abort(400, message='Room is not available')

    # add auto generated fields
    kwargs['username'] = username
    kwargs['privacy'] = db.ResvPrivacy.PUBLIC
    time_slots = [{'start_time': start_time, 'end_time': end_time}]
    if role <= db.UserRole.GUEST:
        time_slots[0]['status'] = db.ResvStatus.PENDING
    else:
        time_slots[0]['status'] = db.ResvStatus.CONFIRMED

    cnx = db.get_cnx(); cursor = cnx.cursor()
    try:
        resv_id = util.insert_reservation(cursor, **kwargs)
        slot_id = util.insert_time_slots(cursor, resv_id, username, time_slots)
        cnx.commit()
    except Error as err:
        cnx.rollback()
        current_app.logger.error(err)
        if err.errno == errorcode.ER_DUP_ENTRY:
            abort(409, message='Reservation already exists')
        else:
            abort(500, message=f'Database error: {err.msg}')
    finally:
        cursor.close()

    return {'resv_id': resv_id, 'slot_id': slot_id}, 201

@bp.route('/<int:resv_id>', methods=['PATCH'])
@auth_required(role=db.UserRole.GUEST)
@use_kwargs(schemas.UserReservationPatchPathSchema, location='path')
@use_kwargs(schemas.UserReservationPatchBodySchema)
def patch(resv_id, username, **kwargs):
    """Update reservation info. reservation status can only be set to CANCELLED.
    ---
    patch:
      summary: Update reservation info
      description: Update reservation info.
      tags:
        - User
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: UserReservationPatchPathSchema
      requestBody:
        content:
          application/json:
            schema: UserReservationPatchBodySchema
      responses:
        204:
          description: Success(No Content)
    """
    db.update(db.Reservation.TABLE, data=kwargs, resv_id=resv_id, username=username)
    return '', 204
  
@bp.route('/<int:resv_id>/<int:slot_id>', methods=['PATCH'])
@auth_required(role=db.UserRole.GUEST)
@use_kwargs(schemas.UserReservationSlotPatchPathSchema, location='path')
@use_kwargs(schemas.UserReservationSlotPatchBodySchema)
def patch_slot(resv_id, slot_id, username, **kwargs):
    """Update reservation time slot info. reservation status can only be set to CANCELLED.
    ---
    patch:
      summary: Update time slot info
      description: Update reservation time slot info.
      tags:
        - User
      security:
        - cookieAuth: []
      parameters:
        - in: path
          schema: UserReservationSlotPatchPathSchema
      requestBody:
        content:
          application/json:
            schema: UserReservationSlotPatchBodySchema
      responses:
        204:
          description: Success(No Content)
    """
    db.update(db.Reservation.TABLE, data=kwargs, resv_id=resv_id, slot_id=slot_id, username=username)
    return '', 204

@bp.route('/advanced', methods=['POST'])
@auth_required(role=db.UserRole.BASIC)
@use_kwargs(schemas.UserReservationAdvancedPostBodySchema)
@marshal_with(schemas.UserReservationAdvancedPostResponseSchema, code=201)
def post_advanced(username, role, time_slots, **kwargs):
    """Create advanced reservation.
    - required fields: `room_id`, `title`, `session_id`, `time_slots`
    - Optional fields: `note`
    - Auto generated fields: `username`, `privacy`=`public`,
        `status`=`pending` if `role`<=`BASIC` else `approved`
    ---
    post:
      summary: Create advanced reservation
      description: Create advanced reservation.
      tags:
        - User
      security:
        - cookieAuth: []
      requestBody:
        content:
          application/json:
            schema: UserReservationAdvancedPostBodySchema
      responses:
        201:
          description: Success(Created)
          content:
            application/json:
              schema: UserReservationAdvancedPostResponseSchema
    """
    now = datetime.now()
    for slot in time_slots:
        start_time = slot['start_time']
        end_time = slot['end_time']
        if start_time > end_time:
            abort(400, message='Invalid time range')
        
        if start_time < now:
            abort(400, message='Cannot reserve in the past')
            
        # time range is combined periods check
        if not util.is_combined_periods(start_time, end_time):
            abort(400, message='Time range is not combined periods')
    
    # room availability check
    if not util.room_is_available(kwargs['room_id']):
        abort(400, message='Room is not available')
    
    # add auto generated fields
    kwargs['username'] = username
    kwargs['privacy'] = db.ResvPrivacy.PUBLIC
    if role <= db.UserRole.BASIC:
        for slot in time_slots:
            slot['status'] = db.ResvStatus.PENDING
    else:
        for slot in time_slots:
            slot['status'] = db.ResvStatus.CONFIRMED
    
    cnx = db.get_cnx(); cursor = cnx.cursor()
    try:
        resv_id = util.insert_reservation(cursor, **kwargs)
        util.insert_time_slots(cursor, resv_id, kwargs['username'], time_slots)
        cnx.commit()
    except Error as err:
        print(err)
        cnx.rollback()
        if err.errno == errorcode.ER_DUP_ENTRY:
            abort(409, message='Reservation already exists')
        else:
            abort(500, message=f'Database error: {err.msg}')
    finally:
        cursor.close()
        
    return {'resv_id': resv_id}, 201
