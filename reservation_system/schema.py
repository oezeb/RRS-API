"""
Schema.py
=========
This module contains the define some constants and triggers
to complete the database schema in `schema.sql`.

Constants
---------
"""

# Immutable
class Language: 
    TABLE = "languages"
    EN = 'en'
class SecuLevel: 
    TABLE = "resv_secu_levels"
    PUBLIC = 0; ANONYMOUS = 1; PRIVATE = 2
class ResvStatus: 
    TABLE = "resv_status"
    PENDING = 0; CONFIRMED = 1; CANCELLED = 2; REJECTED = 3
class RoomStatus:
    TABLE = "room_status"
    UNAVAILABLE = 0; AVAILABLE = 1
class UserRole: 
    TABLE = "user_roles"
    BLOCKED = -1; RESTRICTED = 0; BASIC = 1; ADVANCED = 2
    ADMIN = 3
class Setting: 
    TABLE = "settings"
    TIME_WINDOW = 1; TIME_LIMIT = 2; MAX_DAILY = 3

# others
class Reservation:
    RESV_TABLE = "reservations"
    TS_TABLE = "time_slots"
    TABLE = f"{RESV_TABLE} NATURAL JOIN {TS_TABLE}"
class     User: TABLE = "users"
class  Session: TABLE = "sessions"
class     Room: TABLE = "rooms"
class   Period: TABLE = "periods"    
class RoomType: TABLE = "room_types"
class   Notice: TABLE = "notices"

# ==============================================================
# INSERT Immutable Data
# ==============================================================
IMMUTABLE_INSERTS = f"""
INSERT INTO {Language.TABLE} (lang_code, name) VALUES 
('{Language.EN}', 'English');

INSERT INTO {SecuLevel.TABLE} (secu_level, label) VALUES 
({SecuLevel.PUBLIC}, '公共'), ({SecuLevel.ANONYMOUS}, '匿名'), 
({SecuLevel.PRIVATE}, '私密');

INSERT INTO {ResvStatus.TABLE} (status, label) VALUES 
({ResvStatus.PENDING}, '待定'),
({ResvStatus.CONFIRMED}, '确认'), 
({ResvStatus.CANCELLED}, '取消'),
({ResvStatus.REJECTED}, '拒绝');

INSERT INTO {RoomStatus.TABLE} (status, label) VALUES
({RoomStatus.UNAVAILABLE}, '不可用'), 
({RoomStatus.AVAILABLE}, '可用'  );

INSERT INTO {Setting.TABLE} (id, value, label) VALUES
({Setting.TIME_WINDOW}, '72:00:00', '时间窗口'), 
({Setting.TIME_LIMIT}, '4:00:00', '时间限'), 
({Setting.MAX_DAILY}, '3', '每日最多次数');

INSERT INTO {UserRole.TABLE} (role, label) VALUES 
({UserRole.BLOCKED}, '被封锁的'),
({UserRole.RESTRICTED}, '待审核'),
({UserRole.BASIC}, '基础用户'),
({UserRole.ADVANCED}, '高级用户'),
({UserRole.ADMIN}, '管理员');
"""

# ==============================================================
# Immutable Triggers
# ==============================================================
# `Language`, `SecuLevel`, `ResvStatus`, `RoomStatus`, 
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
        (SecuLevel.TABLE, 'secu_level'),
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
            REGEXP '^[0-9]+:[0-9][0-9]:[0-9][0-9]$'
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
# - time slot in its corresponding session

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
    AND r.room_id = room_id AND r.session_id = session_id
    AND r.status IN (
        {ResvStatus.PENDING}, {ResvStatus.CONFIRMED});

    IF i > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT =
        'Time slot overlaps with existing time slot.';
    END IF;

    SELECT COUNT(*) INTO i FROM {Session.TABLE} s
    WHERE s.session_id = session_id 
    AND s.start_time <= NEW.start_time 
    AND s.end_time >= NEW.end_time;

    IF i = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT =
        'Time slot is not within session time.';
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
    AND r.room_id = room_id AND r.session_id = session_id
    AND r.status IN (
        {ResvStatus.PENDING}, {ResvStatus.CONFIRMED})
    AND t.resv_id <> NEW.resv_id 
    AND t.username <> NEW.username 
    AND t.slot_id <> NEW.slot_id;
            
    IF i > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT =
        'Time slot overlaps with existing time slot.';
    END IF;

    SELECT COUNT(*) INTO i FROM {Session.TABLE} s
    WHERE s.session_id = session_id 
    AND s.start_time <= NEW.start_time 
    AND s.end_time >= NEW.end_time;
    
    IF i = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 
        'Time slot is not within session time.';
    END IF;
END;
"""
