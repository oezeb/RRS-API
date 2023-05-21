from mysql.connector import Error, errorcode
from flask import g

from reservation_system import db
from reservation_system.user_api import reservation as resv
from reservation_system.user_api import util
from reservation_system.util import abort

def create_period(**kwargs):
    """Create period.
    - required fields: `start_time`, `end_time`
    """
    try:
        res = db.insert(db.Period.TABLE, kwargs)
    except Error as err:
        if err.errno == errorcode.ER_DUP_ENTRY:
            abort(409, message='Period already exists')
        else:
            abort(500, message=f'Database error: {err.msg}')

    return {'period_id': res['lastrowid']}, 201

# def update_period(period_id, **kwargs):
#     if len(kwargs) > 0:
#         db.update(db.Period.TABLE, data=kwargs, period_id=period_id)
#     return {}, 204

# def delete_period(period_id):
#     db.delete(db.Period.TABLE, period_id=period_id)
#     return {}, 204