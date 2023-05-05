DROP TABLE IF EXISTS            resv_trans;
DROP TABLE IF EXISTS     resv_status_trans;
DROP TABLE IF EXISTS resv_secu_level_trans;
DROP TABLE IF EXISTS            room_trans;
DROP TABLE IF EXISTS       room_type_trans;
DROP TABLE IF EXISTS     room_status_trans;
DROP TABLE IF EXISTS         session_trans;
DROP TABLE IF EXISTS          notice_trans;
DROP TABLE IF EXISTS            user_trans;
DROP TABLE IF EXISTS       user_role_trans;
DROP TABLE IF EXISTS         setting_trans;
DROP TABLE IF EXISTS             languages;
DROP TABLE IF EXISTS            time_slots;
DROP TABLE IF EXISTS          reservations;
DROP TABLE IF EXISTS           resv_status;
DROP TABLE IF EXISTS      resv_secu_levels;
DROP TABLE IF EXISTS                 rooms;
DROP TABLE IF EXISTS            room_types;
DROP TABLE IF EXISTS           room_status;
DROP TABLE IF EXISTS              sessions;
DROP TABLE IF EXISTS               notices;
DROP TABLE IF EXISTS                 users;
DROP TABLE IF EXISTS            user_roles;
DROP TABLE IF EXISTS               periods;
DROP TABLE IF EXISTS              settings;

/*==============================================================*/
/* Table: settings                                              */
/*==============================================================*/
CREATE TABLE settings
(
   
   id                   INTEGER                        NOT NULL,
   value                VARCHAR(255)                   NOT NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   PRIMARY KEY (id)
);

/*==============================================================*/
/* Table: periods                                               */
/*==============================================================*/
CREATE TABLE periods 
(
   period_id            INTEGER AUTO_INCREMENT         NOT NULL,
   start_time           TIME                           NOT NULL,
   end_time             TIME                           NOT NULL,
   PRIMARY KEY (period_id),
   CHECK (start_time < end_time)
);

/*==============================================================*/
/* Table: user_roles                                            */
/*==============================================================*/
CREATE TABLE user_roles 
(
   role                 INTEGER                        NOT NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   PRIMARY KEY (role)
);

/*==============================================================*/
/* Table: users                                                 */
/*==============================================================*/
CREATE TABLE users 
(
   username             VARCHAR(50)                    NOT NULL CHECK (username <> ''),
   name                 VARCHAR(50)                    NOT NULL CHECK (name <> ''),
   password             VARCHAR(1024)                  NOT NULL,
   role                 INTEGER                        NOT NULL,
   email                VARCHAR(50)                    NULL,
   PRIMARY KEY (username),
   FOREIGN KEY (role) 
      REFERENCES user_roles (role) 
      ON UPDATE CASCADE ON DELETE CASCADE
);

/*==============================================================*/
/* Table: notices                                               */
/*==============================================================*/
CREATE TABLE notices 
(
   username             VARCHAR(50)                    NOT NULL,
   notice_id            INTEGER                        NOT NULL,
   title                VARCHAR(100)                   NOT NULL,
   content              TEXT                           NOT NULL,
   create_time          TIMESTAMP                      NOT NULL DEFAULT CURRENT_TIMESTAMP,
   update_time          TIMESTAMP                      NULL ON UPDATE CURRENT_TIMESTAMP,
   PRIMARY KEY (username, notice_id),
   FOREIGN KEY (username) 
      REFERENCES users (username)
      ON UPDATE CASCADE ON DELETE CASCADE,
   CHECK (create_time <= update_time)
);
/* Make notice_id auto increment */
CREATE INDEX idx_notice_id ON notices (notice_id);
ALTER TABLE notices MODIFY COLUMN notice_id INTEGER AUTO_INCREMENT;

/*==============================================================*/
/* Table: sessions                                              */
/*==============================================================*/
CREATE TABLE sessions 
(
   session_id           INTEGER AUTO_INCREMENT         NOT NULL,
   name                 VARCHAR(50)                    NOT NULL,
   start_time           TIMESTAMP                      NOT NULL,
   end_time             TIMESTAMP                      NOT NULL,
   is_current           BIT                            NULL,
   PRIMARY KEY (session_id),
   CHECK (start_time < end_time)
);

/*==============================================================*/
/* Table: room_status                                           */
/*==============================================================*/
CREATE TABLE room_status 
(
   status               INTEGER                        NOT NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   PRIMARY KEY (status)
);

/*==============================================================*/
/* Table: room_types                                            */
/*==============================================================*/
CREATE TABLE room_types 
(
   type                 INTEGER AUTO_INCREMENT         NOT NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   PRIMARY KEY (type)
);

/*==============================================================*/
/* Table: rooms                                                 */
/*==============================================================*/
CREATE TABLE rooms 
(
   room_id              INTEGER AUTO_INCREMENT         NOT NULL,
   type                 INTEGER                        NOT NULL,
   status               INTEGER                        NOT NULL,
   name                 VARCHAR(50)                    NOT NULL,
   capacity             INTEGER                        NOT NULL,
   PRIMARY KEY (room_id),
   FOREIGN KEY (status) 
      REFERENCES room_status (status) 
      ON UPDATE CASCADE ON DELETE CASCADE,
   FOREIGN KEY (type) 
      REFERENCES room_types(type) 
      ON UPDATE CASCADE ON DELETE CASCADE
);

/*==============================================================*/
/* Table: resv_secu_levels                                      */
/*==============================================================*/
CREATE TABLE resv_secu_levels 
(
   secu_level           INTEGER                        NOT NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   PRIMARY KEY (secu_level)
);

/*==============================================================*/
/* Table: resv_status                                           */
/*==============================================================*/
CREATE TABLE resv_status 
(
   status               INTEGER                        NOT NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   PRIMARY KEY (status)
);

/*==============================================================*/
/* Table: reservations                                          */
/*==============================================================*/
CREATE TABLE reservations 
(
   username             VARCHAR(50)                    NOT NULL,
   resv_id              INTEGER                        NOT NULL,
   room_id              INTEGER                        NOT NULL,
   secu_level           INTEGER                        NOT NULL,
   session_id           INTEGER                        NOT NULL,
   status               INTEGER                        NOT NULL,
   title                VARCHAR(50)                    NOT NULL,
   note                 VARCHAR(100)                   NULL,
   create_time          TIMESTAMP                      NOT NULL DEFAULT CURRENT_TIMESTAMP,
   update_time          TIMESTAMP                      NULL ON UPDATE CURRENT_TIMESTAMP,
   PRIMARY KEY (username, resv_id),
   FOREIGN KEY (room_id) 
      REFERENCES rooms(room_id) 
      ON UPDATE CASCADE ON DELETE CASCADE,
   FOREIGN KEY (secu_level) 
      REFERENCES resv_secu_levels(secu_level) 
      ON UPDATE CASCADE ON DELETE CASCADE,
   FOREIGN KEY (session_id) 
      REFERENCES sessions(session_id) 
      ON UPDATE CASCADE ON DELETE CASCADE,
   FOREIGN KEY (status) 
      REFERENCES resv_status(status) 
      ON UPDATE CASCADE ON DELETE CASCADE,
   FOREIGN KEY (username) 
      REFERENCES users(username) 
      ON UPDATE CASCADE ON DELETE CASCADE,
   CHECK (create_time <= update_time)
);
/* Make resv_id auto-increment */
CREATE INDEX idx_resv_id ON reservations (resv_id);
ALTER TABLE reservations MODIFY COLUMN resv_id INTEGER AUTO_INCREMENT;

/*==============================================================*/
/* Table: time_slots                                            */
/*==============================================================*/
CREATE TABLE time_slots 
(
   username             VARCHAR(50)                    NOT NULL,
   resv_id              INTEGER                        NOT NULL,
   slot_id              INTEGER                        NOT NULL,
   start_time           TIMESTAMP                      NOT NULL,
   end_time             TIMESTAMP                      NOT NULL,
   PRIMARY KEY (username, resv_id, slot_id),
   FOREIGN KEY (username, resv_id) 
      REFERENCES reservations (username, resv_id) 
      ON UPDATE CASCADE ON DELETE CASCADE,
   CHECK (start_time < end_time)
);
/* Make slot_id auto-increment */
CREATE INDEX idx_slot_id ON time_slots (slot_id);
ALTER TABLE time_slots MODIFY COLUMN slot_id INTEGER AUTO_INCREMENT;

/*==============================================================*/
/* Table: languages                                             */
/*==============================================================*/
CREATE TABLE languages 
(
   lang_code            VARCHAR(35)                    NOT NULL,
   name                 VARCHAR(50)                    NOT NULL,
   PRIMARY KEY (lang_code)
);

/*==============================================================*/
/* Table: setting_trans                                         */
/*==============================================================*/
CREATE TABLE setting_trans 
(
   lang_code            VARCHAR(35)                    NOT NULL,
   id                   INTEGER                        NOT NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   PRIMARY KEY (lang_code, id),
   FOREIGN KEY (lang_code)
      REFERENCES languages (lang_code)
      ON UPDATE CASCADE ON DELETE CASCADE,
   FOREIGN KEY (id)
      REFERENCES settings (id)
      ON UPDATE CASCADE ON DELETE CASCADE
);

/*==============================================================*/
/* Table: user_role_trans                                       */
/*==============================================================*/
CREATE TABLE user_role_trans 
(
   role                 INTEGER                        NOT NULL,
   lang_code            VARCHAR(35)                    NOT NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   PRIMARY KEY (role, lang_code),
   FOREIGN KEY (role) 
      REFERENCES user_roles (role) 
      ON UPDATE CASCADE ON DELETE CASCADE,
   FOREIGN KEY (lang_code) 
      REFERENCES languages(lang_code) 
      ON UPDATE CASCADE ON DELETE CASCADE
);

/*==============================================================*/
/* Table: user_trans                                            */
/*==============================================================*/
CREATE TABLE user_trans 
(
   username             VARCHAR(50)                    NOT NULL,
   lang_code            VARCHAR(35)                    NOT NULL,
   name                 VARCHAR(50)                    NOT NULL,
   PRIMARY KEY (username, lang_code),
   FOREIGN KEY (username) 
      REFERENCES users(username) 
      ON UPDATE CASCADE ON DELETE CASCADE,
   FOREIGN KEY (lang_code) 
      REFERENCES languages(lang_code) 
      ON UPDATE CASCADE ON DELETE CASCADE
);

/*==============================================================*/
/* Table: notice_trans                                          */
/*==============================================================*/
CREATE TABLE notice_trans 
(
   username             VARCHAR(50)                    NOT NULL,
   notice_id            INTEGER                        NOT NULL,
   lang_code            VARCHAR(35)                    NOT NULL,
   title                VARCHAR(100)                   NOT NULL,
   content              TEXT                           NOT NULL,
   PRIMARY KEY (username, notice_id, lang_code),
   FOREIGN KEY (username, notice_id)
      REFERENCES notices (username, notice_id)
      ON UPDATE CASCADE ON DELETE CASCADE,
   FOREIGN KEY (lang_code) 
      REFERENCES languages (lang_code)
      ON UPDATE CASCADE ON DELETE CASCADE
);

/*==============================================================*/
/* Table: session_trans                                         */
/*==============================================================*/
CREATE TABLE session_trans 
(
   lang_code            VARCHAR(35)                    NOT NULL,
   session_id           INTEGER                        NOT NULL,
   name                 VARCHAR(50)                    NOT NULL,
   PRIMARY KEY (lang_code, session_id),
   FOREIGN KEY (lang_code) 
      REFERENCES languages(lang_code) 
      ON UPDATE CASCADE ON DELETE CASCADE,
   FOREIGN KEY (session_id) 
      REFERENCES sessions(session_id) 
      ON UPDATE CASCADE ON DELETE CASCADE
);

/*==============================================================*/
/* Table: room_status_trans                                     */
/*==============================================================*/
CREATE TABLE room_status_trans 
(
   status               INTEGER                        NOT NULL,
   lang_code            VARCHAR(35)                    NOT NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   PRIMARY KEY (status, lang_code),
   FOREIGN KEY (status) 
      REFERENCES room_status (status) 
      ON UPDATE CASCADE ON DELETE CASCADE,
   FOREIGN KEY (lang_code) 
      REFERENCES languages(lang_code) 
      ON UPDATE CASCADE ON DELETE CASCADE
);

/*==============================================================*/
/* Table: room_type_trans                                       */
/*==============================================================*/
CREATE TABLE room_type_trans 
(
   lang_code            VARCHAR(35)                    NOT NULL,
   type                 INTEGER                        NOT NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   PRIMARY KEY (lang_code, type),
   FOREIGN KEY (lang_code) 
      REFERENCES languages(lang_code) 
      ON UPDATE CASCADE ON DELETE CASCADE,
   FOREIGN KEY (type) 
      REFERENCES room_types (type) 
      ON UPDATE CASCADE ON DELETE CASCADE
);

/*==============================================================*/
/* Table: room_trans                                            */
/*==============================================================*/
CREATE TABLE room_trans 
(
   lang_code            VARCHAR(35)                    NOT NULL,
   room_id              INTEGER                        NOT NULL,
   name                 VARCHAR(50)                    NOT NULL,
   PRIMARY KEY (lang_code, room_id),
   FOREIGN KEY (lang_code) 
      REFERENCES languages(lang_code) 
      ON UPDATE CASCADE ON DELETE CASCADE,
   FOREIGN KEY (room_id) 
      REFERENCES rooms(room_id) 
      ON UPDATE CASCADE ON DELETE CASCADE
);

/*==============================================================*/
/* Table: resv_secu_level_trans                                 */
/*==============================================================*/
CREATE TABLE resv_secu_level_trans 
(
   lang_code            VARCHAR(35)                    NOT NULL,
   secu_level           INTEGER                        NOT NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   PRIMARY KEY (lang_code, secu_level),
   FOREIGN KEY (lang_code) 
      REFERENCES languages(lang_code) 
      ON UPDATE CASCADE ON DELETE CASCADE,
   FOREIGN KEY (secu_level) 
      REFERENCES resv_secu_levels (secu_level) 
      ON UPDATE CASCADE ON DELETE CASCADE
);

/*==============================================================*/
/* Table: resv_status_trans                                     */
/*==============================================================*/
CREATE TABLE resv_status_trans 
(
   lang_code            VARCHAR(35)                    NOT NULL,
   status               INTEGER                        NOT NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   PRIMARY KEY (lang_code, status),
   FOREIGN KEY (lang_code) 
      REFERENCES languages   (lang_code) 
      ON UPDATE CASCADE ON DELETE CASCADE,
   FOREIGN KEY (status) 
      REFERENCES resv_status (status) 
      ON UPDATE CASCADE ON DELETE CASCADE
);

/*==============================================================*/
/* Table: resv_trans                                            */
/*==============================================================*/
CREATE TABLE resv_trans 
(
   lang_code            VARCHAR(35)                    NOT NULL,
   username             VARCHAR(50)                    NOT NULL,
   resv_id              INTEGER                        NOT NULL,
   title                VARCHAR(50)                    NOT NULL,
   note                 VARCHAR(100)                   NULL,
   PRIMARY KEY (username, lang_code, resv_id),
   FOREIGN KEY (lang_code) 
      REFERENCES languages(lang_code) 
      ON UPDATE CASCADE ON DELETE CASCADE,
   FOREIGN KEY (username, resv_id) 
      REFERENCES reservations (username, resv_id) 
      ON UPDATE CASCADE ON DELETE CASCADE
);

/*--------------------------------------------------------------*/
DROP VIEW IF EXISTS resv_view;
DROP FUNCTION IF EXISTS period_conflict;
DROP FUNCTION IF EXISTS session_conflict;

/* Reservations view */
CREATE VIEW resv_view AS
SELECT * FROM reservations NATURAL JOIN time_slots WITH CHECK OPTION;
/* Ensure no period time conflict */
CREATE FUNCTION period_conflict (start_time TIME, end_time TIME)
RETURNS INTEGER
READS SQL DATA
BEGIN
   DECLARE conflict INTEGER;
   SELECT COUNT(*) INTO conflict FROM periods p
   WHERE (p.start_time=start_time AND p.end_time=end_time)
       OR (p.start_time>start_time AND p.start_time<end_time)
         OR (p.end_time>start_time AND p.end_time<end_time);
   RETURN conflict;
END;

CREATE TRIGGER insert_period_trigger BEFORE INSERT ON periods
FOR EACH ROW
BEGIN
   IF (period_conflict(NEW.start_time, NEW.end_time) > 0) THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Period time conflict.';
   END IF;
END;

CREATE TRIGGER update_period_trigger BEFORE UPDATE ON periods
FOR EACH ROW
BEGIN
   IF (period_conflict(NEW.start_time, NEW.end_time) > 0) THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Period time conflict.';
   END IF;
END;
/* Ensure no session time conflict */
CREATE FUNCTION session_conflict (start_time TIMESTAMP, end_time TIMESTAMP)
RETURNS INTEGER
READS SQL DATA
BEGIN
   DECLARE conflict INTEGER;
   SELECT COUNT(*) INTO conflict FROM sessions s
   WHERE (s.start_time=start_time AND s.end_time=end_time)
       OR (s.start_time>start_time AND s.start_time<end_time)
         OR (s.end_time>start_time AND s.end_time<end_time);
   RETURN conflict;
END;

CREATE TRIGGER insert_session_trigger BEFORE INSERT ON sessions
FOR EACH ROW
BEGIN
   IF (session_conflict(NEW.start_time, NEW.end_time) > 0) THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Session time conflict.';
   END IF;
END;

CREATE TRIGGER update_session_trigger BEFORE UPDATE ON sessions
FOR EACH ROW
BEGIN
   IF (session_conflict(NEW.start_time, NEW.end_time) > 0) THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Session time conflict.';
   END IF;
END;

/* Ensure no time slot conflicts
 * =============================
 * Some time slots may be allowed to overlap.
 * Cancelled reservations time slots for instance can be reused.
 * It depends on the reservation status.
 * Because status are not defined here, the trigger should be
 * implemented in the application.
 */

 /* Ensure time slot in its corresponding session */
CREATE TRIGGER insert_time_slot_trigger BEFORE INSERT ON time_slots
FOR EACH ROW
BEGIN
   DECLARE session_id INTEGER;
   SELECT session_id INTO session_id 
   FROM reservations r JOIN sessions s USING(session_id)
   WHERE r.resv_id=NEW.resv_id AND r.username=NEW.username
      AND NEW.start_time>=s.start_time AND NEW.end_time<=s.end_time;
   IF (session_id IS NULL) THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Time slot not in session.';
   END IF;
END;