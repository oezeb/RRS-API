drop table if exists reservations;
drop table if exists reservation_tickets;
drop table if exists users;
drop table if exists sessions;
drop table if exists rooms;
drop table if exists periods;
drop view  if exists reservations_view;

/*==============================================================*/
/* Table: periods                                               */
/*==============================================================*/
create table periods 
(
   period_id            integer auto_increment         not null,
   name                 varchar(50)                    not null,
   start_time           time                           not null,
   end_time             time                           not null,
   constraint PK_PERIODS primary key clustered (period_id)
);

/*==============================================================*/
/* Table: rooms                                                 */
/*==============================================================*/
create table rooms 
(
   room_id              integer auto_increment         not null,
   name                 varchar(50)                    not null,
   seating_capacity     integer                        not null,
   open_time            time                           not null,
   close_time           time                           not null,
   type                 integer                        not null,
   status               integer                        default 0,
   constraint PK_ROOMS primary key clustered (room_id)
);

/*==============================================================*/
/* Table: sessions                                              */
/*==============================================================*/
create table sessions 
(
   session_id           integer auto_increment         not null,
   name                 varchar(50)                    not null,
   is_current           bit                            null,
   start_time           timestamp                      not null,
   end_time             timestamp                      not null,
   constraint PK_SESSIONS primary key clustered (session_id)
);

/*==============================================================*/
/* Table: users                                                 */
/*==============================================================*/
create table users 
(
   username             varchar(50)                    not null,
   password             varchar(1024)                    not null,
   name                 varchar(50)                    null,
   level                integer                        default 0,
   email                varchar(100)                   null,
   constraint PK_USERS primary key clustered (username)
);

/*==============================================================*/
/* Table: reservation_tickets                                   */
/*==============================================================*/
create table reservation_tickets 
(
   reservation_id       integer auto_increment         not null,
   username             varchar(50)                    not null,
   constraint PK_RESERVATION_TICKETS primary key clustered (reservation_id),
   constraint FK_RESERVAT_USER_RESE_USERS foreign key (username)
      references users (username)
      on update cascade
      on delete cascade
);

/*==============================================================*/
/* Table: reservations                                          */
/*==============================================================*/
create table reservations 
(
   reservation_no       integer                        not null,
   reservation_id       integer                        not null,
   room_id              integer                        not null,
   session_id           integer                        not null,
   start_time           timestamp                      not null,
   end_time             timestamp                      not null,
   status               integer                        default 0,
   note                 varchar(100)                   null,
   create_time          timestamp                      null,
   update_time          timestamp                      null,
   cancel_time          timestamp                      null,
   constraint PK_RESERVATIONS primary key clustered (reservation_id, reservation_no),
   constraint FK_RESERVAT_RESERVATI_RESERVAT foreign key (reservation_id)
      references reservation_tickets (reservation_id)
      on update cascade
      on delete cascade,
   constraint FK_RESERVAT_ROOM_RESE_ROOMS foreign key (room_id)
      references rooms (room_id)
      on update cascade
      on delete cascade,
   constraint FK_RESERVAT_SESSION_R_SESSIONS foreign key (session_id)
      references sessions (session_id)
      on update cascade
      on delete cascade
);
create index idx_reservation_no ON reservations (reservation_no);
alter table reservations MODIFY COLUMN reservation_no INTEGER AUTO_INCREMENT;

/*================================================================*/
/* View: Reservations                                             */
/*================================================================*/

create view reservations_view as 
   select 
      reservation_id,
      reservation_no,
      username,
      users.name as name,
      room_id,
      rooms.name as room_name,
      open_time,
      close_time,
      rooms.status as room_status,
      session_id,
      sessions.name as session_name,
      sessions.start_time as session_start_time,
      sessions.end_time as session_end_time,
      reservations.start_time as reservation_start_time,
      reservations.end_time as reservation_end_time,
      reservations.status as reservation_status,
      note,
      create_time,
      update_time,
      cancel_time 
   from 
      reservations natural join 
      reservation_tickets join 
      sessions using(session_id) join 
      rooms using(room_id) join 
      users using (username);
