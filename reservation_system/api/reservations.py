from flask.views import MethodView
from marshmallow import fields
from webargs.flaskparser import use_kwargs

from reservation_system import db
from reservation_system.models import schemas
from reservation_system.util import marshal_with


class Reservations(MethodView):
    class GetReservationsQuerySchema(schemas.ReservationSchema):
        start_date = fields.Date()
        end_date = fields.Date()
        create_date = fields.Date()
        update_date = fields.Date()

    @use_kwargs(GetReservationsQuerySchema(), location='query')
    @marshal_with(schemas.ManyReservationSchema(), code=200)
    def get(self, **kwargs):
        """Get reservations
        ---
        summary: Get reservations
        description: Get reservations
        tags:
          - Public
        parameters:
          - in: query
            schema: GetReservationsQuerySchema
        responses:
          200:
            description: Success(OK)
            content:
              application/json:
                schema: ManyReservationSchema
        """
        for prefix in ['start', 'end', 'create', 'update']:
            date = f'{prefix}_date'
            if date in kwargs:
                time = f'{prefix}_time'
                kwargs[f'DATE({time})'] = kwargs.pop(date)

        res = db.select(
            db.Reservation.TABLE,
            order_by=['start_time', 'end_time'], 
            **kwargs
        )
        
        # check privacy
        for r in res:
            if r['privacy'] == db.ResvPrivacy.ANONYMOUS:
                r.pop('username')
            if r['privacy'] == db.ResvPrivacy.PRIVATE:
                r = {
                    'start_time': r['start_time'],
                    'end_time': r['end_time'],
                    'status': r['status'],
                    'room_id': r['room_id'],
                }
        return res

class ResvStatus(MethodView):
    @use_kwargs(schemas.ResvStatusSchema(), location='query')
    @marshal_with(schemas.ManyResvStatusSchema(), code=200)
    def get(self, **kwargs):
        """Get reservation status
        ---
        summary: Get reservation status
        description: Get reservation status
        tags:
          - Public
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
    
class ResvPrivacy(MethodView):
    @use_kwargs(schemas.ResvPrivacySchema(), location='query')
    @marshal_with(schemas.ManyResvPrivacySchema(), code=200)
    def get(self, **kwargs):
        """Get reservation privacy
        ---
        summary: Get reservation privacy
        description: Get reservation privacy
        tags:
          - Public
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
