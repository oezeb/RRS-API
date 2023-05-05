"""
Schema.py
=========
This module contains the define some constants and triggers
to complete the database schema in `schema.sql`.
"""
import base64

from marshmallow import Schema as _Schema, fields

# Immutable
class Language: 
    TABLE = "languages"
    EN = 'en'

    # openapi (swagger) parameters
    ARGS = {
        'lang_code': {
            'in': 'query',
            'type': 'string',
            'description': 'Language code',
            'enum': [EN],
        },
        'name': {
            'in': 'query',
            'type': 'string',
            'description': 'Language name',
        },
    }

    @staticmethod
    def args(only=None, exclude=()):
        return _args(Language.ARGS, only, exclude)

    @staticmethod
    def schema(many=False, only=None, exclude=(), load_only=(), dump_only=()):
        class Schema(_Schema):
            lang_code = fields.Str(dump_only=True)
            name = fields.Str()
        return Schema(many=many, only=only, exclude=exclude, load_only=load_only, dump_only=dump_only)
    
class ResvPrivacy:
    TABLE = "resv_privacy"
    PUBLIC = 0; ANONYMOUS = 1; PRIVATE = 2

    # openapi (swagger) parameters
    ARGS = {
        'privacy': {
            'in': 'query',
            'type': 'integer',
            'description': f'Reservation privacy level. {PUBLIC}=public, {ANONYMOUS}=anonymous, {PRIVATE}=private',
            'enum': [PUBLIC, ANONYMOUS, PRIVATE],
        },
        'label': {
            'in': 'query',
            'type': 'string',
            'description': 'Reservation privacy label',
        },
        'description': {
            'in': 'query',
            'type': 'string',
            'description': 'Reservation privacy description',
        },
    }

    @staticmethod
    def args(only=None, exclude=()):
        return _args(ResvPrivacy.ARGS, only, exclude)

    @staticmethod
    def schema(many=False, only=None, exclude=(), load_only=(), dump_only=()):
        class Schema(_Schema):
            privacy = fields.Int(dump_only=True)
            label = fields.Str()
            description = fields.Str()
        return Schema(many=many, only=only, exclude=exclude, load_only=load_only, dump_only=dump_only)

class ResvStatus:
    TABLE = "resv_status"
    PENDING = 0; CONFIRMED = 1; CANCELLED = 2; REJECTED = 3

    # openapi (swagger) parameters
    ARGS = {
        'status': {
            'in': 'query',
            'type': 'integer',
            'description': f'Reservation status. {PENDING}=pending, {CONFIRMED}=confirmed, {CANCELLED}=cancelled, {REJECTED}=rejected',
            'enum': [PENDING, CONFIRMED, CANCELLED, REJECTED],
        },
        'label': {
            'in': 'query',
            'type': 'string',
            'description': 'Reservation status label',
        },
        'description': {
            'in': 'query',
            'type': 'string',
            'description': 'Reservation status description',
        },
    }

    @staticmethod
    def args(only=None, exclude=()):
        return _args(ResvStatus.ARGS, only, exclude)

    @staticmethod
    def schema(many=False, only=None, exclude=(), load_only=(), dump_only=()):
        class Schema(_Schema):
            status = fields.Int(dump_only=True)
            label = fields.Str()
            description = fields.Str()
        return Schema(many=many, only=only, exclude=exclude, load_only=load_only, dump_only=dump_only)
    
class RoomStatus:
    TABLE = "room_status"
    UNAVAILABLE = 0; AVAILABLE = 1

    # openapi (swagger) parameters
    ARGS = {
        'status': {
            'in': 'query',
            'type': 'integer',
            'description': f'Room status. {UNAVAILABLE}=unavailable, {AVAILABLE}=available',
            'enum': [UNAVAILABLE, AVAILABLE],
        },
        'label': {
            'in': 'query',
            'type': 'string',
            'description': 'Room status label',
        },
        'description': {
            'in': 'query',
            'type': 'string',
            'description': 'Room status description',
            'nullable': True,
        },
    }

    @staticmethod
    def args(only=None, exclude=()):
        return _args(RoomStatus.ARGS, only, exclude)

    @staticmethod
    def schema(many=False, only=None, exclude=(), load_only=(), dump_only=()):
        class Schema(_Schema):
            status = fields.Int(dump_only=True)
            label = fields.Str()
            description = fields.Str()
        return Schema(many=many, only=only, exclude=exclude, load_only=load_only, dump_only=dump_only)
    
class UserRole: 
    TABLE = "user_roles"
    INACTIVE = -2; RESTRICTED = -1
    GUEST = 0; BASIC = 1; ADVANCED = 2; ADMIN = 3

    # openapi (swagger) parameters
    ARGS = {
        'role': {
            'in': 'query',
            'type': 'integer',
            'description': f'User role. {INACTIVE}=inactive, {RESTRICTED}=restricted, {GUEST}=guest, {BASIC}=basic, {ADVANCED}=advanced, {ADMIN}=admin',
            'enum': [INACTIVE, RESTRICTED, GUEST, BASIC, ADVANCED, ADMIN],
        },
        'label': {
            'in': 'query',
            'type': 'string',
            'description': 'User role label',
        },
        'description': {
            'in': 'query',
            'type': 'string',
            'description': 'User role description',
        },
    }

    @staticmethod
    def args(only=None, exclude=()):
        return _args(UserRole.ARGS, only, exclude)

    @staticmethod
    def schema(many=False, only=None, exclude=(), load_only=(), dump_only=()):
        class Schema(_Schema):
            role = fields.Int(dump_only=True)
            label = fields.Str()
            description = fields.Str()
        return Schema(many=many, only=only, exclude=exclude, load_only=load_only, dump_only=dump_only)
    
class Setting: 
    TABLE = "settings"
    TIME_WINDOW = 1; TIME_LIMIT = 2; MAX_DAILY = 3

    # openapi (swagger) parameters
    ARGS = {
        'id': {
            'in': 'query',
            'type': 'integer',
            'description': f'Setting ID. {TIME_WINDOW}=time window, {TIME_LIMIT}=time limit, {MAX_DAILY}=max daily',
            'enum': [TIME_WINDOW, TIME_LIMIT, MAX_DAILY],
        },
        'name': {
            'in': 'query',
            'type': 'string',
            'description': 'Setting name',
        },
        'value': {
            'in': 'query',
            'type': 'string',
            'description': 'Setting value',
        },
        'description': {
            'in': 'query',
            'type': 'string',
            'description': 'Setting description',
        },
    }

    @staticmethod
    def args(only=None, exclude=()):
        return _args(Setting.ARGS, only, exclude)

    @staticmethod
    def schema(many=False, only=None, exclude=(), load_only=(), dump_only=()):
        class Schema(_Schema):
            id = fields.Int(description="Setting ID",
                dump_only=True
            )
            name = fields.Str(description="Setting name")
            value = fields.Str(description="Setting value")
            description = fields.Str(description="Setting description")
        return Schema(many=many, only=only, exclude=exclude, load_only=load_only, dump_only=dump_only)

# others
class RoomType:
    TABLE = "room_types"

    # openapi (swagger) parameters
    ARGS = {
        'type': {
            'in': 'query',
            'type': 'integer',
            'description': 'Room type',
        },
        'label': {
            'in': 'query',
            'type': 'string',
            'description': 'Room type label',
        },
        'description': {
            'in': 'query',
            'type': 'string',
            'description': 'Room type description',
        },
    }

    @staticmethod
    def args(only=None, exclude=()):
        return _args(RoomType.ARGS, only, exclude)

    @staticmethod
    def schema(many=False, only=None, exclude=(), load_only=(), dump_only=()):
        class Schema(_Schema):
            type = fields.Int()
            label = fields.Str()
            description = fields.Str()
        return Schema(many=many, only=only, exclude=exclude, load_only=load_only, dump_only=dump_only)
     
class Room: 
    TABLE = "rooms"

    # openapi (swagger) parameters
    ARGS = {
        'room_id': {
            'in': 'query',
            'type': 'integer',
            'description': 'Room ID',
        },
        'name': {
            'in': 'query',
            'type': 'string',
            'description': 'Room name',
        },
        'type': RoomType.ARGS['type'],
        'status': RoomStatus.ARGS['status'],
        'capacity': {
            'in': 'query',
            'type': 'integer',
            'description': 'Room capacity',
        },
        'image': {
            'in': 'query',
            'type': 'string',
            'format': 'byte',
            'description': 'Room image',
        },
    }

    @staticmethod
    def args(only=None, exclude=()):
        return _args(Room.ARGS, only, exclude)        

    @staticmethod
    def schema(many=False, only=None, exclude=(), load_only=(), dump_only=()):
        class Schema(_Schema):
            room_id = fields.Int()
            name = fields.Str()
            type = fields.Int()
            status = fields.Int()
            capacity = fields.Int()
            image = _ImageField()
        return Schema(many=many, only=only, exclude=exclude, load_only=load_only, dump_only=dump_only)
    
class User: 
    TABLE = "users"

    # openapi (swagger) parameters
    ARGS = {
        'username': {
            'in': 'query',
            'type': 'string',
            'description': 'User username',
        },
        'name': {
            'in': 'query',
            'type': 'string',
            'description': 'User full name',
        },
        'password': {
            'in': 'query',
            'type': 'string',
            'description': 'User password',
        },
        'email': {
            'in': 'query',
            'type': 'string',
            'description': 'User email',
        },
        'role': UserRole.ARGS['role'],
    }

    @staticmethod
    def args(only=None, exclude=()):
        return _args(User.ARGS, only, exclude)

    @staticmethod
    def schema(many=False, only=None, exclude=(), load_only=(), dump_only=()):
        class Schema(_Schema):
            username = fields.Str()
            name = fields.Str()
            password = fields.Str(load_only=True)
            email = fields.Email()
            role = fields.Int(description="User role")
        return Schema(many=many, only=only, exclude=exclude, load_only=load_only, dump_only=dump_only)
    
class Reservation:
    RESV_TABLE = "reservations"
    TS_TABLE = "time_slots"
    TABLE = f"{RESV_TABLE} NATURAL JOIN {TS_TABLE}"

    # openapi (swagger) parameters
    ARGS = {
        'resv_id': {
            'in': 'query',
            'type': 'integer',
            'description': 'Reservation ID',
        },
        'username': User.ARGS['username'],
        'room_id': Room.ARGS['room_id'],
        'session_id': {
            'in': 'query',
            'type': 'integer',
            'description': 'Reservation session ID',
        },
        'privacy': ResvPrivacy.ARGS['privacy'],
        'title': {
            'in': 'query',
            'type': 'string',
            'description': 'Reservation title',
        },
        'note': {
            'in': 'query',
            'type': 'string',
            'description': 'Reservation note',
        },
        'create_time': {
            'in': 'query',
            'type': 'string',
            'format': 'date-time',
            'description': 'Reservation creation time',
        },
        'update_time': {
            'in': 'query',
            'type': 'string',
            'format': 'date-time',
            'description': 'Reservation last update time',
        },
        'slot_id': {
            'in': 'query',
            'type': 'integer',
            'description': 'Reservation time slot ID',
        },
        'start_time': {
            'in': 'query',
            'type': 'string',
            'format': 'date-time',
            'description': 'Reservation start time',
        },
        'end_time': {
            'in': 'query',
            'type': 'string',
            'format': 'date-time',
            'description': 'Reservation end time',
        },
        'status': ResvStatus.ARGS['status'],
    }

    @staticmethod
    def args(only=None, exclude=()):
        return _args(Reservation.ARGS, only, exclude)
    
    @staticmethod
    def ts_schema(many=False, only=None, exclude=(), load_only=(), dump_only=()):
        class Schema(_Schema):
            slot_id = fields.Int()
            status = fields.Int()
            start_time = fields.DateTime()
            end_time = fields.DateTime()
        return Schema(many=many, only=only, exclude=exclude, load_only=load_only, dump_only=dump_only)
    
    @staticmethod
    def schema(many=False, only=None, exclude=(), load_only=(), dump_only=()):
        class Schema(_Schema):
            resv_id = fields.Int()
            username = fields.Str()
            room_id = fields.Int()
            session_id = fields.Int()
            privacy = fields.Int()
            title = fields.Str()
            note = fields.Str()
            create_time = fields.DateTime(dump_only=True)
            update_time = fields.DateTime(dump_only=True)
            time_slots = fields.List(fields.Nested(Reservation.ts_schema()))
        return Schema(many=many, only=only, exclude=exclude, load_only=load_only, dump_only=dump_only)
    

class Session:
    TABLE = "sessions"

    # openapi (swagger) parameters
    ARGS = {
        'session_id': {
            'in': 'query',
            'type': 'integer',
            'description': 'Session ID',
        },
        'name': {
            'in': 'query',
            'type': 'string',
            'description': 'Session name',
        },
        'start_time': {
            'in': 'query',
            'type': 'string',
            'format': 'date-time',
            'description': 'Session start time',
        },
        'end_time': {
            'in': 'query',
            'type': 'string',
            'format': 'date-time',
            'description': 'Session end time',
        },
        'is_current': {
            'in': 'query',
            'type': 'integer',
            'description': '0 if not current session, any other value otherwise',
            'enum': [0, 1],
        },
    }

    @staticmethod
    def args(only=None, exclude=()):
        return _args(Session.ARGS, only, exclude)

    @staticmethod
    def schema(many=False, only=None, exclude=(), load_only=(), dump_only=()):
        class Schema(_Schema):
            session_id = fields.Int()
            name = fields.Str()
            start_time = fields.DateTime()
            end_time = fields.DateTime()
            is_current = fields.Bool()
        return Schema(many=many, only=only, exclude=exclude, load_only=load_only, dump_only=dump_only)

class Period: 
    TABLE = "periods"

    # openapi (swagger) parameters
    ARGS = {
        'period_id': {
            'in': 'query',
            'type': 'integer',
            'description': 'Period ID',
        },
        'name': {
            'in': 'query',
            'type': 'string',
            'description': 'Period name',
        },
        'start_time': {
            'in': 'query',
            'type': 'string',
            'format': 'time',
            'description': 'Period start time',
        },
        'end_time': {
            'in': 'query',
            'type': 'string',
            'format': 'time',
            'description': 'Period end time',
        },
    }

    @staticmethod
    def args(only=None, exclude=()):
        return _args(Period.ARGS, only, exclude)

    @staticmethod
    def schema(many=False, only=None, exclude=(), load_only=(), dump_only=()):
        class Schema(_Schema):
            period_id = fields.Int()
            name = fields.Str()
            start_time = _TimeDeltaField()
            end_time = _TimeDeltaField()
        return Schema(many=many, only=only, exclude=exclude, load_only=load_only, dump_only=dump_only)
  
class Notice:
    TABLE = "notices"

    # openapi (swagger) parameters
    ARGS = {
        'notice_id': {
            'in': 'query',
            'type': 'integer',
            'description': 'Notice ID',
        },
        'username': User.ARGS['username'],
        'title': {
            'in': 'query',
            'type': 'string',
            'description': 'Notice title',
        },
        'content': {
            'in': 'query',
            'type': 'string',
            'description': 'Notice content',
        },
        'create_time': {
            'in': 'query',
            'type': 'string',
            'format': 'date-time',
            'description': 'Notice creation time',
        },
        'update_time': {
            'in': 'query',
            'type': 'string',
            'format': 'date-time',
            'description': 'Notice last update time',
        },
    }

    @staticmethod
    def args(only=None, exclude=()):
        return _args(Notice.ARGS, only, exclude)

    @staticmethod
    def schema(many=False, only=None, exclude=(), load_only=(), dump_only=()):
        class Schema(_Schema):
            notice_id = fields.Int()
            username = fields.Str()
            title = fields.Str()
            content = fields.Str()
            create_time = fields.DateTime()
            update_time = fields.DateTime()
        return Schema(many=many, only=only, exclude=exclude, load_only=load_only, dump_only=dump_only)

class _TimeDeltaField(fields.TimeDelta):
    def _serialize(self, value, attr, obj, **kwargs):
        seconds = super()._serialize(value, attr, obj, **kwargs)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return "%02d:%02d:%02d" % (h, m, s)

class _ImageField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return base64.b64encode(value).decode('utf-8')

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        return base64.b64decode(value)

def _args(args, only=None, exclude=()):
    res = {k: v for k, v in args.items() if k not in exclude}
    return res if not only else {k: v for k, v in res.items() if k in only}

# ==============================================================
# INSERT Immutable Data
# ==============================================================
IMMUTABLE_INSERTS = f"""
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
({UserRole.RESTRICTED}, '待审核'),
({UserRole.GUEST}, '来宾'),
({UserRole.BASIC}, '基础用户'),
({UserRole.ADVANCED}, '高级用户'),
({UserRole.ADMIN}, '管理员');

INSERT INTO {Setting.TABLE} (id, value, name, description) VALUES
({Setting.TIME_WINDOW}, '72:00:00', '时间窗口', '从当前时间开始，用户最多可以提前多久预约房间'),
({Setting.TIME_LIMIT}, '4:00:00', '时间限', '用户预约房间的最长时间'),
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
