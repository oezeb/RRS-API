"""
Test the data integrity of the periods table
============================================

The periods table has the following constraints:
    - start_time < end_time
    - '00:00:00' <= start_time < end_time <= '23:59:59'
    - No overlapping periods
"""
from datetime import timedelta
from mysql.connector import Error

from app import db

def test_periods(app):
    with app.app_context():
        # Test: start_time < end_time
        try:
            db.insert(db.Period.TABLE, {'start_time': '12:00:00', 'end_time': '10:00:00'})
            print("Insert period start_time > end_time")
            assert False
        except Error as e:
            assert e.sqlstate == 'HY000'
        
        # Test: '00:00:00' <= start_time < end_time <= '23:59:59'
        try:
            db.insert(db.Period.TABLE, {'start_time': '24:00:00', 'end_time': '10:00:00'})
            print("Insert period start_time out of range")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
        
        try:
            db.insert(db.Period.TABLE, {'start_time': '00:00:00', 'end_time': '24:00:00'})
            print("Insert period end_time out of range")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'

        # Test: No overlapping periods at insert
        # First insert a period
        period = {
            'start_time': timedelta(hours=8),
            'end_time': timedelta(hours=10),
        }
        res = db.insert(db.Period.TABLE, period)
        assert res['rowcount'] == 1
        period['period_id'] = res['lastrowid']

        # Now try to insert some overlapping periods
        for i in range(3):
            _period = {'start_time': period['start_time'] + timedelta(hours=i-1)}
            for j in range(3):
                _period['end_time'] = period['end_time'] + timedelta(hours=j-1)
                try:
                    db.insert(db.Period.TABLE, _period)
                    print(f"Insert period overlapping: {_period}")
                    assert False
                except Error as e:
                    assert e.sqlstate == '45000'

        # Test: No overlapping periods at update
        # First insert another period
        period2 = {
            'start_time': period['end_time'],
            'end_time': period['end_time'] + timedelta(hours=2),
        }
        res = db.insert(db.Period.TABLE, period2)
        assert res['rowcount'] == 1
        period2['period_id'] = res['lastrowid']

        # Now try to update the first period to overlap with the second
        try:
            db.update(db.Period.TABLE, data={'end_time': period2['start_time'] + timedelta(hours=1)}, period_id=period['period_id'])
            print("Update period overlapping")
            assert False
        except Error as e:
            assert e.sqlstate == '45000'
