from app import db
from app.util import strptimedelta


def is_combined_periods(start_time, end_time):
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

def room_is_available(room_id):
    res = db.select(db.Room.TABLE, room_id=room_id)
    if not res: return False
    return res[0]['status'] == db.RoomStatus.AVAILABLE

def time_window():
    res = db.select(db.Setting.TABLE, id=db.Setting.TIME_WINDOW)
    return strptimedelta(res[0]['value']) if res else None
    
def time_limit():
    res = db.select(db.Setting.TABLE, id=db.Setting.TIME_LIMIT)
    return strptimedelta(res[0]['value']) if res else None
    
def max_daily():
    res = db.select(db.Setting.TABLE, id=db.Setting.MAX_DAILY)
    return int(res[0]['value']) if res else None


def get_reservations(start_date=None, end_date=None, create_date=None, update_date=None, **kwargs):
    if start_date:  kwargs['DATE(start_time)']  = '%s' % start_date
    if end_date:    kwargs['DATE(end_time)']    = '%s' % end_date
    if create_date: kwargs['DATE(create_time)'] = '%s' % create_date
    if update_date: kwargs['DATE(update_time)'] = '%s' % update_date

    return db.select(db.Reservation.TABLE, order_by=['start_time', 'end_time'], **kwargs)

def insert_reservation(cursor, **data):
    cols = ', '.join(data.keys())
    values = ', '.join(['%s'] * len(data))
    query = f"""
        INSERT INTO {db.Reservation.RESV_TABLE} ({cols}) 
        VALUES ({values})
    """
    cursor.execute(query, tuple(data.values()))
    return cursor.lastrowid

def insert_time_slots(cursor, resv_id, username, slots):
    query = f"""
        INSERT INTO {db.Reservation.TS_TABLE}
        (resv_id, username, status, start_time, end_time)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.executemany(query, [(
        resv_id, 
        username, 
        slot['status'], 
        slot['start_time'], 
        slot['end_time']
    ) for slot in slots])
    return cursor.lastrowid