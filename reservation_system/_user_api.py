from datetime import datetime, timedelta

from flask import Response, current_app, g
from flask.views import MethodView
from marshmallow import Schema, fields, validate
from mysql.connector import Error, errorcode
from webargs.flaskparser import use_kwargs
from werkzeug.security import check_password_hash, generate_password_hash

from reservation_system import db
from reservation_system import api
from reservation_system.auth import auth_required
from reservation_system.models import fields as _fields
from reservation_system.models import schemas
from reservation_system.util import abort, marshal_with, strptimedelta, strftimedelta


def init_api(app, spec):
    for path, view in (
        ('user', User),
        ('user/reservation', GetPostReservation),
        ('user/reservation/<int:resv_id>', PatchReservation),
        ('user/reservation/<int:resv_id>/<int:slot_id>', PatchReservationSlot),
        ('user/reservation/advanced', AdvancedResv),
    ):
        api.register_view(app, spec, path, view)

def get_user(username):
    res = db.select(db.User.TABLE, username=username)
    if not res:
        abort(404, message='User not found')
    return res[0]

def update_user(username, **kwargs):
    """Can only update password and email.
    Updating password requires `password` and `new_password` in `kwargs`.
    """
    if 'password' in kwargs and 'new_password' in kwargs:
        user  = get_user(username)
        if not check_password_hash(user['password'], kwargs['password']):
            abort(401, message='Invalid password')
        kwargs['password'] = generate_password_hash(kwargs['new_password'])
        kwargs.pop('new_password')
    elif 'password' in kwargs or 'new_password' in kwargs:
        abort(400, message='Missing new password or password')

    if len(kwargs) > 0:
        try:
            db.update(db.User.TABLE, data=kwargs, username=username)
        except Error as err:
            current_app.logger.error(f"Error occurred while updating user: {err}")
            abort(500, message='Failed to update user')

    return {}, 204

def get_reservations(start_date=None, end_date=None, create_date=None, update_date=None, **kwargs):
    if start_date:  kwargs['DATE(start_time)']  = '%s' % start_date
    if end_date:    kwargs['DATE(end_time)']    = '%s' % end_date
    if create_date: kwargs['DATE(create_time)'] = '%s' % create_date
    if update_date: kwargs['DATE(update_time)'] = '%s' % update_date

    return db.select(db.Reservation.TABLE, order_by=['start_time', 'end_time'], **kwargs)

def create_reservation(username, role, start_time, end_time, **kwargs):
    """Create a new reservation.
    - Required fields: `room_id`, `title`, `start_time`, `end_time`
    - Optional fields: `note`, `session_id`
    - Auto generated fields: `username`, `privacy`=`public`, 
    `status`=`pending` if `role`<=`GUEST` else `approved`
    """
    now = datetime.now()
    if start_time > end_time:
        abort(400, message='Invalid time range')
    
    if start_time < now:
        abort(400, message='Cannot reserve in the past')

    # time window check
    tm = _time_window()
    if tm is not None:
        if end_time > now + tm:
            abort(400, message='Cannot reserve too far in the future')
    # time limit check
    tm = _time_limit()
    if tm is not None:
        if end_time - start_time > tm:
            abort(400, message='Cannot reserve too long')
    
    # max daily reservation check
    md = _max_daily()
    if md is not None:
        where = {
            'username': username,
            'DATE(create_time)': '%s' % now.strftime('%Y-%m-%d')
        }

        res = db.select(db.Reservation.TABLE, columns=['COUNT(*) AS num'], **where)
        if res[0]['num'] >= md:
            abort(400, message='Exceed max daily reservation limit')

    # time range is combined periods check
    if not _is_combined_periods(start_time, end_time):
        abort(400, message='Time range is not combined periods')
    
    # room availability check
    if not _room_is_available(kwargs['room_id']):
        abort(400, message='Room is not available')

    # add auto generated fields
    kwargs['username'] = username
    kwargs['privacy'] = db.ResvPrivacy.PUBLIC
    if role <= db.UserRole.GUEST:
        status = db.ResvStatus.PENDING
    else:
        status = db.ResvStatus.CONFIRMED

    cnx = db.get_cnx(); cursor = cnx.cursor()
    try:
        res = cursor.execute(f"""
            INSERT INTO {db.Reservation.RESV_TABLE}
            ({', '.join(kwargs.keys())})
            VALUES ({', '.join(['%s'] * len(kwargs))})
        """, tuple(kwargs.values()))
        resv_id = cursor.lastrowid
        print(cursor.statement)
        res = cursor.execute(f"""
            INSERT INTO {db.Reservation.TS_TABLE}
            (resv_id, username, start_time, end_time, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (resv_id, username, start_time, end_time, status))
        slot_id = cursor.lastrowid
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

def update_reservation(resv_id, username, **kwargs):
    try:
        db.update(db.Reservation.TABLE, data=kwargs, resv_id=resv_id, username=username)
    except Exception as err:
        current_app.logger.error(err)
        abort(500, message=f'Database error: {err.msg}')

    return {}, 204

def update_reservation_slot(resv_id, slot_id, username, **kwargs):
    try:
        db.update(db.Reservation.TABLE, data=kwargs, resv_id=resv_id, slot_id=slot_id, username=username)
    except Exception as err:
        current_app.logger.error(err)
        abort(500, message=f'Database error: {err.msg}')
    
    return {}, 204

def create_advanced_reservation(username, role, time_slots, **kwargs):
    """Create advanced reservation.
    - required fields: `room_id`, `title`, `session_id`, `time_slots`
    - Optional fields: `note`
    - Auto generated fields: `username`, `privacy`=`public`,
        `status`=`pending` if `role`<=`BASIC` else `approved`
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
        if not _is_combined_periods(start_time, end_time):
            abort(400, message='Time range is not combined periods')
    
    # room availability check
    if not _room_is_available(kwargs['room_id']):
        abort(400, message='Room is not available')
    
    # add auto generated fields
    kwargs['username'] = username
    kwargs['privacy'] = db.ResvPrivacy.PUBLIC
    if role <= db.UserRole.BASIC:
        status = db.ResvStatus.PENDING
    else:
        status = db.ResvStatus.CONFIRMED
    
    cnx = db.get_cnx(); cursor = cnx.cursor()
    try:
        cursor.execute(f"""
            INSERT INTO {db.Reservation.RESV_TABLE}
            ({', '.join(kwargs.keys())})
            VALUES ({', '.join(['%s']*len(kwargs))})
        """, tuple(kwargs.values()))
        resv_id = cursor.lastrowid
        cursor.executemany(f"""
            INSERT INTO {db.Reservation.TS_TABLE}
            (resv_id, username, status, start_time, end_time)
            VALUES ({resv_id}, '{username}', {status}, %s, %s)
        """, [(slot['start_time'], slot['end_time']) for slot in time_slots])
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
        
    return {'resv_id': resv_id}, 201

# extra-models
class ResvPatchBodySchema(Schema):
    title = fields.Str()
    note = fields.Str()
    status = _fields.resv_status()

class UserResvPatchPathSchema(Schema):
    resv_id = fields.Int(required=True)

class UserResvSlotPatchBodySchema(Schema):
    status = _fields.resv_status(
        validate=validate.OneOf([db.ResvStatus.CANCELLED]),
        required=True
    )

class UserResvSlotPatchPathSchema(Schema):
    resv_id = fields.Int(required=True)
    slot_id = fields.Int(required=True)

class AdvancedResvPostBodySchema(Schema):
    class TimeSlot(Schema):
        start_time = fields.DateTime(required=True)
        end_time = fields.DateTime(required=True)
    room_id = fields.Int(required=True)
    title = fields.Str(required=True)
    session_id = fields.Int(required=True)
    time_slots = fields.List(fields.Nested(TimeSlot), required=True)
    note = fields.Str()

class AdvancedResvPostResponseSchema(Schema):
    resv_id = fields.Int(required=True)

# views
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
        return get_user(username)

    @auth_required(role=db.UserRole.RESTRICTED)
    @use_kwargs(UserPatchBodySchema())
    def patch(self, **kwargs):
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
        return update_user(**kwargs)

class GetPostReservation(MethodView):
    class UserGetReservationQuerySchema(schemas.ReservationSchema):
        start_date = fields.Date()
        end_date = fields.Date()
        create_date = fields.Date()
        update_date = fields.Date()
    
    class ResvPostBodySchema(Schema):
        room_id = fields.Int(required=True)
        title = fields.Str(required=True)
        start_time = fields.DateTime(required=True)
        end_time = fields.DateTime(required=True)
        note = fields.Str()
        session_id = fields.Int()
    
    class ResvPostResponseSchema(Schema):
        resv_id = fields.Int()
        slot_id = fields.Int()

    @auth_required(role=db.UserRole.RESTRICTED)
    @use_kwargs(UserGetReservationQuerySchema, location='query')
    @marshal_with(schemas.ManyReservationSchema(), code=200)
    def get(self, **kwargs):
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
        return get_reservations(**kwargs)
    
    @auth_required(role=db.UserRole.GUEST)
    @use_kwargs(ResvPostBodySchema())
    @marshal_with(ResvPostResponseSchema(), code=201)
    def post(self, **kwargs):
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
              schema: ResvPostBodySchema
        responses:
          201:
            description: Success(Created)
            content:
              application/json:
                schema: ResvPostResponseSchema
        """
        return create_reservation(**kwargs)

class PatchReservation(MethodView):
    @auth_required(role=db.UserRole.GUEST)
    @use_kwargs(ResvPatchBodySchema())
    @use_kwargs(UserResvPatchPathSchema, location='path')
    def patch(self, **kwargs):
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
        return update_reservation(**kwargs)
        
class PatchReservationSlot(MethodView):
    @auth_required(role=db.UserRole.GUEST)
    @use_kwargs(UserResvSlotPatchBodySchema())
    @use_kwargs(UserResvSlotPatchPathSchema(), location='path')
    def patch(self, **kwargs):
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
        return update_reservation_slot(**kwargs)

class AdvancedResv(MethodView):
    @auth_required(role=db.UserRole.BASIC)
    @use_kwargs(AdvancedResvPostBodySchema())
    @marshal_with(AdvancedResvPostResponseSchema(), code=201)
    def post(self, **kwargs):
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
        return create_advanced_reservation(**kwargs)
        
def _is_combined_periods(start_time, end_time):
    """Check if the time range is a combination of consecutive periods"""
    cnx = db.get_cnx(); cursor = cnx.cursor()
    cursor.execute(f"""
        SELECT SUM(TIME_TO_SEC(TIMEDIFF(p.end_time, p.start_time)))
        FROM {db.Period.TABLE} p WHERE p.period_id NOT IN (
            SELECT p2.period_id FROM {db.Period.TABLE} p2 
            WHERE p2.start_time >= TIME(%s) 
                OR p2.end_time <= TIME(%s)
        )
    """, (end_time, start_time))
    res = cursor.fetchone()
    cursor.close()
    
    return res[0] == (end_time - start_time).total_seconds()

def _room_is_available(room_id):
    res = db.select(db.Room.TABLE, {'room_id': room_id})
    if not res: return False
    return res[0]['status'] == db.RoomStatus.AVAILABLE

def _time_window():
    cnx = db.get_cnx(); cursor = cnx.cursor()
    cursor.execute("""
        SELECT value FROM %s WHERE id = %s
    """ % (db.Setting.TABLE, db.Setting.TIME_WINDOW))
    tm = cursor.fetchone()
    cursor.close()
    if tm is None: return None
    return strptimedelta(tm[0])
    
def _time_limit():
    cnx = db.get_cnx(); cursor = cnx.cursor()
    cursor.execute("""
        SELECT value FROM %s WHERE id = %s
    """ % (db.Setting.TABLE, db.Setting.TIME_LIMIT))
    tm = cursor.fetchone()
    cursor.close()
    if tm is None: return None
    return strptimedelta(tm[0])
    
def _max_daily():
    cnx = db.get_cnx(); cursor = cnx.cursor()
    cursor.execute("""
        SELECT value FROM %s WHERE id = %s
    """ % (db.Setting.TABLE, db.Setting.MAX_DAILY))
    tm = cursor.fetchone()
    cursor.close()
    if tm is None: return None
    return int(tm[0])