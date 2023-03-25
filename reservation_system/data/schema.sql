drop table if exists resv_trans;
drop table if exists resv_status_trans;
drop table if exists resv_secu_level_trans;
drop table if exists room_trans;
drop table if exists room_type_trans;
drop table if exists room_status_trans;
drop table if exists session_trans;
drop table if exists user_trans;
drop table if exists user_role_trans;
drop table if exists languages;
drop table if exists time_slots;
drop table if exists reservations;
drop table if exists resv_status;
drop table if exists resv_secu_levels;
drop table if exists rooms;
drop table if exists room_types;
drop table if exists room_status;
drop table if exists sessions;
drop table if exists users;
drop table if exists user_roles;
drop table if exists periods;
drop table if exists resv_windows;

/*==============================================================*/
/* Table: resv_windows                                          */
/*==============================================================*/
create table resv_windows 
(
   window_id            integer auto_increment         not null,
   time_window          time                           not null,
   is_current           bit                            not null,
   primary key (window_id)
);

/*==============================================================*/
/* Table: periods                                               */
/*==============================================================*/
create table periods 
(
   period_id            integer auto_increment         not null,
   start_time           time                           not null,
   end_time             time                           not null,
   primary key (period_id)
);

/*==============================================================*/
/* Table: user_roles                                            */
/*==============================================================*/
create table user_roles 
(
   role                 integer                        not null,
   label                varchar(50)                    not null,
   description          varchar(200)                   null,
   primary key (role)
);

/*==============================================================*/
/* Table: users                                                 */
/*==============================================================*/
create table users 
(
   username             varchar(50)                    not null,
   role                 integer                        not null,
   password             varchar(1024)                  not null,
   name                 varchar(50)                    null,
   email                varchar(50)                    null,
   primary key (username),
   foreign key (role) 
      references user_roles (role) 
      on update cascade on delete cascade
);

/*==============================================================*/
/* Table: sessions                                              */
/*==============================================================*/
create table sessions 
(
   session_id           integer auto_increment         not null,
   name                 varchar(50)                    not null,
   start_time           timestamp                      not null,
   end_time             timestamp                      not null,
   is_current           bit                       null,
   primary key (session_id)
);

/*==============================================================*/
/* Table: room_status                                           */
/*==============================================================*/
create table room_status 
(
   status               integer                        not null,
   label                varchar(50)                    not null,
   description          varchar(200)                   null,
   primary key (status)
);

/*==============================================================*/
/* Table: room_types                                            */
/*==============================================================*/
create table room_types 
(
   type                 integer auto_increment         not null,
   label                varchar(50)                    not null,
   description          varchar(200)                   null,
   primary key (type)
);

/*==============================================================*/
/* Table: rooms                                                 */
/*==============================================================*/
create table rooms 
(
   room_id              integer auto_increment         not null,
   type                 integer                        not null,
   status               integer                        not null,
   name                 varchar(50)                    not null,
   seating_capacity     integer                        not null,
   open_time            time                           not null,
   close_time           time                           not null,
   primary key (room_id),
   foreign key (status) 
      references room_status (status) 
      on update cascade on delete cascade,
   foreign key (type) 
      references room_types(type) 
      on update cascade on delete cascade
);

/*==============================================================*/
/* Table: resv_secu_levels                                      */
/*==============================================================*/
create table resv_secu_levels 
(
   secu_level           integer                        not null,
   label                varchar(50)                    not null,
   description          varchar(200)                   null,
   primary key (secu_level)
);

/*==============================================================*/
/* Table: resv_status                                           */
/*==============================================================*/
create table resv_status 
(
   status               integer auto_increment         not null,
   label                varchar(50)                    not null,
   description          varchar(200)                   null,
   primary key (status)
);

/*==============================================================*/
/* Table: reservations                                          */
/*==============================================================*/
create table reservations 
(
   username             varchar(50)                    not null,
   resv_id              integer                        not null,
   room_id              integer                        not null,
   secu_level           integer                        not null,
   session_id           integer                        not null,
   status               integer                        not null,
   note                 varchar(100)                   null,
   create_time          timestamp                      null,
   update_time          timestamp                      null,
   cancel_time          timestamp                      null,
   primary key (username, resv_id),
   foreign key (room_id) 
      references rooms(room_id   ) 
      on update cascade on delete cascade,
   foreign key (secu_level) 
      references resv_secu_levels(secu_level) 
      on update cascade on delete cascade,
   foreign key (session_id) 
      references sessions(session_id) 
      on update cascade on delete cascade,
   foreign key (status) 
      references resv_status(status) 
      on update cascade on delete cascade,
   foreign key (username) 
      references users(username) 
      on update cascade on delete cascade
);
create index idx_resv_id ON reservations (resv_id);
alter table reservations modify column resv_id integer auto_increment;

/*==============================================================*/
/* Table: time_slots                                            */
/*==============================================================*/
create table time_slots 
(
   username             varchar(50)                    not null,
   resv_id              integer                        not null,
   slot_id              integer                        not null,
   start_time           timestamp                      not null,
   end_time             timestamp                      not null,
   primary key (username, resv_id, slot_id),
   foreign key (username, resv_id) 
      references reservations (username, resv_id) 
      on update cascade on delete cascade
);
create index idx_slot_id ON time_slots (slot_id);
alter table time_slots modify column slot_id integer auto_increment;

/*==============================================================*/
/* Table: languages                                             */
/*==============================================================*/
create table languages 
(
   lang_code            varchar(35)                    not null,
   name                 varchar(50)                    not null,
   primary key (lang_code)
);

/*==============================================================*/
/* Table: user_role_trans                                       */
/*==============================================================*/
create table user_role_trans 
(
   role                 integer                        not null,
   lang_code            varchar(35)                    not null,
   label                varchar(50)                    not null,
   description          varchar(200)                   null,
   primary key (role, lang_code),
   foreign key (role) 
      references user_roles (role) 
      on update cascade on delete cascade,
   foreign key (lang_code) 
      references languages(lang_code) 
      on update cascade on delete cascade
);

/*==============================================================*/
/* Table: user_trans                                            */
/*==============================================================*/
create table user_trans 
(
   username             varchar(50)                    not null,
   lang_code            varchar(35)                    not null,
   name                 varchar(50)                    not null,
   primary key (username, lang_code),
   foreign key (username) 
      references users(username) 
      on update cascade on delete cascade,
   foreign key (lang_code) 
      references languages(lang_code) 
      on update cascade on delete cascade
);

/*==============================================================*/
/* Table: session_trans                                         */
/*==============================================================*/
create table session_trans 
(
   lang_code            varchar(35)                    not null,
   session_id           integer                        not null,
   name                 varchar(50)                    not null,
   primary key (lang_code, session_id),
   foreign key (lang_code) 
      references languages(lang_code) 
      on update cascade on delete cascade,
   foreign key (session_id) 
      references sessions(session_id) 
      on update cascade on delete cascade
);

/*==============================================================*/
/* Table: room_status_trans                                     */
/*==============================================================*/
create table room_status_trans 
(
   status               integer                        not null,
   lang_code            varchar(35)                    not null,
   label                varchar(50)                    not null,
   description          varchar(200)                   null,
   primary key (status, lang_code),
   foreign key (status) 
      references room_status (status) 
      on update cascade on delete cascade,
   foreign key (lang_code) 
      references languages(lang_code) 
      on update cascade on delete cascade
);

/*==============================================================*/
/* Table: room_type_trans                                       */
/*==============================================================*/
create table room_type_trans 
(
   lang_code            varchar(35)                    not null,
   type                 integer                        not null,
   label                varchar(50)                    not null,
   description          varchar(200)                   null,
   primary key (lang_code, type),
   foreign key (lang_code) 
      references languages(lang_code) 
      on update cascade on delete cascade,
   foreign key (type) 
      references room_types (type) 
      on update cascade on delete cascade
);

/*==============================================================*/
/* Table: room_trans                                            */
/*==============================================================*/
create table room_trans 
(
   lang_code            varchar(35)                    not null,
   room_id              integer                        not null,
   name                 varchar(50)                    not null,
   primary key (lang_code, room_id),
   foreign key (lang_code) 
      references languages(lang_code) 
      on update cascade on delete cascade,
   foreign key (room_id) 
      references rooms(room_id) 
      on update cascade on delete cascade
);

/*==============================================================*/
/* Table: resv_secu_level_trans                                 */
/*==============================================================*/
create table resv_secu_level_trans 
(
   lang_code            varchar(35)                    not null,
   secu_level           integer                        not null,
   label                varchar(50)                    not null,
   description          varchar(200)                   null,
   primary key (lang_code, secu_level),
   foreign key (lang_code) 
      references languages(lang_code) 
      on update cascade on delete cascade,
   foreign key (secu_level) 
      references resv_secu_levels (secu_level) 
      on update cascade on delete cascade
);

/*==============================================================*/
/* Table: resv_status_trans                                     */
/*==============================================================*/
create table resv_status_trans 
(
   lang_code            varchar(35)                    not null,
   status               integer                        not null,
   label                varchar(50)                    not null,
   description          varchar(200)                   null,
   primary key (lang_code, status),
   foreign key (lang_code) 
      references languages   (lang_code) 
      on update cascade on delete cascade,
   foreign key (status) 
      references resv_status (status) 
      on update cascade on delete cascade
);

/*==============================================================*/
/* Table: resv_trans                                            */
/*==============================================================*/
create table resv_trans 
(
   lang_code            varchar(35)                    not null,
   username             varchar(50)                    not null,
   resv_id              integer                        not null,
   note                 varchar(100)                   not null,
   primary key (username, lang_code, resv_id),
   foreign key (lang_code) 
      references languages(lang_code) 
      on update cascade on delete cascade,
   foreign key (username, resv_id) 
      references reservations (username, resv_id) 
      on update cascade on delete cascade
);
