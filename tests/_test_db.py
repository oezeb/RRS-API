import os, json
import logging
from datetime import datetime, timedelta, time, date
from mysql.connector import Error
import random

from mrbs import db

logging.basicConfig(level=logging.DEBUG, filename=os.path.join(os.path.dirname(__file__), 'test.log'))
logger = logging.getLogger(__name__)

def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('reservation_system.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called

# ================================================
# MySQL Database Layer: schema.sql
# ================================================
def test_periods_check(app):
    with app.app_context():
        # start_time < end_time
        cnx = db.get_cnx(); cursor = cnx.cursor(dictionary=True)
        def insert(start, end):
            cursor.execute(f"""
                INSERT INTO {db.Period.TABLE}
                (start_time, end_time) VALUES (%s, %s)
            """, (start, end))
        def try_insert(start, end):
            try:
                insert(start, end)
                assert False
            except Error as e:
                logger.debug(f"error: {e}")
                assert e.sqlstate == 'HY000'
        def try_update_end(id, end):
            try:
                cursor.execute(f"""
                    UPDATE {db.Period.TABLE}
                    SET end_time = %s
                    WHERE period_id = %s
                """, (end, id))
                assert False
            except Error as e:
                logger.debug(f"error: {e}")
                assert e.sqlstate == 'HY000'

        cursor.execute(f"DELETE FROM {db.Period.TABLE}")
        start, end = "08:00", "09:00"
        logger.debug(f"inserting valid period: {start}-{end}")
        insert(start, end)
        assert cursor.rowcount == 1
        id = cursor.lastrowid
        logger.debug(f"period id={id} inserted")
        logger.debug(f"trying to insert invalid period: {end}-{start}")
        try_insert(end, start)
        logger.debug(f"trying to insert invalid period: {start}-{start}")
        try_insert(start, start)
        new_end = "07:00"
        logger.debug(f"trying to update period: {start}-{end} to invalid period: {start}-{new_end}")
        try_update_end(id, new_end)

        cnx.rollback(); cursor.close()

def test_sessions_check(app):
    with app.app_context():
        # start_time < end_time
        cnx = db.get_cnx(); cursor = cnx.cursor(dictionary=True)
        def insert(start, end):
            cursor.execute(f"""
                INSERT INTO {db.Session.TABLE}
                (name, is_current, start_time, end_time) 
                VALUES ('fake', 0, %s, %s)
            """, (start, end))
        def try_insert(start, end):
            try:
                insert(start, end)
                assert False
            except Error as e:
                logger.debug(f"error: {e}")
                assert e.sqlstate == '45000' or e.sqlstate == 'HY000'
        def try_update_end(id, end):
            try:
                logger.debug(f"updating id={id} to end_time={end} ")
                cursor.execute(f"""
                    UPDATE {db.Session.TABLE}
                    SET end_time = %s
                    WHERE session_id = %s
                """, (end, id))
                assert False
            except Error as e:
                logger.debug(f"error: {e}")
                assert e.sqlstate == '45000' or e.sqlstate == 'HY000'

        cursor.execute(f"DELETE FROM {db.Session.TABLE}")
        start, end = "2020-01-01 08:00:00", "2020-06-01 09:00:00"
        logger.debug(f"inserting valid session: {start}-{end}")
        insert(start, end)
        assert cursor.rowcount == 1
        id = cursor.lastrowid
        logger.debug(f"session id={id} inserted")
        logger.debug(f"trying to insert invalid session: {end}-{start}")
        try_insert(end, start)
        logger.debug(f"trying to insert invalid session: {start}-{start}")
        try_insert(start, start)
        new_end = "2019-01-01 07:00:00"
        logger.debug(f"trying to update session: {start}-{end} to invalid session: {start}-{new_end}")
        try_update_end(id, new_end)

        cnx.rollback(); cursor.close()

def test_users_check(app):
    with app.app_context():
        # username and name can't be empty string
        cnx = db.get_cnx(); cursor = cnx.cursor(dictionary=True)
        def insert(username, name):
            cursor.execute(f"""
                INSERT INTO {db.User.TABLE}
                (username, name, password, role)
                VALUES (%s, %s, 'password', 0)
            """, (username, name))
        logger.debug("inserting empty username")
        try:
            insert('', 'name')
            assert False
        except Error as e:
            logger.debug(f"error: {e}")
            assert e.sqlstate == 'HY000'
        logger.debug("inserting empty name")
        try:
            insert('username', '')
            assert False
        except Error as e:
            logger.debug(f"error: {e}")
            assert e.sqlstate == 'HY000'
        cnx.rollback(); cursor.close()

def test_notices_check(app):
    with app.app_context():
        # create_time and update_time auto set
        # and create_time <= update_time
        cnx = db.get_cnx(); cursor = cnx.cursor(dictionary=True)
        def get(id):
            cursor.execute(f"""
                SELECT * FROM {db.Notice.TABLE}
                WHERE notice_id = %s
            """, (id,))
            return cursor.fetchone()
        logger.debug("inserting notice")
        cursor.execute(f"""
            INSERT INTO {db.Notice.TABLE}
            (username, title, content) VALUES ('admin', %s, %s)
        """, ('title', 'content'))
        assert cursor.rowcount == 1
        id = cursor.lastrowid
        data = get(id)
        assert data['update_time'] is None and data['create_time'] is not None
        logger.debug("updating notice")
        cursor.execute(f"""
            UPDATE {db.Notice.TABLE}
            SET title = %s, content = %s
            WHERE notice_id = %s
        """, ('new title', 'new content', id))
        assert cursor.rowcount == 1
        data = get(id)
        assert data['update_time'] is not None and data['create_time'] is not None
        assert data['update_time'] >= data['create_time']
        cnx.rollback(); cursor.close()

def test_reservations_check(app):
    with app.app_context():
        # create_time and update_time auto set
        # and create_time <= update_time
        cnx = db.get_cnx(); cursor = cnx.cursor(dictionary=True)
        def get(id):
            cursor.execute(f"""
                SELECT * FROM {db.Reservation.RESV_TABLE}
                WHERE resv_id = %s
            """, (id,))
            return cursor.fetchone()
        logger.debug("inserting reservation")
        cursor.execute(f"""
            INSERT INTO {db.Reservation.RESV_TABLE}
            (username, room_id, secu_level, session_id, status, title)
            VALUES ('admin', 1, 0, 1, 0, 'title')
        """)
        assert cursor.rowcount == 1
        id = cursor.lastrowid
        data = get(id)
        assert data['update_time'] is None and data['create_time'] is not None
        logger.debug("updating reservation")
        cursor.execute(f"""
            UPDATE {db.Reservation.RESV_TABLE}
            SET title = %s
            WHERE resv_id = %s
        """, ('new title', id))
        assert cursor.rowcount == 1
        data = get(id)
        assert data['update_time'] is not None and data['create_time'] is not None
        assert data['update_time'] >= data['create_time']
        cnx.rollback(); cursor.close()

# ================================================
# Application Layer: schema.py and db.py
# ================================================

def test_select(app):
    with app.app_context():
        res = db.select(db.RoomStatus.TABLE)
        assert len(res) == 2
        assert set([db.RoomStatus.AVAILABLE, db.RoomStatus.UNAVAILABLE]) == set([r['status'] for r in res])
        res = db.select(db.ResvStatus.TABLE, where={'status': db.ResvStatus.CANCELLED})
        assert len(res) == 1
        assert res[0]['status'] == db.ResvStatus.CANCELLED
        res = db.select(db.ResvStatus.TABLE, where={'status': db.ResvStatus.CONFIRMED}, columns=['status'])
        assert len(res) == 1
        assert res[0]['status'] == db.ResvStatus.CONFIRMED
        assert len(res[0]) == 1
        res = db.select(db.Setting.TABLE, order_by=['id'])
        assert len(res) == 3
        assert res[0]['id'] < res[1]['id'] < res[2]['id']
        res = db.select(db.Setting.TABLE, order_by=['id'], order='DESC')
        assert len(res) == 3
        assert res[0]['id'] > res[1]['id'] > res[2]['id']


def test_insert(app):
    with app.app_context():
        users = [
            {
                'username': 'test1',
                'name': 'Test User 1',
                'password': 'test1',
                'role': db.UserRole.RESTRICTED,
            },
            {
                'username': 'test2',
                'name': 'Test User 2',
                'password': 'test2',
                'role': db.UserRole.BASIC,
                'email': 'fake@mail.com',
            },
        ]
        res = db.insert(db.User.TABLE, users)
        assert len(res['affected_rows']) == len(res['last_ids']) == 2
        logger.debug(res)
        assert all([id==0 for id in res['last_ids']])
        periods = [
            {
                'start_time': "12:00",
                'end_time': "13:00",
            },
            {
                'start_time': "13:00",
                'end_time': "14:00",
            },
        ]
        res = db.insert(db.Period.TABLE, periods)
        assert len(res['affected_rows']) == len(res['last_ids']) == 2
        assert all([id!=0 for id in res['last_ids']])

def test_delete(app):
    with app.app_context():
        res = db.delete(db.Session.TABLE, where={'session_id': 1})
        assert res == 1
        ss = db.select(db.Session.TABLE, where={'session_id': 1})
        assert len(ss) == 0
        db.delete(db.Period.TABLE)
        periods = db.select(db.Period.TABLE)
        assert len(periods) == 0

def test_update(app):
    with app.app_context():
        res = db.update(
            db.RoomStatus.TABLE,
            {'description': 'available'},
            where={'status': db.RoomStatus.AVAILABLE},
        )
        assert res == 1
        res = db.update(
            db.RoomStatus.TABLE,
            {'description': 'fake'},
        )
        assert res == 2

# Triggers
# ------------------------------------------------

def test_immutable_trigger(app):
    with app.app_context():
        logger.debug("updating languages")
        assert db.update(
            db.Language.TABLE,
            {'name': 'ENGLISH'},
            where={'lang_code': db.Language.EN},
        ) == 1

        def update_desc(table, id, id_col, desc):
            logger.debug(f"updating {table}")
            assert db.update(
                table,
                {'description': desc},
                where={id_col: id},
            ) == 1

        update_desc(db.SecuLevel .TABLE, db.SecuLevel    .PUBLIC, 'secu_level', 'public'    )
        update_desc(db.RoomStatus.TABLE, db.RoomStatus.AVAILABLE,     'status', 'available' )
        update_desc(db.Setting   .TABLE, db.Setting  .TIME_LIMIT,         'id', 'time limit')
        update_desc(db.UserRole  .TABLE, db.UserRole      .ADMIN,       'role', 'admin'     )

        # other data like id can't be edited or deleted
        def try_update(table, id, id_col, data):
            logger.debug(f"try updating {table} with {data}")
            try:
                db.update(table, data, where={id_col: id})
                res = db.select(table, where={id_col: id})
                logger.debug(f"result: {res}")
                assert False
            except Error as e:
                logger.debug(f"error: {e}")
                assert e.sqlstate == '45000'

        try_update(db.Language.TABLE, db.Language.EN, 'lang_code', {'lang_code': 'EN'})
        try_update(db.SecuLevel.TABLE, db.SecuLevel.PUBLIC, 'secu_level', {'secu_level': 1})
        try_update(db.RoomStatus.TABLE, db.RoomStatus.AVAILABLE, 'status', {'status': 0})
        try_update(db.Setting.TABLE, db.Setting.TIME_LIMIT, 'id', {'id': 1})
        try_update(db.UserRole.TABLE, db.UserRole.ADMIN, 'role', {'role': 0})
        
        def try_delete(table, id, id_col):
            logger.debug(f"try deleting {id_col} from {table}")
            try:
                db.delete(table, where={id_col: id})
                assert False
            except Error as e:
                assert e.sqlstate == '45000'

        try_delete(db.Language.TABLE, db.Language.EN, 'lang_code')
        try_delete(db.SecuLevel.TABLE, db.SecuLevel.PUBLIC, 'secu_level')
        try_delete(db.RoomStatus.TABLE, db.RoomStatus.AVAILABLE, 'status')
        try_delete(db.Setting.TABLE, db.Setting.TIME_LIMIT, 'id')
        try_delete(db.UserRole.TABLE, db.UserRole.ADMIN, 'role')
        
        def try_insert(table, data):
            logger.debug(f"try inserting into {table}")
            try:
                db.insert(table, [data])
                assert False
            except Error as e:
                assert e.sqlstate == '45000'

        try_insert(db.Language.TABLE, {'lang_code': 'FR', 'name': 'French'})
        try_insert(db.SecuLevel.TABLE, {'secu_level': -1, 'label': 'fake'})
        try_insert(db.RoomStatus.TABLE, {'status': -1, 'label': 'fake'})
        try_insert(db.Setting.TABLE, {'id': -1, 'description': 'fake'})
        try_insert(db.UserRole.TABLE, {'role': -1, 'label': 'fake'})

def test_settings_trigger(app):
    with app.app_context():
        # time window and time limit format HH:MM:SS
        # max daily should be integer
        time_window = '48:00:00'
        logger.debug(f"update time window to {time_window}")
        res = db.update(db.Setting.TABLE, {'value': time_window}, where={'id': db.Setting.TIME_WINDOW})
        assert res == 1
        # invalid time window
        for time_window in ('48:00:00:00', '48:00', '48', 'fake'):
            logger.debug(f"update time window to {time_window}")
            try:
                res = db.update(db.Setting.TABLE, {'value': time_window}, where={'id': db.Setting.TIME_WINDOW})
                assert False
            except Error as e:
                logger.debug(f"error: {e}")
                assert e.sqlstate == '45000'

        time_limit = '03:00:00'
        logger.debug(f"update time limit to {time_limit}")
        res = db.update(db.Setting.TABLE, {'value': time_limit}, where={'id': db.Setting.TIME_LIMIT})
        assert res == 1
        # invalid time limit
        for time_limit in ('03:00:00:00', '03:00', '03', 'fake'):
            logger.debug(f"update time limit to {time_limit}")
            try:
                res = db.update(db.Setting.TABLE, {'value': time_limit}, where={'id': db.Setting.TIME_LIMIT})
                assert False
            except Error as e:
                logger.debug(f"error: {e}")
                assert e.sqlstate == '45000'

        max_daily = '8'
        logger.debug(f"update max daily to {max_daily}")
        res = db.update(db.Setting.TABLE, {'value': max_daily}, where={'id': db.Setting.MAX_DAILY})
        assert res == 1
        # invalid max daily
        for max_daily in ('8.0', 'fake'):
            logger.debug(f"update max daily to {max_daily}")
            try:
                res = db.update(db.Setting.TABLE, {'value': max_daily}, where={'id': db.Setting.MAX_DAILY})
                assert False
            except Error as e:
                logger.debug(f"error: {e}")
                assert e.sqlstate == '45000'

def test_periods_trigger(app):
    with app.app_context():
        # start_time and end_time can't overlap
        # periods must be between 00:00 and 23:59
        def insert(start, end):
            logger.debug(f"inserting period {start}-{end}")
            return db.insert(db.Period.TABLE, [{'start_time': start, 'end_time': end}])
        def delete(id):
            logger.debug(f"deleting period id={id}")
            return db.delete(db.Period.TABLE, where={'period_id': id})
        def try_insert(start, end):
            logger.debug(f"trying to insert {start}-{end}")
            try:
                insert(start, end)
                assert False
            except Error as e:
                logger.debug(f"error: {e}")
                assert e.sqlstate == '45000'
        def try_update(id, data):
            try:
                logger.debug(f"trying to update period id={id} to end_time={end} ")
                db.update(db.Period.TABLE, data, where={'period_id': id})
                assert False
            except Error as e:
                assert e.sqlstate == '45000'

        db.delete(db.Period.TABLE)
        # insert periods
        ids = []
        for start, end in [
            ("08:00", "09:00"),
            ("09:00", "09:45"),
            ("10:00", "11:00"),
            ("11:00", "11:45"),
        ]:
            res = insert(start, end)
            assert len(res['last_ids']) == 1
            ids.append(res['last_ids'][0])
        assert len(ids) == 4
        logger.debug(f"period ids={ids} inserted")

        # invalid
        # 08:00-09:00 and 09:00-09:45
        logger.debug(f"trying to insert invalid periods")
        for start in ["07:55", "08:00", "08:05"]:
            for end in ["08:55", "09:00", "09:30", "09:45", "09:50"]:
                try_insert(start, end)
        # 09:00-09:45 and 10:00-11:00 (15 min gap in between)
        for start in ["08:55", "09:00", "09:05"]:
            for end in ["09:40", "09:45", "09:50", "10:00", "10:05", "11:00", "11:05"]:
                try_insert(start, end)
        
        # valid
        logger.debug(f"insert valid periods")
        for start, end in [
            ("07:00", "08:00"),
            ("09:45", "10:00"),
            ("11:45", "12:00"),
            ("13:00", "14:00"),
        ]:
            res = insert(start, end)
            assert len(res['last_ids']) == 1
            id = res['last_ids'][0]
            assert id > 0
            res = delete(id)
            assert res == 1
        
        # invalid update
        logger.debug(f"trying to update periods to invalid values")
        # 08:00-09:00 and 09:00-09:45
        # 08:00-09:00 `id`=ids[0]
        for end in ["09:05", "09:45", "09:50"]:
            try_update(ids[0], {'end_time': end})
        
        # 09:00-09:45 and 10:00-11:00 (15 min gap in between)
        # 09:00-09:45 `id`=ids[1]
        for end in ["10:05", "11:00", "11:05"]:
            try_update(ids[1], {'end_time': end})

        # not between 00:00 and 23:59
        logger.debug(f"trying to insert periods not between 00:00 and 23:59")
        for start, end in [
            ("-01:00", "00:00"),
            ("08:00", "25:00"),
        ]:
            try_insert(start, end)

        logger.debug(f"trying to update periods to not between 00:00 and 23:59")
        # 08:00-09:00 and 09:00-09:45
        # 08:00-09:00 `id`=ids[0]
        try_update(ids[0], {'start_time': '-01:00'})
        try_update(ids[0], {'end_time': '25:00'})

def test_sessions_trigger(app):
    with app.app_context():
        # start_time,  end_time can't overlap
        def insert(start, end):
            logger.debug(f"inserting session {start}-{end}")
            return db.insert(db.Session.TABLE, [{'name': 'fake', 'start_time': start, 'end_time': end}])
        def delete(id):
            logger.debug(f"deleting session id={id}")
            return db.delete(db.Session.TABLE, where={'session_id': id})
        def try_insert(start, end):
            logger.debug(f"trying to insert {start}-{end}")
            try:
                insert(start, end)
                assert False
            except Error as e:
                logger.debug(f"error: {e}")
                assert e.sqlstate == '45000'
        def try_update_end(id, end):
            logger.debug(f"trying to update session id={id} to end_time={end} ")
            try:
                db.update(db.Session.TABLE, {'end_time': end}, where={'session_id': id})
                assert False
            except Error as e:
                logger.debug(f"error: {e}")
                assert e.sqlstate == '45000'

        db.delete(db.Session.TABLE)
        # insert sessions
        ids = []
        for start, end in [
            ("2020-01-01 08:00", "2020-06-01 23:59"),
            ("2020-06-01 23:59", "2020-11-01 08:00"),
            ("2021-01-01 08:00", "2021-06-01 23:59"),
            ("2021-06-01 23:59", "2021-11-01 08:00"),
        ]:
            res = insert(start, end)
            assert len(res['last_ids']) == 1
            ids.append(res['last_ids'][0])
        assert len(ids) == 4
        logger.debug(f"session ids={ids} inserted")

        # invalid
        logger.debug(f"trying to insert invalid sessions")
        # 2020-01-01 08:00-2020-06-01 23:59 and 2020-06-01 23:59-2020-11-01 08:00
        for start in [
            "2019-12-31 08:00",
            "2020-01-01 08:00",
            "2020-01-02 08:00",
        ]:
            for end in [
                "2020-05-31 23:59",
                "2020-06-01 23:59",
                "2020-06-02 23:59",
                "2020-11-01 08:00",
                "2020-11-02 08:00",
            ]:
                try_insert(start, end)

        # 2020-06-01 23:59-2020-11-01 08:00 and 2021-01-01 08:00-2021-06-01 23:59
        # (gap in between)
        for start in [
            "2020-05-01 23:59", "2020-06-01 23:59", "2020-07-01 23:59",
        ]:
            for end in [
                "2020-10-01 08:00",
                "2020-11-01 08:00",
                "2020-12-01 08:00",
                "2021-01-01 08:00",
                "2021-02-01 08:00",
                "2021-06-01 23:59",
                "2021-07-01 23:59",
            ]:
                try_insert(start, end)

        # valid
        logger.debug(f"insert valid sessions")
        for start, end in [
            ("2019-01-01 08:00", "2020-01-01 08:00"),
            ("2020-11-01 08:00", "2021-01-01 08:00"),
            ("2021-11-01 08:00", "2022-01-01 08:00"),
            ("2022-06-01 23:59", "2022-07-01 23:59"),
        ]:
            logger.debug(f"inserting {start}-{end}")
            res = insert(start, end)
            assert len(res['last_ids']) == 1
            id = res['last_ids'][0]
            assert id > 0
            delete(id)

        # invalid update
        logger.debug(f"trying to update sessions to invalid end_time")
        # 2020-01-01 08:00-2020-06-01 23:59 and 2020-06-01 23:59-2020-11-01 08:00
        # 2020-01-01 08:00-2020-06-01 23:59 `id`=ids[0]
        for end in [
            "2020-06-02 23:59",
            "2020-11-01 08:00",
            "2020-11-02 08:00",
        ]:
            try_update_end(ids[0], end)

        # 2020-06-01 23:59-2020-11-01 08:00 and 2021-01-01 08:00-2021-06-01 23:59
        # (gap in between)
        # 2020-06-01 23:59-2020-11-01 08:00 `id`=ids[1]
        for end in [
            "2021-02-01 08:00",
            "2021-06-01 23:59",
            "2021-07-01 23:59",
        ]:
            try_update_end(ids[1], end)

def test_time_slot_trigger(app):
    with app.app_context():
        # start_time < end_time and can't overlap
        # time should be within session time
        logger.debug("add fake room type")
        db.delete(db.RoomType.TABLE)
        room_type = db.insert(db.RoomType.TABLE, [
            { 'label': 'fake room type' }
        ])['last_ids'][0]

        assert room_type != 0

        logger.debug("add fake rooms")
        db.delete(db.Room.TABLE)
        def insert_room(status=db.RoomStatus.AVAILABLE):
            return db.insert(db.Room.TABLE, [
                {
                    'type': room_type,
                    'status': status,
                    'name': 'fake room',
                    'capacity': 0,
                }
            ])['last_ids'][0]
        rooms = []
        room_num = 10
        for i in range(room_num):
            rooms.append(insert_room())

        assert len(rooms) == room_num and all(rooms)
        
        logger.debug("add fake reservations with time slots")
        def insert_resv(username, room_id, status):
            return db.insert(db.Reservation.RESV_TABLE, [
                {
                    'username': username,
                    'room_id': room_id,
                    'secu_level': db.SecuLevel.PUBLIC,
                    'status': status,
                    'title': 'fake title',
                    'note': 'fake note',
                }
            ])['last_ids'][0]
        
        def insert_time_slot(resv_id, username, start, end):
            return db.insert(db.Reservation.TS_TABLE, [
                {
                    'resv_id': resv_id,
                    'username': username,
                    'start_time': start,
                    'end_time': end,
                }
            ])['last_ids'][0]
    
        def try_insert_time_slot(resv_id, username, start, end):
            logger.debug(f"try inserting time slot {start} - {end} for reservation {resv_id}")
            try:
                insert_time_slot(resv_id, username, start, end)
                assert False
            except Error as e:
                assert e.sqlstate == '45000'
        
        resvs = []
        resv_num = 20
        valid_count = 0 # pending, confirmed
        ts_num_list = [random.randint(0, 5) for _ in range(resv_num)] # time slot per reservation
        ts_num = sum(ts_num_list)
        now = datetime.now()
        session_start = int(now.timestamp())
        session_end = int((now + timedelta(days=30)).timestamp())
        stamp = (session_end - session_start) // ts_num if ts_num else 0
        stamp_start = session_start
        logger.debug(f"insert {resv_num} reservations")
        for i in range(resv_num):
            resv = {}
            resv['username'] = random.choice(['restricted', 'basic', 'advanced', 'admin'])
            resv['room_id'] = random.choice(rooms)
            status_list = [db.ResvStatus.PENDING, db.ResvStatus.CONFIRMED]
            if valid_count < resv_num / 2:
                resv['status'] = random.choice(status_list)
                valid_count += 1
            else:
                resv['status'] = random.choice(status_list + [db.ResvStatus.CANCELLED, db.ResvStatus.REJECTED])
            logger.debug(f"insert reservation {resv}")
            resv_id = insert_resv(resv['username'], resv['room_id'], resv['status'])
            assert resv_id != 0
            resv['resv_id'] = resv_id    

            resv['time_slots'] = []
            if ts_num_list[i] == 0:
                logger.debug(f"insert no time slot for reservation {resv_id}")
            else:
                logger.debug(f"insert {ts_num_list[i]} time slots for reservation {resv_id}")
                for j in range(ts_num_list[i]):
                    start = random.randint(
                        stamp_start,
                        stamp_start+stamp-1
                    )
                    end = random.randint(
                        start+1,
                        stamp_start+stamp,
                    )
                    stamp_start = end

                    logger.debug(f"start: {start}, end: {end}")
                    start = datetime.fromtimestamp(start)
                    end = datetime.fromtimestamp(end)

                    logger.debug(f"insert time slot {start} - {end}")
                    ts_id = insert_time_slot(resv_id, resv['username'], start, end)
                    assert ts_id != 0
                    ts = {
                        'slot_id': ts_id,
                        'start_time': start,
                        'end_time': end,
                    }
                    resv['time_slots'].append(ts)

                    if resv['status'] in [db.ResvStatus.PENDING, db.ResvStatus.CONFIRMED]:
                        logger.debug(f"try insert time slot that overlaps with {start} - {end}")
                        before_start = datetime.fromtimestamp(random.randint(
                            session_start,
                            ts['start_time'].timestamp()-1,
                        ))
                        after_end = datetime.fromtimestamp(random.randint(
                            ts['end_time'].timestamp()+1,
                            session_end,
                        ))
                        between_start_end = datetime.fromtimestamp(random.randint(
                            ts['start_time'].timestamp()+1,
                            ts['end_time'].timestamp()-1,
                        ))

                        for s in [ before_start, start, between_start_end ]:
                            for e in [ between_start_end, end, after_end ]:
                                try_insert_time_slot(resv_id, resv['username'], s, e)

            resvs.append(resv)

        assert len(resvs) == resv_num and all(resvs)
        
def test_settings_util(app):
    with app.app_context():
        logger.debug("test get time window")
        time_window = timedelta(days=5)
        tw = db.Setting.timedelta_to_str(time_window)
        assert tw == '120:00:00'
        db.update(db.Setting.TABLE, {'value': tw}, where={'id': db.Setting.TIME_WINDOW})
        assert db.Setting.time_window() == time_window

        logger.debug("test get time limit")
        time_limit = timedelta(hours=3)
        tl = db.Setting.timedelta_to_str(time_limit)
        assert tl == '3:00:00'
        db.update(db.Setting.TABLE, {'value': tl}, where={'id': db.Setting.TIME_LIMIT})
        assert db.Setting.time_limit() == time_limit

        logger.debug("test get max daily")
        max_daily = 2
        db.update(db.Setting.TABLE, {'value': str(max_daily)}, where={'id': db.Setting.MAX_DAILY})
        assert db.Setting.max_daily() == max_daily

        logger.debug("test in time window")
        now = datetime.now()
        start = now
        end = now + timedelta(days=1)
        assert db.Setting.in_time_window([
            { 'start_time': str(start), 'end_time': end }
        ])
        # past
        start = now - timedelta(days=1)
        end = now
        assert not db.Setting.in_time_window([
            { 'start_time': start, 'end_time':str(end) }
        ])
        # future, out of time window
        start = now + time_window + timedelta(days=1)
        end = start + timedelta(days=1)
        assert not db.Setting.in_time_window([
            { 'start_time': start, 'end_time': end }
        ])

        logger.debug("test in time limit")
        now = datetime.now()
        start = now
        end = now + time_limit - timedelta(minutes=1)
        assert db.Setting.in_time_limit([
            { 'start_time': str(start), 'end_time': end }
        ])
        # exceed time limit
        end = now + time_limit + timedelta(minutes=1)
        assert not db.Setting.in_time_limit([
            { 'start_time': start, 'end_time': str(end) }
        ])

        logger.debug("test max daily")
        db.delete(db.Reservation.RESV_TABLE, where={'username': 'admin'})
        assert db.Setting.below_max_daily('admin')
        for _ in range(max_daily):
            logger.debug("insert a reservation")
            res = db.insert(db.Reservation.RESV_TABLE, [
                {
                    'username': 'admin',
                    'room_id': 1,
                    'secu_level': 0,
                    'session_id': 1,
                    'status': 0,
                    'title': 'title',
                }
            ])
            assert len(res['affected_rows']) == 1
        assert not db.Setting.below_max_daily('admin')

def test_sessions_util(app):
    with app.app_context():
        logger.debug("test current session")
        db.update(db.Session.TABLE, {'is_current': 0}, where={'is_current': 1})
        try:
            logger.debug("no current session")
            db.Session.current()
            assert False
        except:
            assert True
        start = datetime.now() + timedelta(days=3650)
        end = start + timedelta(days=365)
        id = db.insert(db.Session.TABLE, [
            {
                'is_current': 1,
                'start_time': start,
                'end_time': end,
                'name': 'test session',
            }
        ])['last_ids'][0]
        assert db.Session.current()['session_id'] == id

def test_rooms_util(app):
    with app.app_context():
        logger.debug("test get available rooms")
        res = db.insert(db.RoomType.TABLE, [
            { 'label': 'test room type' }
        ])
        assert len(res['last_ids']) == 1
        room_type = res['last_ids'][0]
        res = db.insert(db.Room.TABLE, [
            {
                'name': 'test room',
                'type': room_type,
                'capacity': 10,
                'status': db.RoomStatus.AVAILABLE,
            }
        ])
        assert len(res['last_ids']) == 1
        room_id = res['last_ids'][0]
        assert db.Room.available(room_id) == True
        res = db.update(db.Room.TABLE, {'status': db.RoomStatus.UNAVAILABLE}, where={'room_id': room_id})
        assert res == 1
        assert db.Room.available(room_id) == False

def test_periods_util(app):
    with app.app_context():
        logger.debug("test get available periods")
        db.delete(db.Period.TABLE)
        res = db.Period.get()
        assert len(res) == 0
        logger.debug("insert periods")
        periods = [
            { 'start_time': timedelta(hours=8), 'end_time': timedelta(hours=9) },
            { 'start_time': timedelta(hours=9), 'end_time': timedelta(hours=10) },
            { 'start_time': timedelta(hours=10), 'end_time': timedelta(hours=11) },
            { 'start_time': timedelta(hours=14, minutes=30), 'end_time': timedelta(hours=15, minutes=30) },
        ]
        res = db.insert(db.Period.TABLE, periods)
        assert len(res['last_ids']) == len(periods)
        logger.debug(f"insered periods: {res['last_ids']}")

        logger.debug("test is_comb_of_periods")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_str = today.strftime('%Y-%m-%d')
        logger.debug(f"test valid time slots")
        assert db.Period.is_comb_of_periods([
            { 
                'start_time': today + timedelta(hours=8), 
                'end_time': today_str + " 9:00:00"
            },
            { 
                'start_time': today_str + " 9:00:00", 
                'end_time': today + timedelta(hours=10)
            },
            { 
                'start_time': today_str + " 14:30:00", 
                'end_time': today_str + " 15:30:00" 
            },
            { 
                'start_time': today_str + " 8:00:00", 
                'end_time': today + timedelta(hours=11) 
            },
        ])
        logger.debug(f"test invalid time slots")
        assert not db.Period.is_comb_of_periods([
            {
                'start_time': today_str + " 8:00:00",
                'end_time': today_str + " 9:30:00"
            },
            {
                'start_time': today_str + " 9:10:00",
                'end_time': today_str + " 9:30:00"
            },
            {
                'start_time': today_str + " 15:30:00",
                'end_time': today_str + " 16:00:00"
            },
        ])

def test_users_util(app):
    with app.app_context():
        logger.debug("test update user")
        db.User.update('admin', password='123456', email='admin@localhost')

        logger.debug("test get user")
        admin = db.User.get('admin')
        assert not isinstance(admin, list)
        assert admin['username'] == 'admin'
        assert 'password' not in admin
        assert admin['email'] == 'admin@localhost'
        users = db.User.get()
        assert isinstance(users, list)
        assert all([ 'password' not in user for user in users ])

        logger.debug("test get password")
        assert db.User.get_password('admin') == '123456'

def test_reservation_util(app):
    with app.app_context():
        db.delete(db.Session.TABLE)
        db.delete(db.Room.TABLE)
        db.delete(db.RoomType.TABLE)

        logger.debug("insert session")
        start = datetime(2020, 1, 1)
        end = start + timedelta(days=150)
        id = db.insert(db.Session.TABLE, [
            {
                'is_current': 1,
                'start_time': start,
                'end_time': end,
                'name': 'test session',
            }
        ])['last_ids'][0]
        assert db.Session.current()['session_id'] == id

        logger.debug("insert room type")
        res = db.insert(db.RoomType.TABLE, [
            { 'label': 'test room type' }
        ])
        assert len(res['last_ids']) == 1
        room_type = res['last_ids'][0]

        logger.debug("insert room")
        res = db.insert(db.Room.TABLE, [
            {
                'name': 'test room',
                'type': room_type,
                'capacity': 10,
                'status': db.RoomStatus.AVAILABLE,
            }
        ])
        assert len(res['last_ids']) == 1
        room_id = res['last_ids'][0]

        logger.debug("test insert reservations")
        resv = {
            'session_id': id,
            'room_id': room_id,
            'username': 'admin',
            'title': 'test reservation',
            'secu_level': db.SecuLevel.PUBLIC,
            'status': db.ResvStatus.CONFIRMED
        }
        
        logger.debug("test insert reservation")
        slot_start = start + timedelta(hours=8)
        slot_end = slot_start + timedelta(hours=1)
        resv['time_slots'] = [
            {
                'start_time': slot_start,
                'end_time': slot_end,
            }
        ]
        resv_id = db.Reservation.insert(resv)
        assert resv_id
        resv['time_slots'] = [
            {
                'start_time': start + timedelta(hours=14, minutes=30),
                'end_time': start + timedelta(hours=15, minutes=30),
            }
        ]
        assert db.Reservation.insert(resv)

        logger.debug("test insert reservation with invalid time slot")
        resv['time_slots'] = [
            {
                'start_time': slot_end,
                'end_time': slot_start,
            }
        ]
        try:
            db.Reservation.insert(resv)
            assert False
        except Exception as e:
            logger.debug(f"expected exception: {e}")
            assert True

        logger.debug("test update reservation")
        db.Reservation.update(resv_id, resv['username'], title='test reservation 2')

        logger.debug("test get reservation")
        resvs = db.Reservation.get(where={'date': start.strftime('%Y-%m-%d')})
        assert len(resvs) == 2

        resvs = db.Reservation.get(where={'resv_id': resv_id, 'username': resv['username']})
        assert len(resvs) == 1
        assert resvs[0]['title'] == 'test reservation 2'
        resv = resvs[0]

        logger.debug("test update reservation time slot")
        start = start + timedelta(hours=9)
        end = start + timedelta(hours=1)
        db.Reservation.update(resv_id, resv['username'],
            slot_id=resv['slot_id'],
            start_time=start,
            end_time=end
        )
        logger.debug("get reservation")
        resvs = db.Reservation.get(where={'resv_id': resv_id, 'username': resv['username']})
        assert len(resvs) == 1
        assert resvs[0]['start_time'] == start
        assert resvs[0]['end_time'] == end