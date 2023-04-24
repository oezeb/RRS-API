SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

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
   
   id                   INTEGER AUTO_INCREMENT         NOT NULL,
   value                VARCHAR(255)                   NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   CONSTRAINT settings_pk PRIMARY KEY (id)
);

/*==============================================================*/
/* Table: periods                                               */
/*==============================================================*/
CREATE TABLE periods 
(
   period_id            INTEGER AUTO_INCREMENT         NOT NULL,
   start_time           TIME                           NOT NULL,
   end_time             TIME                           NOT NULL,
   CONSTRAINT periods_pk PRIMARY KEY (period_id),
   CHECK (start_time < end_time)
);

/*==============================================================*/
/* Table: user_roles                                            */
/*==============================================================*/
CREATE TABLE user_roles 
(
   role                 INTEGER AUTO_INCREMENT         NOT NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   CONSTRAINT user_roles_pk PRIMARY KEY (role)
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
   CONSTRAINT users_pk PRIMARY KEY (username),
   CONSTRAINT users_users_roles_fk
   FOREIGN KEY (role) 
      REFERENCES user_roles (role) 
      ON UPDATE CASCADE ON DELETE RESTRICT
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
   CONSTRAINT notices_pk PRIMARY KEY (username, notice_id),
   CONSTRAINT notices_users_fk
   FOREIGN KEY (username) 
      REFERENCES users (username)
      ON UPDATE CASCADE ON DELETE RESTRICT,
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
   CONSTRAINT sessions_pk PRIMARY KEY (session_id),
   CHECK (start_time < end_time)
);

/*==============================================================*/
/* Table: room_status                                           */
/*==============================================================*/
CREATE TABLE room_status 
(
   status               INTEGER AUTO_INCREMENT         NOT NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   CONSTRAINT room_status_pk PRIMARY KEY (status)
);

/*==============================================================*/
/* Table: room_types                                            */
/*==============================================================*/
CREATE TABLE room_types 
(
   type                 INTEGER AUTO_INCREMENT         NOT NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   CONSTRAINT room_types_pk PRIMARY KEY (type)
);

/*==============================================================*/
/* Table: rooms                                                 */
/*==============================================================*/
CREATE TABLE rooms 
(
   room_id              INTEGER AUTO_INCREMENT         NOT NULL,
   status               INTEGER                        NOT NULL,
   name                 VARCHAR(50)                    NOT NULL,
   capacity             INTEGER                        NOT NULL,
   type                 INTEGER                        NOT NULL,
   image                BLOB                           NULL,
   CONSTRAINT rooms_pk PRIMARY KEY (room_id),
   CONSTRAINT rooms_room_status_fk
   FOREIGN KEY (status) 
      REFERENCES room_status (status) 
      ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT rooms_room_types_fk
   FOREIGN KEY (type) 
      REFERENCES room_types(type) 
      ON UPDATE CASCADE ON DELETE RESTRICT
);

/*==============================================================*/
/* Table: resv_secu_levels                                      */
/*==============================================================*/
CREATE TABLE resv_secu_levels 
(
   secu_level           INTEGER AUTO_INCREMENT         NOT NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   CONSTRAINT resv_secu_levels_pk PRIMARY KEY (secu_level)
);

/*==============================================================*/
/* Table: resv_status                                           */
/*==============================================================*/
CREATE TABLE resv_status 
(
   status               INTEGER  AUTO_INCREMENT        NOT NULL,
   label                VARCHAR(50)                    NOT NULL,
   description          VARCHAR(200)                   NULL,
   CONSTRAINT resv_status_pk PRIMARY KEY (status)
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
   session_id           INTEGER                        NULL,
   status               INTEGER                        NOT NULL,
   title                VARCHAR(50)                    NOT NULL,
   note                 VARCHAR(100)                   NULL,
   create_time          TIMESTAMP                      NOT NULL DEFAULT CURRENT_TIMESTAMP,
   update_time          TIMESTAMP                      NULL ON UPDATE CURRENT_TIMESTAMP,
   CONSTRAINT reservations_pk PRIMARY KEY (username, resv_id),
   CONSTRAINT reservations_rooms_fk
   FOREIGN KEY (room_id) 
      REFERENCES rooms(room_id) 
      ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT reservations_resv_secu_levels_fk
   FOREIGN KEY (secu_level) 
      REFERENCES resv_secu_levels(secu_level) 
      ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT reservations_sessions_fk
   FOREIGN KEY (session_id)
      REFERENCES sessions(session_id) 
      ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT reservations_resv_status_fk
   FOREIGN KEY (status) 
      REFERENCES resv_status(status) 
      ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT reservations_users_fk
   FOREIGN KEY (username) 
      REFERENCES users(username) 
      ON UPDATE CASCADE ON DELETE RESTRICT,
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
   CONSTRAINT time_slots_pk PRIMARY KEY (username, resv_id, slot_id),
   CONSTRAINT time_slots_reservations_fk
   FOREIGN KEY (username, resv_id) 
      REFERENCES reservations (username, resv_id) 
      ON UPDATE CASCADE ON DELETE RESTRICT,
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
   CONSTRAINT languages_pk PRIMARY KEY (lang_code)
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
   CONSTRAINT setting_trans_pk
   PRIMARY KEY (lang_code, id),
   CONSTRAINT setting_trans_languages_fk
   FOREIGN KEY (lang_code)
      REFERENCES languages (lang_code)
      ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT setting_trans_settings_fk
   FOREIGN KEY (id)
      REFERENCES settings (id)
      ON UPDATE CASCADE ON DELETE RESTRICT
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
   CONSTRAINT user_role_trans_pk
   PRIMARY KEY (role, lang_code),
   CONSTRAINT user_role_trans_languages_fk
   FOREIGN KEY (lang_code) 
      REFERENCES languages(lang_code) 
      ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT user_role_trans_user_roles_fk
   FOREIGN KEY (role) 
      REFERENCES user_roles (role) 
      ON UPDATE CASCADE ON DELETE RESTRICT
);

/*==============================================================*/
/* Table: user_trans                                            */
/*==============================================================*/
CREATE TABLE user_trans 
(
   username             VARCHAR(50)                    NOT NULL,
   lang_code            VARCHAR(35)                    NOT NULL,
   name                 VARCHAR(50)                    NOT NULL,
   CONSTRAINT user_trans_pk
   PRIMARY KEY (username, lang_code),
   CONSTRAINT user_trans_languages_fk
   FOREIGN KEY (lang_code) 
      REFERENCES languages(lang_code) 
      ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT user_trans_users_fk
   FOREIGN KEY (username) 
      REFERENCES users(username) 
      ON UPDATE CASCADE ON DELETE RESTRICT
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
   CONSTRAINT notice_trans_pk
   PRIMARY KEY (username, notice_id, lang_code),
   CONSTRAINT notice_trans_languages_fk
   FOREIGN KEY (lang_code) 
      REFERENCES languages (lang_code)
      ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT notice_trans_notices_fk
   FOREIGN KEY (username, notice_id)
      REFERENCES notices (username, notice_id)
      ON UPDATE CASCADE ON DELETE RESTRICT
);

/*==============================================================*/
/* Table: session_trans                                         */
/*==============================================================*/
CREATE TABLE session_trans 
(
   lang_code            VARCHAR(35)                    NOT NULL,
   session_id           INTEGER                        NOT NULL,
   name                 VARCHAR(50)                    NOT NULL,
   CONSTRAINT session_trans_pk
   PRIMARY KEY (lang_code, session_id),
   CONSTRAINT session_trans_languages_fk
   FOREIGN KEY (lang_code) 
      REFERENCES languages(lang_code) 
      ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT session_trans_sessions_fk
   FOREIGN KEY (session_id) 
      REFERENCES sessions(session_id) 
      ON UPDATE CASCADE ON DELETE RESTRICT
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
   CONSTRAINT room_status_trans_pk
   PRIMARY KEY (status, lang_code),
   CONSTRAINT room_status_trans_languages_fk
   FOREIGN KEY (lang_code) 
      REFERENCES languages(lang_code) 
      ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT room_status_trans_room_status_fk
   FOREIGN KEY (status) 
      REFERENCES room_status (status) 
      ON UPDATE CASCADE ON DELETE RESTRICT
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
   CONSTRAINT room_type_trans_pk
   PRIMARY KEY (lang_code, type),
   CONSTRAINT room_type_trans_languages_fk
   FOREIGN KEY (lang_code) 
      REFERENCES languages(lang_code) 
      ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT room_type_trans_room_types_fk
   FOREIGN KEY (type) 
      REFERENCES room_types (type) 
      ON UPDATE CASCADE ON DELETE RESTRICT
);

/*==============================================================*/
/* Table: room_trans                                            */
/*==============================================================*/
CREATE TABLE room_trans 
(
   lang_code            VARCHAR(35)                    NOT NULL,
   room_id              INTEGER                        NOT NULL,
   name                 VARCHAR(50)                    NOT NULL,
   CONSTRAINT room_trans_pk
   PRIMARY KEY (lang_code, room_id),
   CONSTRAINT room_trans_languages_fk
   FOREIGN KEY (lang_code) 
      REFERENCES languages(lang_code) 
      ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT room_trans_rooms_fk
   FOREIGN KEY (room_id) 
      REFERENCES rooms(room_id) 
      ON UPDATE CASCADE ON DELETE RESTRICT
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
   CONSTRAINT resv_secu_level_trans_pk
   PRIMARY KEY (lang_code, secu_level),
   CONSTRAINT resv_secu_level_trans_languages_fk
   FOREIGN KEY (lang_code) 
      REFERENCES languages(lang_code) 
      ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT resv_secu_level_trans_resv_secu_levels_fk
   FOREIGN KEY (secu_level) 
      REFERENCES resv_secu_levels (secu_level) 
      ON UPDATE CASCADE ON DELETE RESTRICT
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
   CONSTRAINT resv_status_trans_pk
   PRIMARY KEY (lang_code, status),
   CONSTRAINT resv_status_trans_languages_fk
   FOREIGN KEY (lang_code) 
      REFERENCES languages   (lang_code) 
      ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT resv_status_trans_resv_status_fk
   FOREIGN KEY (status) 
      REFERENCES resv_status (status) 
      ON UPDATE CASCADE ON DELETE RESTRICT
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
   CONSTRAINT resv_trans_pk
   PRIMARY KEY (username, lang_code, resv_id),
   CONSTRAINT resv_trans_languages_fk
   FOREIGN KEY (lang_code) 
      REFERENCES languages(lang_code) 
      ON UPDATE CASCADE ON DELETE RESTRICT,
   CONSTRAINT resv_trans_reservations_fk
   FOREIGN KEY (username, resv_id) 
      REFERENCES reservations (username, resv_id) 
      ON UPDATE CASCADE ON DELETE RESTRICT
);

/*--------------------------------------------------------------*/
