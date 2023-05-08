
import json
from typing import Union
from datetime import date, datetime, time, timedelta
import logging
import os
import base64

import mysql.connector
from flask import current_app, g
import click

from reservation_system import schema

logger = logging.getLogger(__name__)

def init_app(app):
    app.teardown_appcontext(close_cnx)
    app.cli.add_command(init_db_command)

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

# ----------------------------------------------------------------
# Database Initialization
# ----------------------------------------------------------------

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
        return "%02d:%02d:%02d" % (hours, minutes, seconds)
    
    @staticmethod
    def str_to_timedelta(s: str) -> timedelta:
        h, m, s = s.split(':')
        return timedelta(hours=int(h), minutes=int(m), seconds=int(s))

    @staticmethod
    def time_window():
        cnx = get_cnx(); cursor = cnx.cursor()
        cursor.execute("""
            SELECT value FROM %s WHERE id = %s
        """ % (Setting.TABLE, Setting.TIME_WINDOW))
        tm = cursor.fetchone()
        cursor.close()
        if tm is None: return None
        return Setting.str_to_timedelta(tm[0])
    
    @staticmethod
    def time_limit():
        cnx = get_cnx(); cursor = cnx.cursor()
        cursor.execute("""
            SELECT value FROM %s WHERE id = %s
        """ % (Setting.TABLE, Setting.TIME_LIMIT))
        tm = cursor.fetchone()
        cursor.close()
        if tm is None: return None
        return Setting.str_to_timedelta(tm[0])
    
    @staticmethod
    def max_daily():
        cnx = get_cnx(); cursor = cnx.cursor()
        cursor.execute("""
            SELECT value FROM %s WHERE id = %s
        """ % (Setting.TABLE, Setting.MAX_DAILY))
        tm = cursor.fetchone()
        cursor.close()
        if tm is None: return None
        return int(tm[0])

class Reservation(schema.Reservation):
    @staticmethod
    def get(where=None, date=None):
        if date: where['DATE(start_time)'] = 'DATE(%s)' % date
        return select(Reservation.TABLE, where, order_by=['start_time', 'end_time'])
    
    @staticmethod
    def insert(data):
        """`data` must contain `time_slots` as a list of dicts"""
        time_slots = data.pop('time_slots')
        if not time_slots:
            raise ValueError("No time slots provided")
        
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
    def update(resv_id, username, data, slot_id=None):
        table = Reservation.RESV_TABLE
        where = {'resv_id': resv_id, 'username': username}
        if slot_id:
            where['slot_id'] = slot_id
            table = Reservation.TS_TABLE
            print(data)
        _update(table, data, where)

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
        _update(User.TABLE, data, {'username': username})

class Session(schema.Session):
    @staticmethod
    def current():
        """Get the current session."""
        res = select(Session.TABLE, {'is_current': 1}, order_by=['start_time', 'end_time'])
        for r in res:
            r['start_time'] = r['start_time'].isoformat(' ')
            r['end_time'] = r['end_time'].isoformat(' ')
        return res[0] if res else None
    
    @staticmethod
    def get(where=None):
        res = select(Session.TABLE, where, order_by=['start_time', 'end_time'])
        for r in res:
            r['start_time'] = r['start_time'].isoformat(' ')
            r['end_time'] = r['end_time'].isoformat(' ')
        return res
    
class Room(schema.Room):
    @staticmethod
    def get(where=None):
        res = select(Room.TABLE, where, order_by=['room_id'])
        for r in res:
            # BLOB image to base64 string
            if r['image']:
                r['image'] = base64.b64encode(r['image']).decode('utf-8')
        return res
    
    @staticmethod
    def insert(data_list):
        for data in data_list:
            if 'image' in data and data['image'] is not None:
                data['image'] = base64.b64decode(data['image'])
        return insert(Room.TABLE, data_list)

    @staticmethod
    def update(data_list):
        for data in data_list:
            if 'image' in data['data'] and data['data']['image'] is not None:
                print(data['data']['image'])
                data['data']['image'] = base64.b64decode(data['data']['image'])
        return update(Room.TABLE, data_list)
    
    @staticmethod
    def is_available(room_id):
        res = select(Room.TABLE, {'room_id': room_id})
        if not res: return False
        return res[0]['status'] == RoomStatus.AVAILABLE


class Period(schema.Period):
    @staticmethod
    def get(where=None):
        res = select(Period.TABLE, where, order_by=['start_time', 'end_time'])
        for r in res:
            r['start_time'] = Setting.timedelta_to_str(r['start_time'])
            r['end_time'] = Setting.timedelta_to_str(r['end_time'])
        return res
    
    @staticmethod
    def is_combined_periods(start_time, end_time):
        """Check if the time range is a combination of consecutive periods"""
        cnx = get_cnx(); cursor = cnx.cursor()
        cursor.execute(f"""
            SELECT SUM(TIME_TO_SEC(TIMEDIFF(p.end_time, p.start_time)))
            FROM {Period.TABLE} p WHERE p.period_id NOT IN (
                SELECT p2.period_id FROM {Period.TABLE} p2 
                WHERE p2.start_time >= TIME(%s) 
                    OR p2.end_time <= TIME(%s)
            )
        """, (end_time, start_time))
        res = cursor.fetchone()
        cursor.close()
        return res[0] == (end_time - start_time).total_seconds()

class Notice(schema.Notice): 
    @staticmethod
    def get(where=None):
        return select(Notice.TABLE, where, order_by=['update_time', 'create_time'])

class RoomType(schema.RoomType): pass
class UserRole(schema.UserRole): pass
class Language(schema.Language): pass
class ResvPrivacy(schema.ResvPrivacy): pass
class ResvStatus(schema.ResvStatus): pass
class RoomStatus(schema.RoomStatus): pass

# ----------------------------------------------------------------
# Database CRUD operations
# ----------------------------------------------------------------

def insert(table, data_list):
    cnx = get_cnx(); cursor = cnx.cursor()
    lastrowid, rowcount = [], []

    for data in data_list:
        cursor.execute(f"""
            INSERT INTO {table} ({', '.join(data.keys())}) 
            VALUES ({', '.join(['%s']*len(data))});
        """, tuple(data.values()))
        lastrowid.append(cursor.lastrowid)
        rowcount.append(cursor.rowcount)
    cnx.commit(); cursor.close()
    return {"lastrowid": lastrowid, "rowcount": rowcount}

def select(table, where=None, 
    columns: list=None, order_by: list=None, order: str="ASC"):
    """
    `where` can be a dict or a string. If it is a dict, elements will be joined by "AND".
    `columns` is a list of columns to be selected. If it is None, all columns will be selected.
    """
    sql = f"SELECT {'*' if columns is None else ', '.join(columns)} FROM {table}"
    if where is not None:
        if isinstance(where, str) and where.strip() != "":
            sql += f" WHERE {where}"
        elif len(where) > 0:
            sql += " WHERE " + " AND ".join([f"{k}=%s" for k in where])
    if order_by is not None and order_by != []:
        sql += f" ORDER BY {' ,'.join(order_by)}"
        if order is not None and order != "":
            sql += f" {order}"
    sql += ";"

    cnx = get_cnx(); cursor = cnx.cursor(dictionary=True)
    cursor.execute(sql, (*where.values(),) if where is not None and where != {} else None)
    data_list = cursor.fetchall()
    
    cnx.commit(); cursor.close()
    return data_list

def update(table, data_list):
    cnx = get_cnx(); cursor = cnx.cursor()
    rowcount = []
    for data in data_list:
        where = data['where'] if 'where' in data else None
        rowcount.append(__update(cursor, table, data['data'], where)['rowcount'])

    cnx.commit(); cursor.close()
    return {"rowcount": rowcount}

def delete(table, where_list):
    cnx = get_cnx(); cursor = cnx.cursor()
    rowcount = []
    for where in where_list:
        rowcount.append(__delete(cursor, table, where)['rowcount'])

    cnx.commit(); cursor.close()
    return {"rowcount": rowcount}

# update with cursor without commit
def __update(cursor, table, data, where=None):
    if  where is not None and where != {}:
        cursor.execute(f"""
            UPDATE {table} SET {', '.join([f'{key} = %s' for key in data])}
            WHERE {' AND '.join([f'{name} = %s' for name in where])};
        """, (*data.values(), *where.values(),))
    else:
        cursor.execute(f"""
            UPDATE {table} SET {', '.join([f'{key} = %s' for key in data])};
        """, (*data.values(),))
    return {"rowcount": cursor.rowcount}

# single update
def _update(table, data, where=None):
    cnx = get_cnx(); cursor = cnx.cursor()
    rowcount = __update(cursor, table, data, where)
    cnx.commit(); cursor.close()
    return rowcount

# delete with cursor without commit
def __delete(cursor, table, where=None):
    if where is not None and where != {}:
        cursor.execute(f"""
            DELETE FROM {table} 
            WHERE {' AND '.join([f'{name} = %s' for name in where])};
        """, (*where.values(),))
    else: cursor.execute(f"DELETE FROM {table};")
    return {"rowcount": cursor.rowcount}

# single delete
def _delete(table, where=None):
    cnx = get_cnx(); cursor = cnx.cursor()
    rowcount = __delete(cursor, table, where)
    cnx.commit(); cursor.close()
    return rowcount