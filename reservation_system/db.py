import mysql.connector
import json
from datetime import datetime, time, timedelta

import click
from flask import current_app, g

RESV_TRANS            = "resv_trans"
RESV_STATUS_TRANS     = "resv_status_trans"
RESV_SECU_LEVEL_TRANS = "resv_secu_level_trans"
ROOM_TRANS            = "room_trans"
ROOM_TYPE_TRANS       = "room_type_trans"
ROOM_STATUS_TRANS     = "room_status_trans"
SESSION_TRANS         = "session_trans"
USER_TRANS            = "user_trans"
USER_ROLE_TRANS       = "user_role_trans"
LANGUAGES             = "languages"
TIME_SLOTS            = "time_slots"
RESERVATIONS          = "reservations"
RESV_STATUS           = "resv_status"
RESV_SECU_LEVELS      = "resv_secu_levels"
ROOMS                 = "rooms"
ROOM_TYPES            = "room_types"
ROOM_STATUS           = "room_status"
SESSIONS              = "sessions"
USERS                 = "users"
USER_ROLES            = "user_roles"
PERIODS               = "periods"
RESV_WINDOWS          = "resv_windows"

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

def get_cursor(dictionary=True):
    cnx = get_cnx()
    return cnx.cursor(dictionary=dictionary)

def init_db():
    cnx = get_cnx()
    cursor = cnx.cursor()

    with current_app.open_resource('data/schema.sql') as f:
        for statement in f.read().decode('utf8').split(';'):
            if statement.strip() != "":
                cursor.execute(statement)

    for filename, table in (
        ( 'resv_windows.json', RESV_WINDOWS   ),
        (      'periods.json', PERIODS        ),
        (     'sessions.json', SESSIONS       ),
        (    'languages.json', LANGUAGES      ),
        (   'room_types.json', ROOM_TYPES     ),
        (  'room_status.json', ROOM_STATUS    ),
        (        'rooms.json', ROOMS          ),
        (   'user_roles.json', USER_ROLES     ),
        ('user_roles-zh.json', USER_ROLE_TRANS),
    ):
        with current_app.open_resource(f'data/{filename}', 'r') as f:
            insert(table, data_list=json.load(f))

    cnx.commit()
    cursor.close()

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

# ----------------------------------------------------------------
# Database basic operations
# ----------------------------------------------------------------

def select(table, where: dict=None):
    cursor = get_cursor()
    if where is not None and where != {}:
        cursor.execute(f"""
            SELECT * FROM {table} 
            WHERE {' AND '.join([f'{name} = %s' for name in where])};
        """, (*where.values(),))
    else: 
        cursor.execute(f"SELECT * FROM {table};")

    data_list = cursor.fetchall()
    for data in data_list:
        for key in data:
            if isinstance(data[key], (datetime, time)): 
                data[key] =  data[key].isoformat()
            elif isinstance(data[key], timedelta):
                data[key] = str(data[key])
    
    return data_list

def insert(table, data_list):
    cnx = get_cnx(); cursor = cnx.cursor()
    for data in data_list:
        cursor.execute(f"""
            INSERT INTO {table} ({', '.join(data.keys())}) 
            VALUES ({', '.join(['%s']*len(data))});
        """, (*data.values(),))
    cnx.commit(); cursor.close()

def delete(table, where=None):
    cnx = get_cnx(); cursor = cnx.cursor()
    if where is not None and where != {}:
        cursor.execute(f"""
            DELETE FROM {table} 
            WHERE {' AND '.join([f'{name} = %s' for name in where])};
        """, (*where.values(),))
    else: cursor.execute(f"DELETE FROM {table};")
    cnx.commit(); cursor.close()

def update(table, data, where=None):
    cnx = get_cnx(); cursor = cnx.cursor()
    if  where is not None and where != {}:
        cursor.execute(f"""
            UPDATE {table} SET {', '.join([f'{key} = %s' for key in data])}
            WHERE {' AND '.join([f'{name} = %s' for name in where])};
        """, (*data.values(), *where.values(),))
    else:
        cursor.execute(f"""
            UPDATE {table} SET {', '.join([f'{key} = %s' for key in data['values']])};
        """, (*data.values(),))
    cnx.commit(); cursor.close()

    