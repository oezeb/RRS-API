
import json
from typing import Union
from datetime import date, datetime, time, timedelta
import click
import dateutil.parser
import logging
import os

import mysql.connector
from flask import current_app, g

from reservation_system import schema

logger = logging.getLogger(__name__)

def init_app(app):
    app.teardown_appcontext(close_cnx)
    app.cli.add_command(init_db_command)

# ----------------------------------------------------------------
# Database Initialization
# ----------------------------------------------------------------
def get_cnx():
    if 'cnx' not in g:
        g.cnx = mysql.connector.connect(
            database=current_app.config['DATABASE'],
            user    =current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD']
        )
        
    return g.cnx

def close_cnx(e=None):
    cnx = g.pop('cnx', None)

    if cnx is not None:
        cnx.close()

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

def init_db():
    cnx = get_cnx(); cursor = cnx.cursor()
    def run(sql):
        it = cursor.execute(sql, multi=True)
        for res in it:
            logger.info(f"Running query: {res}")

    set_current_time_zone(cursor)

    logger.info("Creating tables...")
    with current_app.open_resource('schema.sql') as f:
        run(f.read())

    logger.info("Populating tables with immutable data...")
    run(schema.IMMUTABLE_INSERTS)

    logger.info("Creating triggers...")
    variables = vars(schema)
    for name, value in variables.items():
        if name.endswith('_TRIGGER'):
            run(value)

    logger.info("Populating tables with some default data...")
    for filename, table in (
        (   'periods.json', Period.TABLE  ),
        ('room_types.json', RoomType.TABLE),
        (     'rooms.json', Room.TABLE    ),
    ):
        with current_app.open_resource(f'data/{filename}', 'r') as f:
            insert(table, data_list=json.load(f))
        
    cnx.commit()
    cursor.close()

def set_current_time_zone(cursor):
    offset = datetime.now() - datetime.utcnow()
    hours = offset.total_seconds() // 3600
    minutes = (offset.total_seconds() % 3600) // 60
    sign = '+' if hours >= 0 else '-'
    offset = "%s%02d:%02d" % (sign, abs(hours), minutes)
    cursor.execute(f"SET @@GLOBAL.time_zone = '{offset}';")
    cursor.execute(f"SET @@SESSION.time_zone = '{offset}';")

# ----------------------------------------------------------------
# Database
# ----------------------------------------------------------------

class Setting(schema.Setting):
    @staticmethod
    def timedelta_to_str(td: timedelta) -> str:
        seconds = td.total_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return "%d:%02d:%02d" % (hours, minutes, seconds)
    
    @staticmethod
    def str_to_timedelta(s: str) -> timedelta:
        h, m, s = s.split(':')
        return timedelta(hours=int(h), minutes=int(m), seconds=int(s))

    @staticmethod
    def time_window():
        value = select(Setting.TABLE, {'id': Setting.TIME_WINDOW})[0]['value']
        return Setting.str_to_timedelta(value)
    @staticmethod
    def time_limit():
        value = select(Setting.TABLE, {'id': Setting.TIME_LIMIT})[0]['value']
        return Setting.str_to_timedelta(value)
    @staticmethod
    def max_daily():
        value = select(Setting.TABLE, {'id': Setting.MAX_DAILY})[0]['value']
        return int(value)

    @staticmethod
    def in_time_window(time_slots):
        now = datetime.now()
        time_window = Setting.time_window()
        for ts in time_slots:
            start_time, end_time = ts['start_time'], ts['end_time']
            if not isinstance(start_time, datetime):
                start_time = dateutil.parser.parse(start_time)
            if not isinstance(end_time, datetime):
                end_time = dateutil.parser.parse(end_time)

            if start_time < now or end_time < now:
                return False
            if start_time > now + time_window or end_time > now + time_window:
                return False
        return True
    
    @staticmethod
    def in_time_limit(time_slots):
        time_limit = Setting.time_limit()
        for ts in time_slots:
            start_time, end_time = ts['start_time'], ts['end_time']
            if not isinstance(start_time, datetime):
                start_time = dateutil.parser.parse(start_time)
            if not isinstance(end_time, datetime):
                end_time = dateutil.parser.parse(end_time)
            if end_time - start_time > time_limit:
                return False
        return True
    
    @staticmethod
    def below_max_daily(username):
        return len(Reservation.today_resvs(username)) < Setting.max_daily()

class Reservation(schema.Reservation):
    @staticmethod
    def get(where=None):
        """`where` may contain `date` as `YYYY-MM-DD`"""
        date = where.pop('date', None)
        if date:
            where['DATE(start_time)'] = date
        return select(Reservation.TABLE, where, order_by=['start_time', 'end_time'])
    
    @staticmethod
    def insert(data):
        """`data` must contain `time_slots` as a list of dicts"""
        time_slots = data.pop('time_slots')
        cnx = get_cnx(); cursor = cnx.cursor()
        try:
            cursor.execute(f"""
                INSERT INTO {Reservation.RESV_TABLE} ({', '.join(data.keys())})
                VALUES ({', '.join(['%s'] * len(data))})
            """, (*data.values(),))
            resv_id = cursor.lastrowid
            username = data['username']
            cursor.executemany(f"""
                INSERT INTO {Reservation.TS_TABLE} (resv_id, username, start_time, end_time)
                VALUES ({resv_id}, '{username}', %s, %s)
            """, [(ts['start_time'], ts['end_time']) for ts in time_slots])
        except Exception as e:
            cnx.rollback(); raise e
        else:
            cnx.commit()
        finally:
            cursor.close()
        return resv_id
    
    @staticmethod
    def update(resv_id, username, slot_id=None, **data):
        table = Reservation.RESV_TABLE
        where = {'resv_id': resv_id, 'username': username}
        if slot_id:
            where['slot_id'] = slot_id
            table = Reservation.TS_TABLE
            print(data)
        update(table, data, where)

    @staticmethod
    def today_resvs(username):
        where = {'username': username, 'DATE(create_time)': date.today()}
        return select(Reservation.RESV_TABLE, where, order_by=['create_time'])

class User(schema.User):
    @staticmethod
    def get(username=None, where=None):
        cols = ['username', 'name', 'email', 'role']
        where = where or {}
        if username:
            where['username'] = username
            return select(User.TABLE, where, cols)[0]
        else:
            return select(User.TABLE, where, cols)
        
    @staticmethod
    def get_password(username):
        return select(User.TABLE, {'username': username}, ['password'])[0]['password']
    
    @staticmethod
    def update(username, name=None, password=None, email=None, role=None):
        data = {}
        if name: data['name'] = name
        if password: data['password'] = password
        if email: data['email'] = email
        if role: data['role'] = role
        update(User.TABLE, data, {'username': username})

class Session(schema.Session):
    @staticmethod
    def current():
        """Get the current session."""
        res = select(Session.TABLE, {'is_current': 1}, order_by=['start_time', 'end_time'])
        return res[0] if res else None
    
    @staticmethod
    def get(where=None):
        return select(Session.TABLE, where, order_by=['start_time', 'end_time'])
    
class Room(schema.Room):
    @staticmethod
    def available(room_id):
        # return select(Room.TABLE, {'room_id': room_id})[0]['status'] == RoomStatus.AVAILABLE
        room = select(Room.TABLE, {'room_id': room_id})[0]
        print(room)
        return room['status'] == RoomStatus.AVAILABLE

class Period(schema.Period):
    @staticmethod
    def get(where=None):
        res = select(Period.TABLE, where, order_by=['start_time', 'end_time'])
        for r in res:
            r['start_time'] = Setting.timedelta_to_str(r['start_time'])
            r['end_time'] = Setting.timedelta_to_str(r['end_time'])
        return res
    
    @staticmethod
    def is_comb_of_periods(time_slots):
        """Check if the time range is a combination of consecutive periods"""
        sql = lambda start, end: f"""
            SELECT SUM(TIME_TO_SEC(TIMEDIFF(p.end_time, p.start_time)))
            FROM {Period.TABLE} p
            WHERE p.period_id NOT IN (
                SELECT p2.period_id FROM {Period.TABLE} p2
                WHERE p2.end_time<=TIME('{start}')
                OR p2.start_time>=TIME('{end}')
            );
            """
        cnx = get_cnx(); cursor = cnx.cursor()
        for ts in time_slots:
            start_time = ts['start_time']
            end_time = ts['end_time']
            if not isinstance(start_time, datetime):
                start_time = dateutil.parser.parse(start_time)
            if not isinstance(end_time, datetime):
                end_time = dateutil.parser.parse(end_time)

            start_time = timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=start_time.second)
            end_time = timedelta(hours=end_time.hour, minutes=end_time.minute, seconds=end_time.second)

            if start_time > end_time:
                return False 
            
            cursor.execute(sql(str(start_time), str(end_time)))
            total = cursor.fetchone()[0]
            if total != (end_time - start_time).total_seconds():
                return False
        return True

class Notice(schema.Notice): 
    @staticmethod
    def get(where=None):
        return select(Notice.TABLE, where, order_by=['update_time', 'create_time'])

class RoomType(schema.RoomType): pass
class UserRole(schema.UserRole): pass
class Language(schema.Language): pass
class SecuLevel(schema.SecuLevel): pass
class ResvStatus(schema.ResvStatus): pass
class RoomStatus(schema.RoomStatus): pass

# ----------------------------------------------------------------
# Database basic operations
# ----------------------------------------------------------------
def select(
        table, 
        where: Union[dict, str]=None, 
        columns: list=None, 
        order_by: list=None,
        order: str="ASC",
    ):
    """
    Select data from a `table`.
    `where` can be a dict or a string. If it is a dict, elements will be joined by "AND".
    `columns` is a list of columns to be selected. If it is None, all columns will be selected.
    `order_by` is a list of columns to be ordered by. 
    """
    sql = f"SELECT {'*' if columns is None else ', '.join(columns)} FROM {table}"
    if where is not None:
        if isinstance(where, str) and where.strip() != "":
            sql += f" WHERE {where}"
        elif isinstance(where, dict) and where != {}:
            sql += " WHERE " + " AND ".join([f"{k}=%s" for k in where])
    if order_by is not None and order_by != []:
        sql += f" ORDER BY {' ,'.join(order_by)}"
        if order is not None and order != "":
            sql += f" {order}"
    sql += ";"

    cnx = get_cnx(); cursor = cnx.cursor(dictionary=True)
    cursor.execute(sql, (*where.values(),) if where is not None and where != {} else None)
    data_list = cursor.fetchall()
    
    # for data in data_list:
    #     for key in data:
    #         if isinstance(data[key], (datetime, time)): 
    #             data[key] =  data[key].isoformat()
    #         elif isinstance(data[key], timedelta):
    #             data[key] = str(data[key])
    cnx.commit(); cursor.close()
    return data_list

def insert(table, data_list):
    """If a table has auto increment primary key, it will return the last inserted ids"""
    cnx = get_cnx(); cursor = cnx.cursor()
    last_ids = []
    affected_rows = []
    for data in data_list:
        cursor.execute(f"""
            INSERT INTO {table} ({', '.join(data.keys())}) 
            VALUES ({', '.join(['%s']*len(data))});
        """, (*data.values(),))
        last_ids.append(cursor.lastrowid)
        affected_rows.append(cursor.rowcount)
    cnx.commit(); cursor.close()
    return {"last_ids": last_ids, "affected_rows": affected_rows}

def delete(table, where=None):
    cnx = get_cnx(); cursor = cnx.cursor()
    if where is not None and where != {}:
        cursor.execute(f"""
            DELETE FROM {table} 
            WHERE {' AND '.join([f'{name} = %s' for name in where])};
        """, (*where.values(),))
    else: cursor.execute(f"DELETE FROM {table};")
    cnx.commit(); cursor.close()
    return cursor.rowcount

def update(table, data, where=None):
    cnx = get_cnx(); cursor = cnx.cursor()
    if  where is not None and where != {}:
        cursor.execute(f"""
            UPDATE {table} SET {', '.join([f'{key} = %s' for key in data])}
            WHERE {' AND '.join([f'{name} = %s' for name in where])};
        """, (*data.values(), *where.values(),))
    else:
        cursor.execute(f"""
            UPDATE {table} SET {', '.join([f'{key} = %s' for key in data])};
        """, (*data.values(),))
    cnx.commit(); cursor.close()
    return cursor.rowcount
