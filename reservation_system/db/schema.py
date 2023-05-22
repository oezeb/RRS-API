import logging

from flask import current_app

logger = logging.getLogger(__name__)

def init_schema(cursor):
    def execute(sql):
        it = cursor.execute(sql, multi=True)
        for res in it:
            logger.info(f"Running query: {res}")

    logger.info("Creating tables...")
    with current_app.open_resource('db/schema.sql') as f:
        execute(f.read())

    logger.info("Populating tables with initial data...")
    execute(INSERT_DATA_SQL)

    logger.info("Creating triggers...")
    variables = locals()
    for name, value in variables.items():
        if name.endswith('_TRIGGER'):
            execute(value)

# ----------------------------------------------------------------
# Database Tables
# ----------------------------------------------------------------

class Language: 
    TABLE = "languages"
    EN = 'en'
    
class ResvPrivacy:
    TABLE = "resv_privacy"
    PUBLIC = 0; ANONYMOUS = 1; PRIVATE = 2
    
class ResvStatus:
    TABLE = "resv_status"
    PENDING = 0; CONFIRMED = 1; CANCELLED = 2; REJECTED = 3

class RoomStatus:
    TABLE = "room_status"
    UNAVAILABLE = 0; AVAILABLE = 1

class UserRole:
    TABLE = "user_roles"
    INACTIVE = -2; RESTRICTED = -1
    GUEST = 0; BASIC = 1; ADVANCED = 2; ADMIN = 3

class Setting: 
    TABLE = "settings"
    TIME_WINDOW = 1; TIME_LIMIT = 2; MAX_DAILY = 3

class Reservation:
    RESV_TABLE = "reservations"
    TS_TABLE = "time_slots"
    TABLE = f"{RESV_TABLE} NATURAL JOIN {TS_TABLE}"

class RoomType: TABLE = "room_types"
class     Room: TABLE = "rooms"
class     User: TABLE = "users"
class  Session: TABLE = "sessions"
class   Period: TABLE = "periods"
class   Notice: TABLE = "notices"

# ==============================================================
# INSERT Data
# ==============================================================
INSERT_DATA_SQL = f"""
INSERT INTO {Language.TABLE} (lang_code, name) VALUES 
('{Language.EN}', 'English');

INSERT INTO {ResvPrivacy.TABLE} (privacy, label) VALUES 
({ResvPrivacy.PUBLIC}, '公共'), 
({ResvPrivacy.ANONYMOUS}, '匿名'),
({ResvPrivacy.PRIVATE}, '私密');

INSERT INTO {ResvStatus.TABLE} (status, label, description) VALUES 
({ResvStatus.PENDING}, '待定', '等待管理员审核'),
({ResvStatus.CONFIRMED}, '确认', '预约已有效'),
({ResvStatus.CANCELLED}, '取消', '预约被取消'),
({ResvStatus.REJECTED}, '拒绝', '预约被拒绝');

INSERT INTO {RoomStatus.TABLE} (status, label, description) VALUES
({RoomStatus.UNAVAILABLE}, '不可用', '该房间不可约'),
({RoomStatus.AVAILABLE}, '可用', NULL);

INSERT INTO {UserRole.TABLE} (role, label) VALUES 
({UserRole.INACTIVE}, '未激活'),
({UserRole.RESTRICTED}, '受限用户'),
({UserRole.GUEST}, '来宾'),
({UserRole.BASIC}, '基础用户'),
({UserRole.ADVANCED}, '高级用户'),
({UserRole.ADMIN}, '管理员');

INSERT INTO {Setting.TABLE} (id, value, name, description) VALUES
({Setting.TIME_WINDOW}, '72:00:00', '时间窗口', '从当前时间开始，用户最多可以提前多久预约房间'),
({Setting.TIME_LIMIT}, '3:00:00', '时间限', '用户预约房间的最长时间'),
({Setting.MAX_DAILY}, '3', '每日最多次数', '用户每天最多可以预约多少次房间');
"""

# ==============================================================
# Immutable Triggers
# ==============================================================
# `Language`, `ResvPrivacy`, `ResvStatus`, `RoomStatus`, 
# `UserRole`, and `Setting` trigger make sure that
# the data in these tables are immutable.
# - Non-essential data like `label` and `description`
# can be updated.
# - INSERT, and DELETE are not allowed.
# - UPDATE is allowed only for "non-essential" data.

_immutable_insert_del_trigger = lambda table, method: f"""
DROP TRIGGER IF EXISTS {table}_{method}_trigger;
CREATE TRIGGER {table}_{method}_trigger BEFORE {method}
ON {table} FOR EACH ROW BEGIN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT =
    '{method} on {table} is not allowed';
END;
"""
_immutable_update_trigger = lambda table, pk: f"""
DROP TRIGGER IF EXISTS {table}_update_trigger;
CREATE TRIGGER {table}_update_trigger BEFORE UPDATE
ON {table} FOR EACH ROW BEGIN
    IF NEW.{pk} <> OLD.{pk} THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT =
        'update of {pk} on {table} is not allowed';
    END IF;
END;
"""
_language_update_trigger = lambda: f"""
DROP TRIGGER IF EXISTS {Language.TABLE}_update_trigger;
CREATE TRIGGER {Language.TABLE}_update_trigger BEFORE UPDATE
ON {Language.TABLE} FOR EACH ROW BEGIN
    IF NEW.lang_code COLLATE utf8mb4_bin <> 
        OLD.lang_code COLLATE utf8mb4_bin 
    THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT =
        'update of lang_code on {Language.TABLE} is not allowed';
    END IF;
END;
"""

def _get_immutable_trigger():
    sql = ""
    for table, pk in [
        (Language.TABLE, 'lang_code'),
        (ResvPrivacy.TABLE, 'privacy'),
        (ResvStatus.TABLE, 'status'),
        (RoomStatus.TABLE, 'status'),
        (UserRole.TABLE, 'role'),
        (Setting.TABLE, 'id')
    ]:
        sql += _immutable_insert_del_trigger(table, 'INSERT')
        sql += _immutable_insert_del_trigger(table, 'DELETE')
        if table == Language.TABLE:
            sql += _language_update_trigger()
        elif table != Setting.TABLE:
            # Setting has additional constraints, 
            # see trigger implementation below.
            sql += _immutable_update_trigger(table, pk)
    return sql

IMMUTABLE_TRIGGER = _get_immutable_trigger()

# ==============================================================
# Settings Triggers
# ==============================================================
# `time_window` and `time_limit` must be in the format 
# `HH:MM:SS
# `max_daily` must be a number

SETTING_UPDATE_TRIGGER  = f"""
DROP TRIGGER IF EXISTS {Setting.TABLE}_update_trigger;
CREATE TRIGGER {Setting.TABLE}_update_trigger BEFORE UPDATE 
ON {Setting.TABLE} FOR EACH ROW BEGIN
    IF NEW.id <> OLD.id THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT =
        'update of id on {Setting.TABLE} is not allowed';
    END IF;

    IF NEW.id = {Setting.TIME_WINDOW} 
        OR NEW.id = {Setting.TIME_LIMIT}
    THEN
        IF NEW.value NOT 
            REGEXP '^[0-9]+:[0-9][0-9]?:[0-9][0-9]?$'
        THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT =
            'Time format must be HH:MM:SS.';
        END IF;
    ELSEIF NEW.id = {Setting.MAX_DAILY} THEN
        IF NEW.value NOT REGEXP '^[0-9]+$' THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 
            'Max daily must be an integer.';
        END IF;
    END IF;
END;
"""

# ==============================================================
# Periods Triggers
# ==============================================================
# `Period`, `Session`, and `TimeSlot` triggers
# make sure that different time ranges do not overlap.
# `Period` triggers also make sure that
# `start_time` and `end_time` are within one day
PERIOD_INSERT_TRIGGER = f"""
DROP TRIGGER IF EXISTS {Period.TABLE}_insert_trigger;
CREATE TRIGGER {Period.TABLE}_insert_trigger BEFORE INSERT 
ON {Period.TABLE} FOR EACH ROW BEGIN
    DECLARE conflict INTEGER;

    SELECT COUNT(*) INTO conflict FROM {Period.TABLE} p
    WHERE p.period_id NOT IN (
        SELECT p2.period_id FROM {Period.TABLE} p2
        WHERE p2.end_time<=NEW.start_time 
        OR p2.start_time>=NEW.end_time);

    IF conflict > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT =
        'Period time conflict.';
    END IF;

    IF NEW.start_time < '00:00:00' 
        OR NEW.start_time > '23:59:59' 
        OR NEW.end_time < '00:00:00'
        OR NEW.end_time > '23:59:59'
    THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT =
        'Period start time must be 
        between 00:00:00 and 23:59:59.';
    END IF;
END;
"""

PERIOD_UPDATE_TRIGGER = f"""
DROP TRIGGER IF EXISTS {Period.TABLE}_update_trigger;
CREATE TRIGGER {Period.TABLE}_update_trigger BEFORE UPDATE 
ON {Period.TABLE} FOR EACH ROW BEGIN
    DECLARE conflict INTEGER;
    
    SELECT COUNT(*) INTO conflict FROM {Period.TABLE} p
    WHERE p.period_id NOT IN (
        SELECT p2.period_id FROM {Period.TABLE} p2
        WHERE p2.end_time<=NEW.start_time 
        OR p2.start_time>=NEW.end_time) 
    AND p.period_id <> NEW.period_id;

    IF conflict > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 
        'Period time conflict.';
    END IF;

    IF NEW.start_time < '00:00:00' 
        OR NEW.start_time > '23:59:59' 
    THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 
        'Period start time must be 
        between 00:00:00 and 23:59:59.';
    END IF;
END;
"""

# ==============================================================
# Sessions Triggers
# ==============================================================
SESSION_INSERT_TRIGGER = f"""
DROP TRIGGER IF EXISTS {Session.TABLE}_insert_trigger;
CREATE TRIGGER {Session.TABLE}_insert_trigger BEFORE INSERT 
ON {Session.TABLE} FOR EACH ROW BEGIN
   DECLARE conflict INTEGER;
   
    SELECT COUNT(*) INTO conflict FROM {Session.TABLE} s
    WHERE s.session_id NOT IN (
        SELECT s2.session_id FROM {Session.TABLE} s2
        WHERE s2.end_time<=NEW.start_time 
        OR s2.start_time>=NEW.end_time);

    IF conflict > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT =
        'Session time conflict.';
    END IF;
END;
"""

SESSION_UPDATE_TRIGGER = f"""
DROP TRIGGER IF EXISTS {Session.TABLE}_update_trigger;
CREATE TRIGGER {Session.TABLE}_update_trigger BEFORE UPDATE 
ON {Session.TABLE} FOR EACH ROW BEGIN
   DECLARE conflict INTEGER;

    SELECT COUNT(*) INTO conflict FROM {Session.TABLE} s
    WHERE s.session_id NOT IN (
        SELECT s2.session_id FROM {Session.TABLE} s2
        WHERE s2.end_time<=NEW.start_time 
        OR s2.start_time>=NEW.end_time) 
    AND s.session_id <> NEW.session_id;
            
    IF conflict > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT =
        'Session time conflict.';
    END IF;
END;
"""

# ==============================================================
# TimeSlots Triggers
# ==============================================================
# - slots overlap-free
# Some time slots may be allowed to overlap.
# Cancelled reservations time slots for instance can be reused.
# It depends on the reservation status.
# - time slot should be in its corresponding session
# - `status` can be updated only:
#   - from `pending` to `cancelled`or `confirmed` or `rejected`
#   - from `confirmed` to `cancelled`

TIME_SLOT_INSERT_TRIGGER = f"""
DROP TRIGGER IF EXISTS {Reservation.TS_TABLE}_insert_trigger;
CREATE TRIGGER {Reservation.TS_TABLE}_insert_trigger BEFORE 
INSERT ON {Reservation.TS_TABLE} FOR EACH ROW BEGIN
    DECLARE i INTEGER;
    DECLARE room_id INTEGER;
    DECLARE session_id INTEGER;

    SELECT r.room_id, r.session_id INTO room_id, session_id
    FROM {Reservation.RESV_TABLE} r
    WHERE r.resv_id=NEW.resv_id AND r.username=NEW.username;

    SELECT COUNT(*) INTO i 
    FROM {Reservation.TS_TABLE} t 
    NATURAL JOIN {Reservation.RESV_TABLE} r
    WHERE (t.resv_id, t.username, t.slot_id) NOT IN (
        SELECT t2.resv_id, t2.username, t2.slot_id
        FROM {Reservation.TS_TABLE} t2
        WHERE t2.end_time<=NEW.start_time 
        OR t2.start_time>=NEW.end_time) 
    AND r.room_id = room_id AND t.status IN (
        {ResvStatus.PENDING}, {ResvStatus.CONFIRMED});

    IF i > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT =
        'Time slot overlaps with existing time slot.';
    END IF;

    IF session_id IS NOT NULL THEN
        SELECT COUNT(*) INTO i FROM {Session.TABLE} s
        WHERE s.session_id = session_id 
        AND s.start_time <= NEW.start_time 
        AND s.end_time >= NEW.end_time;

        IF i = 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT =
            'Time slot is not within session time.';
        END IF;
    END IF;
END;
"""

TIME_SLOT_UPDATE_TRIGGER = f"""
DROP TRIGGER IF EXISTS {Reservation.TS_TABLE}_update_trigger;
CREATE TRIGGER {Reservation.TS_TABLE}_update_trigger BEFORE 
UPDATE ON {Reservation.TS_TABLE} FOR EACH ROW BEGIN
    DECLARE i INTEGER;
    DECLARE room_id INTEGER;
    DECLARE session_id INTEGER;
    DECLARE msg TEXT;
    
    SELECT r.room_id, r.session_id INTO room_id, session_id
    FROM {Reservation.RESV_TABLE} r
    WHERE r.resv_id=NEW.resv_id AND r.username=NEW.username;

    SELECT COUNT(*) INTO i FROM {Reservation.TS_TABLE} t
    NATURAL JOIN {Reservation.RESV_TABLE} r
    WHERE (t.resv_id, t.username, t.slot_id) NOT IN (
        SELECT t2.resv_id, t2.username, t2.slot_id
        FROM {Reservation.TS_TABLE} t2
        WHERE t2.end_time<=NEW.start_time 
        OR t2.start_time>=NEW.end_time)
    AND r.room_id = room_id AND t.status IN (
        {ResvStatus.PENDING}, {ResvStatus.CONFIRMED})
    AND t.resv_id <> NEW.resv_id 
    AND t.username <> NEW.username 
    AND t.slot_id <> NEW.slot_id;
            
    IF i > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT =
        'Time slot overlaps with existing time slot.';
    END IF;

    IF session_id IS NOT NULL THEN
        SELECT COUNT(*) INTO i FROM {Session.TABLE} s
        WHERE s.session_id = session_id 
        AND s.start_time <= NEW.start_time 
        AND s.end_time >= NEW.end_time;
        
        IF i = 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 
            'Time slot is not within session time.';
        END IF;
    END IF;

    IF NEW.status <> OLD.status 
    THEN
        IF OLD.status = {ResvStatus.PENDING} 
            AND NEW.status IN ({ResvStatus.CANCELLED}, 
                {ResvStatus.CONFIRMED}, {ResvStatus.REJECTED}) 
        THEN SET msg = '';
        ELSEIF OLD.status = {ResvStatus.CONFIRMED} AND
            NEW.status = {ResvStatus.CANCELLED} 
        THEN SET msg = '';
        ELSE
            SET msg = CONCAT('Updating status from ',
                OLD.status, ' to ', NEW.status, ' is not allowed');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = msg;
        END IF;
    END IF;
END;
"""

# ==============================================================
# Reservations Triggers
# ==============================================================
# - updating `room_id` or `session_id` can cause a lot of
#  time slot conflicts
RESERVATION_UPDATE_TRIGGER = f"""
DROP TRIGGER IF EXISTS {Reservation.RESV_TABLE}_update_trigger;
CREATE TRIGGER {Reservation.RESV_TABLE}_update_trigger BEFORE
UPDATE ON {Reservation.RESV_TABLE} FOR EACH ROW 
BEGIN
    IF NEW.room_id <> OLD.room_id 
        OR NEW.session_id <> OLD.session_id 
    THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 
        'Updating room_id or session_id is not allowed';
    END IF;
END;
"""
