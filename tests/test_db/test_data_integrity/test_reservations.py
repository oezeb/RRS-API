"""
Test Reservations data integrity
================================
Updating room_id and session_id of a reservation can cause
conflicts with other reservations. Therefore, it is forbidden
to update room_id and session_id of a reservation.

Reservation Status and Privacy
------------------------------
The reservation status and privacy tables contain constant
values that are set at the initialization of the database.
Therefore, it is forbidden to insert, delete or update
reservation status and privacy.

Time Slots
----------
The time slots table has the following constraints:
    - start_time < end_time
    - time slots with `pending` or `confirmed` status cannot overlap
    
"""
from mysql.connector import Error

from app import db

def test_resv_status(app):
    with app.app_context():
        # forbidden to insert reservation status
        try:
            db.insert(db.ResvStatus.TABLE, {'status': -1, 'label': 'test'})
            print("Insert reservation status forbidden")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
        
        # forbidden to delete reservation status
        try:
            db.delete(db.ResvStatus.TABLE)
            print("Delete reservation status forbidden")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
        
        # forbidden to update reservation status status
        try:
            db.update(db.ResvStatus.TABLE, data={'status': -1}, status=db.ResvStatus.PENDING)
            print("Update reservation status status forbidden")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'

def test_resv_privacy(app):
    with app.app_context():
        # forbidden to insert reservation privacy
        try:
            db.insert(db.ResvPrivacy.TABLE, {'privacy': -1, 'label': 'test'})
            print("Insert reservation privacy forbidden")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
        
        # forbidden to delete reservation privacy
        try:
            db.delete(db.ResvPrivacy.TABLE)
            print("Delete reservation privacy forbidden")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
        
        # forbidden to update reservation privacy privacy
        try:
            db.update(db.ResvPrivacy.TABLE, data={'privacy': -1}, privacy=db.ResvPrivacy.PUBLIC)
            print("Update reservation privacy privacy forbidden")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'

def test_reservations(app_with_data):
    with app_with_data.app_context():
        # fordidden to update room_id and session_id
        res = db.select(db.User.TABLE)
        assert len(res) > 0
        username = res[0]['username']
        res = db.select(db.Room.TABLE)
        assert len(res) > 1
        room_ids = [r['room_id'] for r in res]
        res = db.select(db.Session.TABLE)
        assert len(res) > 1
        session_ids = [r['session_id'] for r in res]
        res = db.insert(db.Reservation.RESV_TABLE, {
            'username': username,
            'room_id': room_ids[0],
            'session_id': session_ids[0],
            'privacy': db.ResvPrivacy.PUBLIC,
            'title': 'test',
        })
        assert res['rowcount'] == 1
        resv_id = res['lastrowid']
        try:
            db.update(db.Reservation.RESV_TABLE, data={'room_id': room_ids[1]}, resv_id=resv_id)
            print("Update reservation room_id forbidden")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
        try:
            db.update(db.Reservation.RESV_TABLE, data={'session_id': session_ids[1]}, resv_id=resv_id)
            print("Update reservation session_id forbidden")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'

def test_time_slots(app_with_data):
    with app_with_data.app_context():
        pass
