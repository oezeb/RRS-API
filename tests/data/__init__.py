import base64
import json
import os
import typing

from werkzeug.security import generate_password_hash

from app import db

path = os.path.dirname(__file__)

get_notices    = lambda: json.load(open(os.path.join(path, f'{db.Notice.TABLE}.json')))
get_periods    = lambda: json.load(open(os.path.join(path, f'{db.Period.TABLE}.json')))
get_room_types = lambda: json.load(open(os.path.join(path, f'{db.RoomType.TABLE}.json')))
get_rooms      = lambda: json.load(open(os.path.join(path, f'{db.Room.TABLE}.json')))
get_sessions   = lambda: json.load(open(os.path.join(path, f'{db.Session.TABLE}.json')))
get_users      = lambda: json.load(open(os.path.join(path, f'{db.User.TABLE}.json')))

def insert_data(
        only: typing.Iterable[str] = (),
        exclude: typing.Iterable[str] = (),
    ):
    """
    Insert data into database.
    """
    # Room data depends on RoomType data
    if db.Room.TABLE in only and db.RoomType.TABLE not in only:
        only += (db.RoomType.TABLE,)
    if db.RoomType.TABLE in exclude and db.Room.TABLE not in exclude:
        exclude += (db.Room.TABLE,)
    # Notice data depends on User data
    if db.Notice.TABLE in only and db.User.TABLE not in only:
        only += (db.User.TABLE,)
    if db.User.TABLE in exclude and db.Notice.TABLE not in exclude:
        exclude += (db.Notice.TABLE,)

    cnx = db.get_cnx(); cursor = cnx.cursor()
    for table, data in (
        (   db.Period.TABLE, get_periods()    ),
        (   db.RoomType.TABLE, get_room_types() ),
        (   db.Room.TABLE, get_rooms()      ),
        (   db.Session.TABLE, get_sessions()   ),
        (   db.User.TABLE, get_users()      ),
        (   db.Notice.TABLE, get_notices()    ),
    ):
        if only and table not in only:
            continue
        if exclude and table in exclude:
            continue
        
        
        if table == db.User.TABLE:
            for row in data:
                row['password'] = generate_password_hash(row['password'])
        
        if table == db.Room.TABLE:
            for row in data:
                if 'image' in row:
                    row['image'] = base64.b64decode(row['image'])

        for row in data:
            cols = ', '.join(row.keys())
            values = ', '.join(['%s'] * len(row))
            query = f"INSERT INTO {table} ({cols}) VALUES ({values})"
            cursor.execute(query, tuple(row.values()))
            assert cursor.rowcount == 1
    cnx.commit(); cursor.close()
    
def insert_resv(start_time, end_time, status, **resv):
    cnx = db.get_cnx(); cursor = cnx.cursor()

    time_slot = {
        'start_time': start_time,
        'end_time': end_time,
        'status': status,
    }

    if 'slot_id' in resv:
        time_slot['slot_id'] = resv.pop('slot_id')

    try:
        cols = ', '.join(resv.keys())
        values = ', '.join(['%s'] * len(resv))
        query = f"INSERT INTO {db.Reservation.RESV_TABLE} ({cols}) VALUES ({values})"
        cursor.execute(query, tuple(resv.values()))
        assert cursor.rowcount == 1

        resv_id = cursor.lastrowid
        time_slot['resv_id'] = resv_id
        time_slot['username'] = resv['username']
        
        cols = ', '.join(time_slot.keys())
        values = ', '.join(['%s'] * len(time_slot))
        query = f"INSERT INTO {db.Reservation.TS_TABLE} ({cols}) VALUES ({values})"
        cursor.execute(query, tuple(time_slot.values()))
        assert cursor.rowcount == 1
    except Exception as e:
        print(e)
        cnx.rollback()
        raise e
    else:
        cnx.commit()
    finally:
        cursor.close()

    return resv_id

