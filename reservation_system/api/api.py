from reservation_system import db

def get_reservations(**kwargs):
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