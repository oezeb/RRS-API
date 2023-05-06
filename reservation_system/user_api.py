from datetime import date, datetime

from flask import g, request, current_app, Response
from werkzeug.security import check_password_hash, generate_password_hash

from mysql.connector import Error, errorcode
from webargs.flaskparser import use_kwargs

from reservation_system import db
from reservation_system.util import abort, marshal_with
from reservation_system.auth import auth_required
from reservation_system.api import MethodView, register_view

from reservation_system.models.user_api import user
from reservation_system.models.user_api import reservation as resv

def init_api(app, spec):
    for path, view in (
        ('user', User),
        ('user/reservation', Reservation),
        ('user/reservation/<int:resv_id>', PatchResv),
        ('user/reservation/<int:resv_id>/<int:slot_id>', PatchResvSlot),
        ('user/reservation/advanced', AdvancedResv),
    ):
        register_view(app, spec, path, view)
        

class User(MethodView):
    schemas = {
        'user.post.response.200': user.GetRespSchema,
        'user.patch.body': user.PatchBodySchema,
    }

    @auth_required(role=db.UserRole.RESTRICTED)
    @marshal_with(user.GetRespSchema(), code=200)
    def get(self):
        """Get user info.
        ---
        description: Get user info.
        tags:
          - User
        security:
          - cookieAuth: []
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: GetRespSchema
          404:
            description: User not found
        """
        res = db.select(db.User.TABLE, where={'username': g.sub['username']})
        if not res:
            abort(404, message='User not found')
        return res[0]

    @auth_required(role=db.UserRole.RESTRICTED)
    @use_kwargs(user.PatchBodySchema())
    def patch(self, **kwargs):
        """Update user info.
        ---
        description: Update user info.
        tags:
          - User
        security:
          - cookieAuth: []
        requestBody:
          content:
            application/json:
              schema: PatchBodySchema
        responses:
          204:
            description: No Content
          401:
            description: Invalid password
          404:
            description: User not found
        """
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

        if len(kwargs) > 0:
            try:
                db.update(db.User.TABLE, [{'data': kwargs, 'where': {'username': g.sub['username']}}])
            except Error as err:
                current_app.logger.error(f"Error occurred while updating user: {err}")
                abort(500, message='Failed to update user')
        return Response(status=204)

class Reservation(MethodView):
    schemas = {
        'user.reservation.get.response.200': resv.UserResvGetRespSchema(many=True),
        'user.reservation.get.query': resv.UserResvGetQuerySchema(),
        'user.reservation.post.body': resv.UserResvPostBodySchema(),
        'user.reservation.post.response.201': resv.UserResvPostRespSchema(),
    }

    @auth_required(role=db.UserRole.RESTRICTED)
    @marshal_with(resv.UserResvGetRespSchema(many=True), code=200)
    @use_kwargs(resv.UserResvGetQuerySchema(), location='query')
    def get(self, date=None, **kwargs):
        """Get user reservations.
        ---
        description: Get user reservations.
        tags:
          - User
        security:
          - cookieAuth: []
        parameters:
          - in: query
            schema: UserResvGetQuerySchema
        responses:
          200:
            description: OK
            content:
              application/json:
                schema: UserResvGetRespSchema
        """
        kwargs['username'] = g.sub['username']
        if date: kwargs['DATE(start_time)'] = 'DATE(%s)' % date
        return db.select(db.Reservation.TABLE, where=kwargs,
                        order_by=['start_time', 'end_time'])
    
    @auth_required(role=db.UserRole.GUEST)
    @use_kwargs(resv.UserResvPostBodySchema())
    @marshal_with(resv.UserResvPostRespSchema(), code=201)
    def post(self, **kwargs):
        """Create a new reservation.
        - Required fields: `room_id`, `title`, `time_slots`
        - Optional fields: `note`, `session_id`
        - Auto generated fields: `username`, `privacy`=`public`, 
        `status`=`pending` if `role`<=`GUEST` else `approved`
        ---
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
            description: Created
            content:
              application/json:
                schema: UserResvPostRespSchema
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

class PatchResv(MethodView):
    schemas = {
        'user.reservation.patch.path': resv.UserResvPatchPathSchema(),
        'user.reservation.patch.body': resv.UserResvPatchBodySchema(),
    }

    @auth_required(role=db.UserRole.GUEST)
    @use_kwargs(resv.UserResvPatchBodySchema())
    @use_kwargs(resv.UserResvPatchPathSchema(), location='path')
    def patch(self, resv_id, **kwargs):
        """Update reservation info. reservation status can only be set to CANCELLED.
        ---
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
              schema: UserResvPatchBodySchema
        responses:
          204:
            description: No Content
        """
        where = {
            'resv_id': resv_id,
            'username': g.sub['username']
        }

        try:
            db.update(db.Reservation.TABLE, [{
                'data': kwargs,
                'where': where,
            }])
        except Exception as err:
            current_app.logger.error(err)
            abort(500, message=f'Database error: {err.msg}')

        return Response(status=204)

class PatchResvSlot(MethodView):
    schemas = {
        'user.reservation.slot.patch.path': resv.UserResvSlotPatchPathSchema(),
        'user.reservation.slot.patch.body': resv.UserResvSlotPatchBodySchema(),
    }

    @auth_required(role=db.UserRole.GUEST)
    @use_kwargs(resv.UserResvSlotPatchBodySchema())
    @use_kwargs(resv.UserResvSlotPatchPathSchema(), location='path')
    def patch(self, resv_id, slot_id, **kwargs):
        """Update reservation time slot info. reservation status can only be set to CANCELLED.
        ---
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
            description: No Content
        """
        where = {
            'resv_id': resv_id,
            'username': g.sub['username'],
            'slot_id': slot_id,
        }

        try:
            db.update(db.Reservation.TS_TABLE, [{
                'data': kwargs,
                'where': where,
            }])
        except Exception as err:
            current_app.logger.error(err)
            abort(500, message=f'Database error: {err.msg}')
        
        return Response(status=204)

class AdvancedResv(MethodView):
    schemas = {
        'user.advanced.reservation.post': resv.AdvancedResvPostSchema(),
    }

    @auth_required(role=db.UserRole.BASIC)
    @use_kwargs(resv.AdvancedResvPostSchema())
    @marshal_with(resv.UserResvPostRespSchema(), code=201)
    def post(self, time_slots, **kwargs):
        """Create advanced reservation.
        - required fields: `room_id`, `title`, `session_id`, `time_slots`
        - Optional fields: `note`
        - Auto generated fields: `username`, `privacy`=`public`,
            `status`=`pending` if `role`<=`BASIC` else `approved`
        ---
        description: Create advanced reservation.
        tags:
          - User
        security:
          - cookieAuth: []
        requestBody:
          content:
            application/json:
              schema: AdvancedResvPostSchema
        responses:
          201:
            description: Created
            content:
              application/json:
                schema: UserResvPostRespSchema
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
