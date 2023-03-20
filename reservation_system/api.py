import logging
import jwt
from dateutil import parser
from datetime import datetime, timedelta, time

from flask import make_response, g, abort, current_app
from flask_restful import Resource, request, abort, wraps
from werkzeug.security import check_password_hash, generate_password_hash

from mysql.connector import Error, errorcode

from reservation_system import db

def init_api(api):
    api.add_resource(Authenticate,          '/auth'               )
    api.add_resource(Register,              '/auth/register'      )
    api.add_resource(Periods,               '/periods'            )
    api.add_resource(Rooms,                 '/rooms'              )
    api.add_resource(Sessions,              '/sessions'           )
    api.add_resource(Users,                 '/users'              )
    api.add_resource(ReservationTickets,    '/reservation_tickets')
    api.add_resource(Reservations,          '/reservations'       )
    api.add_resource(ReservationsView,      '/reservations/view'  )

# ----------------------------------------------------------------
# Authentication
# ----------------------------------------------------------------
class Register(Resource):
    def post(self):
        user = dict(request.json)
        user['password'] = generate_password_hash(user['password'])
        try: 
            return db.insert(Users.TABLE, [user]), 201
        except Error as err:
            logging.warning(str(err))
            if err.errno == errorcode.ER_DUP_ENTRY:
                return f"Username {user['username']} already exists", 409 # conflict
            else:
                return "Registration failed. Please try again later", 500

class Authenticate(Resource):
    def post(self):
        logging.info("Authentication...")
        if request.content_type == "application/json" and 'username' in request.json and 'password' in request.json:
            logging.info("Username and password authentication...")
            user = db.select(Users.TABLE, {'username': request.json['username']})[0]
            if check_password_hash(user['password'], request.json['password']):
                g.user_cookie = {"username": request.json['username']}
                response = make_response("")
                response.set_cookie(
                    "user", jwt.encode(g.user_cookie, current_app.config['SECRET_KEY'], algorithm="HS256"),
                )
                return response
        else:
            msg, code, _ = token_auth()
            return msg, code

# ----------------------------------------------------------------
# Periods
# ----------------------------------------------------------------
class Periods(Resource):
    TABLE = "periods"
    def get(self):
        return format_time(db.select(self.TABLE, where=request.json))

    def post(self):
        return db.insert(self.TABLE, data_list=request.json), 201

    def delete(self):
        return db.delete(self.TABLE, where=request.json), 204


# ----------------------------------------------------------------
# Rooms
# ----------------------------------------------------------------
class Rooms(Resource):
    TABLE = "rooms"
    def get(self):
        return format_time(db.select(self.TABLE, where=request.json))

    def post(self):
        return db.insert(self.TABLE, data_list=request.json), 201

    def delete(self):
        return db.delete(self.TABLE, where=request.json), 204


# ----------------------------------------------------------------
# Sessions
# ----------------------------------------------------------------
class Sessions(Resource):
    TABLE = "sessions"
    def get(self):
        return format_time(db.select(self.TABLE, where=request.json))

    def post(self):
        return db.insert(self.TABLE, data_list=request.json), 201

    def delete(self):
        return db.delete(self.TABLE, where=request.json), 204


# ----------------------------------------------------------------
# Users
# ----------------------------------------------------------------
class Users(Resource):
    TABLE = "users"
    def get(self):
        return db.select(self.TABLE, where=request.json)

    def post(self):
        return db.insert(self.TABLE, data_list=request.json), 201

    def delete(self):
        return db.delete(self.TABLE, where=request.json), 204

# ----------------------------------------------------------------
# ReservationTickets
# ----------------------------------------------------------------
class ReservationTickets(Resource):
    TABLE = "reservation_tickets"
    def get(self):
        return db.select(self.TABLE, where=request.json)

    def post(self):
        return db.insert(self.TABLE, data_list=request.json), 201

    def delete(self):
        return db.delete(self.TABLE, where=request.json), 204
# ----------------------------------------------------------------
# Reservations
# ----------------------------------------------------------------
class Reservations(Resource):
    TABLE = "reservations"
    def get(self):
        return format_time(db.select(self.TABLE, where=request.json))

    def post(self):
        validate_reservations(request.json)
        return db.insert(self.TABLE, data_list=request.json), 201

    def delete(self):
        return db.delete(self.TABLE, where=request.json), 204

# ----------------------------------------------------------------
# Reservations View
# ----------------------------------------------------------------
class ReservationsView(Resource):
    VIEW = "reservations_view"
    def get(self):
        return db.select(self.VIEW, where=request.json)
    
# ----------------------------------------------------------------

USER_COOKIE = "user"
def decode_user_cookie():
    cookie = request.cookies.get(USER_COOKIE)
    if not cookie:
        g.user_cookie = {}
        return

    try:
        g.user_cookie = jwt.decode(cookie, current_app.config['SECRET_KEY'], algorithms=["HS256"])
    except jwt.InvalidTokenError as err:
        logging.warning(str(err))
        abort(401)

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        msg, code, user = token_auth()
        if code == 200:
            return func(*args, **kwargs)
        else:
            return msg, 401

    return wrapper

def token_auth():
    logging.info("Token Authentication...")
    try:
        user = db.get(Users.TABLE, {"username": g.user_cookie["username"]})[0]
        return "Authenticated", 200, user
    except Exception as e:
        logging.warning("Authentication failed", e)
        return "Authentication failed", 401, None

def validate_reservations(data):
    for reservation in data:
        
        if parser.parse(reservation['end_time']) <= parser.parse(reservation['start_time']):
            abort(400, message="Invalid reservation", reservation=reservation)

        cursor = db.get_cursor()
        cursor.execute(f"""
            SELECT * FROM 
                {Reservations.TABLE} 
            WHERE 
                (start_time BETWEEN '{reservation['start_time']}' AND '{reservation['end_time']}')
                OR
                (end_time BETWEEN '{reservation['start_time']}' AND '{reservation['end_time']}');
        """)
        if len(cursor.fetchall()) != 0:
            abort(400, message=f"Reservation time conflict", reservation=reservation)

        cursor.execute(f"""
            SELECT room_id FROM 
                {Rooms.TABLE}
            WHERE 
                room_id='{reservation['room_id']}' AND
                status=0 AND 
                open_time <= TIME('{reservation['start_time']}') AND 
                close_time >= TIME('{reservation['end_time']}');
        """)
        if len(cursor.fetchall()) == 0:
            abort(400, message="Room unavailable", reservation=reservation)
        
        cursor.execute(f"""
            SELECT session_id FROM
                {Sessions.TABLE}
            WHERE
                session_id={reservation['session_id']} AND
                is_current=1 AND 
                start_time <= '{reservation['start_time']}' AND 
                end_time >= '{reservation['end_time']}';
        """)
        if len(cursor.fetchall()) == 0:
            abort(400, message="Out of session space", reservation=reservation)

def format_time(data_list: list[dict]):
    for data in data_list:
        for key in data:
            if type(data[key]) == datetime:
                data[key] = datetime.strftime(data[key], '%Y-%m-%d %H:%M:%S')
            elif type(data[key]) == timedelta:
                data[key] = str(data[key])
    return data_list