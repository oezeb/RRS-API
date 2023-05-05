from datetime import date, datetime

from flask import g, request, current_app
from flask.views import MethodView
from werkzeug.security import check_password_hash, generate_password_hash

from mysql.connector import Error, errorcode

from flask_apispec import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from marshmallow import Schema, fields, validate

from reservation_system import db
from reservation_system.util import abort
from reservation_system.auth import auth_required, openapi_cookie_auth

def init_api(app, docs):
    for path, view in (
        ('user', User),
        ('user/reservation', Reservation),
        ('user/reservation/<string:date>', GetReservation),
        ('user/reservation/<int:resv_id>', PatchReservation),
        ('user/reservation/<int:resv_id>/<int:slot_id>', PatchReservation),
        ('user/reservation/advanced', AdvancedResv),
    ):
        app.add_url_rule(f'/api/{path}', view_func=view.as_view(path))
        docs.register(view, endpoint=path)

class User(MethodResource):
    @auth_required(role=db.UserRole.RESTRICTED)
    @marshal_with(db.User.schema(), code=200, description='Success')
    @marshal_with(None, code=404, description='User not found')
    @doc(description='Get user info', tags=['User'], **openapi_cookie_auth)
    def get(self):
        res = db.select(db.User.TABLE, where={'username': g.sub['username']})
        if not res:
            abort(404, message='User not found')
        return res[0]

    @auth_required(role=db.UserRole.RESTRICTED)
    @marshal_with(Schema(), code=204, description='Success')
    @use_kwargs(Schema.from_dict({
        'email': fields.Email(),
        'password': fields.Str(),
        'new_password': fields.Str(),
    }))
    @doc(description='Update user info', tags=['User'], **openapi_cookie_auth)
    def patch(self, **kwargs):
        if 'password' in kwargs and 'new_password' in kwargs:
            res = db.select(db.User.TABLE, where={'username': g.sub['username']})
            if not res:
                abort(404, message='User not found')
            if not check_password_hash(res[0]['password'], kwargs['password']):
                abort(401, message='Invalid password')
            kwargs['password'] = generate_password_hash(kwargs['new_password'])
            kwargs.pop('new_password')
        elif 'password' in kwargs or 'new_password' in kwargs:
            abort(400, message='Missing new password or password')

        try:
            db.update(db.User.TABLE, [{'data': kwargs, 'where': {'username': g.sub['username']}}])
            return None, 204
        except Error as err:
            current_app.logger.error(f"Error occurred while updating user: {err}")
            abort(500, message='Failed to update user')

def _resv_post_schema():
    schema = db.Reservation.schema(exclude=['resv_id', 'username', 'privacy', 'time_slots'])
    time_slots = fields.List(fields.Nested(db.Reservation.ts_schema(exclude=['slot_id', 'status'])))
    # schema.room_id.required = True
    # schema.title.required = True
    # schema.time_slots.required = True
    return Schema.from_dict({
        **schema.fields,
        'time_slots': time_slots,
    })

class GetReservation(MethodResource):
    @auth_required(role=db.UserRole.RESTRICTED)
    @marshal_with(
        db.Reservation.schema(many=True), 
        code=200, description='Success'
    )
    @doc(description='Get user reservations',
         tags=['User'], params={
        'date': {
            'in': 'path', 
            'type': 'string', 
            'format': 'date', 
            'description': 'Date of reservations to get'
        },
        **db.Reservation.args(exclude=['username'])},
        **openapi_cookie_auth
    )
    def get(self):
        args = request.args
        if date: args['DATE(start_time)'] = 'DATE(%s)' % date
        return db.select(db.Reservation.TABLE, where=args, 
                        order_by=['start_time', 'end_time'])

class UserResvPostSchema(Schema):
    room_id = fields.Int(required=True)
    title = fields.Str(required=True)
    note = fields.Str()
    session_id = fields.Int()
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)

class Reservation(GetReservation):
    @auth_required(role=db.UserRole.GUEST)
    @marshal_with(db.Reservation.schema(only=['resv_id']), code=201, description='Success')
    @use_kwargs(UserResvPostSchema())
    @doc(description='Create a new reservation', tags=['User'], **openapi_cookie_auth)
    def post(self, **kwargs):
        """
        Create a new reservation.
        - Required fields: `room_id`, `title`, `time_slots`
        - Optional fields: `note`, `session_id`
        - Auto generated fields: `username`, `privacy`=`public`, 
        `status`=`pending` if `role`<=`GUEST` else `approved`
        """
        now = datetime.now()
        if kwargs['start_time'] > kwargs['end_time']:
            abort(400, message='Invalid time range')
        
        # time window check
        if kwargs['start_time'] < now:
            abort(400, message='Cannot reserve in the past')
        tm = db.Setting.time_window()
        if tm is not None:
            if kwargs['end_time'] > now + tm:
                abort(400, message='Cannot reserve too far in the future')
        # time limit check
        tm = db.Setting.time_limit()
        if tm is not None:
            if kwargs['end_time'] - kwargs['start_time'] > tm:
                abort(400, message='Cannot reserve too long')
        
        # max daily reservation check
        md = db.Setting.max_daily()
        if md is not None:
            res = db.select(db.Reservation.TABLE, where={
                'username': g.sub['username'],
                'DATE(create_time)': 'DATE(%s)' % now.strftime('%Y-%m-%d')
            }, columns=['COUNT(*) AS num'])
            if res[0]['num'] >= md:
                abort(400, message='Exceed max daily reservation limit')

        # time range is combined periods check
        if not db.Period.is_combined_periods(kwargs['start_time'], kwargs['end_time']):
            abort(400, message='Time range is not combined periods')
        
        # room availability check
        if not db.Room.is_available(kwargs['room_id']):
            abort(400, message='Room is not available')

        # add auto generated fields
        kwargs['username'] = g.sub['username']
        kwargs['privacy'] = db.ResvPrivacy.PUBLIC
        if g.sub['role'] <= db.UserRole.GUEST:
            kwargs['status'] = db.ResvStatus.PENDING
        else:
            kwargs['status'] = db.ResvStatus.CONFIRMED

        try:
            res = db.insert(db.Reservation.TABLE, [kwargs])
            return {'resv_id': res['lastrowid'][0]}, 201
        except Error as err:
            current_app.logger.error(err)
            if err.errno == errorcode.ER_DUP_ENTRY:
                abort(409, message='Reservation already exists')
            else:
                abort(500, message=f'Database error: {err.msg}')
    
class PatchReservation(MethodResource):
    class UserResvPatchSchema(Schema):
        title = fields.Str()
        note = fields.Str()
        status = fields.Int(validate=validate.OneOf([db.ResvStatus.CANCELLED]))

    @auth_required(role=db.UserRole.GUEST)
    @marshal_with(Schema(), code=204, description='Success')
    @use_kwargs(UserResvPatchSchema())
    @doc(description='Update reservation info', tags=['User'], 
        params={
            'resv_id': {
                'in': 'path',
                'type': 'integer',
                'description': 'Reservation ID',
            },
            'slot_id': {
                'in': 'path',
                'type': 'integer',
                'description': 'Reservation time slot ID',
            },
        },
         **openapi_cookie_auth)
    def patch(self, resv_id, slot_id=None, status=None, **kwargs):
        """
        Update reservation info.
        `request.json` should contain:
            - `resv_id`
            - `data`: contains the fields to be updated. `title`, `note`, `status`
                - `status` if exists=CANCELLED
        """
        where = {
            'resv_id': resv_id,
            'username': g.sub['username']
        }

        if len(kwargs) > 0:
            db.update(db.Reservation.RESV_TABLE, [{
                'data': kwargs,
                'where': where,
            }])
        if status is not None:
            if slot_id is not None:
                where['slot_id'] = slot_id
            db.update(db.Reservation.TS_TABLE, [{
                'data': {'status': status},
                'where': where,
            }])
        
        return None, 204

class AdvancedResvPostSchema(Schema):
    class TimeSlotSchema(Schema):
        start_time = fields.DateTime(required=True)
        end_time = fields.DateTime(required=True)
    
    room_id = fields.Int(required=True)
    title = fields.Str(required=True)
    session_id = fields.Int(required=True)
    note = fields.Str()
    time_slots = fields.List(
        fields.Nested(TimeSlotSchema()), 
        required=True,
        validate=validate.Length(min=1)
    )

class AdvancedResv(MethodResource):
    @auth_required(role=db.UserRole.BASIC)
    @marshal_with(db.Reservation.schema(only=['resv_id'], many=True), code=201, description='Success')
    @use_kwargs(AdvancedResvPostSchema())
    @doc(description='Create advanced reservation', tags=['User'], 
        **openapi_cookie_auth)
    def post(self, time_slots, **kwargs):
        """
        Create advanced reservation.
        - required fields: `room_id`, `title`, `session_id`, `time_slots`
        - Optional fields: `note`
        - Auto generated fields: `username`, `privacy`=`public`,
            `status`=`pending` if `role`<=`BASIC` else `approved`
        """
        # time range is combined periods check
        for start_time, end_time in time_slots:
            if not db.Period.is_combined_periods(start_time, end_time):
                abort(400, message='Time range is not combined periods')
        
        # room availability check
        if not db.Room.is_available(kwargs['room_id']):
            abort(400, message='Room is not available')
        
        # add auto generated fields
        kwargs['username'] = g.sub['username']
        kwargs['privacy'] = db.ResvPrivacy.PUBLIC
        if g.sub['role'] <= db.UserRole.BASIC:
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
                VALUES ({resv_id}, '{g.sub['username']}', {status}, %s, %s)
            """, [(start_time, end_time) for start_time, end_time in time_slots])
            cnx.commit()
        except Exception as e:
            abort(500, str(e))
        finally:
            cursor.close()
            
        return {'resv_id': resv_id}, 201
